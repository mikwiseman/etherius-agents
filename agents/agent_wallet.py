"""
Agent Wallet Manager
Handles wallet creation and x402 payments using CDP or eth-account
"""

import os
import json
import asyncio
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# Try to use CDP if available, otherwise fall back to eth-account
CDP_AVAILABLE = False
try:
    from cdp import CdpClient
    CDP_API_KEY_ID = os.getenv("CDP_API_KEY_ID")
    CDP_API_KEY_SECRET = os.getenv("CDP_API_KEY_SECRET")
    if CDP_API_KEY_ID and CDP_API_KEY_SECRET:
        CDP_AVAILABLE = True
        print("✅ Using CDP for wallet management")
    else:
        print("⚠️ CDP API keys not found, using eth-account instead")
except ImportError:
    print("⚠️ CDP not available, using eth-account")

from eth_account import Account
from x402.clients.requests import x402_requests

class AgentWallet:
    """
    Agent wallet that can use either CDP or eth-account
    Handles x402 payments automatically
    """
    
    def __init__(self):
        self.account = None
        self.session = None
        self.wallet_address = None
        self.wallet_data_file = "agent_wallet_data.json"
        self.using_cdp = False
        
    async def initialize(self):
        """Initialize wallet using CDP or eth-account"""
        
        # Try to load existing wallet data
        if os.path.exists(self.wallet_data_file):
            with open(self.wallet_data_file, 'r') as f:
                wallet_data = json.load(f)
                self.wallet_address = wallet_data.get('address')
                print(f"📱 Loaded existing agent wallet: {self.wallet_address}")
        
        if CDP_AVAILABLE:
            await self._initialize_cdp()
        else:
            self._initialize_eth_account()
        
        # Create x402 session if account is available
        if self.account:
            self.session = x402_requests(self.account)
            print(f"✅ x402 session created for wallet: {self.wallet_address}")
    
    async def _initialize_cdp(self):
        """Initialize using CDP (Coinbase Developer Platform)"""
        try:
            self.cdp_client = CdpClient()
            
            # Create new account if no existing wallet
            if not self.wallet_address:
                self.account = await self.cdp_client.evm.create_account()
                self.wallet_address = self.account.address
                self.using_cdp = True
                
                # Save wallet address
                with open(self.wallet_data_file, 'w') as f:
                    json.dump({
                        "address": self.wallet_address,
                        "type": "CDP"
                    }, f)
                
                print(f"✨ Created new CDP wallet: {self.wallet_address}")
                print(f"💰 Fund this wallet with USDC on Base Sepolia")
            else:
                # For existing wallets, we'd need to restore from CDP
                # This is simplified - in production you'd store wallet_id
                print(f"⚠️ Cannot restore CDP wallet yet, creating new one")
                self.account = await self.cdp_client.evm.create_account()
                self.wallet_address = self.account.address
                self.using_cdp = True
                
        except Exception as e:
            print(f"❌ CDP initialization failed: {e}")
            print("Falling back to eth-account")
            self._initialize_eth_account()
    
    def _initialize_eth_account(self):
        """Initialize using eth-account (with private key)"""
        private_key_file = "agent_wallet.key"
        
        # Check for existing private key
        if os.path.exists(private_key_file):
            with open(private_key_file, 'r') as f:
                private_key = f.read().strip()
            self.account = Account.from_key(private_key)
            self.wallet_address = self.account.address
            print(f"🔑 Loaded wallet from private key: {self.wallet_address}")
        else:
            # Generate new wallet
            self.account = Account.create()
            self.wallet_address = self.account.address
            
            # Save private key (CAREFUL - only for demo!)
            with open(private_key_file, 'w') as f:
                f.write(self.account.key.hex())
            
            # Save wallet data
            with open(self.wallet_data_file, 'w') as f:
                json.dump({
                    "address": self.wallet_address,
                    "type": "eth-account"
                }, f)
            
            print(f"🔐 Generated new wallet: {self.wallet_address}")
            print(f"⚠️ Private key saved to {private_key_file} (keep this secret!)")
            print(f"💰 Fund this wallet with USDC on Base Sepolia")
    
    async def execute_payment(self, payment_id: str, amount: float = 0.01):
        """
        Execute payment using x402 protocol
        
        Args:
            payment_id: Unique payment identifier
            amount: Payment amount in USDC
        
        Returns:
            Response from x402 payment
        """
        if not self.session:
            if not self.account:
                print("❌ No wallet account available")
                return None
            
            # Create new session
            self.session = x402_requests(self.account)
        
        # Make x402 payment request
        url = f"http://localhost:8402/nft/purchase/{payment_id}"
        
        print(f"💸 Executing x402 payment...")
        print(f"   Payment ID: {payment_id}")
        print(f"   Amount: ${amount}")
        print(f"   From wallet: {self.wallet_address}")
        
        try:
            response = self.session.post(url)
            
            if response.status_code == 200:
                print(f"✅ Payment successful!")
                return response
            elif response.status_code == 402:
                print(f"⚠️ Payment required - checking wallet balance")
                return response
            else:
                print(f"❌ Payment failed: {response.status_code}")
                return response
                
        except Exception as e:
            print(f"❌ Payment error: {e}")
            return None
    
    def get_address(self) -> str:
        """Get wallet address for funding"""
        return self.wallet_address
    
    def get_wallet_info(self) -> dict:
        """Get wallet information"""
        return {
            "address": self.wallet_address,
            "type": "CDP" if self.using_cdp else "eth-account",
            "network": "base-sepolia",
            "ready": self.account is not None
        }

# Utility function for testing
async def test_wallet():
    """Test wallet creation and info"""
    wallet = AgentWallet()
    await wallet.initialize()
    
    info = wallet.get_wallet_info()
    print("\n📊 Wallet Info:")
    print(f"   Address: {info['address']}")
    print(f"   Type: {info['type']}")
    print(f"   Network: {info['network']}")
    print(f"   Ready: {info['ready']}")
    
    print("\n💡 Next steps:")
    print(f"1. Fund wallet with USDC on Base Sepolia")
    print(f"2. Use wallet.execute_payment() to make x402 payments")

if __name__ == "__main__":
    # Test wallet initialization
    asyncio.run(test_wallet())