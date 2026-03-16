from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

# 1. Data Models
class CheckoutRequest(BaseModel):
    customer_name: str
    delivery_address: str

# 2. In-Memory Database
products = {
    1: {"name": "Wireless Mouse", "price": 499, "in_stock": True},
    2: {"name": "Notebook", "price": 99, "in_stock": True},
    3: {"name": "USB Hub", "price": 599, "in_stock": False},
    4: {"name": "Pen Set", "price": 49, "in_stock": True},
}

cart = []
orders = []

# 3. Helper Functions
def calculate_grand_total():
    """Calculates the sum of all item subtotals in the cart"""
    return sum(item["subtotal"] for item in cart)

# 4. Endpoints

@app.post("/cart/add")
def add_to_cart(product_id: int, quantity: int):
    # Q3: Verify product exists
    if product_id not in products:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product = products[product_id]
    
    # Q3: Check stock availability
    if not product["in_stock"]:
        raise HTTPException(
            status_code=400, 
            detail=f"{product['name']} is out of stock"
        )

    # Q4: Check if item is already in cart to update quantity instead of duplicating
    for item in cart:
        if item["product_id"] == product_id:
            item["quantity"] += quantity
            item["subtotal"] = item["quantity"] * item["unit_price"]
            return {"message": "Cart updated", "cart_item": item}

    # Q1: Add new item if not already present
    new_item = {
        "product_id": product_id,
        "product_name": product["name"],
        "quantity": quantity,
        "unit_price": product["price"],
        "subtotal": quantity * product["price"]
    }
    cart.append(new_item)
    return {"message": "Added to cart", "cart_item": new_item}

@app.get("/cart")
def view_cart():
    # Q2: Return 'Cart is empty' message or current cart state
    if not cart:
        return {"message": "Cart is empty"}
    
    return {
        "items": cart,
        "item_count": len(cart), # Q2: Unique products count
        "grand_total": calculate_grand_total()
    }

@app.delete("/cart/{product_id}")
def remove_from_cart(product_id: int):
    # Q5: Remove specific item by product_id
    global cart
    initial_len = len(cart)
    cart = [item for item in cart if item["product_id"] != product_id]
    
    if len(cart) == initial_len:
        raise HTTPException(status_code=404, detail="Item not in cart")
    return {"message": "Item removed from cart"}

@app.post("/cart/checkout")
def checkout(request: CheckoutRequest):
    global cart
    # ⭐ Bonus: Reject checkout if cart is empty
    if not cart:
        raise HTTPException(status_code=400, detail="Cart is empty — add items first")

    # Q5 & Q6: Create an order for each item in the cart
    final_total = calculate_grand_total()
    for item in cart:
        new_order = {
            "order_id": len(orders) + 1,
            "customer_name": request.customer_name,
            "product": item["product_name"],
            "total_price": item["subtotal"]
        }
        orders.append(new_order)

    cart = [] # Q5: Clear cart after successful checkout
    
    return {
        "message": "Order placed successfully",
        "orders_placed": len(orders), 
        "grand_total": final_total
    }

@app.get("/orders")
def get_orders():
    # Q5: View all historical orders
    return {
        "orders": orders,
        "total_orders": len(orders)
    }
