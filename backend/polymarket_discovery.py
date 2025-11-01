#!/usr/bin/env python3
"""
Polymarket Discovery Agent

This agent uses browser-use to:
1. Navigate to Polymarket.com
2. Find trending/active markets
3. Extract market data
4. Feed it to the multi-agent decision system
"""

import asyncio
import json
import os
from typing import List, Dict, Optional
from datetime import datetime
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()

from browser_use import Agent, Browser, ChatBrowserUse


class PolymarketMarket(BaseModel):
    """A discovered market from Polymarket."""
    title: str
    url: Optional[str] = None
    yes_price: float
    no_price: float
    volume: Optional[str] = None
    liquidity: Optional[str] = None
    category: Optional[str] = None


class PolymarketDiscovery:
    """Discovers and collects data from Polymarket markets."""
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.llm = ChatBrowserUse()
    
    async def discover_trending_markets(self, limit: int = 10) -> List[PolymarketMarket]:
        """
        Navigate to Polymarket and discover trending markets.
        
        Returns:
            List of discovered markets with basic info
        """
        print(f"\n🔍 Discovering trending markets on Polymarket...")
        
        browser = Browser(headless=self.headless)
        
        agent = Agent(
            task=f"""Go to https://polymarket.com and find the top {limit} trending markets.

For each market, extract:
1. Market title/question
2. Current YES price (as decimal, e.g., 0.65 for 65¢)
3. Current NO price (as decimal, e.g., 0.35 for 35¢)
4. Total volume (if visible)
5. Category (Politics, Crypto, Sports, etc.)
6. URL to the market

Return a JSON array with this structure:
[
  {{
    "title": "Will Trump win 2024?",
    "url": "https://polymarket.com/event/...",
    "yes_price": 0.65,
    "no_price": 0.35,
    "volume": "$10.5M",
    "category": "Politics"
  }},
  ...
]

Focus on markets with high volume and liquidity.
Only return markets that are currently active (not resolved).
""",
            llm=self.llm,
            browser=browser,
            use_vision=True
        )
        
        try:
            history = await agent.run(max_steps=15)
            result = history.final_result()
            
            # Try to parse the JSON result
            if result:
                try:
                    # Extract JSON from the result
                    result_str = str(result)
                    
                    # Find JSON array in the result - look for ```json blocks too
                    if '```json' in result_str:
                        start_idx = result_str.find('[', result_str.find('```json'))
                        end_idx = result_str.find('```', start_idx)
                        if end_idx > start_idx:
                            end_idx = result_str.rfind(']', start_idx, end_idx) + 1
                    else:
                        start_idx = result_str.find('[')
                        end_idx = result_str.rfind(']') + 1
                    
                    if start_idx >= 0 and end_idx > start_idx:
                        json_str = result_str[start_idx:end_idx]
                        markets_data = json.loads(json_str)
                        
                        markets = []
                        for market_data in markets_data:
                            try:
                                market = PolymarketMarket(**market_data)
                                markets.append(market)
                            except Exception as e:
                                print(f"⚠️  Could not parse market: {e}")
                                continue
                        
                        print(f"✅ Discovered {len(markets)} markets")
                        return markets
                    else:
                        print(f"⚠️  No JSON array found in result")
                        return []
                        
                except json.JSONDecodeError as e:
                    print(f"⚠️  Failed to parse JSON: {e}")
                    print(f"Raw result: {result}")
                    return []
            else:
                print(f"⚠️  No result from agent")
                return []
                
        except Exception as e:
            print(f"❌ Error discovering markets: {e}")
            import traceback
            traceback.print_exc()
            return []
        finally:
            # Close browser properly - BrowserSession doesn't have .close()
            try:
                if hasattr(browser, 'session') and browser.session:
                    await browser.session.close()
            except Exception as e:
                print(f"⚠️  Error closing browser: {e}")
    
    async def get_detailed_market_data(self, market_url: str) -> Optional[Dict]:
        """
        Get detailed data for a specific market.
        
        Args:
            market_url: URL to the Polymarket market
            
        Returns:
            Detailed market data
        """
        print(f"\n🔍 Getting detailed data for: {market_url}")
        
        browser = Browser(headless=self.headless)
        
        agent = Agent(
            task=f"""Go to {market_url} and extract detailed information:

1. Market question/title
2. Current YES price (decimal)
3. Current NO price (decimal)
4. Total trading volume
5. Current liquidity
6. Number of traders
7. Market end/resolution date
8. Market description
9. Recent activity or price movements
10. Top outcomes and their probabilities

Return as JSON with this structure:
{{
  "title": "...",
  "yes_price": 0.65,
  "no_price": 0.35,
  "volume": "$10.5M",
  "liquidity": "$500K",
  "traders": 1234,
  "end_date": "2024-11-05",
  "description": "...",
  "recent_activity": "Price moved from 60¢ to 65¢ in last 24h",
  "url": "{market_url}"
}}
""",
            llm=self.llm,
            browser=browser,
            use_vision=True
        )
        
        try:
            history = await agent.run(max_steps=10)
            result = history.final_result()
            
            if result:
                try:
                    result_str = str(result)
                    
                    # Find JSON object
                    start_idx = result_str.find('{')
                    end_idx = result_str.rfind('}') + 1
                    
                    if start_idx >= 0 and end_idx > start_idx:
                        json_str = result_str[start_idx:end_idx]
                        market_data = json.loads(json_str)
                        
                        print(f"✅ Got detailed data for: {market_data.get('title', 'Unknown')}")
                        return market_data
                    else:
                        print(f"⚠️  No JSON found in result")
                        return None
                        
                except json.JSONDecodeError as e:
                    print(f"⚠️  Failed to parse JSON: {e}")
                    return None
            else:
                print(f"⚠️  No result from agent")
                return None
                
        except Exception as e:
            print(f"❌ Error getting market data: {e}")
            import traceback
            traceback.print_exc()
            return None
        finally:
            await browser.close()
    
    async def search_markets(self, query: str, limit: int = 5) -> List[PolymarketMarket]:
        """
        Search for markets matching a query.
        
        Args:
            query: Search query (e.g., "Trump", "Bitcoin", "Climate")
            limit: Maximum number of results
            
        Returns:
            List of matching markets
        """
        print(f"\n🔍 Searching Polymarket for: {query}")
        
        browser = Browser(headless=self.headless)
        
        agent = Agent(
            task=f"""Go to https://polymarket.com and search for markets related to "{query}".

Find the top {limit} most relevant active markets and extract:
1. Market title/question
2. Current YES price (as decimal)
3. Current NO price (as decimal)
4. Total volume
5. URL to the market

Return as JSON array:
[
  {{
    "title": "...",
    "url": "https://polymarket.com/event/...",
    "yes_price": 0.65,
    "no_price": 0.35,
    "volume": "$10.5M"
  }},
  ...
]

Only return active markets (not resolved).
Sort by relevance to the query "{query}".
""",
            llm=self.llm,
            browser=browser,
            use_vision=True
        )
        
        try:
            history = await agent.run(max_steps=12)
            result = history.final_result()
            
            if result:
                try:
                    result_str = str(result)
                    start_idx = result_str.find('[')
                    end_idx = result_str.rfind(']') + 1
                    
                    if start_idx >= 0 and end_idx > start_idx:
                        json_str = result_str[start_idx:end_idx]
                        markets_data = json.loads(json_str)
                        
                        markets = []
                        for market_data in markets_data:
                            try:
                                market = PolymarketMarket(**market_data)
                                markets.append(market)
                            except Exception as e:
                                print(f"⚠️  Could not parse market: {e}")
                                continue
                        
                        print(f"✅ Found {len(markets)} markets for '{query}'")
                        return markets
                    else:
                        print(f"⚠️  No JSON array found")
                        return []
                        
                except json.JSONDecodeError as e:
                    print(f"⚠️  Failed to parse JSON: {e}")
                    return []
            else:
                print(f"⚠️  No result from agent")
                return []
                
        except Exception as e:
            print(f"❌ Error searching markets: {e}")
            import traceback
            traceback.print_exc()
            return []
        finally:
            await browser.close()


async def main():
    """Test the discovery system."""
    discovery = PolymarketDiscovery(headless=True)
    
    print("\n" + "="*60)
    print("🎯 POLYMARKET DISCOVERY TEST")
    print("="*60)
    
    # Test 1: Discover trending markets
    print("\n📊 Test 1: Discover Trending Markets")
    trending = await discovery.discover_trending_markets(limit=5)
    
    if trending:
        print(f"\n✅ Found {len(trending)} trending markets:")
        for i, market in enumerate(trending, 1):
            print(f"\n{i}. {market.title}")
            print(f"   YES: ${market.yes_price:.2f} | NO: ${market.no_price:.2f}")
            if market.volume:
                print(f"   Volume: {market.volume}")
            if market.url:
                print(f"   URL: {market.url}")
    
    # Test 2: Search for specific markets
    print("\n\n📊 Test 2: Search for 'Trump' markets")
    search_results = await discovery.search_markets("Trump", limit=3)
    
    if search_results:
        print(f"\n✅ Found {len(search_results)} Trump markets:")
        for i, market in enumerate(search_results, 1):
            print(f"\n{i}. {market.title}")
            print(f"   YES: ${market.yes_price:.2f} | NO: ${market.no_price:.2f}")
    
    print("\n" + "="*60)
    print("✅ Discovery test complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
