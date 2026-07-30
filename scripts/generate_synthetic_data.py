from pathlib import Path
import csv, random, datetime

out = Path(__file__).resolve().parents[1] / "data" / "synthetic"
out.mkdir(parents=True, exist_ok=True)
random.seed(42)

stores = [(i, f"Store {i:02d}", random.choice(["HCMC", "Hanoi", "Da Nang"]), random.choice(["Urban", "Suburban"])) for i in range(1, 11)]
products = [(i, random.choice(["Pizza", "Pasta", "Drink", "Side"]), f"Product {i:02d}", round(random.uniform(1.0, 5.0),2), round(random.uniform(3.0, 12.0),2)) for i in range(1, 31)]
customers = [(i, random.choice(["Premium", "Regular", "Occasional", "New"]), random.choice(["Low", "Medium", "High"])) for i in range(1, 501)]
channels = ["dine-in", "delivery", "app", "web", "phone"]

def write(name, header, rows):
    with open(out / name, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)

write("stores.csv", ["store_id", "store_name", "region", "store_type"], stores)
write("products.csv", ["product_id", "category", "product_name", "unit_cost", "unit_price"], products)
write("customers.csv", ["customer_id", "customer_segment", "churn_risk"], customers)

orders=[]
order_items=[]
start=datetime.date(2025,1,1)
for order_id in range(1, 5001):
    d=start + datetime.timedelta(days=random.randint(0, 545))
    customer_id=random.randint(1,500)
    store_id=random.randint(1,10)
    channel=random.choice(channels)
    orders.append((order_id, d.isoformat(), customer_id, store_id, channel))
    for _ in range(random.randint(1,4)):
        product=random.choice(products)
        qty=random.randint(1,3)
        order_items.append((order_id, product[0], qty, product[3], product[4]))

write("orders.csv", ["order_id", "order_date", "customer_id", "store_id", "channel"], orders)
write("order_items.csv", ["order_id", "product_id", "quantity", "unit_cost", "unit_price"], order_items)
print(f"Generated synthetic data in {out}")
