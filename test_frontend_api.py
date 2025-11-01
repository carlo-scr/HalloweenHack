#!/usr/bin/env python3
"""
Test the exact API call the frontend makes
"""
import asyncio
import httpx

async def test_frontend_call():
    """Simulate what the frontend does"""
    
    print("🧪 Testing Frontend → Backend Connection\n")
    
    # This is the exact call the frontend makes
    url = "http://localhost:8000/api/run-task"
    
    payload = {
        "task": "Go to example.com and get the page title",
        "max_steps": 5,
        "headless": True,
        "use_vision": True
    }
    
    headers = {
        "Content-Type": "application/json",
        "Origin": "http://localhost:8080"  # Simulating browser origin
    }
    
    print(f"📤 POST {url}")
    print(f"   Payload: {payload}")
    print(f"   Headers: {headers}\n")
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            # First, test OPTIONS (CORS preflight)
            print("1️⃣  Testing CORS preflight (OPTIONS)...")
            options_response = await client.options(
                url,
                headers={
                    "Origin": "http://localhost:8080",
                    "Access-Control-Request-Method": "POST",
                    "Access-Control-Request-Headers": "Content-Type"
                }
            )
            print(f"   Status: {options_response.status_code}")
            print(f"   CORS Headers: {dict(options_response.headers)}\n")
            
            if options_response.status_code != 200:
                print("❌ CORS preflight failed!")
                return False
            
            print("✅ CORS preflight passed!\n")
            
            # Now test actual POST request
            print("2️⃣  Testing actual POST request...")
            response = await client.post(
                url,
                json=payload,
                headers=headers
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"\n✅ SUCCESS!")
                print(f"   Task: {data.get('task')}")
                print(f"   Success: {data.get('success')}")
                print(f"   Steps: {data.get('steps_taken')}")
                print(f"   Result: {data.get('final_result')}")
                return True
            else:
                print(f"\n❌ FAILED!")
                print(f"   Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_frontend_call())
    exit(0 if success else 1)
