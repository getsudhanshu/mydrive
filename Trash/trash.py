import sqlite3
import requests
import json

# CouchDB config
COUCHDB_URL = "http://localhost:5984"
HEADERS = {"Content-Type": "application/json"}

# Connect to your relational DB
conn = sqlite3.connect("your_database.db")
cursor = conn.cursor()

# Step 1: Migrate product_category table
cursor.execute("SELECT prod_cat_id, category_name FROM product_category")
categories = cursor.fetchall()

for cat in categories:
    doc = {
        "_id": f"category_{cat[0]}",
        "type": "product_category",
        "prod_cat_id": cat[0],
        "category_name": cat[1]
    }
    res = requests.put(f"{COUCHDB_URL}/product_category/{doc['_id']}", headers=HEADERS, data=json.dumps(doc))
    print(f"Inserted category {cat[0]}: {res.status_code}")

# Step 2: Migrate product table
cursor.execute("SELECT prod_id, prod_color, prod_cat_id, prod_name FROM product")
products = cursor.fetchall()

for prod in products:
    doc = {
        "_id": f"product_{prod[0]}_{prod[1]}",
        "type": "product",
        "prod_id": prod[0],
        "prod_color": prod[1],
        "prod_name": prod[3],
        "prod_cat_id": prod[2],  # Reference to category
        "category_ref": f"category_{prod[2]}"  # Optional: link to category doc
    }
    res = requests.put(f"{COUCHDB_URL}/product/{doc['_id']}", headers=HEADERS, data=json.dumps(doc))
    print(f"Inserted product {prod[0]}-{prod[1]}: {res.status_code}")

conn.close()
