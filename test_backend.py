#!/usr/bin/env python3
"""
Test script for Browser-Use Backend
Tests the agent and API functionality
"""

import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

async def test_basic_agent():
    """Test basic browser-use agent functionality."""
    print("🧪 Testing Browser-Use Agent...")
    
    try:
        from browser_use import Agent, Browser, ChatBrowserUse
        from dotenv import load_dotenv
        
        # Load environment
        load_dotenv(backend_dir / ".env")
        
        # Check API key
        api_key = os.getenv("BROWSER_USE_API_KEY")
        if not api_key:
            print("❌ BROWSER_USE_API_KEY not found in backend/.env")
            return False
        
        print(f"✅ API Key found: {api_key[:10]}...")
        
        # Create LLM
        print("📝 Creating ChatBrowserUse LLM...")
        llm = ChatBrowserUse()
        print("✅ LLM created successfully")
        
        # Create browser
        print("🌐 Creating browser (headless mode)...")
        browser = Browser(headless=True)
        print("✅ Browser created successfully")
        
        # Create agent
        print("🤖 Creating agent...")
        agent = Agent(
            task="Go to example.com and tell me the page title",
            llm=llm,
            browser=browser,
            use_vision=True
        )
        print("✅ Agent created successfully")
        
        # Run agent
        print("\n🚀 Running agent (max 3 steps)...\n")
        history = await agent.run(max_steps=3)
        
        # Get results
        final_result = history.final_result()
        urls_visited = history.urls()
        steps = history.number_of_steps()
        
        print("\n" + "="*60)
        print("📊 RESULTS:")
        print("="*60)
        print(f"✅ Steps taken: {steps}")
        print(f"✅ URLs visited: {urls_visited}")
        print(f"✅ Final result: {final_result}")
        print("="*60 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_api_health():
    """Test API health endpoint."""
    print("\n🧪 Testing API Health Endpoint...")
    
    try:
        import httpx
        
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/health")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API Health: {data}")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Could not connect to API: {e}")
        print("💡 Make sure the backend is running: make start-backend")
        return False

async def test_api_task():
    """Test API task endpoint."""
    print("\n🧪 Testing API Task Endpoint...")
    
    try:
        import httpx
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            task_data = {
                "task": "Go to example.com",
                "max_steps": 2,
                "headless": True
            }
            
            print(f"📤 Sending task: {task_data['task']}")
            response = await client.post(
                "http://localhost:8000/api/run-task",
                json=task_data
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Task completed!")
                print(f"   Success: {data.get('success')}")
                print(f"   Steps: {data.get('steps_taken')}")
                print(f"   URLs: {data.get('urls_visited')}")
                print(f"   Result: {data.get('final_result')}")
                return True
            else:
                print(f"❌ Task failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ API error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("🎃 HALLOWEENHACK - BACKEND TEST SUITE")
    print("="*60 + "\n")
    
    # Test 1: Direct agent test
    print("TEST 1: Direct Browser-Use Agent")
    print("-" * 60)
    agent_ok = await test_basic_agent()
    
    # Test 2: API health
    print("\nTEST 2: API Health Check")
    print("-" * 60)
    health_ok = await test_api_health()
    
    # Test 3: API task (only if health passed)
    if health_ok:
        print("\nTEST 3: API Task Execution")
        print("-" * 60)
        task_ok = await test_api_task()
    else:
        print("\n⏭️  Skipping API task test (health check failed)")
        task_ok = False
    
    # Summary
    print("\n" + "="*60)
    print("📋 TEST SUMMARY")
    print("="*60)
    print(f"Direct Agent:     {'✅ PASS' if agent_ok else '❌ FAIL'}")
    print(f"API Health:       {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"API Task:         {'✅ PASS' if task_ok else '❌ FAIL'}")
    print("="*60 + "\n")
    
    if all([agent_ok, health_ok, task_ok]):
        print("🎉 ALL TESTS PASSED!")
        return 0
    else:
        print("⚠️  SOME TESTS FAILED - Check errors above")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
