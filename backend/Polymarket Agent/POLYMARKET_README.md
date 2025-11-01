# Polymarket Data Collector for Betting Decisions

This system consists of two components:
1. **Data Collector Agent** - Collects structured data from Polymarket about specific trades/markets
2. **Decision Agent** - Uses the collected data to make betting decisions

## Setup

1. **Install dependencies**:
   ```bash
   pip install browser-use python-dotenv pydantic httpx hyperspell
   ```

2. **Set your API keys** in `.env` file:
   ```
   BROWSER_USE_API_KEY=your_browser_use_api_key_here
   PERPLEXITY_API_KEY=your_perplexity_api_key_here
   REPLIT_API_KEY=your_replit_api_key_here  # Optional, for Replit integration
   HYPERSPELL_API_KEY=your_hyperspell_api_key_here  # For learning from past decisions
   ```
   
   - Browser-Use API key: https://cloud.browser-use.com/new-api-key
   - Perplexity API key: https://www.perplexity.ai/settings/api
   - Replit API key: https://replit.com/account/api-keys (optional)
   - Hyperspell API key: https://hyperspell.com (for learning)

## Usage

### Step 1: Collect Market Data

The data collector agent navigates to Polymarket and extracts structured information about a market.

#### Option 1: Collect by Market URL
```bash
python polymarket_collector.py --market-url "https://polymarket.com/event/your-market-id"
```

#### Option 2: Collect by Market ID
```bash
python polymarket_collector.py --market-id "your-market-id"
```

#### Option 3: Search for a Market
```bash
python polymarket_collector.py --query "Will Biden win the election?"
```

#### Options:
- `--output` - Output JSON file path (default: `polymarket_data.json`)
- `--headless` - Run browser in headless mode
- `--model` - LLM model to use (e.g., `gpt-4`, `gpt-4o-mini`)

#### Example:
```bash
python polymarket_collector.py --query "2024 US Presidential Election" --output election_data.json
```

### Step 2: Make Betting Decision

After collecting data, use the decision agent to analyze and make betting decisions:

#### Local Analysis:
```bash
python polymarket_decision_example.py
```

#### Using Replit (if deployed):
```bash
python polymarket_decision_example.py --replit
```

This will:
1. Load the most recent data from `polymarket_data.json`
2. Analyze the market data (locally or via Replit)
3. Make a betting decision (buy/sell/hold/no_action)
4. Save the decision to `betting_decision.json`

See [REPLIT_DEPLOYMENT.md](./REPLIT_DEPLOYMENT.md) for details on deploying to Replit.

## Data Structure

### Collected Market Data

The collector extracts the following information:

```json
{
  "market_id": "unique-market-id",
  "market_url": "https://polymarket.com/event/...",
  "market_title": "Market question/title",
  "market_category": "Politics/Elections/etc",
  "outcomes": ["Option 1", "Option 2"],
  "current_prices": {
    "Option 1": 0.65,
    "Option 2": 0.35
  },
  "total_volume": 12345.67,
  "liquidity": 5678.90,
  "number_of_traders": 1234,
  "end_date": "2024-11-05",
  "time_remaining": "30 days",
  "status": "active",
  "resolution": null,
  "description": "Market description...",
  "recent_activity": "Recent trading activity...",
  "perplexity_research": {
    "content": "Additional context from Perplexity...",
    "citations": ["url1", "url2"],
    "model": "llama-3.1-sonar-large-128k-online"
  },
  "market_context": "Contextual information from Perplexity...",
  "collected_at": "2024-01-01T12:00:00"
}
```

### Decision Output

The decision agent outputs:

```json
{
  "market_id": "unique-market-id",
  "decision": "buy|sell|hold|no_action",
  "outcome": "Option to bet on",
  "confidence": 0.75,
  "reasoning": "Detailed reasoning for the decision",
  "suggested_position_size": 50.00,
  "risk_assessment": "low|medium|high",
  "price_discrepancy": 0.05,
  "value_opportunity": true,
  "past_decisions_used": [
    {
      "text": "Previous decision text...",
      "score": 0.85
    }
  ],
  "learning_insights": "Based on 5 past similar decisions: 70.0% success rate. Similar markets have been profitable.",
  "analyzed_at": "2024-01-01T12:00:00",
  "analysis_method": "local|replit"
}
```

## Features

### Data Collection with Perplexity

The collector now automatically queries Perplexity API to gather additional context about the market topic:
- Latest news and analysis
- Research citations
- Contextual information for better decision-making

Set `PERPLEXITY_API_KEY` in your `.env` file to enable this feature.

### Decision Making with Replit

The decision agent can use Replit for analysis:
- Deploy the decision agent to Replit
- Use Replit's API for code execution
- Or run directly on Replit platform

See [REPLIT_DEPLOYMENT.md](./REPLIT_DEPLOYMENT.md) for deployment instructions.

### Learning with Hyperspell

The decision agent uses Hyperspell to remember and learn from past decisions:
- Automatically queries past similar decisions before making new ones
- Adjusts confidence and strategy based on historical success rates
- Stores all decisions for future learning
- Tracks decision outcomes to improve over time

Set `HYPERSPELL_API_KEY` in your `.env` file to enable learning.

## Customizing the Decision Agent

The `polymarket_decision_example.py` includes a simple decision-making strategy as an example. To customize:

1. **Replace the decision logic** in `analyze_market_for_betting()`:
   - Add your own ML models
   - Implement statistical analysis
   - Use historical data
   - Apply your betting strategy

2. **Customize Replit integration** in `analyze_with_replit()`:
   - Adjust based on Replit's actual API endpoints
   - Add custom analysis code
   - Use Replit's models or code execution

3. **Add additional analysis**:
   - Price movement trends
   - Volume analysis
   - Market sentiment
   - Historical market performance
   - Use Perplexity research data

## Integration Example

Here's how to use both agents together programmatically:

```python
import asyncio
from polymarket_collector import collect_market_data, PolymarketTradeData
from polymarket_decision_example import analyze_market_for_betting, BettingDecision

async def collect_and_decide(market_url: str):
    # Step 1: Collect data
    market_data = await collect_market_data(
        market_identifier=market_url,
        method='url',
        headless=True
    )
    
    # Step 2: Make decision
    decision = analyze_market_for_betting(market_data.model_dump())
    
    # Step 3: Use decision (place bet, update strategy, etc.)
    print(f"Decision: {decision.decision}")
    print(f"Reasoning: {decision.reasoning}")
    
    return decision

# Run
asyncio.run(collect_and_decide("https://polymarket.com/event/..."))
```

## Tips

1. **Data Collection**: Run the collector periodically to get updated market data
2. **Decision Timing**: Make decisions based on fresh data
3. **Risk Management**: Use the `suggested_position_size` and `risk_assessment` fields
4. **Multiple Markets**: Collect data for multiple markets and compare opportunities
5. **Historical Data**: Store historical decisions to improve your model

## Next Steps

1. **Enhance the decision logic**: Replace the simple example with your own ML model
2. **Add more data sources**: Combine Polymarket data with news, social media, etc.
3. **Backtesting**: Test your decision strategy on historical data
4. **Automation**: Set up automated data collection and decision-making
5. **Portfolio Management**: Track multiple positions and manage risk

## Notes

- The collector uses Browser-Use to navigate Polymarket and extract data
- Prices are returned as decimals (0-1 range), where 0.65 means 65% probability
- The decision agent is just an example - customize it with your own strategy
- Always validate data before making real trading decisions
- This is for educational purposes - implement proper risk management

