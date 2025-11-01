#!/usr/bin/env python3
"""
Quick test to verify Polymarket data collection works
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend", "Polymarket Agent"))

from dotenv import load_dotenv
load_dotenv("backend/.env")

async def test_polymarket():
    """Test Polymarket data collection"""
    
    print("🧪 Testing Polymarket Data Collection\n")
    
    try:
        from polymarket_collector import collect_market_data
        
        print("📊 Collecting data from Polymarket...")
        print("   Method: Search for trending markets\n")
        
        # Test with a search query
        market_data = await collect_market_data(
            market_identifier="Trump 2024",
            method='search',
            headless=True
        )
        
        print("✅ Data collected successfully!\n")
        print("=" * 60)
        print("MARKET DATA:")
        print("=" * 60)
        print(f"📌 Title: {market_data.market_title}")
        print(f"🔗 URL: {market_data.market_url}")
        print(f"📊 Status: {market_data.status}")
        print(f"\n💰 Outcomes & Prices:")
        for outcome, price in market_data.current_prices.items():
            print(f"   • {outcome}: {price:.2%}")
        
        if market_data.total_volume:
            print(f"\n📈 Total Volume: ${market_data.total_volume:,.2f}")
        if market_data.number_of_traders:
            print(f"👥 Traders: {market_data.number_of_traders:,}")
        
        print("\n" + "=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_polymarket())
    sys.exit(0 if success else 1)
