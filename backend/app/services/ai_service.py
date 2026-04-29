"""
AI Service (OpenAI Wrapper)
Handles NL to SQL generation and Insight Generation.
"""

import json
import logging
import asyncio
from typing import Any
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
import openai

from app.config import get_settings
from app.database import async_session, engine
from app.models.insight import ChatHistory, Insight

settings = get_settings()
logger = logging.getLogger(__name__)


class AIService:
    def __init__(self):
        self.enabled = settings.has_openai_key
        if self.enabled:
            self.client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
            self.model = settings.openai_model
        else:
            self.client = None
            self.model = None

    async def get_db_schema(self) -> str:
        """Get database schema as string for LLM context."""
        # Hardcoding the schema for simplicity and token efficiency
        return """
        Table: customers
        Columns: id, name, email, segment, rfm_recency, rfm_frequency, rfm_monetary, rfm_score, churn_probability, total_orders, lifetime_value, avg_order_value

        Table: products
        Columns: id, name, sku, category, subcategory, price, cost, margin, stock_quantity

        Table: orders
        Columns: id, order_number, customer_id, product_id, quantity, unit_price, discount, total, status, channel, region, order_date

        Relations:
        - orders.customer_id = customers.id
        - orders.product_id = products.id
        """

    async def ask_data(self, query: str, session_id: str) -> dict[str, Any]:
        """Convert natural language to SQL, execute, and explain."""
        if not self.enabled:
            return {"error": "AI not configured. Add OpenAI API Key."}

        schema = await self.get_db_schema()

        # Step 1: NL to SQL
        prompt = f"""
        You are an expert Data Analyst. Given the following PostgreSQL database schema:
        
        {schema}
        
        Write a SQL query to answer this question: "{query}"
        
        IMPORTANT RULES:
        - Return ONLY the SQL query. No markdown formatting, no explanations, no `sql...` blocks.
        - Ensure the query is valid SQLite/PostgreSQL (use standard SQL).
        - Limit results to 100 rows using LIMIT 100.
        - Only SELECT operations are allowed. NEVER use INSERT, UPDATE, DELETE, DROP.
        """

        try:
            sql_response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a SQL generator."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            raw_sql = sql_response.choices[0].message.content.strip()
            
            # Clean up markdown if LLM includes it
            if raw_sql.startswith("```sql"):
                raw_sql = raw_sql[6:]
            if raw_sql.startswith("```"):
                raw_sql = raw_sql[3:]
            if raw_sql.endswith("```"):
                raw_sql = raw_sql[:-3]
                
            sql = raw_sql.strip()

            # Security check
            forbidden = ["insert", "update", "delete", "drop", "alter", "truncate", "grant", "revoke"]
            if any(f in sql.lower() for f in forbidden):
                raise ValueError("Generated SQL contains forbidden operations.")

        except Exception as e:
            logger.error(f"Error generating SQL: {str(e)}")
            return {"error": "Failed to generate SQL", "details": str(e)}

        # Step 2: Execute Query
        try:
            async with async_session() as db:
                result = await db.execute(text(sql))
                rows = result.fetchall()
                cols = result.keys()
                # Limit returned data to 50 rows for explanation to save tokens
                data_subset = [dict(zip(cols, row)) for row in rows[:50]]
                total_rows = len(rows)
        except Exception as e:
            logger.error(f"Error executing SQL: {str(e)}")
            return {"error": "Failed to execute SQL", "sql": sql, "details": str(e)}

        # Step 3: Explanation
        explanation_prompt = f"""
        You are a business intelligence assistant.
        
        Question: {query}
        SQL Used: {sql}
        Result Data (up to 50 rows): {json.dumps(data_subset, default=str)}
        
        Provide a concise, business-friendly answer to the user's question based ONLY on the result data.
        If there are many rows, summarize the key findings.
        Format your answer nicely. Do not mention the SQL query in your answer unless the user asked for it.
        """

        try:
            expl_response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful data analyst."},
                    {"role": "user", "content": explanation_prompt}
                ],
                temperature=0.4
            )
            explanation = expl_response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error generating explanation: {str(e)}")
            explanation = "Failed to generate explanation. See data table below."

        # Suggest a chart type
        chart_type = "table"
        if len(cols) == 2 and data_subset:
            vals = list(data_subset[0].values())
            if isinstance(vals[0], (int, float)) or isinstance(vals[1], (int, float)):
                chart_type = "bar"

        # Log history
        async with async_session() as db:
            history = ChatHistory(
                session_id=session_id,
                user_query=query,
                generated_sql=sql,
                ai_explanation=explanation,
                is_successful=True
            )
            db.add(history)
            await db.commit()

        return {
            "answer": explanation,
            "sql_query": sql,
            "data": data_subset,
            "chart_suggestion": chart_type,
            "session_id": session_id,
            "is_successful": True
        }


# Singleton
ai_service = AIService()
