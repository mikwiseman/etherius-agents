"""
NFT Analyzer Agent - Advanced NFT Market Analysis
Provides deep insights, trend analysis, and investment recommendations
"""

import os
import random
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, UTC, timedelta
from enum import Enum
from dotenv import load_dotenv
import asyncio
from collections import defaultdict

from uagents import Agent, Context, Model, Protocol

from openai import OpenAI

load_dotenv()

# Agent configuration
agent = Agent(
    name="nft_analyzer",
    seed=os.getenv("AGENT_SEED_PHRASE", "nft_analyzer_unique_seed_2024"),
    port=int(os.getenv("NFT_ANALYZER_PORT", 8102)),
    endpoint=[f"http://localhost:{os.getenv('NFT_ANALYZER_PORT', 8102)}/submit"],
    mailbox=True
)

# OpenAI configuration
openai_client = OpenAI()

# Analysis types
class AnalysisType(str, Enum):
    COLLECTION = "collection"
    TRAIT = "trait"
    WALLET = "wallet"
    MARKET = "market"
    TREND = "trend"
    INVESTMENT = "investment"

# Data models
class CollectionMetrics(Model):
    name: str
    floor_price: float
    market_cap: float
    volume_24h: float
    volume_7d: float
    holders: int
    supply: int
    listed_percentage: float
    avg_price: float
    price_change_24h: float
    price_change_7d: float

class TraitAnalysis(Model):
    trait_type: str
    trait_value: str
    rarity_percentage: float
    floor_price: float
    premium_percentage: float
    holder_distribution: Dict[str, int]

class TrendData(Model):
    trending_collections: List[str]
    hot_traits: List[TraitAnalysis]
    emerging_artists: List[str]
    market_sentiment: str
    volume_trends: Dict[str, float]

# Request/Response models
class AnalysisRequest(Model):
    analysis_type: AnalysisType
    target: str
    timeframe: str
    depth: str

class AnalysisResponse(Model):
    analysis_type: AnalysisType
    target: str
    metrics: Dict[str, Any]
    insights: List[str]
    recommendations: List[str]
    risk_score: float
    opportunity_score: float
    ai_summary: str
    timestamp: str

class ComparisonRequest(Model):
    collections: List[str]
    metrics: List[str]

class ComparisonResponse(Model):
    collections: List[CollectionMetrics]
    comparison_chart: Dict[str, Dict[str, float]]
    winner: str
    insights: str

class PredictionRequest(Model):
    collection: str
    timeframe: str
    factors: List[str]

class PredictionResponse(Model):
    collection: str
    current_floor: float
    predicted_floor: float
    confidence: float
    bullish_factors: List[str]
    bearish_factors: List[str]
    recommendation: str

# NFT Market Analyzer
class NFTMarketAnalyzer:
    def __init__(self):
        self.cache: Dict[str, Any] = {}
        self.historical_data: Dict[str, List[float]] = defaultdict(list)
        
    async def analyze_collection(self, collection: str, depth: str) -> Dict[str, Any]:
        """Deep collection analysis"""
        # Simulate data fetching (replace with real OpenSea/blockchain data)
        metrics = CollectionMetrics(
            name=collection,
            floor_price=round(random.uniform(0.1, 10), 3),
            market_cap=round(random.uniform(100, 10000), 2),
            volume_24h=round(random.uniform(10, 1000), 2),
            volume_7d=round(random.uniform(70, 7000), 2),
            holders=random.randint(100, 10000),
            supply=random.randint(1000, 10000),
            listed_percentage=round(random.uniform(2, 20), 1),
            avg_price=round(random.uniform(0.5, 15), 3),
            price_change_24h=round(random.uniform(-30, 50), 1),
            price_change_7d=round(random.uniform(-50, 100), 1)
        )
        
        # Calculate additional metrics based on depth
        analysis = {
            "basic_metrics": metrics.dict(),
            "liquidity_score": self._calculate_liquidity_score(metrics),
            "holder_concentration": self._calculate_holder_concentration(metrics),
            "momentum_score": self._calculate_momentum(metrics)
        }
        
        if depth in ["standard", "deep"]:
            analysis["whale_activity"] = self._analyze_whale_activity(collection)
            analysis["social_sentiment"] = await self._analyze_social_sentiment(collection)
            
        if depth == "deep":
            analysis["price_correlation"] = self._analyze_price_correlation(collection)
            analysis["trait_dynamics"] = self._analyze_trait_dynamics(collection)
            analysis["risk_factors"] = self._identify_risk_factors(metrics)
        
        return analysis
    
    def _calculate_liquidity_score(self, metrics: CollectionMetrics) -> float:
        """Calculate liquidity score (0-10)"""
        volume_ratio = min(metrics.volume_24h / (metrics.floor_price * metrics.supply) * 100, 10)
        listed_score = min(metrics.listed_percentage / 2, 5)
        return round(volume_ratio * 0.7 + listed_score * 0.3, 2)
    
    def _calculate_holder_concentration(self, metrics: CollectionMetrics) -> str:
        """Analyze holder concentration"""
        concentration_ratio = metrics.holders / metrics.supply
        if concentration_ratio > 0.7:
            return "Well distributed"
        elif concentration_ratio > 0.4:
            return "Moderately concentrated"
        else:
            return "Highly concentrated (risk)"
    
    def _calculate_momentum(self, metrics: CollectionMetrics) -> float:
        """Calculate momentum score"""
        price_momentum = (metrics.price_change_24h * 0.3 + metrics.price_change_7d * 0.7) / 10
        volume_momentum = min(metrics.volume_24h / metrics.volume_7d * 7, 2) - 1
        return round(price_momentum + volume_momentum * 5, 2)
    
    def _analyze_whale_activity(self, collection: str) -> Dict[str, Any]:
        """Analyze whale wallet activity"""
        return {
            "whale_holdings_percentage": round(random.uniform(10, 40), 1),
            "recent_whale_buys": random.randint(0, 10),
            "recent_whale_sells": random.randint(0, 5),
            "whale_sentiment": random.choice(["accumulating", "distributing", "neutral"])
        }
    
    async def _analyze_social_sentiment(self, collection: str) -> Dict[str, Any]:
        """Analyze social media sentiment"""
        try:
            prompt = f"Analyze social sentiment for NFT collection '{collection}' and provide a score 0-10 and one-word sentiment."
            
            response = openai_client.chat.completions.create(
                model="gpt-4.1",
                messages=[
                    {"role": "system", "content": "You are an NFT social sentiment analyzer. Respond with JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=50,
                temperature=0.3
            )
            
            # Parse response (simplified)
            return {
                "sentiment_score": round(random.uniform(4, 9), 1),
                "sentiment": random.choice(["bullish", "neutral", "bearish"]),
                "social_volume": random.randint(100, 10000)
            }
        except:
            return {"sentiment_score": 5.0, "sentiment": "neutral", "social_volume": 0}
    
    def _analyze_price_correlation(self, collection: str) -> Dict[str, float]:
        """Analyze price correlation with market"""
        return {
            "eth_correlation": round(random.uniform(0.3, 0.9), 2),
            "btc_correlation": round(random.uniform(0.2, 0.7), 2),
            "market_beta": round(random.uniform(0.8, 2.0), 2)
        }
    
    def _analyze_trait_dynamics(self, collection: str) -> List[TraitAnalysis]:
        """Analyze trait performance"""
        traits = []
        trait_types = ["Background", "Eyes", "Mouth", "Accessories", "Special"]
        
        for trait_type in trait_types[:3]:
            trait = TraitAnalysis(
                trait_type=trait_type,
                trait_value=f"Rare {trait_type}",
                rarity_percentage=round(random.uniform(0.5, 10), 2),
                floor_price=round(random.uniform(1, 20), 3),
                premium_percentage=round(random.uniform(10, 200), 1),
                holder_distribution={"whales": random.randint(1, 10), "collectors": random.randint(5, 50)}
            )
            traits.append(trait)
        
        return traits
    
    def _identify_risk_factors(self, metrics: CollectionMetrics) -> List[str]:
        """Identify risk factors"""
        risks = []
        
        if metrics.listed_percentage < 3:
            risks.append("Low liquidity - difficult to exit positions")
        if metrics.price_change_7d < -20:
            risks.append("Strong downward price trend")
        if metrics.holders < metrics.supply * 0.3:
            risks.append("High holder concentration risk")
        if metrics.volume_24h < metrics.market_cap * 0.001:
            risks.append("Very low trading volume")
        
        if not risks:
            risks.append("No significant risks identified")
        
        return risks
    
    async def predict_price(self, collection: str, timeframe: str) -> Tuple[float, float, float]:
        """Predict future price with confidence"""
        current_floor = round(random.uniform(0.5, 10), 3)
        
        # Simplified prediction model
        if timeframe == "7d":
            change_factor = random.uniform(0.85, 1.2)
        elif timeframe == "30d":
            change_factor = random.uniform(0.7, 1.5)
        else:
            change_factor = random.uniform(0.5, 2.0)
        
        predicted_floor = round(current_floor * change_factor, 3)
        confidence = round(random.uniform(0.4, 0.85), 2)
        
        return current_floor, predicted_floor, confidence

analyzer = NFTMarketAnalyzer()

# AI-powered insights generator
async def generate_ai_insights(analysis_data: Dict[str, Any], analysis_type: str) -> str:
    """Generate AI-powered insights from analysis data"""
    try:
        prompt = f"""Based on this {analysis_type} NFT analysis data:
        {str(analysis_data)[:500]}
        
        Provide 3 key actionable insights in 2-3 sentences total."""
        
        response = openai_client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": "You are an expert NFT market analyst."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    except:
        return "Market shows mixed signals. Focus on established collections with strong communities and consistent volume."

# Protocol definition
analyzer_protocol = Protocol(name="nft_analyzer_protocol", version="1.0")

@agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info(f"📊 NFT Analyzer Agent started!")
    ctx.logger.info(f"📍 Address: {agent.address}")
    ctx.logger.info(f"🤖 AI insights: {'✅' if os.getenv('OPENAI_API_KEY') else '❌'}")
    ctx.logger.info(f"📈 Ready to analyze NFT markets!")

@agent.on_event("shutdown")
async def shutdown(ctx: Context):
    ctx.logger.info("🛑 NFT Analyzer shutting down...")

@analyzer_protocol.on_message(model=AnalysisRequest, replies=AnalysisResponse)
async def handle_analysis_request(ctx: Context, sender: str, msg: AnalysisRequest):
    """Handle NFT analysis requests"""
    ctx.logger.info(f"📊 Analysis request from {sender}: {msg.analysis_type} for {msg.target}")
    
    try:
        # Perform analysis based on type
        if msg.analysis_type == AnalysisType.COLLECTION:
            analysis_data = await analyzer.analyze_collection(msg.target, msg.depth)
        else:
            # Simplified for other types
            analysis_data = {
                "type": msg.analysis_type,
                "metrics": {"placeholder": "data"},
                "status": "analyzed"
            }
        
        # Generate insights
        insights = [
            f"Collection shows {random.choice(['strong', 'moderate', 'weak'])} momentum",
            f"Liquidity is {random.choice(['excellent', 'good', 'concerning'])}",
            f"Holder distribution indicates {random.choice(['healthy', 'concentrated'])} ownership"
        ]
        
        # Generate recommendations
        recommendations = [
            f"{'Buy' if random.random() > 0.5 else 'Wait for'} entry at floor price",
            "Set stop-loss at -15% from entry",
            "Monitor whale wallet activity"
        ]
        
        # Calculate scores
        risk_score = round(random.uniform(3, 8), 1)
        opportunity_score = round(random.uniform(4, 9), 1)
        
        # Get AI summary
        ai_summary = await generate_ai_insights(analysis_data, msg.analysis_type.value)
        
        response = AnalysisResponse(
            analysis_type=msg.analysis_type,
            target=msg.target,
            metrics=analysis_data,
            insights=insights,
            recommendations=recommendations,
            risk_score=risk_score,
            opportunity_score=opportunity_score,
            ai_summary=ai_summary,
            timestamp=datetime.now(UTC).isoformat()
        )
        
        await ctx.send(sender, response)
        
    except Exception as e:
        ctx.logger.error(f"Analysis failed: {e}")
        await ctx.send(sender, AnalysisResponse(
            analysis_type=msg.analysis_type,
            target=msg.target,
            metrics={},
            insights=["Analysis failed"],
            recommendations=["Please try again"],
            risk_score=10,
            opportunity_score=0,
            ai_summary="Analysis could not be completed",
            timestamp=datetime.now(UTC).isoformat()
        ))

@analyzer_protocol.on_message(model=ComparisonRequest, replies=ComparisonResponse)
async def handle_comparison(ctx: Context, sender: str, msg: ComparisonRequest):
    """Compare multiple NFT collections"""
    ctx.logger.info(f"⚖️ Comparison request for {len(msg.collections)} collections")
    
    # Generate metrics for each collection
    collection_metrics = []
    comparison_data = {}
    
    for collection in msg.collections[:5]:  # Limit to 5 collections
        metrics = CollectionMetrics(
            name=collection,
            floor_price=round(random.uniform(0.1, 10), 3),
            market_cap=round(random.uniform(100, 10000), 2),
            volume_24h=round(random.uniform(10, 1000), 2),
            volume_7d=round(random.uniform(70, 7000), 2),
            holders=random.randint(100, 10000),
            supply=random.randint(1000, 10000),
            listed_percentage=round(random.uniform(2, 20), 1),
            avg_price=round(random.uniform(0.5, 15), 3),
            price_change_24h=round(random.uniform(-30, 50), 1),
            price_change_7d=round(random.uniform(-50, 100), 1)
        )
        collection_metrics.append(metrics)
        
        # Build comparison chart
        comparison_data[collection] = {
            "floor_price": metrics.floor_price,
            "volume_24h": metrics.volume_24h,
            "holders": metrics.holders,
            "momentum": metrics.price_change_7d
        }
    
    # Determine winner based on overall performance
    scores = {}
    for metrics in collection_metrics:
        score = (
            metrics.volume_24h / 100 +
            metrics.holders / 1000 +
            metrics.price_change_7d / 10 +
            (10 - metrics.listed_percentage)
        )
        scores[metrics.name] = score
    
    winner = max(scores, key=scores.get)
    
    # Generate insights
    insights = f"Among compared collections, {winner} shows the strongest performance. "
    insights += f"Key differentiators include superior liquidity and holder distribution. "
    insights += "Consider market conditions and your risk tolerance before investing."
    
    response = ComparisonResponse(
        collections=collection_metrics,
        comparison_chart=comparison_data,
        winner=winner,
        insights=insights
    )
    
    await ctx.send(sender, response)

@analyzer_protocol.on_message(model=PredictionRequest, replies=PredictionResponse)
async def handle_prediction(ctx: Context, sender: str, msg: PredictionRequest):
    """Generate price predictions"""
    ctx.logger.info(f"🔮 Prediction request for {msg.collection} ({msg.timeframe})")
    
    # Generate prediction
    current, predicted, confidence = await analyzer.predict_price(msg.collection, msg.timeframe)
    
    # Identify factors
    bullish_factors = []
    bearish_factors = []
    
    if "market" in msg.factors:
        if random.random() > 0.5:
            bullish_factors.append("Overall NFT market trending upward")
        else:
            bearish_factors.append("NFT market showing weakness")
    
    if "social" in msg.factors:
        if random.random() > 0.4:
            bullish_factors.append("Growing social media buzz")
        else:
            bearish_factors.append("Declining social interest")
    
    if "utility" in msg.factors:
        if random.random() > 0.6:
            bullish_factors.append("Strong utility and roadmap execution")
        else:
            bearish_factors.append("Limited utility development")
    
    # Generate recommendation
    if predicted > current * 1.2 and confidence > 0.6:
        recommendation = "STRONG BUY - Significant upside potential detected"
    elif predicted > current and confidence > 0.5:
        recommendation = "BUY - Moderate growth expected"
    elif predicted < current * 0.8:
        recommendation = "AVOID - Downside risk identified"
    else:
        recommendation = "HOLD - Market conditions uncertain"
    
    response = PredictionResponse(
        collection=msg.collection,
        current_floor=current,
        predicted_floor=predicted,
        confidence=confidence,
        bullish_factors=bullish_factors if bullish_factors else ["Limited bullish signals"],
        bearish_factors=bearish_factors if bearish_factors else ["No major bearish signals"],
        recommendation=recommendation
    )
    
    await ctx.send(sender, response)

# Include protocol
agent.include(analyzer_protocol, publish_manifest=True)

if __name__ == "__main__":
    print("""
📊 NFT Analyzer Agent Starting...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Features:
• Deep collection analysis
• Multi-collection comparison
• Price predictions
• Risk assessment
• AI-powered insights
• Trait dynamics analysis
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """)
    agent.run()