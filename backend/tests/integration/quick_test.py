#!/usr/bin/env python3
"""Quick API test"""
import httpx
import asyncio

async def test():
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                "http://localhost:8000/api/run-task",
                json={
                    "task": "Go to example.com",
                    "max_steps": 2,
                    "headless": True
                }
            )
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            if response.status_code == 200:
                print(f"JSON: {response.json()}")
        except Exception as e:
            print(f"Error: {e}")

asyncio.run(test())
