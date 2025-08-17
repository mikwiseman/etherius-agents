"""
x402 Payment Service
Handles real blockchain payment verification for NFT purchases
Uses x402 middleware with Coinbase infrastructure
"""

import os
import json
from typing import Dict, Any
from datetime import datetime
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from x402.fastapi.middleware import require_payment
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="x402 Payment Service", version="1.0.0")

# Store payment records
payment_records: Dict[str, Any] = {}

# Get configuration from environment
WALLET_ADDRESS = os.getenv("X402_WALLET_ADDRESS", "0x0000000000000000000000000000000000000000")
NETWORK = os.getenv("X402_NETWORK", "base-sepolia")
FACILITATOR_URL = os.getenv("X402_FACILITATOR_URL", "https://x402.org/facilitator")
DEFAULT_PRICE = 0.01  # Default price in USD

# Health check endpoint (no payment required)
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "x402 Payment Service",
        "network": NETWORK,
        "wallet": WALLET_ADDRESS[:6] + "..." + WALLET_ADDRESS[-4:]
    }

# Payment verification endpoint with x402 middleware
# This endpoint requires payment before access
@app.post("/nft/purchase/{payment_id}")
@require_payment(
    price=f"${DEFAULT_PRICE}",
    pay_to_address=WALLET_ADDRESS,
    network=NETWORK,
    facilitator_url=FACILITATOR_URL,
    description="NFT Purchase Payment"
)
async def verify_nft_purchase(payment_id: str, request: Request):
    """
    This endpoint is protected by x402 middleware.
    It will only execute if payment has been verified.
    """
    logger.info(f"Payment verified for ID: {payment_id}")
    
    # Record successful payment
    payment_records[payment_id] = {
        "status": "completed",
        "timestamp": datetime.now().isoformat(),
        "amount": DEFAULT_PRICE,
        "network": NETWORK,
        "verified": True
    }
    
    # Extract transaction hash if available from x402 headers
    tx_hash = request.headers.get("X-Transaction-Hash", f"0x{payment_id}")
    payment_records[payment_id]["tx_hash"] = tx_hash
    
    return {
        "status": "paid",
        "payment_id": payment_id,
        "tx_hash": tx_hash,
        "message": "Payment successfully verified via x402"
    }

# Check payment status (no payment required for checking)
@app.get("/payment/status/{payment_id}")
async def check_payment_status(payment_id: str):
    """Check if a payment has been completed"""
    if payment_id in payment_records:
        return payment_records[payment_id]
    else:
        return {
            "status": "pending",
            "payment_id": payment_id,
            "message": "Payment not yet verified"
        }

# Create payment request (returns payment instructions)
@app.post("/payment/create")
async def create_payment_request(nft_name: str = "NFT", price: float = DEFAULT_PRICE):
    """
    Create a new payment request with x402 instructions
    """
    import hashlib
    import time
    
    # Generate unique payment ID
    payment_id = hashlib.sha256(f"{nft_name}{time.time()}".encode()).hexdigest()[:8]
    
    # Return payment instructions
    return {
        "payment_id": payment_id,
        "nft": nft_name,
        "price": price,
        "currency": "USDC",
        "network": NETWORK,
        "pay_to": WALLET_ADDRESS,
        "verification_url": f"/nft/purchase/{payment_id}",
        "instructions": {
            "1": f"Send {price} USDC to {WALLET_ADDRESS}",
            "2": "On network: " + NETWORK,
            "3": f"Then POST to /nft/purchase/{payment_id} with payment proof",
            "4": "x402 will automatically verify the payment"
        },
        "facilitator": FACILITATOR_URL
    }

# List all payments (for debugging)
@app.get("/payments")
async def list_payments():
    """List all payment records"""
    return {
        "total": len(payment_records),
        "payments": payment_records
    }

# Clear payment records (for testing)
@app.delete("/payments/clear")
async def clear_payments():
    """Clear all payment records (testing only)"""
    payment_records.clear()
    return {"message": "All payment records cleared"}

# Custom error handler for 402 Payment Required
@app.exception_handler(402)
async def payment_required_handler(request: Request, exc: HTTPException):
    """Handle 402 Payment Required responses"""
    return JSONResponse(
        status_code=402,
        content={
            "error": "Payment Required",
            "message": "This endpoint requires payment via x402",
            "payment_instructions": {
                "network": NETWORK,
                "pay_to": WALLET_ADDRESS,
                "amount": DEFAULT_PRICE,
                "currency": "USDC",
                "facilitator": FACILITATOR_URL
            }
        },
        headers={
            "X-Payment-Required": "true",
            "X-Payment-Network": NETWORK,
            "X-Payment-Address": WALLET_ADDRESS
        }
    )

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("X402_PORT", 8402))
    logger.info(f"Starting x402 Payment Service on port {port}")
    logger.info(f"Network: {NETWORK}")
    logger.info(f"Wallet: {WALLET_ADDRESS}")
    logger.info(f"Facilitator: {FACILITATOR_URL}")
    
    uvicorn.run(app, host="0.0.0.0", port=port)