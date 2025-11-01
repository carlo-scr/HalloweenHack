#!/usr/bin/env python3
"""
Force an immediate trade analysis to test the system.
"""

import asyncio
import requests

# Test the multi-agent analysis endpoint directly
async def test_analysis():
    print("\n🧪 Testing Multi-Agent Analysis Endpoint")
    print("="*60)
    
    url = "http://localhost:8000/api/polymarket/analyze"
    payload = {"market_query": "Trump 2024"}
    
    print(f"📤 Sending request to: {url}")
    print(f"📦 Payload: {payload}")
    
    try:
        response = requests.post(url, json=payload)
        print(f"\n📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Analysis Successful!")
            print(f"\n📋 Decision:")
            print(f"   Recommendation: {data.get('final_recommendation')}")
            print(f"   Confidence: {data.get('overall_confidence', 0)*100:.1f}%")
            print(f"   Consensus: {data.get('consensus_level', 0)*100:.1f}%")
            print(f"   Suggested Bet: ${data.get('suggested_bet_size', 0):.2f}")
            
            print(f"\n🤖 Agent Decisions:")
            for agent in data.get('agent_decisions', []):
                print(f"   - {agent['agent_name']}: {agent['recommendation']} ({agent['confidence']*100:.0f}%)")
                print(f"     {agent['reasoning'][:100]}...")
            
            print(f"\n✅ Supporting Factors:")
            for factor in data.get('supporting_factors', [])[:3]:
                print(f"   • {factor}")
            
            print(f"\n⚠️  Risk Factors:")
            for factor in data.get('risk_factors', [])[:3]:
                print(f"   • {factor}")
        else:
            print(f"\n❌ Request failed")
            print(f"Response: {response.text}")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_analysis())
