#!/usr/bin/env python3
"""
Polymarket Decision Agent using Replit and Hyperspell

This agent uses data collected by polymarket_collector.py to make betting decisions.
It uses Hyperspell to remember and learn from previous decisions.
It can run locally or be deployed on Replit.

Usage:
    python polymarket_decision_example.py [--replit] [--learn]
    
For Replit deployment:
    - Set REPLIT_API_KEY environment variable
    - Or deploy this script to Replit and run it there
    
For Hyperspell learning:
    - Set HYPERSPELL_API_KEY environment variable
    - The agent will automatically store and retrieve past decisions
"""

import argparse
import json
import os
from datetime import datetime
from typing import Literal

import httpx
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()

# Import Hyperspell
try:
	from hyperspell import Hyperspell
	HYPERSPELL_AVAILABLE = True
except ImportError:
	HYPERSPELL_AVAILABLE = False
	print('⚠️  Hyperspell not installed. Install with: pip install hyperspell')


class BettingDecision(BaseModel):
	"""Decision model for betting agent."""
	
	market_id: str
	decision: Literal['buy', 'sell', 'hold', 'no_action']
	outcome: str | None = Field(description="Which outcome to bet on (if buy/sell)")
	confidence: float = Field(description="Confidence level 0-1")
	reasoning: str = Field(description="Reasoning for the decision")
	suggested_position_size: float | None = Field(description="Suggested position size in USD")
	risk_assessment: str = Field(description="Risk assessment (low/medium/high)")
	
	# Market analysis
	price_discrepancy: float | None = Field(
		description="Difference between perceived probability and market price"
	)
	value_opportunity: bool = Field(
		description="Whether this represents a value betting opportunity"
	)
	
	# Learning from past decisions
	past_decisions_used: list[dict] | None = Field(
		description="Past decisions that influenced this decision"
	)
	learning_insights: str | None = Field(
		description="Insights learned from past decisions"
	)


class DecisionOutcome(BaseModel):
	"""Model for tracking decision outcomes and learning."""
	
	decision_id: str = Field(description="Unique identifier for this decision")
	market_id: str = Field(description="Market ID")
	decision_made: dict = Field(description="The original decision")
	market_data: dict = Field(description="Market data at time of decision")
	
	# Outcome tracking
	outcome_known: bool = Field(default=False, description="Whether the outcome is known")
	outcome_result: str | None = Field(description="Actual outcome if known")
	was_correct: bool | None = Field(description="Whether the decision was correct")
	actual_return: float | None = Field(description="Actual return if bet was placed")
	
	# Metadata
	decision_timestamp: str = Field(description="When decision was made")
	outcome_timestamp: str | None = Field(description="When outcome was recorded")
	
	def to_memory_text(self) -> str:
		"""Convert to text format for Hyperspell storage."""
		result = f"Decision on market {self.market_id}:\n"
		result += f"Market: {self.market_data.get('market_title', 'N/A')}\n"
		result += f"Decision: {self.decision_made.get('decision', 'N/A')}\n"
		result += f"Outcome: {self.decision_made.get('outcome', 'N/A')}\n"
		result += f"Confidence: {self.decision_made.get('confidence', 0)}\n"
		result += f"Reasoning: {self.decision_made.get('reasoning', 'N/A')}\n"
		
		if self.outcome_known:
			result += f"Result: {'CORRECT' if self.was_correct else 'INCORRECT'}\n"
			result += f"Actual Outcome: {self.outcome_result}\n"
			if self.actual_return is not None:
				result += f"Return: {self.actual_return}%\n"
		
		return result


def get_hyperspell_client() -> 'Hyperspell | None':
	"""Get Hyperspell client if available."""
	if not HYPERSPELL_AVAILABLE:
		return None
	
	api_key = os.getenv('HYPERSPELL_API_KEY')
	if not api_key or api_key == 'your_hyperspell_api_key_here':
		return None
	
	try:
		return Hyperspell(api_key=api_key)
	except Exception as e:
		print(f'⚠️  Hyperspell initialization error: {e}')
		return None


async def query_past_decisions(
	hyperspell_client: 'Hyperspell',
	market_title: str,
	market_category: str | None = None,
	limit: int = 5
) -> list[dict]:
	"""
	Query Hyperspell for past similar decisions.
	
	Args:
		hyperspell_client: Hyperspell client instance
		market_title: Current market title to find similar markets
		market_category: Market category to narrow search
		limit: Maximum number of past decisions to retrieve
		
	Returns:
		List of past decision documents
	"""
	if not hyperspell_client:
		return []
	
	try:
		# Build search query
		query = f"previous betting decisions on {market_title}"
		if market_category:
			query += f" in {market_category}"
		
		# Search for relevant past decisions
		response = hyperspell_client.memories.search(
			query=query,
			sources=["vault"],
			options={"vault": {"collection": "betting_decisions"}},
			limit=limit
		)
		
		past_decisions = []
		if hasattr(response, 'documents'):
			for doc in response.documents[:limit]:
				if hasattr(doc, 'text'):
					past_decisions.append({
						'text': doc.text,
						'score': getattr(doc, 'score', 0.0) if hasattr(doc, 'score') else 0.0,
					})
		elif hasattr(response, 'data') and isinstance(response.data, list):
			for item in response.data[:limit]:
				past_decisions.append({
					'text': item.get('text', ''),
					'score': item.get('score', 0.0),
				})
		
		return past_decisions
	except Exception as e:
		print(f'⚠️  Error querying Hyperspell: {e}')
		return []


async def store_decision(
	hyperspell_client: 'Hyperspell',
	decision: BettingDecision,
	market_data: dict,
) -> bool:
	"""
	Store a decision in Hyperspell for future learning.
	
	Args:
		hyperspell_client: Hyperspell client instance
		decision: The betting decision made
		market_data: Market data used for the decision
		
	Returns:
		True if successfully stored, False otherwise
	"""
	if not hyperspell_client:
		return False
	
	try:
		# Create memory text
		memory_text = f"Betting decision on market {decision.market_id}:\n"
		memory_text += f"Market: {market_data.get('market_title', 'N/A')}\n"
		memory_text += f"Category: {market_data.get('market_category', 'N/A')}\n"
		memory_text += f"Decision: {decision.decision}\n"
		memory_text += f"Outcome: {decision.outcome or 'N/A'}\n"
		memory_text += f"Confidence: {decision.confidence:.2%}\n"
		memory_text += f"Reasoning: {decision.reasoning}\n"
		memory_text += f"Risk: {decision.risk_assessment}\n"
		memory_text += f"Value Opportunity: {decision.value_opportunity}\n"
		memory_text += f"Prices: {market_data.get('current_prices', {})}\n"
		memory_text += f"Timestamp: {datetime.now().isoformat()}\n"
		
		# Store in Hyperspell
		result = hyperspell_client.memories.add(
			text=memory_text,
			collection="betting_decisions"
		)
		
		return result is not None
	except Exception as e:
		print(f'⚠️  Error storing decision in Hyperspell: {e}')
		return False


async def update_decision_outcome(
	hyperspell_client: 'Hyperspell',
	decision_id: str,
	was_correct: bool,
	actual_outcome: str,
	actual_return: float | None = None,
) -> bool:
	"""
	Update a stored decision with its outcome for learning.
	
	Args:
		hyperspell_client: Hyperspell client instance
		decision_id: Identifier for the decision
		was_correct: Whether the decision was correct
		actual_outcome: The actual outcome
		actual_return: Actual return percentage if available
		
	Returns:
		True if successfully updated, False otherwise
	"""
	if not hyperspell_client:
		return False
	
	try:
		# Create outcome update text
		outcome_text = f"Decision outcome for {decision_id}:\n"
		outcome_text += f"Result: {'CORRECT' if was_correct else 'INCORRECT'}\n"
		outcome_text += f"Actual Outcome: {actual_outcome}\n"
		if actual_return is not None:
			outcome_text += f"Return: {actual_return}%\n"
		outcome_text += f"Updated: {datetime.now().isoformat()}\n"
		
		# Store outcome in separate collection for tracking
		result = hyperspell_client.memories.add(
			text=outcome_text,
			collection="decision_outcomes"
		)
		
		return result is not None
	except Exception as e:
		print(f'⚠️  Error updating decision outcome in Hyperspell: {e}')
		return False


async def analyze_with_replit(data: dict, replit_api_key: str | None = None) -> BettingDecision:
	"""
	Use Replit API to analyze market data and make betting decision.
	
	Args:
		data: Market data from polymarket_collector.py
		replit_api_key: Replit API key (defaults to REPLIT_API_KEY env var)
		
	Returns:
		BettingDecision: Decision with reasoning
	"""
	if not replit_api_key:
		replit_api_key = os.getenv('REPLIT_API_KEY')
	
	if not replit_api_key:
		raise ValueError(
			'REPLIT_API_KEY not set. Set it in .env or pass as argument. '
			'Alternatively, deploy this script to Replit and run it there.'
		)
	
	# Prepare analysis prompt for Replit
	market_summary = {
		'market_title': data.get('market_title'),
		'outcomes': data.get('outcomes', []),
		'current_prices': data.get('current_prices', {}),
		'total_volume': data.get('total_volume'),
		'liquidity': data.get('liquidity'),
		'market_context': data.get('market_context'),
		'status': data.get('status'),
	}
	
	prompt = f"""Analyze this Polymarket trade data and make a betting decision:

Market: {market_summary['market_title']}
Outcomes: {market_summary['outcomes']}
Current Prices: {market_summary['current_prices']}
Volume: ${market_summary['total_volume']} | Liquidity: ${market_summary['liquidity']}
Status: {market_summary['status']}

Additional Context:
{market_summary.get('market_context', 'N/A')}

Provide a betting decision with:
1. Decision: buy, sell, hold, or no_action
2. Outcome: which outcome to bet on (if buy/sell)
3. Confidence: 0-1
4. Reasoning: detailed explanation
5. Suggested position size: USD amount
6. Risk assessment: low/medium/high
7. Price discrepancy: if you think market is mispriced
8. Value opportunity: true/false

Return as JSON matching this structure:
{{
  "decision": "buy|sell|hold|no_action",
  "outcome": "...",
  "confidence": 0.75,
  "reasoning": "...",
  "suggested_position_size": 50.00,
  "risk_assessment": "low|medium|high",
  "price_discrepancy": 0.05,
  "value_opportunity": true
}}
"""
	
	try:
		# Use Replit's API (example - adjust based on actual Replit API)
		# This is a placeholder - Replit may have different API endpoints
		async with httpx.AsyncClient(timeout=60.0) as client:
			headers = {
				'Authorization': f'Bearer {replit_api_key}',
				'Content-Type': 'application/json',
			}
			
			# Option 1: If Replit has a code execution API
			# response = await client.post(
			#     'https://api.replit.com/v1/run',
			#     json={'code': analysis_code, 'language': 'python'},
			#     headers=headers,
			# )
			
			# Option 2: If using Replit's model API
			# For now, we'll use OpenAI-compatible endpoint (Replit may support this)
			# Or you can deploy this script to Replit and call it via HTTP
			
			# Placeholder: Return the result from local analysis
			# In production, you'd make actual Replit API calls here
			print('⚠️  Using local analysis (Replit API integration pending)')
			print('   To use Replit: Deploy this script to Replit and call it via HTTP')
			
			# Fall back to local analysis for now
			# Initialize Hyperspell for learning
			hyperspell_client = get_hyperspell_client()
			return await analyze_market_for_betting(data, hyperspell_client)
			
	except Exception as e:
		print(f'⚠️  Replit API error: {e}')
		print('   Falling back to local analysis...')
		hyperspell_client = get_hyperspell_client()
		return await analyze_market_for_betting(data, hyperspell_client)


async def analyze_market_for_betting(
	data: dict,
	hyperspell_client: 'Hyperspell | None' = None,
) -> BettingDecision:
	"""
	Analyze collected Polymarket data and make a betting decision.
	
	This function now uses Hyperspell to learn from past decisions.
	
	Args:
		data: Market data from polymarket_collector.py
		hyperspell_client: Hyperspell client for learning from past decisions
		
	Returns:
		BettingDecision: Decision with reasoning
	"""
	
	# Query past similar decisions from Hyperspell
	past_decisions = []
	learning_insights = None
	
	if hyperspell_client:
		try:
			print('\n🧠 Querying Hyperspell for past decisions...')
			past_decisions = await query_past_decisions(
				hyperspell_client,
				data.get('market_title', ''),
				data.get('market_category'),
				limit=5
			)
			
			if past_decisions:
				print(f'✓ Found {len(past_decisions)} relevant past decisions')
				# Extract insights from past decisions
				correct_count = sum(1 for d in past_decisions if 'CORRECT' in d.get('text', ''))
				incorrect_count = sum(1 for d in past_decisions if 'INCORRECT' in d.get('text', ''))
				
				if correct_count + incorrect_count > 0:
					success_rate = correct_count / (correct_count + incorrect_count)
					learning_insights = f"Based on {len(past_decisions)} past similar decisions: "
					learning_insights += f"{success_rate:.1%} success rate. "
					
					# Extract common patterns
					if success_rate > 0.6:
						learning_insights += "Similar markets have been profitable. "
					elif success_rate < 0.4:
						learning_insights += "Caution: Similar markets have had poor results. "
			else:
				print('ℹ️  No past decisions found for similar markets')
		except Exception as e:
			print(f'⚠️  Error learning from past decisions: {e}')
	
	# Extract key information
	market_id = data.get('market_id')
	outcomes = data.get('outcomes', [])
	current_prices = data.get('current_prices', {})
	total_volume = data.get('total_volume', 0)
	liquidity = data.get('liquidity', 0)
	status = data.get('status', 'active')
	
	# Simple decision logic (example only)
	# In practice, you'd use ML models, statistical analysis, etc.
	
	if status != 'active':
		return BettingDecision(
			market_id=market_id,
			decision='no_action',
			confidence=1.0,
			reasoning=f"Market is {status}, cannot trade",
			risk_assessment='high',
			value_opportunity=False,
		)
	
	# Find outcome with lowest price (might be undervalued)
	lowest_price_outcome = None
	lowest_price = 1.0
	
	for outcome, price in current_prices.items():
		if price < lowest_price:
			lowest_price = price
			lowest_price_outcome = outcome
	
	# Find outcome with highest price (most likely)
	highest_price_outcome = None
	highest_price = 0.0
	
	for outcome, price in current_prices.items():
		if price > highest_price:
			highest_price = price
			highest_price_outcome = outcome
	
	# Incorporate learning from past decisions
	if learning_insights and 'profitable' in learning_insights.lower():
		# Past similar decisions were profitable - slightly increase confidence
		if lowest_price < 0.35:  # Lower threshold if past decisions were good
			base_threshold = 0.35
		else:
			base_threshold = 0.3
	elif learning_insights and 'poor' in learning_insights.lower():
		# Past similar decisions had poor results - be more cautious
		if lowest_price < 0.25:  # Lower threshold, need stronger signal
			base_threshold = 0.25
		else:
			base_threshold = 0.3
	else:
		base_threshold = 0.3
	
	# Simple strategy: if lowest price is below threshold, might be undervalued
	# If highest price is above 0.7, might be overvalued
	# This is just an example - implement your own strategy!
	
	if lowest_price < base_threshold:
		# Potential value bet on lowest priced outcome
		base_confidence = 0.5
		
		# Adjust confidence based on past decisions
		if learning_insights and 'profitable' in learning_insights.lower():
			base_confidence = min(0.7, base_confidence + 0.1)  # Increase confidence
		elif learning_insights and 'poor' in learning_insights.lower():
			base_confidence = max(0.3, base_confidence - 0.1)  # Decrease confidence
		
		confidence = base_confidence
		decision = 'buy'
		outcome = lowest_price_outcome
		
		reasoning = f"Lowest priced outcome '{outcome}' at {lowest_price:.2%} may be undervalued. Market price suggests {lowest_price:.2%} probability but might have higher actual probability."
		if learning_insights:
			reasoning += f"\n\nLearning: {learning_insights}"
		
		risk_assessment = 'medium'
		value_opportunity = True
		price_discrepancy = None  # Would calculate based on your model
		
	elif highest_price > 0.7:
		# High probability outcome - might sell if you have position
		confidence = 0.6
		decision = 'sell' if highest_price > 0.85 else 'hold'
		outcome = highest_price_outcome
		reasoning = f"Highest priced outcome '{outcome}' at {highest_price:.2%} is heavily favored. Consider taking profit if holding position."
		risk_assessment = 'low'
		value_opportunity = False
		price_discrepancy = None
		
	else:
		# Balanced market - hold or no action
		confidence = 0.4
		decision = 'hold'
		outcome = None
		reasoning = "Market prices are relatively balanced. No clear value opportunity identified."
		risk_assessment = 'medium'
		value_opportunity = False
		price_discrepancy = None
	
	# Calculate suggested position size (simple example)
	# In practice, use Kelly criterion, bankroll management, etc.
	suggested_position_size = None
	if decision in ['buy', 'sell'] and liquidity and liquidity > 1000:
		# Conservative: risk 1% of available liquidity
		suggested_position_size = min(liquidity * 0.01, 100)  # Cap at $100
	
	return BettingDecision(
		market_id=market_id,
		decision=decision,
		outcome=outcome,
		confidence=confidence,
		reasoning=reasoning,
		suggested_position_size=suggested_position_size,
		risk_assessment=risk_assessment,
		price_discrepancy=price_discrepancy,
		value_opportunity=value_opportunity,
		past_decisions_used=[{'text': d.get('text', ''), 'score': d.get('score', 0)} for d in past_decisions] if past_decisions else None,
		learning_insights=learning_insights,
	)


async def main():
	"""Example usage."""
	
	parser = argparse.ArgumentParser(description='Make betting decisions using Polymarket data')
	parser.add_argument('--replit', action='store_true', help='Use Replit API for analysis')
	parser.add_argument('--replit-api-key', type=str, help='Replit API key')
	parser.add_argument('--input', type=str, default='polymarket_data.json', help='Input JSON file')
	parser.add_argument('--output', type=str, default='betting_decision.json', help='Output JSON file')
	
	args = parser.parse_args()
	
	# Load data collected by polymarket_collector.py
	try:
		with open(args.input, 'r') as f:
			data_list = json.load(f)
			# Use most recent data
			if data_list:
				latest_data = data_list[-1]
			else:
				print("❌ No data found in polymarket_data.json")
				print("   Run polymarket_collector.py first to collect data")
				return
	except FileNotFoundError:
		print(f"❌ {args.input} not found")
		print("   Run polymarket_collector.py first to collect data")
		return
	
	print("📊 Analyzing Polymarket Data for Betting Decision")
	if args.replit:
		print("🤖 Using Replit API for analysis")
	
	# Initialize Hyperspell for learning
	hyperspell_client = None
	if HYPERSPELL_AVAILABLE:
		hyperspell_client = get_hyperspell_client()
		if hyperspell_client:
			print("🧠 Hyperspell enabled - learning from past decisions")
	else:
		print("⚠️  Hyperspell not available - install with: pip install hyperspell")
	
	print("=" * 60)
	
	# Make decision
	if args.replit:
		decision = await analyze_with_replit(latest_data, args.replit_api_key)
	else:
		decision = await analyze_market_for_betting(latest_data, hyperspell_client)
	
	# Display decision
	print(f"\n🎯 Decision: {decision.decision.upper()}")
	print(f"📈 Outcome: {decision.outcome or 'N/A'}")
	print(f"💪 Confidence: {decision.confidence:.2%}")
	print(f"⚠️  Risk: {decision.risk_assessment.upper()}")
	print(f"💰 Suggested Position: ${decision.suggested_position_size:.2f}" if decision.suggested_position_size else "💰 Suggested Position: N/A")
	print(f"💡 Value Opportunity: {'Yes' if decision.value_opportunity else 'No'}")
	
	# Display learning insights
	if decision.learning_insights:
		print(f"\n🧠 Learning Insights:\n{decision.learning_insights}")
	if decision.past_decisions_used:
		print(f"\n📚 Used {len(decision.past_decisions_used)} past decisions for learning")
	
	print(f"\n📝 Reasoning:\n{decision.reasoning}")
	
	# Save decision
	decision_data = decision.model_dump()
	decision_data['analyzed_at'] = datetime.now().isoformat()
	decision_data['analysis_method'] = 'replit' if args.replit else 'local'
	
	with open(args.output, 'w') as f:
		json.dump(decision_data, f, indent=2, ensure_ascii=False)
	
	print(f"\n💾 Decision saved to: {args.output}")
	
	# Store decision in Hyperspell for future learning
	if hyperspell_client:
		try:
			print('\n💾 Storing decision in Hyperspell for future learning...')
			success = await store_decision(hyperspell_client, decision, latest_data)
			if success:
				print('✓ Decision stored successfully')
			else:
				print('⚠️  Failed to store decision in Hyperspell')
		except Exception as e:
			print(f'⚠️  Error storing decision: {e}')
	
	print("\n📋 JSON Output:")
	print(json.dumps(decision_data, indent=2, ensure_ascii=False))


if __name__ == '__main__':
	import asyncio
	asyncio.run(main())

