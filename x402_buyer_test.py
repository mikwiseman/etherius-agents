#!/usr/bin/env python3
"""
x402 Buyer Test - Properly complete a payment with x402 protocol
This demonstrates how to make a payment that x402 can verify
"""

import os
import json
import httpx
from dotenv import load_dotenv
from x402.types import ExactPaymentPayload, EIP712Domain, TokenAmount, TokenAsset

load_dotenv()

async def test_x402_payment():
    """
    Test making a proper x402 payment
    Note: x402 requires a specific payment proof format, not just sending USDC
    """
    
    # Step 1: Make initial request to get payment requirements
    print("1️⃣ Getting payment requirements...")
    async with httpx.AsyncClient() as client:
        response = await client.post("http://localhost:8402/nft/purchase/test123")
        
        if response.status_code == 402:
            print("✅ Got 402 Payment Required")
            payment_req = response.json()
            print(f"Payment requirements: {json.dumps(payment_req, indent=2)}")
            
            # The payment requirements tell us what we need to pay
            accepts = payment_req.get("accepts", [])
            if accepts:
                requirement = accepts[0]
                print(f"\n💰 Need to pay to: {requirement['payTo']}")
                print(f"   Network: {requirement['network']}")
                print(f"   Asset: {requirement['asset']} (USDC)")
                
                # Step 2: Create payment payload
                # This is what x402 expects - a signed payment proof
                print("\n2️⃣ Creating payment payload...")
                
                # NOTE: In a real implementation, you would:
                # 1. Sign a transaction sending USDC to the payTo address
                # 2. Create an EIP-712 signed message proving the payment
                # 3. Submit that proof in the X-Payment header
                
                print("⚠️  Manual payment verification needed:")
                print("   x402 expects a cryptographically signed payment proof")
                print("   Simply sending USDC isn't enough - it needs the X-Payment header")
                print("   This requires either:")
                print("   - Using x402 client libraries (x402-fetch for JS)")
                print("   - Implementing EIP-712 signing manually")
                print("   - Using a facilitator that monitors on-chain transactions")
                
                return requirement
        else:
            print(f"❌ Expected 402, got {response.status_code}")
            return None

async def check_facilitator_status():
    """Check if the facilitator can see our payment"""
    print("\n3️⃣ Checking facilitator...")
    
    # The facilitator at https://x402.org/facilitator should verify payments
    # But it needs to be configured to monitor your specific transaction
    
    facilitator_url = os.getenv("X402_FACILITATOR_URL", "https://x402.org/facilitator")
    print(f"Facilitator URL: {facilitator_url}")
    
    # Try to check facilitator health
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(facilitator_url)
            print(f"Facilitator response: {response.status_code}")
        except Exception as e:
            print(f"Could not reach facilitator: {e}")

if __name__ == "__main__":
    import asyncio
    
    print("=" * 60)
    print("x402 Payment Test")
    print("=" * 60)
    print("\n⚠️  IMPORTANT: x402 Payment Process")
    print("1. Client requests resource → Gets 402 with payment details")
    print("2. Client creates signed payment proof (EIP-712)")
    print("3. Client sends proof in X-Payment header")
    print("4. Facilitator verifies the cryptographic proof")
    print("5. Server grants access to resource")
    print("\nSimply sending USDC to the wallet is NOT enough!")
    print("The facilitator needs a proper payment proof.\n")
    print("=" * 60)
    
    asyncio.run(test_x402_payment())
    asyncio.run(check_facilitator_status())
    
    print("\n" + "=" * 60)
    print("💡 Solution Options:")
    print("1. Use x402 JavaScript client libraries for proper payment flow")
    print("2. Implement EIP-712 signing in Python (complex)")
    print("3. Use a different facilitator that monitors on-chain txs")
    print("4. For testing: Mock the payment verification")
    print("=" * 60)