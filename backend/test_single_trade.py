#!/usr/bin/env python3
"""
Quick test to manually trigger autonomous trading analysis and trade.
This will help debug why trades aren't being executed.
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from autonomous_trading_agent import AutonomousTradingAgent


async def test_single_analysis():
    """Test a single market analysis and potential trade."""
    
    print("\n" + "="*60)
    print("🧪 TESTING AUTONOMOUS TRADING CYCLE")
    print("="*60)
    
    # Create agent
    agent = AutonomousTradingAgent(
        markets_to_monitor=["Trump 2024"],
        check_interval=60,
        min_confidence=0.7,
        min_consensus=0.6,
        max_position_size=500.0,
    )
    
    print(f"\n📊 Initial Portfolio:")
    print(f"   Total Value: ${agent.portfolio.total_value:.2f}")
    print(f"   Cash: ${agent.portfolio.cash:.2f}")
    print(f"   Active Positions: {len(agent.portfolio.active_positions)}")
    
    # Run single analysis
    print(f"\n🔍 Analyzing: Trump 2024")
    print("-" * 60)
    
    try:
        # Analyze the market
        decision = await agent.analyze_market("Trump 2024")
        
        if not decision:
            print("❌ No decision returned from analysis")
            return False
        
        print(f"\n✅ Analysis Complete!")
        print(f"   Recommendation: {decision.final_recommendation}")
        print(f"   Confidence: {decision.overall_confidence:.1%}")
        print(f"   Consensus: {decision.consensus_level:.1%}")
        print(f"   Suggested Bet: ${decision.suggested_bet_size:.2f}")
        
        # Check if it should trade
        should_trade = agent.should_execute_trade(decision)
        print(f"\n🎯 Should Execute Trade: {should_trade}")
        
        if not should_trade:
            print("\n⚠️  Trade NOT executed. Reasons:")
            if decision.final_recommendation == "HOLD":
                print("   - Recommendation is HOLD")
            if decision.overall_confidence < agent.min_confidence:
                print(f"   - Confidence too low: {decision.overall_confidence:.1%} < {agent.min_confidence:.1%}")
            if decision.consensus_level < agent.min_consensus:
                print(f"   - Consensus too low: {decision.consensus_level:.1%} < {agent.min_consensus:.1%}")
            suggested_size = min(decision.suggested_bet_size or 0, agent.max_position_size)
            if suggested_size > agent.portfolio.cash:
                print(f"   - Insufficient cash: ${agent.portfolio.cash:.2f} < ${suggested_size:.2f}")
        else:
            print("\n✅ Trade criteria met! Executing...")
            
            # Execute trade (market data fetched inside)
            trade = await agent.execute_trade(decision, "Trump 2024")
            
            if trade:
                print(f"\n🎉 TRADE EXECUTED!")
                print(f"   Trade ID: {trade.trade_id}")
                print(f"   Market: {trade.market_title}")
                print(f"   Action: {trade.action.upper()}")
                print(f"   Outcome: {trade.outcome}")
                print(f"   Size: ${trade.size:.2f}")
                print(f"   Shares: {trade.shares:.2f}")
                print(f"   Price: ${trade.price:.2f}")
            else:
                print("\n❌ Trade execution failed")
        
        # Show final portfolio
        print(f"\n📊 Final Portfolio:")
        print(f"   Total Value: ${agent.portfolio.total_value:.2f}")
        print(f"   Cash: ${agent.portfolio.cash:.2f}")
        print(f"   Active Positions: {len(agent.portfolio.active_positions)}")
        print(f"   Total Trades: {agent.portfolio.total_trades}")
        
        # Show agent votes
        print(f"\n🗳️  Agent Votes:")
        for agent_decision in decision.agent_decisions:
            print(f"   - {agent_decision.agent_name}: {agent_decision.recommendation} ({agent_decision.confidence:.1%})")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    success = await test_single_analysis()
    
    print("\n" + "="*60)
    if success:
        print("✅ Test completed successfully")
    else:
        print("❌ Test failed")
    print("="*60 + "\n")
    
    return success


if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
