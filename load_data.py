import duckdb
from pathlib import Path
con = duckdb.connect("olist.duckdb")
for f in Path("data/raw").glob("*.csv"):
    table = f.stem
    con.execute(
        f"CREATE OR REPLACE TABLE {table} AS "
        f"SELECT * FROM read_csv_auto('{f.as_posix()}')"
    )
    n = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    print(table, n, "rows")
con = duckdb.connect("olist.duckdb", read_only=True)

print("1) Revenue per month")
con.sql("""
    SELECT strftime(CAST(o.order_purchase_timestamp AS TIMESTAMP), '%Y-%m') AS month,
           ROUND(SUM(p.payment_value), 2) AS revenue
    FROM olist_orders_dataset o
    JOIN olist_order_payments_dataset p USING (order_id)
    WHERE o.order_status = 'delivered'
    GROUP BY 1
    ORDER BY 1
""").show()

print("2) Top 10 product categories by sales")
con.sql("""
    SELECT t.product_category_name_english AS category,
           ROUND(SUM(i.price), 2) AS sales
    FROM olist_order_items_dataset i
    JOIN olist_products_dataset pr USING (product_id)
    JOIN product_category_name_translation t USING (product_category_name)
    GROUP BY 1
    ORDER BY sales DESC
    LIMIT 10
""").show()

print("3) Customers per state")
con.sql("""
    SELECT customer_state, COUNT(DISTINCT customer_unique_id) AS customers
    FROM olist_customers_dataset
    GROUP BY 1
    ORDER BY customers DESC
""").show()

print("4) Average delivery time (days)")
con.sql("""
    SELECT ROUND(AVG(date_diff('day',
               CAST(order_purchase_timestamp AS TIMESTAMP),
               CAST(order_delivered_customer_date AS TIMESTAMP))), 1) AS avg_days
    FROM olist_orders_dataset
    WHERE order_status = 'delivered'
      AND order_delivered_customer_date IS NOT NULL
""").show()

print("5) Top 10 customers by spending (with RANK)")
con.sql("""
    SELECT c.customer_unique_id,
           ROUND(SUM(p.payment_value), 2) AS total_spent,
           RANK() OVER (ORDER BY SUM(p.payment_value) DESC) AS rnk
    FROM olist_orders_dataset o
    JOIN olist_customers_dataset c USING (customer_id)
    JOIN olist_order_payments_dataset p USING (order_id)
    GROUP BY 1
    ORDER BY rnk
    LIMIT 10
""").show()