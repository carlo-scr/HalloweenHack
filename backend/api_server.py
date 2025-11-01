#!/usr/bin/env python3
"""
Polymarket API Server

Flask/FastAPI server exposing endpoints for Polymarket data collection
and decision-making. Can be used with any frontend framework.

Usage:
    python api_server.py
    
Endpoints:
    POST /api/collect - Collect market data
    POST /api/decide - Make betting decision
    GET /api/decisions - Get all decisions
    GET /api/markets - Get all collected markets
    POST /api/outcome - Update decision outcome
    GET /api/health - Health check
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Optional

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS

# Load environment variables
load_dotenv()

# Import our modules
from polymarket_collector import (
	collect_market_data,
	save_data,
	display_data,
	PolymarketTradeData,
)
from polymarket_decision_example import (
	analyze_market_for_betting,
	store_decision,
	get_hyperspell_client,
	update_decision_outcome,
)

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

# Data storage (in production, use a database)
markets_data = []
decisions_data = []


def run_async(coro):
	"""Run async function in Flask."""
	loop = asyncio.new_event_loop()
	asyncio.set_event_loop(loop)
	return loop.run_until_complete(coro)


@app.route('/api/health', methods=['GET'])
def health():
	"""Health check endpoint."""
	return jsonify({
		'status': 'ok',
		'service': 'Polymarket API Server',
		'timestamp': datetime.now().isoformat(),
	})


@app.route('/api/collect', methods=['POST'])
def collect_market():
	"""
	Collect market data from Polymarket.
	
	Request body:
	{
		"market_identifier": "search query or URL",
		"method": "search|url|id",
		"headless": true
	}
	"""
	try:
		data = request.json
		market_identifier = data.get('market_identifier')
		method = data.get('method', 'search')
		headless = data.get('headless', True)
		
		if not market_identifier:
			return jsonify({'error': 'market_identifier is required'}), 400
		
		# Collect market data
		market_data = run_async(
			collect_market_data(
				market_identifier=market_identifier,
				method=method,
				headless=headless,
			)
		)
		
		# Save to file
		run_async(save_data(market_data, 'polymarket_data.json'))
		
		# Store in memory
		market_dict = market_data.model_dump()
		markets_data.append(market_dict)
		
		return jsonify({
			'success': True,
			'data': market_dict,
			'message': 'Market data collected successfully',
		}), 200
		
	except Exception as e:
		return jsonify({
			'success': False,
			'error': str(e),
		}), 500


@app.route('/api/decide', methods=['POST'])
def make_decision():
	"""
	Make a betting decision based on market data.
	
	Request body:
	{
		"market_id": "market-id",  # Optional, uses latest if not provided
		"use_replit": false,       # Optional, use Replit for analysis
		"market_data": {...}      # Optional, use provided market data
	}
	"""
	try:
		data = request.json or {}
		market_id = data.get('market_id')
		use_replit = data.get('use_replit', False)
		provided_market_data = data.get('market_data')
		
		# Get market data
		if provided_market_data:
			market_data_dict = provided_market_data
		elif market_id:
			# Find market by ID
			market_data_dict = next(
				(m for m in markets_data if m.get('market_id') == market_id),
				None
			)
			if not market_data_dict:
				# Try loading from file
				try:
					with open('polymarket_data.json', 'r') as f:
						all_markets = json.load(f)
						market_data_dict = next(
							(m for m in all_markets if m.get('market_id') == market_id),
							None
						)
				except Exception:
					pass
		else:
			# Use latest market data
			try:
				with open('polymarket_data.json', 'r') as f:
					all_markets = json.load(f)
					market_data_dict = all_markets[-1] if all_markets else None
			except Exception:
				market_data_dict = markets_data[-1] if markets_data else None
		
		if not market_data_dict:
			return jsonify({
				'success': False,
				'error': 'No market data found. Collect market data first.',
			}), 404
		
		# Get Hyperspell client
		hyperspell_client = get_hyperspell_client()
		
		# Make decision
		if use_replit:
			from polymarket_decision_example import analyze_with_replit
			decision = run_async(
				analyze_with_replit(market_data_dict)
			)
		else:
			decision = run_async(
				analyze_market_for_betting(market_data_dict, hyperspell_client)
			)
		
		# Store decision in Hyperspell
		if hyperspell_client:
			run_async(store_decision(hyperspell_client, decision, market_data_dict))
		
		# Save decision
		decision_dict = decision.model_dump()
		decision_dict['analyzed_at'] = datetime.now().isoformat()
		decision_dict['analysis_method'] = 'replit' if use_replit else 'local'
		
		decisions_data.append(decision_dict)
		
		# Save to file
		try:
			with open('betting_decision.json', 'r') as f:
				all_decisions = json.load(f)
		except Exception:
			all_decisions = []
		
		all_decisions.append(decision_dict)
		
		with open('betting_decision.json', 'w') as f:
			json.dump(all_decisions, f, indent=2, ensure_ascii=False)
		
		return jsonify({
			'success': True,
			'decision': decision_dict,
			'market_data': market_data_dict,
			'message': 'Decision made successfully',
		}), 200
		
	except Exception as e:
		return jsonify({
			'success': False,
			'error': str(e),
		}), 500


@app.route('/api/decisions', methods=['GET'])
def get_decisions():
	"""Get all decisions."""
	try:
		# Try loading from file
		try:
			with open('betting_decision.json', 'r') as f:
				all_decisions = json.load(f)
		except Exception:
			all_decisions = decisions_data
		
		# Get query parameters
		limit = request.args.get('limit', type=int)
		market_id = request.args.get('market_id')
		
		if market_id:
			all_decisions = [d for d in all_decisions if d.get('market_id') == market_id]
		
		if limit:
			all_decisions = all_decisions[-limit:]
		
		return jsonify({
			'success': True,
			'decisions': all_decisions,
			'count': len(all_decisions),
		}), 200
		
	except Exception as e:
		return jsonify({
			'success': False,
			'error': str(e),
		}), 500


@app.route('/api/markets', methods=['GET'])
def get_markets():
	"""Get all collected markets."""
	try:
		# Try loading from file
		try:
			with open('polymarket_data.json', 'r') as f:
				all_markets = json.load(f)
		except Exception:
			all_markets = markets_data
		
		# Get query parameters
		limit = request.args.get('limit', type=int)
		category = request.args.get('category')
		
		if category:
			all_markets = [m for m in all_markets if m.get('market_category') == category]
		
		if limit:
			all_markets = all_markets[-limit:]
		
		return jsonify({
			'success': True,
			'markets': all_markets,
			'count': len(all_markets),
		}), 200
		
	except Exception as e:
		return jsonify({
			'success': False,
			'error': str(e),
		}), 500


@app.route('/api/outcome', methods=['POST'])
def update_outcome():
	"""
	Update decision outcome after market resolves.
	
	Request body:
	{
		"decision_id": "market-id",
		"was_correct": true,
		"actual_outcome": "Option A won",
		"actual_return": 25.5
	}
	"""
	try:
		data = request.json
		decision_id = data.get('decision_id')
		was_correct = data.get('was_correct')
		actual_outcome = data.get('actual_outcome')
		actual_return = data.get('actual_return')
		
		if not decision_id:
			return jsonify({'error': 'decision_id is required'}), 400
		
		# Update in Hyperspell
		hyperspell_client = get_hyperspell_client()
		if hyperspell_client:
			success = run_async(
				update_decision_outcome(
					hyperspell_client,
					decision_id,
					was_correct,
					actual_outcome,
					actual_return,
				)
			)
			
			if success:
				return jsonify({
					'success': True,
					'message': 'Outcome updated in Hyperspell',
				}), 200
			else:
				return jsonify({
					'success': False,
					'error': 'Failed to update outcome in Hyperspell',
				}), 500
		else:
			return jsonify({
				'success': False,
				'error': 'Hyperspell not configured',
			}), 400
		
	except Exception as e:
		return jsonify({
			'success': False,
			'error': str(e),
		}), 500


@app.route('/api/collect-and-decide', methods=['POST'])
def collect_and_decide():
	"""
	Collect market data and make decision in one call.
	
	Request body:
	{
		"market_identifier": "search query or URL",
		"method": "search|url|id",
		"use_replit": false,
		"headless": true
	}
	"""
	try:
		data = request.json
		market_identifier = data.get('market_identifier')
		method = data.get('method', 'search')
		use_replit = data.get('use_replit', False)
		headless = data.get('headless', True)
		
		if not market_identifier:
			return jsonify({'error': 'market_identifier is required'}), 400
		
		# Step 1: Collect market data
		market_data = run_async(
			collect_market_data(
				market_identifier=market_identifier,
				method=method,
				headless=headless,
			)
		)
		
		# Save market data
		run_async(save_data(market_data, 'polymarket_data.json'))
		market_dict = market_data.model_dump()
		markets_data.append(market_dict)
		
		# Step 2: Make decision
		hyperspell_client = get_hyperspell_client()
		
		if use_replit:
			from polymarket_decision_example import analyze_with_replit
			decision = run_async(
				analyze_with_replit(market_dict)
			)
		else:
			decision = run_async(
				analyze_market_for_betting(market_dict, hyperspell_client)
			)
		
		# Store decision
		if hyperspell_client:
			run_async(store_decision(hyperspell_client, decision, market_dict))
		
		decision_dict = decision.model_dump()
		decision_dict['analyzed_at'] = datetime.now().isoformat()
		decision_dict['analysis_method'] = 'replit' if use_replit else 'local'
		
		decisions_data.append(decision_dict)
		
		# Save decision
		try:
			with open('betting_decision.json', 'r') as f:
				all_decisions = json.load(f)
		except Exception:
			all_decisions = []
		
		all_decisions.append(decision_dict)
		
		with open('betting_decision.json', 'w') as f:
			json.dump(all_decisions, f, indent=2, ensure_ascii=False)
		
		return jsonify({
			'success': True,
			'market': market_dict,
			'decision': decision_dict,
			'message': 'Market data collected and decision made successfully',
		}), 200
		
	except Exception as e:
		return jsonify({
			'success': False,
			'error': str(e),
		}), 500


if __name__ == '__main__':
	print("🚀 Starting Polymarket API Server...")
	print("📡 API endpoints:")
	print("   POST /api/collect - Collect market data")
	print("   POST /api/decide - Make betting decision")
	print("   GET  /api/decisions - Get all decisions")
	print("   GET  /api/markets - Get all markets")
	print("   POST /api/outcome - Update decision outcome")
	print("   POST /api/collect-and-decide - Collect and decide in one call")
	print("   GET  /api/health - Health check")
	print("\n🌐 Server will start on http://localhost:5000")
	print("   Frontend can access API at: http://localhost:5000/api/*\n")
	
	app.run(host='0.0.0.0', port=5000, debug=True)

