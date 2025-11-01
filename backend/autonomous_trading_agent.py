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
from multi_agent_decision import DecisionCoordinator, CollectiveDecision


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


class PolymarketCollector:
    """Stub collector for autonomous trading."""
    
    async def collect_market_data(self, query: str) -> Optional[MarketData]:
        """Collect market data - this would use browser automation in production."""
        # For now, return stub data
        # In production, this would use the actual polymarket_collector
        return MarketData(
            market_id=query.lower().replace(" ", "-"),
            market_title=query,
            outcomes=["Yes", "No"],
            current_prices={"Yes": 0.65, "No": 0.35},
            total_volume=1000000,
            liquidity=500000,
            status="active"
        )


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
        self.collector = PolymarketCollector()
        
        # Load or create portfolio
        self.portfolio = self._load_portfolio()
        
        # Tracking
        self.last_analysis: Dict[str, datetime] = {}
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
        """Analyze a market using multi-agent system."""
        try:
            print(f"\n🔍 Analyzing market: {market_query}")
            
            # Collect market data
            market_data = await self.collector.collect_market_data(query=market_query)
            
            if not market_data:
                print(f"❌ Could not collect data for: {market_query}")
                return None
            
            # Run multi-agent analysis
            decision = await self.coordinator.make_collective_decision(market_data)
            
            print(f"✅ Analysis complete:")
            print(f"   Recommendation: {decision.final_recommendation}")
            print(f"   Confidence: {decision.overall_confidence:.1%}")
            print(f"   Consensus: {decision.consensus_level:.1%}")
            
            return decision
            
        except Exception as e:
            print(f"❌ Error analyzing {market_query}: {e}")
            return None
    
    def should_execute_trade(self, decision: CollectiveDecision) -> bool:
        """Determine if trade should be executed based on thresholds."""
        if decision.final_recommendation == "HOLD":
            return False
        
        if decision.overall_confidence < self.min_confidence:
            print(f"⚠️  Confidence too low: {decision.overall_confidence:.1%} < {self.min_confidence:.1%}")
            return False
        
        if decision.consensus_level < self.min_consensus:
            print(f"⚠️  Consensus too low: {decision.consensus_level:.1%} < {self.min_consensus:.1%}")
            return False
        
        # Check if we have enough cash
        suggested_size = min(decision.suggested_bet_size or 0, self.max_position_size)
        if suggested_size > self.portfolio.cash:
            print(f"⚠️  Insufficient cash: ${self.portfolio.cash:.2f} < ${suggested_size:.2f}")
            return False
        
        return True
    
    async def execute_trade(
        self,
        decision: CollectiveDecision,
        market_data: MarketData
    ) -> Optional[TradeExecution]:
        """Execute a trade based on decision."""
        
        if not self.should_execute_trade(decision):
            return None
        
        try:
            # Determine trade parameters
            action = decision.final_recommendation.lower()
            outcome = decision.recommended_outcome or list(market_data.current_prices.keys())[0]
            price = market_data.current_prices.get(outcome, 0.5)
            size = min(decision.suggested_bet_size or 100, self.max_position_size, self.portfolio.cash)
            shares = size / price if price > 0 else 0
            
            # Create trade execution
            trade = TradeExecution(
                trade_id=f"trade_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                market_id=market_data.market_id or "unknown",
                market_title=market_data.market_title,
                action=action,
                outcome=outcome,
                price=price,
                size=size,
                shares=shares,
                confidence=decision.overall_confidence,
                consensus=decision.consensus_level,
                agent_votes={
                    agent.agent_name: agent.recommendation
                    for agent in decision.agent_decisions
                },
                executed_at=datetime.now().isoformat(),
                market_end_date=market_data.end_date,
            )
            
            # Add to portfolio
            self.portfolio.add_trade(trade)
            self.portfolio.update_total_value()
            self._save_portfolio()
            self._save_trade_history(trade)
            
            print(f"\n✅ TRADE EXECUTED!")
            print(f"   Market: {trade.market_title}")
            print(f"   Action: {trade.action.upper()} {trade.outcome}")
            print(f"   Size: ${trade.size:.2f} ({trade.shares:.2f} shares @ ${trade.price:.2f})")
            print(f"   Portfolio Cash: ${self.portfolio.cash:.2f}")
            print(f"   Total Value: ${self.portfolio.total_value:.2f}")
            
            return trade
            
        except Exception as e:
            print(f"❌ Error executing trade: {e}")
            return None
    
    async def check_and_trade_market(self, market_query: str):
        """Check a market and potentially execute a trade."""
        
        # Analyze market
        decision = await self.analyze_market(market_query)
        
        if not decision:
            return
        
        # Get market data (re-collect for trade execution)
        market_data = await self.collector.collect_market_data(query=market_query)
        
        if not market_data:
            return
        
        # Execute trade if criteria met
        await self.execute_trade(decision, market_data)
    
    async def monitoring_loop(self):
        """Main loop that monitors markets continuously."""
        
        print("\n🤖 Autonomous Trading Agent Started")
        print(f"📊 Portfolio: ${self.portfolio.total_value:.2f} (Cash: ${self.portfolio.cash:.2f})")
        print(f"🎯 Monitoring {len(self.markets_to_monitor)} markets")
        print(f"⏱️  Check interval: {self.check_interval}s")
        print(f"📈 Min confidence: {self.min_confidence:.1%}")
        print(f"🗳️  Min consensus: {self.min_consensus:.1%}")
        print(f"💰 Max position: ${self.max_position_size:.2f}")
        print("\n" + "="*60 + "\n")
        
        self.running = True
        
        while self.running:
            try:
                # Check each market
                for market in self.markets_to_monitor:
                    if not self.running:
                        break
                    
                    print(f"\n🔄 Checking: {market}")
                    await self.check_and_trade_market(market)
                    
                    # Small delay between markets
                    await asyncio.sleep(10)
                
                # Update portfolio value
                self.portfolio.update_total_value()
                self._save_portfolio()
                
                # Show status
                print(f"\n📊 Portfolio Update:")
                print(f"   Total Value: ${self.portfolio.total_value:.2f}")
                print(f"   Cash: ${self.portfolio.cash:.2f}")
                print(f"   Active Positions: {len(self.portfolio.active_positions)}")
                print(f"   Total PnL: ${self.portfolio.total_pnl:.2f}")
                print(f"   Win Rate: {self.portfolio.win_rate:.1%}")
                
                # Wait for next check interval
                print(f"\n⏳ Waiting {self.check_interval}s until next check...")
                await asyncio.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                print("\n⚠️  Stopping agent...")
                self.running = False
                break
            except Exception as e:
                print(f"❌ Error in monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait a minute before retrying
        
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
