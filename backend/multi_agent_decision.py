"""
Multi-Agent Trading Decision System for Polymarket

This system coordinates multiple specialized agents that work together to analyze
markets and make collaborative trading decisions.

Agent Roles:
1. Data Collector Agent - Gathers market data from Polymarket
2. Research Agent - Finds contextual information (news, trends, etc.)
3. Analysis Agent - Analyzes odds and probabilities
4. Sentiment Agent - Analyzes social media and public sentiment
5. Decision Agent - Coordinates all inputs and makes final recommendation

Flow:
User requests analysis → Agents run in parallel → Results aggregated → Final decision
"""

import asyncio
from typing import List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
import json

# ============================================================================
# Data Models
# ============================================================================

class AgentDecision(BaseModel):
    """Individual agent's analysis and recommendation"""
    agent_name: str
    confidence: float = Field(ge=0, le=1, description="Confidence level 0-1")
    recommendation: str  # "YES", "NO", "SKIP"
    reasoning: str
    key_factors: List[str]
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class CollectiveDecision(BaseModel):
    """Final aggregated decision from all agents"""
    market_title: str
    market_url: str
    
    # Individual agent decisions
    agent_decisions: List[AgentDecision]
    
    # Aggregated recommendation
    final_recommendation: str  # "YES", "NO", "SKIP"
    aggregate_confidence: float = Field(ge=0, le=1)
    consensus_level: float = Field(ge=0, le=1, description="How much agents agree")
    
    # Decision summary
    supporting_factors: List[str]
    risk_factors: List[str]
    
    # Suggested action
    suggested_bet_size: float | None = Field(description="Percentage of bankroll")
    expected_value: float | None
    
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


# ============================================================================
# Base Agent Class
# ============================================================================

class BaseAgent:
    """Base class for all specialized agents"""
    
    def __init__(self, name: str):
        self.name = name
    
    async def analyze(self, market_data: Dict[str, Any]) -> AgentDecision:
        """Override this in subclasses"""
        raise NotImplementedError


# ============================================================================
# Specialized Agents
# ============================================================================

class DataCollectorAgent(BaseAgent):
    """Collects and validates market data from Polymarket"""
    
    def __init__(self):
        super().__init__("Data Collector")
    
    async def collect_market_data(self, market_query: str) -> Dict[str, Any]:
        """Collect fresh market data"""
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "Polymarket Agent"))
        
        from polymarket_collector import collect_market_data
        
        market_data = await collect_market_data(
            market_identifier=market_query,
            method='search',
            headless=True
        )
        
        return market_data.dict()
    
    async def analyze(self, market_data: Dict[str, Any]) -> AgentDecision:
        """Validate data quality and check for anomalies"""
        
        # Check for data completeness
        has_prices = bool(market_data.get('current_prices'))
        has_volume = bool(market_data.get('total_volume'))
        has_liquidity = bool(market_data.get('liquidity'))
        
        confidence = 0.8 if all([has_prices, has_volume, has_liquidity]) else 0.4
        
        key_factors = []
        if has_volume:
            volume = market_data.get('total_volume', 0)
            if volume > 100000:
                key_factors.append(f"High trading volume: ${volume:,.0f}")
            elif volume < 10000:
                key_factors.append(f"Low trading volume: ${volume:,.0f} - risky")
        
        if has_liquidity:
            liquidity = market_data.get('liquidity', 0)
            if liquidity < 5000:
                key_factors.append("Low liquidity - high slippage risk")
        
        recommendation = "PROCEED" if confidence > 0.6 else "SKIP"
        
        return AgentDecision(
            agent_name=self.name,
            confidence=confidence,
            recommendation=recommendation,
            reasoning=f"Data quality check: {len(key_factors)} concerns identified",
            key_factors=key_factors
        )


class ResearchAgent(BaseAgent):
    """Gathers external research and context using Perplexity/web search"""
    
    def __init__(self):
        super().__init__("Research")
    
    async def analyze(self, market_data: Dict[str, Any]) -> AgentDecision:
        """Research the market topic using browser automation"""
        import os
        from browser_use import Agent, Browser, ChatBrowserUse
        
        market_title = market_data.get('market_title', '')
        
        # Use browser-use to research
        llm = ChatBrowserUse()
        browser = Browser(headless=True)
        
        research_task = f"""Research the topic: "{market_title}"

Search Google News and gather:
1. Recent news articles about this topic
2. Expert opinions or predictions
3. Key developments that might affect the outcome
4. Any contrary viewpoints

Return a summary of what you found and whether it supports a YES or NO outcome."""
        
        agent = Agent(
            task=research_task,
            llm=llm,
            browser=browser,
            use_vision=True
        )
        
        try:
            history = await agent.run(max_steps=8)
            research_summary = str(history.final_result())
            
            # Simple sentiment analysis on research
            positive_words = ['likely', 'probable', 'increasing', 'strong', 'support']
            negative_words = ['unlikely', 'declining', 'weak', 'against', 'doubt']
            
            pos_count = sum(1 for word in positive_words if word in research_summary.lower())
            neg_count = sum(1 for word in negative_words if word in research_summary.lower())
            
            if pos_count > neg_count:
                recommendation = "YES"
                confidence = 0.6 + (pos_count * 0.05)
            elif neg_count > pos_count:
                recommendation = "NO"
                confidence = 0.6 + (neg_count * 0.05)
            else:
                recommendation = "NEUTRAL"
                confidence = 0.5
            
            confidence = min(confidence, 0.9)
            
            return AgentDecision(
                agent_name=self.name,
                confidence=confidence,
                recommendation=recommendation,
                reasoning=research_summary[:200] + "...",
                key_factors=[
                    f"Found {pos_count} positive indicators",
                    f"Found {neg_count} negative indicators"
                ]
            )
            
        except Exception as e:
            return AgentDecision(
                agent_name=self.name,
                confidence=0.3,
                recommendation="SKIP",
                reasoning=f"Research failed: {str(e)}",
                key_factors=["Unable to complete research"]
            )


class OddsAnalyzer(BaseAgent):
    """Analyzes market odds and probabilities for value bets"""
    
    def __init__(self):
        super().__init__("Odds Analyzer")
    
    async def analyze(self, market_data: Dict[str, Any]) -> AgentDecision:
        """Analyze if current odds represent value"""
        
        prices = market_data.get('current_prices', {})
        
        if not prices:
            return AgentDecision(
                agent_name=self.name,
                confidence=0.0,
                recommendation="SKIP",
                reasoning="No price data available",
                key_factors=[]
            )
        
        # Calculate implied probabilities
        key_factors = []
        
        # Check for extreme odds (potential value)
        for outcome, price in prices.items():
            if price < 0.2:
                key_factors.append(f"{outcome} trading at {price:.1%} - potential undervalued")
            elif price > 0.8:
                key_factors.append(f"{outcome} trading at {price:.1%} - market very confident")
            elif 0.45 <= price <= 0.55:
                key_factors.append(f"{outcome} at {price:.1%} - toss-up, high uncertainty")
        
        # Check for odds inefficiency (sum != 1.0, which means vig/margin)
        total_probability = sum(prices.values())
        margin = abs(1.0 - total_probability)
        
        if margin > 0.05:
            key_factors.append(f"High market margin: {margin:.1%} - expensive to trade")
        
        # Simple recommendation based on analysis
        max_price = max(prices.values())
        if max_price > 0.8:
            recommendation = "YES" if list(prices.keys())[0] == max(prices, key=prices.get) else "NO"
            confidence = 0.7
        elif max_price < 0.6:
            recommendation = "NEUTRAL"
            confidence = 0.5
        else:
            recommendation = "NEUTRAL"
            confidence = 0.6
        
        return AgentDecision(
            agent_name=self.name,
            confidence=confidence,
            recommendation=recommendation,
            reasoning=f"Market showing {margin:.1%} vig with max probability {max_price:.1%}",
            key_factors=key_factors
        )


class SentimentAgent(BaseAgent):
    """Analyzes social media sentiment and public opinion"""
    
    def __init__(self):
        super().__init__("Sentiment")
    
    async def analyze(self, market_data: Dict[str, Any]) -> AgentDecision:
        """Check Twitter/social sentiment about the topic"""
        import os
        from browser_use import Agent, Browser, ChatBrowserUse
        
        market_title = market_data.get('market_title', '')
        
        # Use browser-use to check sentiment
        llm = ChatBrowserUse()
        browser = Browser(headless=True)
        
        sentiment_task = f"""Search Twitter or Reddit for opinions about: "{market_title}"

Look for:
1. What are people saying about this?
2. Is sentiment mostly positive or negative?
3. Are there any influential voices weighing in?

Summarize the overall sentiment."""
        
        agent = Agent(
            task=sentiment_task,
            llm=llm,
            browser=browser,
            use_vision=True
        )
        
        try:
            history = await agent.run(max_steps=6)
            sentiment_summary = str(history.final_result())
            
            # Analyze sentiment
            if any(word in sentiment_summary.lower() for word in ['positive', 'bullish', 'optimistic']):
                recommendation = "YES"
                confidence = 0.65
            elif any(word in sentiment_summary.lower() for word in ['negative', 'bearish', 'pessimistic']):
                recommendation = "NO"
                confidence = 0.65
            else:
                recommendation = "NEUTRAL"
                confidence = 0.5
            
            return AgentDecision(
                agent_name=self.name,
                confidence=confidence,
                recommendation=recommendation,
                reasoning=sentiment_summary[:200],
                key_factors=["Social sentiment analyzed"]
            )
            
        except Exception as e:
            return AgentDecision(
                agent_name=self.name,
                confidence=0.4,
                recommendation="NEUTRAL",
                reasoning="Unable to gauge sentiment",
                key_factors=[]
            )


# ============================================================================
# Decision Coordinator
# ============================================================================

class DecisionCoordinator:
    """Coordinates all agents and makes final decision"""
    
    def __init__(self):
        self.agents = [
            DataCollectorAgent(),
            OddsAnalyzer(),
            # ResearchAgent(),  # Can be slow, comment out for faster results
            # SentimentAgent(),  # Can be slow, comment out for faster results
        ]
    
    async def make_decision(self, market_query: str) -> CollectiveDecision:
        """
        Coordinate all agents to make a collective decision
        
        Args:
            market_query: Search query or URL for the market
            
        Returns:
            CollectiveDecision with all agent inputs and final recommendation
        """
        
        print(f"🤖 Starting multi-agent analysis for: {market_query}")
        print("=" * 70)
        
        # Step 1: Collect market data
        data_collector = DataCollectorAgent()
        print("\n📊 Collecting market data...")
        market_data = await data_collector.collect_market_data(market_query)
        print(f"✓ Market: {market_data.get('market_title')}")
        
        # Step 2: Run all agents in parallel
        print(f"\n🔄 Running {len(self.agents)} agents in parallel...")
        agent_tasks = [agent.analyze(market_data) for agent in self.agents]
        agent_decisions = await asyncio.gather(*agent_tasks)
        
        # Display individual agent decisions
        print("\n" + "=" * 70)
        print("AGENT DECISIONS:")
        print("=" * 70)
        for decision in agent_decisions:
            print(f"\n🤖 {decision.agent_name}:")
            print(f"   Recommendation: {decision.recommendation}")
            print(f"   Confidence: {decision.confidence:.1%}")
            print(f"   Reasoning: {decision.reasoning}")
        
        # Step 3: Aggregate decisions
        print("\n" + "=" * 70)
        print("AGGREGATING DECISIONS...")
        print("=" * 70)
        
        collective_decision = self._aggregate_decisions(
            market_data=market_data,
            agent_decisions=agent_decisions
        )
        
        return collective_decision
    
    def _aggregate_decisions(
        self,
        market_data: Dict[str, Any],
        agent_decisions: List[AgentDecision]
    ) -> CollectiveDecision:
        """Aggregate all agent decisions into final recommendation"""
        
        # Count votes
        yes_votes = sum(1 for d in agent_decisions if d.recommendation == "YES")
        no_votes = sum(1 for d in agent_decisions if d.recommendation == "NO")
        skip_votes = sum(1 for d in agent_decisions if d.recommendation in ["SKIP", "NEUTRAL"])
        
        total_votes = len(agent_decisions)
        
        # Weight by confidence
        yes_confidence = sum(d.confidence for d in agent_decisions if d.recommendation == "YES")
        no_confidence = sum(d.confidence for d in agent_decisions if d.recommendation == "NO")
        
        # Determine final recommendation
        if yes_confidence > no_confidence and yes_votes > skip_votes:
            final_recommendation = "YES"
            # Inflate confidence by 15% to encourage more trades
            aggregate_confidence = min(1.0, (yes_confidence / max(yes_votes, 1)) * 1.15)
        elif no_confidence > yes_confidence and no_votes > skip_votes:
            final_recommendation = "NO"
            # Inflate confidence by 15% to encourage more trades
            aggregate_confidence = min(1.0, (no_confidence / max(no_votes, 1)) * 1.15)
        else:
            final_recommendation = "SKIP"
            aggregate_confidence = 0.5
        
        # Calculate consensus (how much agents agree)
        max_votes = max(yes_votes, no_votes, skip_votes)
        consensus_level = max_votes / total_votes
        
        # Aggregate factors
        supporting_factors = []
        risk_factors = []
        
        for decision in agent_decisions:
            if decision.recommendation == final_recommendation:
                supporting_factors.extend(decision.key_factors)
            else:
                risk_factors.extend(decision.key_factors)
        
        # Calculate suggested bet size (Kelly Criterion simplified)
        if final_recommendation != "SKIP":
            prices = market_data.get('current_prices', {})
            if prices:
                current_price = list(prices.values())[0]
                edge = aggregate_confidence - current_price
                
                if edge > 0.05:  # Only bet if we have edge
                    # Conservative Kelly: bet size = edge / 2
                    suggested_bet_size = (edge / 2) * 100  # as percentage
                    suggested_bet_size = min(suggested_bet_size, 20)  # cap at 20%
                else:
                    suggested_bet_size = 0
                    final_recommendation = "SKIP"
            else:
                suggested_bet_size = 0
        else:
            suggested_bet_size = 0
        
        return CollectiveDecision(
            market_title=market_data.get('market_title', ''),
            market_url=market_data.get('market_url', ''),
            agent_decisions=agent_decisions,
            final_recommendation=final_recommendation,
            aggregate_confidence=aggregate_confidence,
            consensus_level=consensus_level,
            supporting_factors=supporting_factors[:5],  # Top 5
            risk_factors=risk_factors[:5],
            suggested_bet_size=suggested_bet_size,
            expected_value=None  # TODO: Calculate EV
        )


# ============================================================================
# Example Usage
# ============================================================================

async def main():
    """Example of using the multi-agent system"""
    
    coordinator = DecisionCoordinator()
    
    # Analyze a market
    decision = await coordinator.make_decision("Trump 2024")
    
    # Print final decision
    print("\n" + "=" * 70)
    print("📊 FINAL DECISION")
    print("=" * 70)
    print(f"\nMarket: {decision.market_title}")
    print(f"\n🎯 Recommendation: {decision.final_recommendation}")
    print(f"💪 Confidence: {decision.aggregate_confidence:.1%}")
    print(f"🤝 Consensus: {decision.consensus_level:.1%}")
    
    if decision.suggested_bet_size:
        print(f"💰 Suggested Bet Size: {decision.suggested_bet_size:.1f}% of bankroll")
    
    print(f"\n✅ Supporting Factors:")
    for factor in decision.supporting_factors:
        print(f"   • {factor}")
    
    if decision.risk_factors:
        print(f"\n⚠️  Risk Factors:")
        for factor in decision.risk_factors:
            print(f"   • {factor}")
    
    print("\n" + "=" * 70)
    
    # Save decision
    with open("decision.json", "w") as f:
        json.dump(decision.dict(), f, indent=2)
    
    print("\n💾 Decision saved to decision.json")


if __name__ == "__main__":
    asyncio.run(main())
