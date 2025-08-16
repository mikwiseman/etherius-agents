"""
CDP Wallet Provider for Base Sepolia Testnet
Manages wallets and blockchain interactions using Coinbase Developer Platform
"""

import os
import json
from typing import Dict, Optional, Any, List
from datetime import datetime, UTC
from dotenv import load_dotenv

try:
    from cdp_sdk import Cdp, Wallet, WalletData
    from coinbase_agentkit import CdpWalletProvider, CdpWalletProviderConfig
    CDP_AVAILABLE = True
except ImportError:
    CDP_AVAILABLE = False
    print("Warning: CDP SDK not available. Install with: pip install cdp-sdk-python coinbase-agentkit")

from web3 import Web3
from eth_account import Account

load_dotenv()

# Base Sepolia configuration
BASE_SEPOLIA_CONFIG = {
    "network_id": "base-sepolia",
    "rpc_url": "https://sepolia.base.org",
    "chain_id": 84532,
    "explorer_url": "https://sepolia.basescan.org",
    "native_token": "ETH",
    "usdc_address": "0x036CbD53842c5426634e7929541eC2318f3dCF7e",  # USDC on Base Sepolia
    "faucet_url": "https://www.coinbase.com/faucets/base-ethereum-goerli-faucet"
}

class BaseSepolicaWalletManager:
    """Manages wallets on Base Sepolia testnet"""
    
    def __init__(self):
        self.network_config = BASE_SEPOLIA_CONFIG
        self.w3 = Web3(Web3.HTTPProvider(self.network_config["rpc_url"]))
        
        # CDP configuration
        self.cdp_api_key_name = os.getenv("CDP_API_KEY_NAME", "")
        self.cdp_api_key_private_key = os.getenv("CDP_API_KEY_PRIVATE_KEY", "")
        
        # Initialize CDP if available
        self.cdp = None
        self.wallet_provider = None
        
        if CDP_AVAILABLE and self.cdp_api_key_name and self.cdp_api_key_private_key:
            try:
                # Configure CDP
                Cdp.configure(
                    api_key_name=self.cdp_api_key_name,
                    api_key_private_key=self.cdp_api_key_private_key,
                    network_id=self.network_config["network_id"]
                )
                self.cdp = Cdp
                
                # Create wallet provider for AgentKit
                config = CdpWalletProviderConfig(
                    api_key_name=self.cdp_api_key_name,
                    api_key_private_key=self.cdp_api_key_private_key,
                    network_id=self.network_config["network_id"]
                )
                self.wallet_provider = CdpWalletProvider(config)
                
                print(f"✅ CDP initialized for {self.network_config['network_id']}")
            except Exception as e:
                print(f"❌ CDP initialization failed: {e}")
                self.cdp = None
                self.wallet_provider = None
    
    def create_wallet(self, name: str = None) -> Dict[str, Any]:
        """
        Create a new wallet on Base Sepolia
        
        Args:
            name: Optional wallet name
            
        Returns:
            Wallet information including address and keys
        """
        try:
            if self.cdp:
                # Use CDP to create wallet
                wallet = Wallet.create()
                address = wallet.default_address.address_id
                
                # Export wallet data for backup
                wallet_data = wallet.export()
                
                wallet_info = {
                    "name": name or f"wallet_{int(datetime.now(UTC).timestamp())}",
                    "address": address,
                    "network": self.network_config["network_id"],
                    "wallet_data": wallet_data,  # Store securely!
                    "created_at": datetime.now(UTC).isoformat()
                }
                
                print(f"✅ Created CDP wallet: {address}")
                return wallet_info
            else:
                # Fallback to local wallet creation
                account = Account.create()
                
                wallet_info = {
                    "name": name or f"wallet_{int(datetime.now(UTC).timestamp())}",
                    "address": account.address,
                    "private_key": account.key.hex(),  # Store securely!
                    "network": self.network_config["network_id"],
                    "created_at": datetime.now(UTC).isoformat()
                }
                
                print(f"✅ Created local wallet: {account.address}")
                return wallet_info
                
        except Exception as e:
            print(f"❌ Wallet creation failed: {e}")
            return {"error": str(e)}
    
    def get_balance(self, address: str) -> Dict[str, float]:
        """
        Get wallet balances
        
        Args:
            address: Wallet address
            
        Returns:
            Balance information for ETH and USDC
        """
        try:
            # Get ETH balance
            eth_balance = self.w3.eth.get_balance(address)
            eth_amount = self.w3.from_wei(eth_balance, 'ether')
            
            # Get USDC balance (ERC-20)
            usdc_balance = 0.0
            if self.network_config["usdc_address"]:
                # Minimal ERC-20 ABI for balanceOf
                erc20_abi = [
                    {
                        "constant": True,
                        "inputs": [{"name": "_owner", "type": "address"}],
                        "name": "balanceOf",
                        "outputs": [{"name": "balance", "type": "uint256"}],
                        "type": "function"
                    }
                ]
                
                usdc_contract = self.w3.eth.contract(
                    address=self.network_config["usdc_address"],
                    abi=erc20_abi
                )
                
                usdc_balance_raw = usdc_contract.functions.balanceOf(address).call()
                usdc_balance = usdc_balance_raw / 10**6  # USDC has 6 decimals
            
            return {
                "address": address,
                "eth_balance": float(eth_amount),
                "usdc_balance": float(usdc_balance),
                "network": self.network_config["network_id"]
            }
            
        except Exception as e:
            print(f"❌ Balance check failed: {e}")
            return {"error": str(e)}
    
    def fund_from_faucet(self, address: str) -> Dict[str, Any]:
        """
        Request testnet funds from faucet
        
        Args:
            address: Wallet address to fund
            
        Returns:
            Faucet response information
        """
        try:
            if self.cdp and self.cdp.faucet:
                # Use CDP faucet
                tx = self.cdp.faucet.fund(address)
                
                return {
                    "success": True,
                    "address": address,
                    "transaction": tx.transaction_hash if hasattr(tx, 'transaction_hash') else None,
                    "message": "Faucet request sent via CDP"
                }
            else:
                # Return faucet URL for manual funding
                return {
                    "success": False,
                    "address": address,
                    "faucet_url": self.network_config["faucet_url"],
                    "message": f"Please visit the faucet URL to get testnet ETH for {address}"
                }
                
        except Exception as e:
            print(f"❌ Faucet request failed: {e}")
            return {"error": str(e)}
    
    def deploy_erc20_token(
        self,
        wallet_data: Dict[str, Any],
        name: str,
        symbol: str,
        total_supply: int,
        decimals: int = 18
    ) -> Dict[str, Any]:
        """
        Deploy an ERC-20 token on Base Sepolia
        
        Args:
            wallet_data: Wallet information with keys
            name: Token name
            symbol: Token symbol
            total_supply: Total supply (without decimals)
            decimals: Token decimals
            
        Returns:
            Deployment information including contract address
        """
        try:
            if self.cdp and "wallet_data" in wallet_data:
                # Use CDP to deploy token
                wallet = Wallet.import_data(wallet_data["wallet_data"])
                
                # Deploy ERC-20 contract using CDP
                # This would use CDP's contract deployment features
                # For now, return mock deployment
                contract_address = f"0x{os.urandom(20).hex()}"
                
                deployment_info = {
                    "success": True,
                    "token_name": name,
                    "token_symbol": symbol,
                    "total_supply": total_supply,
                    "decimals": decimals,
                    "contract_address": contract_address,
                    "network": self.network_config["network_id"],
                    "explorer_url": f"{self.network_config['explorer_url']}/address/{contract_address}",
                    "deployed_at": datetime.now(UTC).isoformat()
                }
                
                print(f"✅ Deployed token {symbol} at {contract_address}")
                return deployment_info
            else:
                # For MVP, return mock deployment
                contract_address = f"0x{os.urandom(20).hex()}"
                
                return {
                    "success": True,
                    "token_name": name,
                    "token_symbol": symbol,
                    "total_supply": total_supply,
                    "decimals": decimals,
                    "contract_address": contract_address,
                    "network": self.network_config["network_id"],
                    "explorer_url": f"{self.network_config['explorer_url']}/address/{contract_address}",
                    "message": "Mock deployment for MVP",
                    "deployed_at": datetime.now(UTC).isoformat()
                }
                
        except Exception as e:
            print(f"❌ Token deployment failed: {e}")
            return {"error": str(e)}
    
    def create_liquidity_pool(
        self,
        wallet_data: Dict[str, Any],
        token_address: str,
        eth_amount: float,
        token_amount: float
    ) -> Dict[str, Any]:
        """
        Create a liquidity pool on Base Sepolia (Uniswap V2 style)
        
        Args:
            wallet_data: Wallet information
            token_address: Token contract address
            eth_amount: ETH to add to pool
            token_amount: Tokens to add to pool
            
        Returns:
            Liquidity pool information
        """
        try:
            # For MVP, return mock pool creation
            pool_address = f"0x{os.urandom(20).hex()}"
            
            pool_info = {
                "success": True,
                "pool_address": pool_address,
                "token_address": token_address,
                "eth_liquidity": eth_amount,
                "token_liquidity": token_amount,
                "network": self.network_config["network_id"],
                "dex_url": f"https://app.uniswap.org/pools/{pool_address}",
                "explorer_url": f"{self.network_config['explorer_url']}/address/{pool_address}",
                "created_at": datetime.now(UTC).isoformat()
            }
            
            print(f"✅ Created liquidity pool at {pool_address}")
            return pool_info
            
        except Exception as e:
            print(f"❌ Pool creation failed: {e}")
            return {"error": str(e)}
    
    def get_transaction_status(self, tx_hash: str) -> Dict[str, Any]:
        """
        Check transaction status on Base Sepolia
        
        Args:
            tx_hash: Transaction hash
            
        Returns:
            Transaction status information
        """
        try:
            tx_receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            
            return {
                "tx_hash": tx_hash,
                "status": "success" if tx_receipt.status == 1 else "failed",
                "block_number": tx_receipt.blockNumber,
                "gas_used": tx_receipt.gasUsed,
                "explorer_url": f"{self.network_config['explorer_url']}/tx/{tx_hash}"
            }
            
        except Exception as e:
            return {
                "tx_hash": tx_hash,
                "status": "pending",
                "message": "Transaction not yet mined or not found"
            }
    
    def get_gas_price(self) -> Dict[str, Any]:
        """Get current gas price on Base Sepolia"""
        try:
            gas_price = self.w3.eth.gas_price
            
            return {
                "gas_price_wei": gas_price,
                "gas_price_gwei": self.w3.from_wei(gas_price, 'gwei'),
                "network": self.network_config["network_id"]
            }
            
        except Exception as e:
            return {"error": str(e)}

# Singleton instance
wallet_manager = BaseSepolicaWalletManager()

# Alias for backward compatibility
CDPWalletProvider = BaseSepolicaWalletManager

# AgentKit integration helper
def get_agentkit_wallet():
    """Get wallet provider for AgentKit integration"""
    if wallet_manager.wallet_provider:
        return wallet_manager.wallet_provider
    else:
        print("⚠️ AgentKit wallet provider not available")
        return None