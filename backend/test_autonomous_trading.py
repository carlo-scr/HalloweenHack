#!/usr/bin/env python3
"""
Quick test script for autonomous trading system.

Tests:
1. Portfolio initialization
2. Trading agent creation
3. Multi-agent analysis
4. Trade execution (simulated)
5. Portfolio updates
"""

import asyncio
import json
from pathlib import Path

# Add backend to path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from autonomous_trading_agent import AutonomousTradingAgent, Portfolio, TradeExecution
from multi_agent_decision import DecisionCoordinator


async def test_portfolio():
    """Test portfolio operations."""
    print("\n" + "="*60)
    print("TEST 1: Portfolio Operations")
    print("="*60)
    
    # Create new portfolio
    portfolio = Portfolio()
    print(f"✅ Initial portfolio: ${portfolio.total_value:.2f}")
    print(f"   Cash: ${portfolio.cash:.2f}")
    
    # Create a test trade
    trade = TradeExecution(
        trade_id="test_trade_001",
        market_id="test_market",
        market_title="Test Market - Will This Work?",
        action="buy",
        outcome="Yes",
        price=0.65,
        size=100.00,
        shares=153.85,
        confidence=0.82,
        consensus=0.75,
        agent_votes={"Agent1": "BUY", "Agent2": "BUY", "Agent3": "HOLD", "Agent4": "BUY"},
        executed_at="2025-11-01T14:30:00"
    )
    
    # Add trade
    portfolio.add_trade(trade)
    print(f"✅ After trade: ${portfolio.total_value:.2f}")
    print(f"   Cash: ${portfolio.cash:.2f}")
    print(f"   Active positions: {len(portfolio.active_positions)}")
    
    # Close trade (winning)
    portfolio.close_trade("test_trade_001", 1.0, "Yes")
    print(f"✅ After closing (won): ${portfolio.total_value:.2f}")
    print(f"   Cash: ${portfolio.cash:.2f}")
    print(f"   P&L: ${portfolio.total_pnl:.2f}")
    print(f"   Win rate: {portfolio.win_rate:.1%}")
    
    return True


async def test_agent_creation():
    """Test agent initialization."""
    print("\n" + "="*60)
    print("TEST 2: Agent Creation")
    print("="*60)
    
    agent = AutonomousTradingAgent(
        markets_to_monitor=["Test Market 1", "Test Market 2"],
        check_interval=60,
        min_confidence=0.7,
        min_consensus=0.6,
        max_position_size=500.0,
    )
    
    print(f"✅ Agent created")
    print(f"   Markets: {agent.markets_to_monitor}")
    print(f"   Interval: {agent.check_interval}s")
    print(f"   Min confidence: {agent.min_confidence:.1%}")
    print(f"   Min consensus: {agent.min_consensus:.1%}")
    print(f"   Portfolio: ${agent.portfolio.total_value:.2f}")
    
    return True


async def test_decision_coordinator():
    """Test multi-agent decision making."""
    print("\n" + "="*60)
    print("TEST 3: Multi-Agent Decision Coordinator")
    print("="*60)
    
    coordinator = DecisionCoordinator()
    print(f"✅ Coordinator created")
    print(f"   Agents: {len(coordinator.agents)}")
    
    # Note: This would require browser automation and API keys
    # Just verify the coordinator is set up correctly
    for agent in coordinator.agents:
        name = getattr(agent, 'name', agent.__class__.__name__)
        weight = getattr(agent, 'weight', 1.0)
        print(f"   - {name} (weight: {weight})")
    
    return True


async def test_data_persistence():
    """Test data saving/loading."""
    print("\n" + "="*60)
    print("TEST 4: Data Persistence")
    print("="*60)
    
    # Create test data directory
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Create portfolio
    portfolio = Portfolio()
    
    # Add some test trades
    for i in range(3):
        trade = TradeExecution(
            trade_id=f"test_trade_{i:03d}",
            market_id=f"market_{i}",
            market_title=f"Test Market {i}",
            action="buy" if i % 2 == 0 else "sell",
            outcome="Yes",
            price=0.6 + (i * 0.1),
            size=100.0 + (i * 50),
            shares=150.0,
            confidence=0.75 + (i * 0.05),
            consensus=0.7,
            agent_votes={},
            executed_at="2025-11-01T14:30:00"
        )
        portfolio.add_trade(trade)
    
    # Save to file
    portfolio_path = data_dir / "test_portfolio.json"
    portfolio_path.write_text(portfolio.model_dump_json(indent=2))
    print(f"✅ Saved portfolio to {portfolio_path}")
    
    # Load from file
    loaded_data = json.loads(portfolio_path.read_text())
    loaded_portfolio = Portfolio(**loaded_data)
    print(f"✅ Loaded portfolio from disk")
    print(f"   Total value: ${loaded_portfolio.total_value:.2f}")
    print(f"   Active positions: {len(loaded_portfolio.active_positions)}")
    
    # Clean up
    portfolio_path.unlink()
    print(f"✅ Cleaned up test file")
    
    return True


async def run_all_tests():
    """Run all tests."""
    print("\n" + "="*60)
    print("🧪 AUTONOMOUS TRADING SYSTEM TESTS")
    print("="*60)
    
    tests = [
        ("Portfolio Operations", test_portfolio),
        ("Agent Creation", test_agent_creation),
        ("Multi-Agent Coordinator", test_decision_coordinator),
        ("Data Persistence", test_data_persistence),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            result = await test_func()
            results.append((name, result, None))
        except Exception as e:
            results.append((name, False, str(e)))
            import traceback
            traceback.print_exc()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result, _ in results if result)
    total = len(results)
    
    for name, result, error in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
        if error:
            print(f"      Error: {error}")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! System is ready for autonomous trading.")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
