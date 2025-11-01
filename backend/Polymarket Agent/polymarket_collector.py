#!/usr/bin/env python3
"""
Polymarket Data Collector Agent

This agent navigates to Polymarket and collects structured data about a specific trade/market.
It also uses Perplexity API to gather additional context about the market topic.
The collected data is formatted for use by another agent that makes betting decisions.

Usage:
    python polymarket_collector.py --market-url "https://polymarket.com/event/..."
    python polymarket_collector.py --market-id "your-market-id"
    python polymarket_collector.py --query "search query for market"
"""

import argparse
import asyncio
import json
import os
from datetime import datetime
from typing import Literal

import httpx
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()

from browser_use import Agent, Browser, ChatBrowserUse


class PolymarketTradeData(BaseModel):
	"""Structured data model for Polymarket trade information."""

	# Market identification
	market_id: str = Field(description="Unique identifier for the market")
	market_url: str = Field(description="Full URL to the market page")
	market_title: str = Field(description="Title/question of the market")
	market_category: str | None = Field(description="Category or type of market")
	
	# Outcome data
	outcomes: list[str] = Field(description="List of possible outcomes/options")
	current_prices: dict[str, float] = Field(
		description="Current price (probability) for each outcome, as decimal (0-1)"
	)
	
	# Market statistics
	total_volume: float | None = Field(
		description="Total trading volume in USD"
	)
	liquidity: float | None = Field(
		description="Current liquidity in USD"
	)
	number_of_traders: int | None = Field(
		description="Number of traders participating"
	)
	
	# Time information
	end_date: str | None = Field(
		description="Resolution/end date for the market"
	)
	time_remaining: str | None = Field(
		description="Time remaining until resolution"
	)
	
	# Market status
	status: Literal['active', 'resolved', 'closed'] = Field(
		description="Current status of the market"
	)
	resolution: str | None = Field(
		description="Resolution outcome if market is resolved"
	)
	
	# Additional context
	description: str | None = Field(
		description="Market description or context"
	)
	recent_activity: str | None = Field(
		description="Recent trading activity or notable changes"
	)
	
	# Perplexity research data
	perplexity_research: dict | None = Field(
		description="Additional research and context from Perplexity API"
	)
	market_context: str | None = Field(
		description="Contextual information about the market topic from Perplexity"
	)
	
	# Metadata
	collected_at: str = Field(
		description="Timestamp when this data was collected (ISO format)"
	)


async def query_perplexity(query: str, api_key: str | None = None) -> dict:
	"""
	Query Perplexity API for additional context about the market.
	
	Args:
		query: Search query for Perplexity
		api_key: Perplexity API key (defaults to PERPLEXITY_API_KEY env var)
		
	Returns:
		dict: Perplexity search results
	"""
	if not api_key:
		api_key = os.getenv('PERPLEXITY_API_KEY')
	
	if not api_key or api_key == 'your_perplexity_api_key_here':
		print('⚠️  Warning: PERPLEXITY_API_KEY not set. Skipping Perplexity research.')
		return {}
	
	try:
		async with httpx.AsyncClient(timeout=30.0) as client:
			headers = {
				'Authorization': f'Bearer {api_key}',
				'Content-Type': 'application/json',
			}
			
			payload = {
				'model': 'llama-3.1-sonar-large-128k-online',
				'messages': [
					{
						'role': 'user',
						'content': query
					}
				],
				'temperature': 0.2,
				'max_tokens': 2000,
			}
			
			response = await client.post(
				'https://api.perplexity.ai/chat/completions',
				json=payload,
				headers=headers,
			)
			
			if response.status_code == 200:
				result = response.json()
				content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
				citations = result.get('citations', [])
				
				return {
					'content': content,
					'citations': citations,
					'model': result.get('model', ''),
				}
			else:
				print(f'⚠️  Perplexity API error: {response.status_code} - {response.text}')
				return {}
	except Exception as e:
		print(f'⚠️  Perplexity API error: {e}')
		return {}


async def collect_market_data(
	market_identifier: str,
	method: Literal['url', 'id', 'search'] = 'url',
	headless: bool = True,
	llm_model: str | None = None,
) -> PolymarketTradeData:
	"""
	Collect structured data about a Polymarket trade/market.
	
	Args:
		market_identifier: URL, market ID, or search query
		method: How to find the market ('url', 'id', or 'search')
		headless: Run browser in headless mode
		llm_model: LLM model to use (default: ChatBrowserUse)
		
	Returns:
		PolymarketTradeData: Structured data about the market
	"""
	
	# Validate API key
	api_key = os.getenv('BROWSER_USE_API_KEY')
	if not api_key or api_key == 'your_api_key_here':
		raise ValueError(
			'BROWSER_USE_API_KEY not set. Get one from: https://cloud.browser-use.com/new-api-key'
		)
	
	# Initialize LLM
	if llm_model:
		from browser_use import ChatOpenAI
		llm = ChatOpenAI(model=llm_model)
	else:
		llm = ChatBrowserUse()
	
	# Build task prompt based on method
	if method == 'url':
		url = market_identifier
		if not url.startswith('http'):
			url = f'https://polymarket.com{market_identifier}'
		prompt = f"""Navigate to {url} and extract all market data.

Extract the following information:
1. Market ID and URL
2. Market title/question
3. Category/type
4. All possible outcomes/options
5. Current price (probability) for each outcome as decimal (0-1)
6. Total trading volume in USD
7. Current liquidity in USD
8. Number of traders
9. Resolution/end date
10. Time remaining until resolution
11. Market status (active/resolved/closed)
12. Resolution outcome if resolved
13. Market description/context
14. Recent trading activity

When done, call the done action with success=True and put ALL extracted data in the text field as valid JSON matching this exact structure:
{{
  "market_id": "...",
  "market_url": "...",
  "market_title": "...",
  "market_category": "...",
  "outcomes": ["option1", "option2"],
  "current_prices": {{"option1": 0.65, "option2": 0.35}},
  "total_volume": 12345.67,
  "liquidity": 5678.90,
  "number_of_traders": 1234,
  "end_date": "...",
  "time_remaining": "...",
  "status": "active|resolved|closed",
  "resolution": "...",
  "description": "...",
  "recent_activity": "...",
  "collected_at": "{datetime.now().isoformat()}"
}}

Extract prices as decimals between 0 and 1 (e.g., 0.65 means 65% probability).
If a field is not available, use null."""
	
	elif method == 'id':
		prompt = f"""Navigate to https://polymarket.com/event/{market_identifier} and extract all market data.

Extract the following information:
1. Market ID and URL
2. Market title/question
3. Category/type
4. All possible outcomes/options
5. Current price (probability) for each outcome as decimal (0-1)
6. Total trading volume in USD
7. Current liquidity in USD
8. Number of traders
9. Resolution/end date
10. Time remaining until resolution
11. Market status (active/resolved/closed)
12. Resolution outcome if resolved
13. Market description/context
14. Recent trading activity

When done, call the done action with success=True and put ALL extracted data in the text field as valid JSON matching this exact structure:
{{
  "market_id": "...",
  "market_url": "...",
  "market_title": "...",
  "market_category": "...",
  "outcomes": ["option1", "option2"],
  "current_prices": {{"option1": 0.65, "option2": 0.35}},
  "total_volume": 12345.67,
  "liquidity": 5678.90,
  "number_of_traders": 1234,
  "end_date": "...",
  "time_remaining": "...",
  "status": "active|resolved|closed",
  "resolution": "...",
  "description": "...",
  "recent_activity": "...",
  "collected_at": "{datetime.now().isoformat()}"
}}

Extract prices as decimals between 0 and 1 (e.g., 0.65 means 65% probability).
If a field is not available, use null."""
	
	else:  # search
		prompt = f"""Navigate to https://polymarket.com and search for: "{market_identifier}"

Find the most relevant market from search results and navigate to it.
Extract all market data including:
1. Market ID and URL
2. Market title/question
3. Category/type
4. All possible outcomes/options
5. Current price (probability) for each outcome as decimal (0-1)
6. Total trading volume in USD
7. Current liquidity in USD
8. Number of traders
9. Resolution/end date
10. Time remaining until resolution
11. Market status (active/resolved/closed)
12. Resolution outcome if resolved
13. Market description/context
14. Recent trading activity

When done, call the done action with success=True and put ALL extracted data in the text field as valid JSON matching this exact structure:
{{
  "market_id": "...",
  "market_url": "...",
  "market_title": "...",
  "market_category": "...",
  "outcomes": ["option1", "option2"],
  "current_prices": {{"option1": 0.65, "option2": 0.35}},
  "total_volume": 12345.67,
  "liquidity": 5678.90,
  "number_of_traders": 1234,
  "end_date": "...",
  "time_remaining": "...",
  "status": "active|resolved|closed",
  "resolution": "...",
  "description": "...",
  "recent_activity": "...",
  "collected_at": "{datetime.now().isoformat()}"
}}

Extract prices as decimals between 0 and 1 (e.g., 0.65 means 65% probability).
If a field is not available, use null."""
	
	# Initialize browser and agent
	browser = Browser(headless=headless)
	agent = Agent(
		task=prompt,
		llm=llm,
		browser=browser,
		use_vision='auto',
	)
	
	print(f'🔍 Collecting Polymarket data...')
	print(f'   Method: {method}')
	print(f'   Identifier: {market_identifier}')
	print('-' * 60)
	
	# Run agent
	result = await agent.run(max_steps=50)
	
	# Extract JSON from result
	raw_result = result.final_result() if result else None
	
	if not raw_result:
		raise ValueError('Failed to extract market data')
	
	# Parse JSON from result
	text = str(raw_result).strip()
	
	# Clean up JSON extraction (handle various formats)
	if '<json>' in text and '</json>' in text:
		text = text.split('<json>', 1)[1].split('</json>', 1)[0].strip()
	
	if text.startswith('```'):
		text = text.lstrip('`\n ').strip()
		if text.lower().startswith('json'):
			text = text[4:].lstrip()
		text = text.rstrip('`').strip()
	
	# Find first JSON object
	brace = text.find('{')
	if brace != -1:
		text = text[brace:]
	
	try:
		data = json.loads(text)
	except json.JSONDecodeError as e:
		# Try to extract just the JSON portion
		brace_count = 0
		start_idx = None
		end_idx = None
		
		for i, char in enumerate(text):
			if char == '{':
				if brace_count == 0:
					start_idx = i
				brace_count += 1
			elif char == '}':
				brace_count -= 1
				if brace_count == 0 and start_idx is not None:
					end_idx = i + 1
					break
		
		if start_idx is not None and end_idx is not None:
			data = json.loads(text[start_idx:end_idx])
		else:
			raise ValueError(f'Could not parse JSON from result: {e}')
	
	# Collect additional context from Perplexity
	perplexity_data = {}
	market_context = None
	
	if data.get('market_title'):
		print('\n🔍 Querying Perplexity for additional context...')
		perplexity_query = f"Provide latest news, analysis, and context about: {data.get('market_title')}"
		perplexity_data = await query_perplexity(perplexity_query)
		
		if perplexity_data and perplexity_data.get('content'):
			market_context = perplexity_data.get('content')
			print('✓ Perplexity research completed')
	
	# Add Perplexity data to market data
	data['perplexity_research'] = perplexity_data
	data['market_context'] = market_context
	
	# Validate and add timestamp
	if 'collected_at' not in data or not data['collected_at']:
		data['collected_at'] = datetime.now().isoformat()
	
	# Convert to Pydantic model for validation
	trade_data = PolymarketTradeData(**data)
	
	return trade_data


async def save_data(
	data: PolymarketTradeData,
	output_file: str = 'polymarket_data.json',
):
	"""Save collected data to JSON file."""
	data_dict = data.model_dump()
	
	# Append to file or create new
	existing_data = []
	if os.path.exists(output_file):
		try:
			with open(output_file, 'r') as f:
				existing_data = json.load(f)
		except Exception:
			existing_data = []
	
	existing_data.append(data_dict)
	
	with open(output_file, 'w') as f:
		json.dump(existing_data, f, indent=2, ensure_ascii=False)
	
	print(f'\n💾 Data saved to: {output_file}')


def display_data(data: PolymarketTradeData):
	"""Display collected data in a readable format."""
	print('\n' + '=' * 60)
	print('📊 POLYMARKET DATA COLLECTED')
	print('=' * 60)
	print(f'\n🎯 Market: {data.market_title}')
	print(f'🔗 URL: {data.market_url}')
	print(f'📁 Category: {data.market_category or "N/A"}')
	print(f'🏷️  Status: {data.status.upper()}')
	print(f'🆔 Market ID: {data.market_id}')
	
	if data.description:
		print(f'\n📝 Description: {data.description[:200]}...' if len(data.description) > 200 else f'\n📝 Description: {data.description}')
	
	print(f'\n💰 Market Stats:')
	if data.total_volume:
		print(f'   Total Volume: ${data.total_volume:,.2f}')
	if data.liquidity:
		print(f'   Liquidity: ${data.liquidity:,.2f}')
	if data.number_of_traders:
		print(f'   Traders: {data.number_of_traders:,}')
	
	print(f'\n🎲 Outcomes & Current Prices:')
	for outcome in data.outcomes:
		price = data.current_prices.get(outcome, 0)
		percentage = price * 100
		print(f'   • {outcome}: {price:.4f} ({percentage:.2f}%)')
	
	if data.end_date:
		print(f'\n📅 End Date: {data.end_date}')
	if data.time_remaining:
		print(f'⏱️  Time Remaining: {data.time_remaining}')
	
	if data.status == 'resolved' and data.resolution:
		print(f'\n✅ Resolution: {data.resolution}')
	
	if data.recent_activity:
		print(f'\n📈 Recent Activity: {data.recent_activity[:200]}...' if len(data.recent_activity) > 200 else f'\n📈 Recent Activity: {data.recent_activity}')
	
	print(f'\n🕐 Collected At: {data.collected_at}')
	print('=' * 60)


async def main():
	"""Main entry point."""
	parser = argparse.ArgumentParser(
		description='Collect Polymarket trade data for betting decisions'
	)
	parser.add_argument(
		'--market-url',
		type=str,
		help='Full URL to the Polymarket market page',
	)
	parser.add_argument(
		'--market-id',
		type=str,
		help='Polymarket market ID',
	)
	parser.add_argument(
		'--query',
		type=str,
		help='Search query to find a market',
	)
	parser.add_argument(
		'--output',
		type=str,
		default='polymarket_data.json',
		help='Output JSON file path',
	)
	parser.add_argument(
		'--headless',
		action='store_true',
		help='Run browser in headless mode',
	)
	parser.add_argument(
		'--model',
		type=str,
		help='LLM model to use (e.g., gpt-4, gpt-4o-mini)',
	)
	
	args = parser.parse_args()
	
	# Determine method and identifier
	if args.market_url:
		method = 'url'
		identifier = args.market_url
	elif args.market_id:
		method = 'id'
		identifier = args.market_id
	elif args.query:
		method = 'search'
		identifier = args.query
	else:
		parser.error('Must provide --market-url, --market-id, or --query')
	
	try:
		# Collect data
		data = await collect_market_data(
			market_identifier=identifier,
			method=method,
			headless=args.headless,
			llm_model=args.model,
		)
		
		# Display results
		display_data(data)
		
		# Save to file
		await save_data(data, args.output)
		
		# Print JSON for programmatic use
		print('\n📋 JSON Output (for use by decision agent):')
		print(json.dumps(data.model_dump(), indent=2, ensure_ascii=False))
		
	except Exception as e:
		print(f'\n❌ Error: {e}')
		import traceback
		if args.headless:
			traceback.print_exc()
		raise


if __name__ == '__main__':
	asyncio.run(main())

