#!/usr/bin/env python3
"""
Test script for x402 payment verification
Run this to test the real blockchain payment flow
"""

import asyncio
import httpx
import sys
import time
from typing import Optional

# Configuration
X402_SERVICE_URL = "http://localhost:8402"
ETHERIUS_AGENT_URL = "http://localhost:8100"

async def test_x402_service():
    """Test if x402 service is running"""
    print("🔍 Testing x402 service...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{X402_SERVICE_URL}/health")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ x402 service is healthy")
                print(f"   Network: {data['network']}")
                print(f"   Wallet: {data['wallet']}")
                return True
            else:
                print(f"❌ x402 service returned status {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Could not connect to x402 service: {e}")
        print("   Make sure to run: python agents/x402_service.py")
        return False

async def create_payment_request(nft_name: str = "Test NFT", price: float = 0.01):
    """Create a payment request via x402"""
    print(f"\n💳 Creating payment request for {nft_name}...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{X402_SERVICE_URL}/payment/create",
                params={"nft_name": nft_name, "price": price}
            )
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Payment request created")
                print(f"   Payment ID: {data['payment_id']}")
                print(f"   Price: ${data['price']} {data['currency']}")
                print(f"   Network: {data['network']}")
                print(f"   Pay to: {data['pay_to']}")
                return data
            else:
                print(f"❌ Failed to create payment request: {response.status_code}")
                return None
    except Exception as e:
        print(f"❌ Error creating payment request: {e}")
        return None

async def check_payment_status(payment_id: str):
    """Check payment status"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{X402_SERVICE_URL}/payment/status/{payment_id}"
            )
            if response.status_code == 200:
                return response.json()
            else:
                return None
    except:
        return None

async def test_payment_verification(payment_id: str):
    """Test payment verification endpoint (will return 402 unless paid)"""
    print(f"\n🔐 Testing payment verification for {payment_id}...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{X402_SERVICE_URL}/nft/purchase/{payment_id}",
                json={"payment_id": payment_id}
            )
            
            if response.status_code == 402:
                print("⏳ Payment required (402) - This is expected before payment")
                data = response.json()
                print(f"   Instructions: {data}")
                return False
            elif response.status_code == 200:
                print("✅ Payment verified!")
                data = response.json()
                print(f"   Transaction: {data.get('tx_hash', 'N/A')}")
                return True
            else:
                print(f"❌ Unexpected status: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Error verifying payment: {e}")
        return False

async def test_etherius_buy_command():
    """Test the buy command through Etherius agent"""
    print("\n🤖 Testing Etherius agent buy command...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{ETHERIUS_AGENT_URL}/chat",
                json={"message": "buy Bored Ape #1234"}
            )
            if response.status_code == 200:
                data = response.json()
                print("✅ Buy command processed")
                print(f"Response preview: {data['response'][:200]}...")
                return True
            else:
                print(f"❌ Etherius agent returned status {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Could not connect to Etherius agent: {e}")
        print("   Make sure to run: python agents/etherius_agent.py")
        return False

async def main():
    print("=" * 60)
    print("🧪 x402 Payment System Test Suite")
    print("=" * 60)
    
    # Test 1: Check x402 service
    if not await test_x402_service():
        print("\n⚠️  Please start the x402 service first:")
        print("   python agents/x402_service.py")
        return
    
    # Test 2: Create payment request
    payment_data = await create_payment_request("Test NFT", 0.01)
    if not payment_data:
        return
    
    payment_id = payment_data["payment_id"]
    
    # Test 3: Check payment status (should be pending)
    print(f"\n📊 Checking payment status...")
    status = await check_payment_status(payment_id)
    if status:
        print(f"   Status: {status.get('status', 'unknown')}")
    
    # Test 4: Try to verify payment (should get 402)
    await test_payment_verification(payment_id)
    
    # Test 5: Test Etherius agent integration
    await test_etherius_buy_command()
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("\nTo complete a real payment:")
    print(f"1. Send {payment_data['price']} USDC to {payment_data['pay_to']}")
    print(f"2. On network: {payment_data['network']}")
    print(f"3. Then verify at: {X402_SERVICE_URL}/nft/purchase/{payment_id}")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())