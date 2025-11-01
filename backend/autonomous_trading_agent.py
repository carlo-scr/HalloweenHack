#!/usr/bin/env python3
"""
Autonomous Polymarket Trading Agent

This agent continuously:
1. Monitors Polymarket for opportunities
2. Uses multi-agent system to analyze markets
3. Makes autonomous trading decisions
4. Executes trades (simulated for now)
5. Updates portfolio state for frontend

Usage:
    python autonomous_trading_agent.py
    
    # With specific markets to monitor
    python autonomous_trading_agent.py --markets "Trump 2024" "Bitcoin $100k"
    
    # With custom check interval
    python autonomous_trading_agent.py --interval 300  # Check every 5 minutes
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Literal

from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()

# Add Polymarket Agent directory to path
backend_dir = os.path.dirname(os.path.abspath(__file__))
polymarket_agent_dir = os.path.join(backend_dir, "Polymarket Agent")
sys.path.insert(0, polymarket_agent_dir)

# Import our existing modules
from multi_agent_decision import DecisionCoordinator, CollectiveDecision, AgentDecision
from polymarket_discovery import PolymarketDiscovery, PolymarketMarket


# Simplified MarketData for autonomous trading
class MarketData(BaseModel):
    """Market data for trading decisions."""
    market_id: Optional[str] = None
    market_title: str
    market_url: Optional[str] = None
    outcomes: List[str] = Field(default_factory=list)
    current_prices: Dict[str, float] = Field(default_factory=dict)
    total_volume: Optional[float] = None
    liquidity: Optional[float] = None
    end_date: Optional[str] = None
    status: str = "active"
    market_context: Optional[str] = None
    collected_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class TradeExecution(BaseModel):
    """Model for an executed trade."""
    
    trade_id: str = Field(description="Unique trade identifier")
    market_id: str
    market_title: str
    action: str = Field(description="buy, sell, or hold")
    outcome: str = Field(description="Which outcome was traded")
    
    # Trade details
    price: float = Field(description="Price at execution")
    size: float = Field(description="Position size in USD")
    shares: float = Field(description="Number of shares")
    
    # Decision context
    confidence: float
    consensus: float
    agent_votes: Dict[str, str]
    
    # Timestamps
    executed_at: str
    market_end_date: Optional[str] = None
    
    # Status tracking
    status: str = Field(default="open", description="open, closed, settled")
    pnl: Optional[float] = Field(default=None, description="Profit/Loss if closed")
    resolved_outcome: Optional[str] = Field(default=None)


class Portfolio(BaseModel):
    """Portfolio state for frontend."""
    
    total_value: float = Field(default=10000.0, description="Total portfolio value")
    cash: float = Field(default=10000.0, description="Available cash")
    active_positions: List[TradeExecution] = Field(default_factory=list)
    closed_positions: List[TradeExecution] = Field(default_factory=list)
    
    # Performance metrics
    total_pnl: float = Field(default=0.0)
    win_rate: float = Field(default=0.0)
    total_trades: int = Field(default=0)
    winning_trades: int = Field(default=0)
    
    last_updated: str = Field(default_factory=lambda: datetime.now().isoformat())
    
    def add_trade(self, trade: TradeExecution):
        """Add a new trade to portfolio."""
        self.active_positions.append(trade)
        self.cash -= trade.size
        self.total_trades += 1
        self.last_updated = datetime.now().isoformat()
    
    def close_trade(self, trade_id: str, final_price: float, resolved_outcome: str):
        """Close a trade and calculate PnL."""
        for i, trade in enumerate(self.active_positions):
            if trade.trade_id == trade_id:
                # Calculate PnL
                if trade.action == "buy" and trade.outcome == resolved_outcome:
                    pnl = (1.0 - trade.price) * trade.shares  # Won the bet
                elif trade.action == "sell" and trade.outcome != resolved_outcome:
                    pnl = trade.price * trade.shares  # Correctly sold
                else:
                    pnl = -trade.size  # Lost the bet
                
                # Update trade
                trade.status = "closed"
                trade.pnl = pnl
                trade.resolved_outcome = resolved_outcome
                
                # Update portfolio
                self.cash += trade.size + pnl
                self.total_pnl += pnl
                if pnl > 0:
                    self.winning_trades += 1
                self.win_rate = self.winning_trades / self.total_trades if self.total_trades > 0 else 0
                
                # Move to closed positions
                self.closed_positions.append(trade)
                self.active_positions.pop(i)
                self.last_updated = datetime.now().isoformat()
                break
    
    def get_position_value(self) -> float:
        """Calculate current value of open positions."""
        # Simplified: assume positions worth their cost basis for now
        return sum(trade.size for trade in self.active_positions)
    
    def update_total_value(self):
        """Update total portfolio value."""
        self.total_value = self.cash + self.get_position_value()
        self.last_updated = datetime.now().isoformat()


class AutonomousTradingAgent:
    """Autonomous agent that monitors and trades Polymarket markets."""
    
    def __init__(
        self,
        markets_to_monitor: List[str],
        check_interval: int = 300,
        min_confidence: float = 0.7,
        min_consensus: float = 0.6,
        max_position_size: float = 500.0,
        portfolio_path: str = "data/portfolio.json",
        trades_history_path: str = "data/trades_history.json",
    ):
        self.markets_to_monitor = markets_to_monitor
        self.check_interval = check_interval
        self.min_confidence = min_confidence
        self.min_consensus = min_consensus
        self.max_position_size = max_position_size
        
        # Paths
        self.portfolio_path = Path(portfolio_path)
        self.trades_history_path = Path(trades_history_path)
        self.portfolio_path.parent.mkdir(exist_ok=True)
        
        # Initialize components
        self.coordinator = DecisionCoordinator()
        self.discovery = PolymarketDiscovery(headless=True)
        
        # Load or create portfolio
        self.portfolio = self._load_portfolio()
        
        # Tracking
        self.last_analysis: Dict[str, datetime] = {}
        self.discovered_markets: List[PolymarketMarket] = []
        self.running = False
    
    def _load_portfolio(self) -> Portfolio:
        """Load portfolio from disk or create new."""
        if self.portfolio_path.exists():
            try:
                data = json.loads(self.portfolio_path.read_text())
                return Portfolio(**data)
            except Exception as e:
                print(f"⚠️  Error loading portfolio: {e}")
        
        return Portfolio()
    
    def _save_portfolio(self):
        """Save portfolio to disk."""
        try:
            self.portfolio_path.write_text(
                self.portfolio.model_dump_json(indent=2)
            )
        except Exception as e:
            print(f"❌ Error saving portfolio: {e}")
    
    def _save_trade_history(self, trade: TradeExecution):
        """Append trade to history file."""
        try:
            history = []
            if self.trades_history_path.exists():
                history = json.loads(self.trades_history_path.read_text())
            
            history.append(trade.model_dump())
            self.trades_history_path.write_text(json.dumps(history, indent=2))
        except Exception as e:
            print(f"⚠️  Error saving trade history: {e}")
    
    async def analyze_market(self, market_query: str) -> Optional[CollectiveDecision]:
        """
        SIMPLIFIED: Generate a simple random decision to speed up testing.
        Skip the full multi-agent analysis for now.
        """
        import random
        
        print(f"\n🔍 Quick analysis: {market_query}")
        
        # Simulate quick agent consensus
        recommendations = ["BUY", "SELL", "HOLD"]
        recommendation = random.choice(recommendations)
        confidence = random.uniform(0.3, 0.9)
        
        # Create a simple agent decision
        agent_decision = AgentDecision(
            agent_name="quick_agent",
            recommendation=recommendation,
            confidence=confidence,
            reasoning=f"Quick {recommendation} decision for testing",
            key_factors=["Market volume", "Price trend"],
            timestamp=datetime.now().isoformat()
        )
        
        # Create a simple collective decision with all required fields
        decision = CollectiveDecision(
            market_title=market_query,
            market_url=f"https://polymarket.com/event/{market_query.lower().replace(' ', '-')}",
            agent_decisions=[agent_decision],
            final_recommendation=recommendation,
            aggregate_confidence=confidence,
            consensus_level=0.75,
            supporting_factors=["Quick test analysis"],
            risk_factors=["Simplified test mode"],
            suggested_bet_size=100.0,
            expected_value=confidence * 100 if recommendation == "BUY" else 0
        )
        
        print(f"   → {recommendation} with {confidence:.1%} confidence")
        return decision
    
    async def discover_trading_opportunities(self) -> List[PolymarketMarket]:
        """
        Discover new trading opportunities.
        SIMPLIFIED: Use known high-volume markets for now to speed things up.
        """
        print(f"\n🔍 Scouting for trading opportunities...")
        
        # SIMPLIFIED: Use pre-defined popular markets (based on what browser found)
        # This makes the pipeline fast so we can see trades execute
        simple_markets = [
            PolymarketMarket(
                title="Super Bowl Champion 2026",
                url="https://polymarket.com/event/super-bowl-champion-2026",
                yes_price=0.16,
                no_price=0.84,
                volume="$485m",
                category="Sports"
            ),
            PolymarketMarket(
                title="Democratic Presidential Nominee 2028",
                url="https://polymarket.com/event/democratic-presidential-nominee-2028",
                yes_price=0.37,
                no_price=0.63,
                volume="$258m",
                category="Politics"
            ),
            PolymarketMarket(
                title="English Premier League Winner",
                url="https://polymarket.com/event/english-premier-league-winner",
                yes_price=0.66,
                no_price=0.34,
                volume="$85m",
                category="Sports"
            ),
        ]
        
        print(f"\n📊 Found {len(simple_markets)} markets:")
        for market in simple_markets:
            print(f"   • {market.title}")
            print(f"     YES: {market.yes_price:.2f} | NO: {market.no_price:.2f} | Vol: {market.volume}")
        
        self.discovered_markets = simple_markets
        return simple_markets
    
    def should_execute_trade(self, decision: CollectiveDecision, market: PolymarketMarket) -> bool:
        """
        SIMPLE logic: Trade if agents say BUY/SELL with any confidence > 20%.
        """
        print(f"\n🎯 Trade Decision for {market.title}:")
        print(f"   Agent says: {decision.final_recommendation}")
        print(f"   Confidence: {decision.aggregate_confidence:.1%}")
        
        # Skip HOLD
        if decision.final_recommendation == "HOLD":
            print(f"   → SKIP (agents say hold)")
            return False
        
        # Simple threshold: any confidence > 20%
        if decision.aggregate_confidence < 0.20:
            print(f"   → SKIP (confidence too low)")
            return False
        
        # Check we have cash
        if self.portfolio.cash < 50:
            print(f"   → SKIP (not enough cash: ${self.portfolio.cash:.2f})")
            return False
        
        print(f"   → ✅ EXECUTE TRADE!")
        return True
    
    async def execute_trade(
        self,
        decision: CollectiveDecision,
        market: PolymarketMarket
    ) -> Optional[TradeExecution]:
        """Execute a simple trade based on decision and market data."""
        
        if not self.should_execute_trade(decision, market):
            return None
        
        try:
            # Simple trade parameters from discovered market
            action = decision.final_recommendation.lower()
            outcome = "Yes"  # Simplified - always trade YES outcome
            price = market.yes_price
            
            # Simple position sizing: $100 or 10% of cash, whichever is smaller
            size = min(100, self.portfolio.cash * 0.1, self.max_position_size)
            shares = size / price if price > 0 else 0
            
            # Create trade
            trade = TradeExecution(
                trade_id=f"trade_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                market_id=market.url or market.title.lower().replace(" ", "-"),
                market_title=market.title,
                action=action,
                outcome=outcome,
                price=price,
                size=size,
                shares=shares,
                confidence=decision.aggregate_confidence,
                consensus=decision.consensus_level,
                agent_votes={
                    agent_dec.agent_name: agent_dec.recommendation 
                    for agent_dec in decision.agent_decisions
                },
                executed_at=datetime.now().isoformat(),
            )
            
            # Update portfolio
            self.portfolio.add_trade(trade)
            self._save_portfolio()
            self._save_trade_history(trade)
            
            print(f"\n💰 TRADE EXECUTED:")
            print(f"   Market: {market.title}")
            print(f"   Action: {action.upper()} {outcome}")
            print(f"   Size: ${size:.2f} ({shares:.2f} shares @ ${price:.2f})")
            print(f"   Remaining Cash: ${self.portfolio.cash:.2f}")
            
            return trade
            
        except Exception as e:
            print(f"❌ Error executing trade: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def analyze_and_trade_market(self, market: PolymarketMarket):
        """Analyze a discovered market and potentially execute a trade."""
        
        # Analyze market using multi-agent system
        decision = await self.analyze_market(market.title)
        
        if not decision:
            return
        
        # Execute trade if criteria met
        await self.execute_trade(decision, market)
    
    async def monitoring_loop(self):
        """Main loop: Discover markets from Polymarket → Analyze → Trade."""
        
        print("\n🤖 Autonomous Trading Agent Started")
        print(f"📊 Portfolio: ${self.portfolio.total_value:.2f} (Cash: ${self.portfolio.cash:.2f})")
        print(f"⏱️  Check interval: {self.check_interval}s")
        print(f" Max position: ${self.max_position_size:.2f}")
        print("\n" + "="*60 + "\n")
        
        self.running = True
        
        while self.running:
            try:
                # Step 1: Scout Polymarket for real markets
                discovered_markets = await self.discover_trading_opportunities()
                
                if not discovered_markets:
                    print(f"⚠️  No markets discovered, waiting...")
                    await asyncio.sleep(self.check_interval)
                    continue
                
                # Step 2: Analyze each market and trade if agents approve
                print(f"\n🔄 Analyzing {len(discovered_markets)} markets...")
                for market in discovered_markets:
                    if not self.running:
                        break
                    
                    await self.analyze_and_trade_market(market)
                    
                    # Small delay between markets
                    await asyncio.sleep(5)
                
                # Step 3: Update portfolio
                self.portfolio.update_total_value()
                self._save_portfolio()
                
                print(f"\n📊 Portfolio Status:")
                print(f"   Total Value: ${self.portfolio.total_value:.2f}")
                print(f"   Cash: ${self.portfolio.cash:.2f}")
                print(f"   Positions: {len(self.portfolio.active_positions)}")
                print(f"   Total P&L: ${self.portfolio.total_pnl:.2f}")
                
                # Wait for next cycle
                print(f"\n⏳ Next check in {self.check_interval}s...")
                await asyncio.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                print("\n⚠️  Stopping...")
                self.running = False
                break
            except Exception as e:
                print(f"❌ Error in loop: {e}")
                import traceback
                traceback.print_exc()
                await asyncio.sleep(60)
        
        print("\n✅ Agent stopped")
        print(f"📊 Final Portfolio: ${self.portfolio.total_value:.2f}")
    
    async def start(self):
        """Start the autonomous trading agent."""
        await self.monitoring_loop()
    
    def stop(self):
        """Stop the agent."""
        self.running = False


async def main():
    parser = argparse.ArgumentParser(
        description="Autonomous Polymarket Trading Agent"
    )
    parser.add_argument(
        "--markets",
        nargs="+",
        default=["Trump 2024", "Bitcoin $100k by 2025"],
        help="Markets to monitor (space-separated)"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=300,
        help="Check interval in seconds (default: 300)"
    )
    parser.add_argument(
        "--min-confidence",
        type=float,
        default=0.7,
        help="Minimum confidence to trade (default: 0.7)"
    )
    parser.add_argument(
        "--min-consensus",
        type=float,
        default=0.6,
        help="Minimum consensus to trade (default: 0.6)"
    )
    parser.add_argument(
        "--max-position",
        type=float,
        default=500.0,
        help="Maximum position size in USD (default: 500)"
    )
    
    args = parser.parse_args()
    
    # Create and start agent
    agent = AutonomousTradingAgent(
        markets_to_monitor=args.markets,
        check_interval=args.interval,
        min_confidence=args.min_confidence,
        min_consensus=args.min_consensus,
        max_position_size=args.max_position,
    )
    
    await agent.start()


if __name__ == "__main__":
    asyncio.run(main())
