"""
X402 Payment Handler Module
Handles real payment processing using the X402 protocol
"""

import os
import json
import time
import asyncio
from typing import Dict, Optional, Any, Tuple
from datetime import datetime, UTC
from enum import Enum
from dotenv import load_dotenv

from web3 import Web3
import httpx

load_dotenv()

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"

class PaymentNetwork(str, Enum):
    BASE_SEPOLIA = "base-sepolia"
    BASE = "base"
    ETHEREUM = "ethereum"

class X402PaymentHandler:
    """Handles X402 payment requests and verification for sellers"""
    
    def __init__(self):
        # Load seller configuration from environment
        # Sellers only need a wallet address to receive payments, no private key required
        self.wallet_address = os.getenv("X402_WALLET_ADDRESS", "")
        self.facilitator_url = os.getenv("X402_FACILITATOR_URL", "https://x402.org/facilitator")
        self.network = os.getenv("X402_NETWORK", "base-sepolia")
        self.usdc_contract = os.getenv("X402_USDC_CONTRACT", "0x036CbD53842c5426634e7929541eC2318f3dCF7e")
        
        # Initialize Web3 for blockchain interactions (read-only for sellers)
        self._init_web3()
        
        # Payment tracking
        self.pending_payments: Dict[str, Dict[str, Any]] = {}
        self.completed_payments: Dict[str, Dict[str, Any]] = {}
        
    def _init_web3(self):
        """Initialize Web3 connection for sellers (read-only)"""
        # Use appropriate RPC based on network
        if self.network == "base-sepolia":
            rpc_url = "https://sepolia.base.org"
        elif self.network == "base":
            rpc_url = "https://mainnet.base.org"
        else:
            rpc_url = os.getenv("WEB3_PROVIDER_URL", "https://mainnet.infura.io/v3/")
            
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        
        # Sellers don't need an account - they only receive payments
        # Buyers handle the actual transaction signing
        self.account = None
    
    def create_payment_request(
        self,
        product_id: str,
        amount_usd: float,
        description: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a payment request for X402 protocol
        
        Args:
            product_id: Unique identifier for the product/service
            amount_usd: Amount in USD to charge
            description: Description of the payment
            metadata: Additional metadata for the payment
            
        Returns:
            Payment request details including payment ID and instructions
        """
        # Generate unique payment ID
        payment_id = f"PAY_{int(time.time())}_{product_id}"
        
        # Create payment request structure
        payment_request = {
            "payment_id": payment_id,
            "product_id": product_id,
            "amount_usd": amount_usd,
            "amount_usdc": amount_usd,  # 1:1 for stablecoins
            "description": description,
            "recipient_address": self.wallet_address,
            "network": self.network,
            "usdc_contract": self.usdc_contract,
            "status": PaymentStatus.PENDING,
            "created_at": datetime.now(UTC).isoformat(),
            "expires_at": datetime.fromtimestamp(time.time() + 600, UTC).isoformat(),  # 10 min expiry
            "metadata": metadata or {},
            "payment_instructions": {
                "method": "x402",
                "network": self.network,
                "token": "USDC",
                "recipient": self.wallet_address,
                "amount": str(amount_usd),
                "facilitator": self.facilitator_url
            }
        }
        
        # Store in pending payments
        self.pending_payments[payment_id] = payment_request
        
        return payment_request
    
    def generate_payment_url(self, payment_request: Dict[str, Any]) -> str:
        """
        Generate a payment URL for X402 protocol
        
        Args:
            payment_request: Payment request details
            
        Returns:
            Payment URL string
        """
        # Create X402 payment URL with all necessary parameters
        base_url = "https://pay.x402.org/checkout"
        
        # Build query parameters
        params = {
            "recipient": payment_request["recipient_address"],
            "amount": str(payment_request["amount_usdc"]),
            "token": "USDC",
            "network": payment_request["network"],
            "payment_id": payment_request["payment_id"],
            "description": payment_request["description"],
            "return_url": f"https://your-app.com/payment/success/{payment_request['payment_id']}",
            "cancel_url": f"https://your-app.com/payment/cancel/{payment_request['payment_id']}"
        }
        
        # Construct URL with parameters
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        payment_url = f"{base_url}?{query_string}"
        
        return payment_url
    
    async def verify_payment(
        self,
        payment_id: str,
        transaction_hash: Optional[str] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Verify a payment through the X402 facilitator
        
        Args:
            payment_id: Unique payment identifier
            transaction_hash: Optional blockchain transaction hash
            
        Returns:
            Tuple of (success, payment_details)
        """
        if payment_id not in self.pending_payments:
            return False, {"error": "Payment not found", "payment_id": payment_id}
        
        payment = self.pending_payments[payment_id]
        
        try:
            # Check if payment has expired
            expires_at = datetime.fromisoformat(payment["expires_at"])
            if datetime.now(UTC) > expires_at:
                payment["status"] = PaymentStatus.EXPIRED
                return False, {"error": "Payment expired", "payment": payment}
            
            # Verify payment through facilitator
            async with httpx.AsyncClient() as client:
                verify_url = f"{self.facilitator_url}/verify"
                
                verify_data = {
                    "payment_id": payment_id,
                    "recipient": payment["recipient_address"],
                    "amount": str(payment["amount_usdc"]),
                    "network": payment["network"]
                }
                
                if transaction_hash:
                    verify_data["transaction_hash"] = transaction_hash
                
                response = await client.post(
                    verify_url,
                    json=verify_data,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if result.get("verified", False):
                        # Payment verified successfully
                        payment["status"] = PaymentStatus.COMPLETED
                        payment["transaction_hash"] = result.get("transaction_hash")
                        payment["completed_at"] = datetime.now(UTC).isoformat()
                        
                        # Move to completed payments
                        self.completed_payments[payment_id] = payment
                        del self.pending_payments[payment_id]
                        
                        return True, payment
                    else:
                        # Payment not yet confirmed
                        payment["status"] = PaymentStatus.PROCESSING
                        return False, {"error": "Payment not yet confirmed", "payment": payment}
                else:
                    # Facilitator returned error
                    error_msg = response.text if response.text else "Unknown error"
                    return False, {"error": f"Facilitator error: {error_msg}", "payment": payment}
                    
        except Exception as e:
            # Handle verification errors
            payment["status"] = PaymentStatus.FAILED
            return False, {"error": f"Verification failed: {str(e)}", "payment": payment}
    
    async def check_payment_status(self, payment_id: str) -> Dict[str, Any]:
        """
        Check the current status of a payment
        
        Args:
            payment_id: Unique payment identifier
            
        Returns:
            Payment status details
        """
        # Check completed payments first
        if payment_id in self.completed_payments:
            return self.completed_payments[payment_id]
        
        # Check pending payments
        if payment_id in self.pending_payments:
            payment = self.pending_payments[payment_id]
            
            # Try to verify if still pending
            if payment["status"] == PaymentStatus.PENDING:
                verified, details = await self.verify_payment(payment_id)
                return details if "payment" in details else payment
            
            return payment
        
        # Payment not found
        return {
            "payment_id": payment_id,
            "status": "not_found",
            "error": "Payment ID not found in system"
        }
    
    def calculate_network_fee(self, network: str = None) -> float:
        """
        Calculate network fee for the payment
        
        Args:
            network: Network to use (defaults to configured network)
            
        Returns:
            Estimated network fee in USD
        """
        network = network or self.network
        
        # X402 on Base has minimal fees
        fees = {
            "base": 0.001,  # ~$0.001 on Base mainnet
            "base-sepolia": 0.0,  # Free on testnet
            "ethereum": 5.0  # Higher on Ethereum mainnet
        }
        
        return fees.get(network, 0.01)
    
    async def process_refund(
        self,
        payment_id: str,
        reason: str,
        amount: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Process a refund for a completed payment
        Note: Sellers would need to manually process refunds through their wallet
        
        Args:
            payment_id: Payment to refund
            reason: Reason for refund
            amount: Optional partial refund amount
            
        Returns:
            Refund details
        """
        if payment_id not in self.completed_payments:
            return {
                "success": False,
                "error": "Payment not found or not completed"
            }
        
        payment = self.completed_payments[payment_id]
        refund_amount = amount or payment["amount_usdc"]
        
        # Sellers need to manually process refunds from their wallet
        # This just tracks the refund request
        refund = {
            "refund_id": f"REF_{int(time.time())}_{payment_id}",
            "payment_id": payment_id,
            "amount": refund_amount,
            "reason": reason,
            "status": "manual_processing_required",
            "initiated_at": datetime.now(UTC).isoformat(),
            "instructions": f"Please manually send {refund_amount} USDC to the buyer's wallet"
        }
        
        return {
            "success": True,
            "refund": refund,
            "note": "Manual refund processing required from seller's wallet"
        }
    
    def get_payment_analytics(self) -> Dict[str, Any]:
        """
        Get payment analytics and statistics
        
        Returns:
            Analytics data
        """
        total_pending = len(self.pending_payments)
        total_completed = len(self.completed_payments)
        
        total_volume = sum(
            p.get("amount_usdc", 0) 
            for p in self.completed_payments.values()
        )
        
        return {
            "total_pending": total_pending,
            "total_completed": total_completed,
            "total_volume_usdc": total_volume,
            "network": self.network,
            "wallet_address": self.wallet_address,
            "facilitator": self.facilitator_url
        }

# Singleton instance
payment_handler = X402PaymentHandler()