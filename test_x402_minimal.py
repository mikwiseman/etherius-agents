#!/usr/bin/env python3
"""
Minimal x402 test to verify the correct decorator syntax
"""

import os
from dotenv import load_dotenv
from fastapi import FastAPI
from x402.fastapi.middleware import require_payment

load_dotenv()

app = FastAPI()

# Test with minimal configuration
@app.get("/test")
@require_payment(
    price="$0.01",
    pay_to_address=os.getenv("X402_WALLET_ADDRESS", "0x0000000000000000000000000000000000000000"),
    network="base-sepolia"
)
async def test_endpoint():
    return {"status": "payment verified"}

if __name__ == "__main__":
    import uvicorn
    print("Testing minimal x402 configuration...")
    print("If this starts without errors, the decorator syntax is correct.")
    uvicorn.run(app, host="0.0.0.0", port=8403)