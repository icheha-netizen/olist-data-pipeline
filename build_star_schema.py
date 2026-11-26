import duckdb

con = duckdb.connect("olist.duckdb")

con.execute("""
    CREATE OR REPLACE TABLE dim_customers AS
    SELECT DISTINCT customer_id, customer_unique_id, customer_city, customer_state
    FROM olist_customers_dataset
""")

con.execute("""
    CREATE OR REPLACE TABLE dim_products AS
    SELECT p.product_id,
           COALESCE(t.product_category_name_english, p.product_category_name, 'unknown') AS category,
           p.product_weight_g
    FROM olist_products_dataset p
    LEFT JOIN product_category_name_translation t USING (product_category_name)
""")

con.execute("""
    CREATE OR REPLACE TABLE dim_sellers AS
    SELECT DISTINCT seller_id, seller_city, seller_state
    FROM olist_sellers_dataset
""")

con.execute("""
    CREATE OR REPLACE TABLE dim_date AS
    SELECT d::DATE AS date_key,
           year(d) AS year,
           month(d) AS month,
           strftime(d, '%Y-%m') AS year_month,
           dayname(d) AS day_name
    FROM generate_series(DATE '2016-09-01', DATE '2018-10-31', INTERVAL 1 DAY) AS t(d)
""")

con.execute("""
    CREATE OR REPLACE TABLE fact_order_items AS
    SELECT i.order_id,
           i.order_item_id,
           o.customer_id,
           i.product_id,
           i.seller_id,
           CAST(o.order_purchase_timestamp AS TIMESTAMP)::DATE AS order_date,
           o.order_status,
           i.price,
           i.freight_value
    FROM olist_order_items_dataset i
    JOIN olist_orders_dataset o USING (order_id)
""")

for t in ["dim_customers", "dim_products", "dim_sellers", "dim_date", "fact_order_items"]:
    n = con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    print(t, n, "rows")