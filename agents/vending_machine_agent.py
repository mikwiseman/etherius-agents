"""
AI Vending Machine Agent with OpenAI Integration
Features dynamic pricing, inventory management, and X402 payment processing
"""

import os
import json
import random
from typing import Dict, List, Optional, Any
from datetime import datetime, UTC
from enum import Enum
from dotenv import load_dotenv

from uagents import Agent, Context, Model, Protocol
from pydantic import Field
from openai import OpenAI

load_dotenv()

# Agent configuration
agent = Agent(
    name="ai_vending_machine",
    seed=os.getenv("AGENT_SEED_PHRASE", "vending_machine_unique_seed_2024"),
    port=int(os.getenv("VENDING_AGENT_PORT", 8100)),
    endpoint=[f"http://localhost:{os.getenv('VENDING_AGENT_PORT', 8100)}/submit"],
    mailbox=True
)

# OpenAI configuration
openai_client = OpenAI()

# Product categories
class ProductCategory(str, Enum):
    DRINKS = "drinks"
    SNACKS = "snacks"
    CANDY = "candy"
    HEALTHY = "healthy"
    SPECIAL = "special"

# Product inventory with dynamic pricing
class Product(Model):
    id: str = Field(..., description="Product ID")
    name: str = Field(..., description="Product name")
    category: ProductCategory = Field(..., description="Product category")
    price: float = Field(..., description="Current price")
    base_price: float = Field(..., description="Base price")
    quantity: int = Field(..., description="Available quantity")
    description: str = Field(..., description="Product description")
    calories: int = Field(default=0, description="Calorie count")
    allergens: List[str] = Field(default_factory=list, description="Allergen information")
    popularity_score: float = Field(default=0.5, description="Popularity score for pricing")

# Message models
class ProductQuery(Model):
    query: str = Field(..., description="Natural language query about products")
    category: Optional[ProductCategory] = Field(None, description="Specific category filter")
    max_price: Optional[float] = Field(None, description="Maximum price filter")

class ProductResponse(Model):
    products: List[Product] = Field(..., description="Matching products")
    recommendation: str = Field(..., description="AI-generated recommendation")
    total_items: int = Field(..., description="Total items found")

class PurchaseRequest(Model):
    product_id: str = Field(..., description="Product ID to purchase")
    quantity: int = Field(default=1, description="Quantity to purchase")
    payment_method: str = Field(default="x402", description="Payment method")

class PurchaseResponse(Model):
    success: bool = Field(..., description="Purchase success status")
    product: Optional[Product] = Field(None, description="Purchased product")
    total_price: float = Field(..., description="Total price")
    payment_url: Optional[str] = Field(None, description="X402 payment URL")
    transaction_id: str = Field(..., description="Transaction ID")
    message: str = Field(..., description="Response message")

class InventoryUpdate(Model):
    product_id: str = Field(..., description="Product ID")
    quantity_change: int = Field(..., description="Quantity change (positive for restock)")
    new_price: Optional[float] = Field(None, description="New price if updating")

# Initialize inventory
INVENTORY: Dict[str, Product] = {
    "DRINK001": Product(
        id="DRINK001",
        name="Coca-Cola",
        category=ProductCategory.DRINKS,
        price=2.50,
        base_price=2.00,
        quantity=20,
        description="Classic Coca-Cola, refreshing carbonated beverage",
        calories=140,
        allergens=[]
    ),
    "DRINK002": Product(
        id="DRINK002",
        name="Smart Water",
        category=ProductCategory.DRINKS,
        price=3.00,
        base_price=2.50,
        quantity=15,
        description="Premium vapor-distilled water with electrolytes",
        calories=0,
        allergens=[]
    ),
    "SNACK001": Product(
        id="SNACK001",
        name="Doritos Nacho Cheese",
        category=ProductCategory.SNACKS,
        price=2.00,
        base_price=1.75,
        quantity=25,
        description="Bold nacho cheese flavored tortilla chips",
        calories=250,
        allergens=["dairy", "corn"]
    ),
    "SNACK002": Product(
        id="SNACK002",
        name="Pringles Original",
        category=ProductCategory.SNACKS,
        price=2.25,
        base_price=2.00,
        quantity=18,
        description="Stackable potato crisps with classic flavor",
        calories=150,
        allergens=["wheat"]
    ),
    "CANDY001": Product(
        id="CANDY001",
        name="Snickers Bar",
        category=ProductCategory.CANDY,
        price=1.75,
        base_price=1.50,
        quantity=30,
        description="Chocolate bar with peanuts, caramel, and nougat",
        calories=280,
        allergens=["peanuts", "dairy", "soy"]
    ),
    "HEALTHY001": Product(
        id="HEALTHY001",
        name="Kind Bar - Almond & Coconut",
        category=ProductCategory.HEALTHY,
        price=3.50,
        base_price=3.00,
        quantity=12,
        description="Healthy nut bar with almonds and coconut",
        calories=200,
        allergens=["tree nuts", "coconut"]
    ),
    "SPECIAL001": Product(
        id="SPECIAL001",
        name="Limited Edition Energy Drink",
        category=ProductCategory.SPECIAL,
        price=5.00,
        base_price=4.00,
        quantity=5,
        description="Exclusive AI-recommended energy boost",
        calories=110,
        allergens=[]
    )
}

# Dynamic pricing algorithm
class DynamicPricer:
    def __init__(self):
        self.purchase_history: Dict[str, List[float]] = {}
        self.demand_multiplier = 1.0
        
    def calculate_price(self, product: Product, quantity: int = 1) -> float:
        """Calculate dynamic price based on demand and inventory"""
        # Scarcity pricing - increase price when stock is low
        stock_ratio = product.quantity / 50  # Assume max capacity is 50
        scarcity_multiplier = 1.0
        if stock_ratio < 0.2:  # Less than 20% stock
            scarcity_multiplier = 1.3
        elif stock_ratio < 0.1:  # Less than 10% stock
            scarcity_multiplier = 1.5
            
        # Bulk discount - decrease price for larger quantities
        bulk_discount = 1.0
        if quantity >= 5:
            bulk_discount = 0.85
        elif quantity >= 3:
            bulk_discount = 0.92
            
        # Popularity adjustment
        popularity_multiplier = 0.9 + (product.popularity_score * 0.4)
        
        # Calculate final price
        final_price = product.base_price * scarcity_multiplier * bulk_discount * popularity_multiplier
        return round(final_price, 2)
    
    def update_popularity(self, product_id: str, purchased: bool):
        """Update product popularity based on interactions"""
        if product_id in INVENTORY:
            product = INVENTORY[product_id]
            if purchased:
                product.popularity_score = min(1.0, product.popularity_score + 0.05)
            else:
                product.popularity_score = max(0.0, product.popularity_score - 0.01)

pricer = DynamicPricer()

# AI-powered product recommendation
async def get_ai_recommendation(query: str, available_products: List[Product]) -> str:
    """Use OpenAI to generate personalized recommendations"""
    try:
        products_info = "\n".join([
            f"- {p.name}: {p.description} (${p.price}, {p.calories} cal)"
            for p in available_products[:5]
        ])
        
        prompt = f"""Based on the user query: "{query}"
        
        Available products:
        {products_info}
        
        Provide a friendly, personalized recommendation in 2-3 sentences.
        Consider factors like price, health, and user preferences."""
        
        response = openai_client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": "You are a helpful AI vending machine assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"I recommend checking out our {available_products[0].name if available_products else 'special items'}!"

# Protocol definition
vending_protocol = Protocol(name="ai_vending_protocol", version="1.0")

@agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info(f"🎰 AI Vending Machine started!")
    ctx.logger.info(f"📍 Address: {agent.address}")
    ctx.logger.info(f"📦 Products loaded: {len(INVENTORY)}")
    ctx.logger.info(f"🤖 OpenAI integration: {'✅' if os.getenv('OPENAI_API_KEY') else '❌'}")

@agent.on_event("shutdown")
async def shutdown(ctx: Context):
    ctx.logger.info("🛑 AI Vending Machine shutting down...")

@vending_protocol.on_message(model=ProductQuery, replies=ProductResponse)
async def handle_product_query(ctx: Context, sender: str, msg: ProductQuery):
    """Handle natural language product queries"""
    ctx.logger.info(f"📨 Product query from {sender}: {msg.query}")
    
    # Filter products based on query
    filtered_products = []
    for product in INVENTORY.values():
        # Apply category filter
        if msg.category and product.category != msg.category:
            continue
        # Apply price filter
        if msg.max_price and product.price > msg.max_price:
            continue
        # Simple keyword matching
        if any(keyword.lower() in product.name.lower() or 
               keyword.lower() in product.description.lower() 
               for keyword in msg.query.split()):
            filtered_products.append(product)
    
    # If no keyword matches, return all matching filters
    if not filtered_products and (msg.category or msg.max_price):
        filtered_products = [p for p in INVENTORY.values()
                           if (not msg.category or p.category == msg.category) and
                              (not msg.max_price or p.price <= msg.max_price)]
    
    # Get AI recommendation
    recommendation = await get_ai_recommendation(msg.query, filtered_products)
    
    # Update dynamic pricing for displayed products
    for product in filtered_products:
        product.price = pricer.calculate_price(product)
    
    response = ProductResponse(
        products=filtered_products[:10],  # Limit to 10 products
        recommendation=recommendation,
        total_items=len(filtered_products)
    )
    
    await ctx.send(sender, response)

@vending_protocol.on_message(model=PurchaseRequest, replies=PurchaseResponse)
async def handle_purchase(ctx: Context, sender: str, msg: PurchaseRequest):
    """Handle product purchase with dynamic pricing"""
    ctx.logger.info(f"💰 Purchase request from {sender}: {msg.product_id} x{msg.quantity}")
    
    if msg.product_id not in INVENTORY:
        await ctx.send(sender, PurchaseResponse(
            success=False,
            product=None,
            total_price=0,
            transaction_id=f"TXN_{datetime.now(UTC).timestamp()}",
            message="Product not found"
        ))
        return
    
    product = INVENTORY[msg.product_id]
    
    # Check availability
    if product.quantity < msg.quantity:
        await ctx.send(sender, PurchaseResponse(
            success=False,
            product=product,
            total_price=0,
            transaction_id=f"TXN_{datetime.now(UTC).timestamp()}",
            message=f"Insufficient stock. Only {product.quantity} available"
        ))
        return
    
    # Calculate dynamic price
    unit_price = pricer.calculate_price(product, msg.quantity)
    total_price = unit_price * msg.quantity
    
    # Process payment (simulated X402 integration)
    payment_url = f"https://x402.pay/vending/{msg.product_id}?amount={total_price}&qty={msg.quantity}"
    
    # Update inventory
    product.quantity -= msg.quantity
    pricer.update_popularity(msg.product_id, True)
    
    # Log transaction
    transaction_id = f"TXN_{int(datetime.now(UTC).timestamp())}_{random.randint(1000, 9999)}"
    
    await ctx.send(sender, PurchaseResponse(
        success=True,
        product=product,
        total_price=total_price,
        payment_url=payment_url,
        transaction_id=transaction_id,
        message=f"Purchase successful! Unit price: ${unit_price} (dynamic pricing applied)"
    ))
    
    ctx.logger.info(f"✅ Sale completed: {product.name} x{msg.quantity} for ${total_price}")

@vending_protocol.on_message(model=InventoryUpdate)
async def handle_inventory_update(ctx: Context, sender: str, msg: InventoryUpdate):
    """Handle inventory updates (admin function)"""
    if msg.product_id in INVENTORY:
        product = INVENTORY[msg.product_id]
        product.quantity += msg.quantity_change
        if msg.new_price:
            product.base_price = msg.new_price
            product.price = pricer.calculate_price(product)
        
        ctx.logger.info(f"📦 Inventory updated: {product.name} - Qty: {product.quantity}")

# Include protocol
agent.include(vending_protocol, publish_manifest=True)

if __name__ == "__main__":
    print("""
🎰 AI Vending Machine Agent Starting...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Features:
• OpenAI-powered recommendations
• Dynamic pricing algorithm
• X402 payment integration
• Real-time inventory management
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """)
    agent.run()