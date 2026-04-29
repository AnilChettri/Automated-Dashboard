import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath('backend'))

from app.services.ai_service import ai_service

async def main():
    try:
        res = await ai_service.ask_data("Show me total revenue", session_id="test")
        print("RESULT:", res)
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
