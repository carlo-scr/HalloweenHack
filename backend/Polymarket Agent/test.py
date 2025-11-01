#!/usr/bin/env python3
"""
Example: Polymarket Data Collection and Decision-Making with Learning

This demonstrates the full workflow:
1. Collect market data from Polymarket (with Perplexity research)
2. Make betting decision (with Hyperspell learning)
3. Store decision for future learning
"""

import asyncio
import json
import os
from datetime import datetime

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the collector and decision modules
from polymarket_collector import collect_market_data, save_data, display_data, PolymarketTradeData
from polymarket_decision_example import (
	analyze_market_for_betting,
	store_decision,
	get_hyperspell_client,
)


async def example_workflow(market_query: str = "Will Biden win the 2024 election?"):
	"""
	Complete workflow example: collect data → make decision → learn.
	
	Args:
		market_query: Search query for the market to analyze
	"""
	
	print("=" * 70)
	print("POLYMARKET DATA COLLECTION & DECISION-MAKING EXAMPLE")
	print("=" * 70)
	print(f"\n📊 Analyzing Market: {market_query}\n")
	
	# Step 1: Collect market data
	print("\n" + "=" * 70)
	print("STEP 1: Collecting Market Data")
	print("=" * 70)
	
	try:
		# Collect data from Polymarket (with Perplexity research)
		market_data = await collect_market_data(
			market_identifier=market_query,
			method='search',
			headless=True,
		)
		
		# Display collected data
		display_data(market_data)
		
		# Save to file
		await save_data(market_data, 'polymarket_data.json')
		
		print("\n✅ Data collection complete!")
		
	except Exception as e:
		print(f"\n❌ Error collecting data: {e}")
		print("\n⚠️  Using mock data for demonstration...")
		
		# Create mock data for demonstration
		market_data = PolymarketTradeData(
			market_id="mock-market-123",
			market_url="https://polymarket.com/event/mock-market-123",
			market_title=market_query,
			market_category="Politics",
			outcomes=["Yes", "No"],
			current_prices={"Yes": 0.65, "No": 0.35},
			total_volume=50000.0,
			liquidity=10000.0,
			number_of_traders=1250,
			end_date="2024-11-05",
			time_remaining="30 days",
			status="active",
			description="Mock market for demonstration",
			recent_activity="Recent trading activity",
			perplexity_research={
				"content": "Latest polls show Biden leading...",
				"citations": ["poll1.com", "news1.com"],
			},
			market_context="Based on latest polling data and analysis...",
			collected_at=datetime.now().isoformat(),
		)
		
		display_data(market_data)
		await save_data(market_data, 'polymarket_data.json')
	
	# Step 2: Make betting decision with learning
	print("\n\n" + "=" * 70)
	print("STEP 2: Making Betting Decision (with Hyperspell Learning)")
	print("=" * 70)
	
	# Initialize Hyperspell for learning
	hyperspell_client = get_hyperspell_client()
	if hyperspell_client:
		print("\n🧠 Hyperspell enabled - learning from past decisions")
	else:
		print("\n⚠️  Hyperspell not available - install with: pip install hyperspell")
		print("   Set HYPERSPELL_API_KEY in .env to enable learning")
	
	# Convert market data to dict for decision analysis
	market_data_dict = market_data.model_dump()
	
	# Make decision (with learning from past decisions)
	decision = await analyze_market_for_betting(
		market_data_dict,
		hyperspell_client
	)
	
	# Display decision
	print("\n" + "-" * 70)
	print("🎯 DECISION RESULT")
	print("-" * 70)
	print(f"\nDecision: {decision.decision.upper()}")
	print(f"Outcome: {decision.outcome or 'N/A'}")
	print(f"Confidence: {decision.confidence:.2%}")
	print(f"Risk: {decision.risk_assessment.upper()}")
	print(f"Suggested Position: ${decision.suggested_position_size:.2f}" if decision.suggested_position_size else "Suggested Position: N/A")
	print(f"Value Opportunity: {'Yes' if decision.value_opportunity else 'No'}")
	
	if decision.learning_insights:
		print(f"\n🧠 Learning Insights:")
		print(f"   {decision.learning_insights}")
	
	if decision.past_decisions_used:
		print(f"\n📚 Used {len(decision.past_decisions_used)} past decisions for learning")
	
	print(f"\n📝 Reasoning:")
	print(f"   {decision.reasoning}")
	
	# Save decision
	decision_data = decision.model_dump()
	decision_data['analyzed_at'] = datetime.now().isoformat()
	decision_data['analysis_method'] = 'local'
	
	with open('betting_decision.json', 'w') as f:
		json.dump(decision_data, f, indent=2, ensure_ascii=False)
	
	print(f"\n💾 Decision saved to: betting_decision.json")
	
	# Step 3: Store decision in Hyperspell for future learning
	if hyperspell_client:
		print("\n\n" + "=" * 70)
		print("STEP 3: Storing Decision for Future Learning")
		print("=" * 70)
		
		try:
			print("\n💾 Storing decision in Hyperspell...")
			success = await store_decision(
				hyperspell_client,
				decision,
				market_data_dict
			)
			
			if success:
				print("✅ Decision stored successfully in Hyperspell")
				print("   Future decisions will learn from this decision")
			else:
				print("⚠️  Failed to store decision in Hyperspell")
		except Exception as e:
			print(f"⚠️  Error storing decision: {e}")
	
	# Summary
	print("\n\n" + "=" * 70)
	print("SUMMARY")
	print("=" * 70)
	print("\n✅ Complete workflow executed:")
	print("   1. Collected market data from Polymarket")
	print("   2. Added Perplexity research for context")
	print("   3. Made betting decision with Hyperspell learning")
	print("   4. Stored decision for future learning")
	print("\n📁 Files created:")
	print("   - polymarket_data.json (market data)")
	print("   - betting_decision.json (decision result)")
	print("\n💡 Next steps:")
	print("   - When market resolves, update outcome using:")
	print("     update_decision_outcome(hyperspell_client, decision_id, was_correct, ...)")
	print("   - Run this again to see how past decisions influence new ones")
	
	return market_data, decision


async def quick_example():
	"""Quick example with mock data (no API calls needed)."""
	
	print("=" * 70)
	print("QUICK EXAMPLE: Decision-Making with Mock Data")
	print("=" * 70)
	
	# Create mock market data
	mock_market = {
		"market_id": "quick-example-123",
		"market_url": "https://polymarket.com/event/example",
		"market_title": "Will it rain tomorrow?",
		"market_category": "Weather",
		"outcomes": ["Yes", "No"],
		"current_prices": {"Yes": 0.30, "No": 0.70},
		"total_volume": 10000.0,
		"liquidity": 2000.0,
		"number_of_traders": 500,
		"end_date": "2024-12-01",
		"time_remaining": "5 days",
		"status": "active",
		"description": "Simple weather prediction market",
		"recent_activity": "Active trading",
		"collected_at": datetime.now().isoformat(),
	}
	
	# Initialize Hyperspell (optional)
	hyperspell_client = get_hyperspell_client()
	
	if hyperspell_client:
		print("\n🧠 Hyperspell enabled")
	else:
		print("\n⚠️  Hyperspell not configured (optional)")
	
	print("\n📊 Mock Market Data:")
	print(f"   Market: {mock_market['market_title']}")
	print(f"   Prices: {mock_market['current_prices']}")
	print(f"   Volume: ${mock_market['total_volume']:,.2f}")
	
	# Make decision
	print("\n🤔 Making decision...")
	decision = await analyze_market_for_betting(
		mock_market,
		hyperspell_client
	)
	
	# Display result
	print("\n" + "-" * 70)
	print("DECISION RESULT")
	print("-" * 70)
	print(f"\n🎯 Decision: {decision.decision.upper()}")
	print(f"📈 Outcome: {decision.outcome or 'N/A'}")
	print(f"💪 Confidence: {decision.confidence:.2%}")
	print(f"⚠️  Risk: {decision.risk_assessment.upper()}")
	
	if decision.learning_insights:
		print(f"\n🧠 Learning: {decision.learning_insights}")
	
	print(f"\n📝 Reasoning:\n   {decision.reasoning}")
	
	# Store in Hyperspell if available
	if hyperspell_client:
		print("\n💾 Storing in Hyperspell...")
		await store_decision(hyperspell_client, decision, mock_market)
		print("✅ Stored!")


async def main():
	"""Main function with options."""
	import sys
	
	if len(sys.argv) > 1 and sys.argv[1] == '--quick':
		# Quick example with mock data (no API calls)
		await quick_example()
	else:
		# Full example (requires API keys)
		market_query = sys.argv[1] if len(sys.argv) > 1 else "2024 US Presidential Election"
		await example_workflow(market_query)


if __name__ == '__main__':
	print("\n🚀 Starting Polymarket Data Collection & Decision-Making Example\n")
	
	# Run the example
	asyncio.run(main())
