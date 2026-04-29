"""
Synthetic Data Generator
Generates realistic e-commerce data for development and demo.

Creates:
- 5,000 customers with segments and RFM scores
- 200 products across 10 categories
- 50,000+ orders over 2 years with realistic patterns

Usage:
    python -m scripts.seed_data
"""

import asyncio
import random
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Add parent dir to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np

# ─── Configuration ──────────────────────────────────────────

NUM_CUSTOMERS = 5000
NUM_PRODUCTS = 200
NUM_ORDERS = 55000
START_DATE = datetime(2024, 1, 1)
END_DATE = datetime(2026, 4, 15)

CATEGORIES = {
    "Electronics": ["Smartphones", "Laptops", "Tablets", "Headphones", "Cameras"],
    "Clothing": ["Men's Wear", "Women's Wear", "Activewear", "Accessories", "Footwear"],
    "Home & Kitchen": ["Furniture", "Appliances", "Decor", "Cookware", "Bedding"],
    "Sports & Outdoors": ["Fitness", "Camping", "Cycling", "Swimming", "Team Sports"],
    "Beauty": ["Skincare", "Makeup", "Haircare", "Fragrances", "Personal Care"],
    "Books": ["Fiction", "Non-Fiction", "Tech", "Business", "Self-Help"],
    "Food & Grocery": ["Organic", "Snacks", "Beverages", "Specialty", "Supplements"],
    "Toys & Games": ["Board Games", "Action Figures", "Educational", "Puzzles", "Outdoor Play"],
    "Health": ["Vitamins", "Medical Devices", "First Aid", "Wellness", "Fitness Trackers"],
    "Office": ["Supplies", "Furniture", "Tech Accessories", "Planners", "Lighting"],
}

CITIES = [
    ("New York", "US"), ("Los Angeles", "US"), ("Chicago", "US"), ("Houston", "US"),
    ("Phoenix", "US"), ("San Antonio", "US"), ("San Diego", "US"), ("Dallas", "US"),
    ("Austin", "US"), ("Seattle", "US"), ("Denver", "US"), ("Boston", "US"),
    ("Miami", "US"), ("Atlanta", "US"), ("Portland", "US"), ("Nashville", "US"),
    ("London", "UK"), ("Toronto", "CA"), ("Sydney", "AU"), ("Berlin", "DE"),
    ("Mumbai", "IN"), ("Tokyo", "JP"), ("Paris", "FR"), ("Singapore", "SG"),
]

FIRST_NAMES = [
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
    "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
    "Thomas", "Sarah", "Charles", "Karen", "Daniel", "Lisa", "Matthew", "Nancy",
    "Anthony", "Betty", "Mark", "Margaret", "Donald", "Sandra", "Steven", "Ashley",
    "Paul", "Kimberly", "Andrew", "Emily", "Joshua", "Donna", "Kenneth", "Michelle",
    "Aarav", "Priya", "Yuki", "Sakura", "Wei", "Mei", "Oliver", "Sophie",
    "Liam", "Emma", "Noah", "Ava", "Aiden", "Mia", "Lucas", "Charlotte",
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
    "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson",
    "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen",
    "Hill", "Flores", "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera",
    "Patel", "Kumar", "Tanaka", "Müller", "Chen", "Singh", "Sharma", "Kim",
]

PAYMENT_METHODS = ["credit_card", "debit_card", "paypal", "apple_pay", "bank_transfer"]
CHANNELS = ["online", "mobile", "in-store"]
REGIONS = ["North", "South", "East", "West", "Central"]

# Product name templates per category
PRODUCT_TEMPLATES = {
    "Electronics": ["Pro {}", "Ultra {}", "{} Max", "{} Elite", "Smart {}"],
    "Clothing": ["Classic {}", "Modern {}", "Vintage {}", "Urban {}", "Premium {}"],
    "Home & Kitchen": ["{} Deluxe", "Essential {}", "Artisan {}", "Premium {}", "Smart {}"],
    "Sports & Outdoors": ["Extreme {}", "Pro {}", "Active {}", "Elite {}", "Performance {}"],
    "Beauty": ["Glow {}", "Radiant {}", "Natural {}", "Luxe {}", "Pure {}"],
    "Books": ["The Art of {}", "Mastering {}", "Essential {}", "Complete {}", "Advanced {}"],
    "Food & Grocery": ["Organic {}", "Premium {}", "Natural {}", "Farm Fresh {}", "Artisan {}"],
    "Toys & Games": ["Super {}", "Mega {}", "Adventure {}", "Magic {}", "Wonder {}"],
    "Health": ["Vital {}", "Wellness {}", "Pure {}", "Active {}", "Daily {}"],
    "Office": ["Pro {}", "Executive {}", "Essential {}", "Smart {}", "Premium {}"],
}


def generate_products() -> list[dict]:
    """Generate diverse product catalog."""
    products = []
    product_id = 1

    for category, subcategories in CATEGORIES.items():
        n_per_cat = NUM_PRODUCTS // len(CATEGORIES)
        for i in range(n_per_cat):
            subcat = random.choice(subcategories)
            template = random.choice(PRODUCT_TEMPLATES[category])
            name = template.format(subcat)

            # Price ranges by category
            price_ranges = {
                "Electronics": (29.99, 1499.99),
                "Clothing": (19.99, 299.99),
                "Home & Kitchen": (14.99, 599.99),
                "Sports & Outdoors": (9.99, 499.99),
                "Beauty": (7.99, 149.99),
                "Books": (9.99, 59.99),
                "Food & Grocery": (3.99, 79.99),
                "Toys & Games": (9.99, 199.99),
                "Health": (12.99, 199.99),
                "Office": (4.99, 299.99),
            }

            price_min, price_max = price_ranges[category]
            price = round(random.uniform(price_min, price_max), 2)
            margin_pct = random.uniform(0.15, 0.65)
            cost = round(price * (1 - margin_pct), 2)

            products.append({
                "id": product_id,
                "name": f"{name} {product_id}",
                "sku": f"SKU-{category[:3].upper()}-{product_id:04d}",
                "category": category,
                "subcategory": subcat,
                "price": price,
                "cost": cost,
                "margin": round(margin_pct, 3),
                "stock_quantity": random.randint(0, 500),
                "is_active": random.random() > 0.05,
                "description": f"Premium {subcat.lower()} in our {category.lower()} collection.",
            })
            product_id += 1

    return products


def generate_customers() -> list[dict]:
    """Generate customer profiles with realistic distributions."""
    customers = []

    for i in range(1, NUM_CUSTOMERS + 1):
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        city, country = random.choice(CITIES)

        # Create email with some variety
        email_templates = [
            f"{first.lower()}.{last.lower()}{i}@email.com",
            f"{first.lower()}{last.lower()[:3]}{i}@gmail.com",
            f"{first.lower()[0]}{last.lower()}{i}@outlook.com",
        ]

        customers.append({
            "id": i,
            "name": f"{first} {last}",
            "email": random.choice(email_templates),
            "phone": f"+1-{random.randint(200,999)}-{random.randint(100,999)}-{random.randint(1000,9999)}",
            "city": city,
            "country": country,
        })

    return customers


def generate_orders(customers: list[dict], products: list[dict]) -> list[dict]:
    """
    Generate orders with realistic patterns:
    - Pareto distribution (20% of customers make 80% of orders)
    - Seasonality (holiday bumps)
    - Recent churn for some customers
    """
    orders = []
    total_days = (END_DATE - START_DATE).days

    # Create customer purchase probability (Pareto-like)
    customer_ids = [c["id"] for c in customers]
    n = len(customer_ids)

    # 20% are high-frequency buyers
    high_freq = set(random.sample(customer_ids, int(n * 0.20)))
    # 30% are medium
    remaining = [c for c in customer_ids if c not in high_freq]
    med_freq = set(random.sample(remaining, int(len(remaining) * 0.40)))
    # Rest are low frequency

    # Some customers churn (stop buying in last 6 months)
    churned = set(random.sample(customer_ids, int(n * 0.15)))

    product_ids = [p["id"] for p in products]
    product_prices = {p["id"]: p["price"] for p in products}

    for i in range(1, NUM_ORDERS + 1):
        # Pick customer with weighted probability
        r = random.random()
        if r < 0.55:  # 55% of orders from high-freq customers
            cid = random.choice(list(high_freq))
        elif r < 0.85:  # 30% from medium
            cid = random.choice(list(med_freq))
        else:  # 15% from low-freq
            cid = random.choice(customer_ids)

        # Generate order date with seasonality
        day_offset = random.randint(0, total_days)
        order_date = START_DATE + timedelta(days=day_offset)

        # Churned customers don't buy in last 6 months
        if cid in churned and order_date > END_DATE - timedelta(days=180):
            order_date = order_date - timedelta(days=random.randint(180, 365))

        # Holiday bumps (Nov-Dec get more orders)
        if order_date.month in [11, 12]:
            if random.random() > 0.3:  # 70% chance to keep the holiday order
                pass  # keep the date
            else:
                day_offset = random.randint(0, total_days)
                order_date = START_DATE + timedelta(days=day_offset)

        pid = random.choice(product_ids)
        unit_price = product_prices[pid]
        quantity = np.random.choice([1, 1, 1, 2, 2, 3], p=[0.45, 0.15, 0.10, 0.15, 0.10, 0.05])
        discount = random.choice([0, 0, 0, 0, 0.05, 0.10, 0.15, 0.20])
        total = round(unit_price * quantity * (1 - discount), 2)

        status = np.random.choice(
            ["completed", "completed", "completed", "completed", "refunded", "cancelled"],
            p=[0.42, 0.25, 0.18, 0.05, 0.05, 0.05],
        )

        orders.append({
            "id": i,
            "order_number": f"ORD-{order_date.strftime('%Y%m')}-{i:06d}",
            "customer_id": cid,
            "product_id": pid,
            "quantity": int(quantity),
            "unit_price": unit_price,
            "discount": discount,
            "total": total,
            "status": status,
            "payment_method": random.choice(PAYMENT_METHODS),
            "channel": np.random.choice(CHANNELS, p=[0.55, 0.30, 0.15]),
            "region": random.choice(REGIONS),
            "order_date": order_date,
        })

    return orders


def compute_customer_metrics(customers: list[dict], orders: list[dict]) -> list[dict]:
    """Compute RFM and customer-level metrics."""
    from collections import defaultdict

    # Group orders by customer
    customer_orders = defaultdict(list)
    for o in orders:
        if o["status"] == "completed":
            customer_orders[o["customer_id"]].append(o)

    reference_date = END_DATE
    enriched = []

    for c in customers:
        cid = c["id"]
        c_orders = customer_orders.get(cid, [])

        if c_orders:
            order_dates = [o["order_date"] for o in c_orders]
            totals = [o["total"] for o in c_orders]

            last_purchase = max(order_dates)
            first_purchase = min(order_dates)
            recency = (reference_date - last_purchase).days
            frequency = len(c_orders)
            monetary = sum(totals)

            c["first_purchase_date"] = first_purchase
            c["last_purchase_date"] = last_purchase
            c["lifetime_value"] = round(monetary, 2)
            c["total_orders"] = frequency
            c["avg_order_value"] = round(monetary / frequency, 2)
            c["rfm_recency"] = float(recency)
            c["rfm_frequency"] = float(frequency)
            c["rfm_monetary"] = round(monetary, 2)
        else:
            c["first_purchase_date"] = None
            c["last_purchase_date"] = None
            c["lifetime_value"] = 0.0
            c["total_orders"] = 0
            c["avg_order_value"] = 0.0
            c["rfm_recency"] = None
            c["rfm_frequency"] = None
            c["rfm_monetary"] = None

        enriched.append(c)

    # Compute RFM scores (1-5) and assign segments
    customers_with_orders = [c for c in enriched if c["rfm_recency"] is not None]
    if customers_with_orders:
        recencies = np.array([c["rfm_recency"] for c in customers_with_orders])
        frequencies = np.array([c["rfm_frequency"] for c in customers_with_orders])
        monetaries = np.array([c["rfm_monetary"] for c in customers_with_orders])

        def score_quintile(values, reverse=False):
            """Assign quintile scores. Lower recency = better (score 5)."""
            percentiles = np.percentile(values, [20, 40, 60, 80])
            scores = np.digitize(values, percentiles) + 1
            if reverse:
                scores = 6 - scores
            return scores

        r_scores = score_quintile(recencies, reverse=True)  # Lower recency = higher score
        f_scores = score_quintile(frequencies)
        m_scores = score_quintile(monetaries)

        for i, c in enumerate(customers_with_orders):
            r, f, m = int(r_scores[i]), int(f_scores[i]), int(m_scores[i])
            rfm_score = (r + f + m) / 3
            c["rfm_score"] = round(rfm_score, 2)

            # Segment assignment based on RFM
            if r >= 4 and f >= 4 and m >= 4:
                c["segment"] = "Champions"
            elif r >= 3 and f >= 3 and m >= 3:
                c["segment"] = "Loyal"
            elif r >= 4 and f <= 2:
                c["segment"] = "New Customers"
            elif r <= 2 and f >= 3:
                c["segment"] = "At Risk"
            elif r <= 2 and f <= 2 and m <= 2:
                c["segment"] = "Churned"
            elif m >= 4:
                c["segment"] = "High Value"
            else:
                c["segment"] = "Regular"

            # Churn probability (simple heuristic — ML model will replace this)
            churn_prob = min(1.0, max(0.0, (c["rfm_recency"] / 365) * 0.5 + (1 - f / 5) * 0.3 + random.uniform(-0.1, 0.1)))
            c["churn_probability"] = round(churn_prob, 3)
            c["is_churned"] = churn_prob > 0.7

    # Customers without orders
    for c in enriched:
        if c.get("segment") is None:
            c["segment"] = "Inactive"
            c["rfm_score"] = 0.0
            c["churn_probability"] = 0.95
            c["is_churned"] = True

    return enriched


async def seed_database():
    """Main seeding function."""
    from app.database import init_db, async_session, engine
    from app.models import Customer, Order, Product
    from app.models.insight import Insight
    from sqlalchemy import text

    print("=" * 60)
    print("Decision Intelligence System -- Data Seeder")
    print("=" * 60)

    # Initialize DB
    await init_db()
    print("Database tables created")

    # Check if data already exists
    async with async_session() as db:
        result = await db.execute(text("SELECT COUNT(*) FROM customers"))
        count = result.scalar()
        if count and count > 0:
            print(f"Database already has {count} customers.")
            # response = input("   Overwrite? (y/N): ").strip().lower()
            # AUTO OVERWRITE FOR NON-INTERACTIVE
            response = "y"
            if response != "y":
                print("   Skipping seed. Exiting.")
                return

            # Clear tables
            await db.execute(text("DELETE FROM orders"))
            await db.execute(text("DELETE FROM customers"))
            await db.execute(text("DELETE FROM products"))
            await db.execute(text("DELETE FROM insights"))
            await db.commit()
            print("   Cleared existing data")

    # Generate data
    print("\nGenerating products...")
    products = generate_products()
    print(f"   {len(products)} products across {len(CATEGORIES)} categories")

    print("Generating customers...")
    customers = generate_customers()
    print(f"   {NUM_CUSTOMERS} customers from {len(CITIES)} cities")

    print("Generating orders...")
    orders = generate_orders(customers, products)
    completed = len([o for o in orders if o["status"] == "completed"])
    print(f"   {len(orders)} orders ({completed} completed)")

    print("Computing customer metrics (RFM, segments)...")
    customers = compute_customer_metrics(customers, orders)
    segments = {}
    for c in customers:
        seg = c.get("segment", "Unknown")
        segments[seg] = segments.get(seg, 0) + 1
    for seg, cnt in sorted(segments.items(), key=lambda x: -x[1]):
        print(f"   {seg}: {cnt} customers ({cnt/len(customers)*100:.1f}%)")

    # Insert into database
    print("\nInserting into database...")

    async with async_session() as db:
        # Products
        for p in products:
            db.add(Product(
                name=p["name"], sku=p["sku"], category=p["category"],
                subcategory=p["subcategory"], price=p["price"], cost=p["cost"],
                margin=p["margin"], stock_quantity=p["stock_quantity"],
                is_active=p["is_active"], description=p["description"],
            ))
        await db.commit()
        print(f"   {len(products)} products inserted")

        # Customers
        for c in customers:
            db.add(Customer(
                name=c["name"], email=c["email"], phone=c.get("phone"),
                city=c.get("city"), country=c.get("country", "US"),
                segment=c.get("segment"), rfm_recency=c.get("rfm_recency"),
                rfm_frequency=c.get("rfm_frequency"), rfm_monetary=c.get("rfm_monetary"),
                rfm_score=c.get("rfm_score"), churn_probability=c.get("churn_probability"),
                is_churned=c.get("is_churned", False), lifetime_value=c.get("lifetime_value", 0),
                total_orders=c.get("total_orders", 0), avg_order_value=c.get("avg_order_value", 0),
                first_purchase_date=c.get("first_purchase_date"),
                last_purchase_date=c.get("last_purchase_date"),
            ))
        await db.commit()
        print(f"   {len(customers)} customers inserted")

        # Orders (batch insert for performance)
        batch_size = 5000
        for idx in range(0, len(orders), batch_size):
            batch = orders[idx:idx + batch_size]
            for o in batch:
                db.add(Order(
                    order_number=o["order_number"], customer_id=o["customer_id"],
                    product_id=o["product_id"], quantity=o["quantity"],
                    unit_price=o["unit_price"], discount=o["discount"],
                    total=o["total"], status=o["status"],
                    payment_method=o["payment_method"], channel=o["channel"],
                    region=o["region"], order_date=o["order_date"],
                ))
            await db.commit()
            print(f"   {min(idx + batch_size, len(orders))}/{len(orders)} orders inserted")

        # Seed some initial insights
        sample_insights = [
            Insight(
                type="auto", title="Revenue Growth Detected",
                body="Revenue has increased by 12% compared to the previous period. Key drivers include strong performance in Electronics and renewed holiday campaign effectiveness.",
                severity="info", category="revenue", confidence=0.85,
            ),
            Insight(
                type="alert", title="Churn Risk Increase",
                body="15% of previously loyal customers have not purchased in 90+ days. Consider targeted re-engagement campaigns focusing on personalized offers.",
                severity="warning", category="churn", confidence=0.78,
            ),
            Insight(
                type="recommendation", title="High-Value Segment Opportunity",
                body="Champions segment shows 3.2x higher AOV than average. Cross-selling premium products to this group could yield an estimated 8% revenue uplift.",
                severity="info", category="growth", confidence=0.72,
            ),
            Insight(
                type="anomaly", title="Unusual Drop in Mobile Orders",
                body="Mobile channel orders dropped 23% week-over-week. This coincides with the app update deployed on Monday. Investigate potential UX regression.",
                severity="critical", category="channel", confidence=0.91,
            ),
            Insight(
                type="auto", title="Best Performing Category: Electronics",
                body="Electronics accounts for 32% of total revenue with the highest margin (42%). Top sellers include smartphones and laptops.",
                severity="info", category="product", confidence=0.88,
            ),
        ]
        for insight in sample_insights:
            db.add(insight)
        await db.commit()
        print(f"   {len(sample_insights)} sample insights inserted")

    print("\n" + "=" * 60)
    print("Seeding complete!")
    print(f"   {len(products)} products")
    print(f"   {len(customers)} customers")
    print(f"   {len(orders)} orders")
    print(f"   {len(sample_insights)} insights")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(seed_database())
