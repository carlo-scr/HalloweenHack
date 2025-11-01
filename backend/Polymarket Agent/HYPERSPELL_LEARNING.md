# Hyperspell Learning Integration

The Polymarket decision agent uses Hyperspell to remember and learn from previous decisions, improving over time.

## How It Works

### 1. Storing Decisions

After making each betting decision, the agent automatically stores:
- Market information
- Decision made (buy/sell/hold)
- Confidence level
- Reasoning
- Market prices and statistics
- Timestamp

All decisions are stored in the `betting_decisions` collection in Hyperspell.

### 2. Learning from Past Decisions

Before making a new decision, the agent:
- Queries Hyperspell for similar past decisions
- Analyzes success rates of similar markets
- Adjusts confidence based on historical performance
- Incorporates learning insights into reasoning

### 3. Tracking Outcomes

After markets resolve, you can update decision outcomes:
- Mark decisions as correct/incorrect
- Record actual returns
- Store outcomes for future learning

## Usage

### Automatic Learning

The agent automatically learns when `HYPERSPELL_API_KEY` is set:

```bash
# Make a decision (automatically learns from past)
python polymarket_decision_example.py
```

The agent will:
1. Query past similar decisions from Hyperspell
2. Analyze historical success rates
3. Make a decision incorporating learnings
4. Store the new decision for future learning

### Updating Decision Outcomes

After a market resolves, update the outcome to improve learning:

```python
from polymarket_decision_example import update_decision_outcome, get_hyperspell_client

hyperspell_client = get_hyperspell_client()

# Update outcome when market resolves
await update_decision_outcome(
    hyperspell_client=hyperspell_client,
    decision_id="decision-123",
    was_correct=True,
    actual_outcome="Option A won",
    actual_return=25.5  # 25.5% return
)
```

## Learning Adjustments

The agent automatically adjusts based on past decisions:

### Confidence Adjustment
- **High success rate (>60%)**: Increases confidence by +0.1
- **Low success rate (<40%)**: Decreases confidence by -0.1
- **Medium success rate**: No adjustment

### Strategy Thresholds
- **Profitable markets**: Lowers buy threshold (more aggressive)
- **Poor performing markets**: Raises buy threshold (more conservative)

### Learning Insights

The agent includes learning insights in the reasoning:

```
Based on 5 past similar decisions: 70.0% success rate. 
Similar markets have been profitable.
```

## Query Examples

### Find Similar Past Decisions

```python
from polymarket_decision_example import query_past_decisions, get_hyperspell_client

hyperspell_client = get_hyperspell_client()

past_decisions = await query_past_decisions(
    hyperspell_client=hyperspell_client,
    market_title="2024 US Presidential Election",
    market_category="Politics",
    limit=10
)

for decision in past_decisions:
    print(f"Score: {decision['score']}")
    print(f"Text: {decision['text']}")
```

## Data Structure

### Stored Decision Format

Each decision is stored as:

```
Betting decision on market {market_id}:
Market: {market_title}
Category: {market_category}
Decision: buy|sell|hold|no_action
Outcome: {outcome}
Confidence: {confidence}%
Reasoning: {reasoning}
Risk: {risk_assessment}
Value Opportunity: {value_opportunity}
Prices: {current_prices}
Timestamp: {iso_timestamp}
```

### Outcome Update Format

```
Decision outcome for {decision_id}:
Result: CORRECT|INCORRECT
Actual Outcome: {actual_outcome}
Return: {return}%
Updated: {iso_timestamp}
```

## Best Practices

1. **Regular Updates**: Update decision outcomes regularly for better learning
2. **Relevant Categories**: Use specific market categories for better matching
3. **Track Returns**: Record actual returns to learn from profitability
4. **Review Insights**: Check learning insights to understand decision adjustments

## Integration Example

```python
import asyncio
from polymarket_decision_example import (
    analyze_market_for_betting,
    store_decision,
    update_decision_outcome,
    get_hyperspell_client
)

async def full_cycle():
    # Get Hyperspell client
    hyperspell_client = get_hyperspell_client()
    
    # Load market data
    with open('polymarket_data.json') as f:
        market_data = json.load(f)[-1]
    
    # Make decision (learns from past)
    decision = await analyze_market_for_betting(
        market_data,
        hyperspell_client
    )
    
    # Store decision
    await store_decision(hyperspell_client, decision, market_data)
    
    # ... wait for market to resolve ...
    
    # Update outcome when resolved
    await update_decision_outcome(
        hyperspell_client,
        decision_id=decision.market_id,
        was_correct=True,
        actual_outcome="Option A",
        actual_return=15.5
    )

asyncio.run(full_cycle())
```

## Benefits

- **Improved Accuracy**: Learns from past successes and failures
- **Adaptive Confidence**: Adjusts based on historical performance
- **Risk Management**: More conservative after poor results
- **Pattern Recognition**: Identifies profitable market patterns

## Notes

- Decisions are stored in the `betting_decisions` collection
- Outcomes are stored in the `decision_outcomes` collection
- Similarity matching uses market title and category
- Learning happens automatically when Hyperspell is enabled

