# 🤖 Multi-Agent Trading Decision System

## 🎯 Concept: Collaborative AI Agents

Instead of one agent making decisions, you have **multiple specialized agents** that:
1. Each analyze different aspects of a trade
2. Share their findings and confidence levels
3. Vote on the final recommendation
4. Provide collective intelligence

---

## 🏗️ System Architecture

```
User Request
    ↓
Decision Coordinator
    ↓
    ├─→ Data Collector Agent (validates data quality)
    ├─→ Odds Analyzer Agent (finds value bets)
    ├─→ Research Agent (gathers news/context)
    ├─→ Sentiment Agent (checks social sentiment)
    ↓
Aggregate Results
    ↓
Final Recommendation
```

---

## 🤖 The Agents

### 1. **Data Collector Agent**
- **Role**: Gathers and validates market data
- **Checks**:
  - Trading volume (is it liquid enough?)
  - Data completeness
  - Market anomalies
- **Output**: Data quality score + red flags

### 2. **Odds Analyzer Agent**
- **Role**: Mathematical analysis of probabilities
- **Analyzes**:
  - Current odds vs fair value
  - Market margins (vig)
  - Price inefficiencies
- **Output**: Value bet opportunities

### 3. **Research Agent** (Optional - slower)
- **Role**: Gathers external context
- **Searches**:
  - Google News for recent developments
  - Expert predictions
  - Key events affecting outcome
- **Output**: Supporting/contradicting evidence

### 4. **Sentiment Agent** (Optional - slower)
- **Role**: Public opinion analysis
- **Checks**:
  - Twitter sentiment
  - Reddit discussions
  - Influencer opinions
- **Output**: Bullish/bearish sentiment

---

## 📊 How Decisions Are Made

### Individual Agent Analysis:
Each agent returns:
```python
{
  "agent_name": "Odds Analyzer",
  "confidence": 0.75,  # 75% confident
  "recommendation": "YES",
  "reasoning": "Current odds undervalue this outcome",
  "key_factors": [
    "Trading at 0.45 but should be 0.60",
    "Low market margin of 2%"
  ]
}
```

### Aggregation Process:
1. **Vote Count**: Count YES/NO/SKIP votes
2. **Confidence Weighting**: Weight votes by confidence
3. **Consensus Calculation**: How much do agents agree?
4. **Final Decision**: Weighted majority wins

### Output Example:
```json
{
  "final_recommendation": "YES",
  "aggregate_confidence": 0.72,
  "consensus_level": 0.85,  // 85% of agents agree
  "suggested_bet_size": 8.5,  // % of bankroll
  "supporting_factors": [
    "High trading volume: $500,000",
    "Current odds undervalued by 15%",
    "Positive news sentiment"
  ],
  "risk_factors": [
    "Low liquidity might cause slippage"
  ]
}
```

---

## 🚀 How to Use

### Method 1: Direct Python Script

```bash
cd backend
source .venv/bin/activate
python multi_agent_decision.py
```

This will:
1. Search for "Trump 2024" market
2. Run all agents
3. Display individual agent decisions
4. Show final collective decision
5. Save result to `decision.json`

### Method 2: Via API (NEW!)

```bash
# Start backend
make start-backend

# Analyze a market
curl -X POST http://localhost:8000/api/polymarket/analyze \
  -H "Content-Type: application/json" \
  -d '{"market_query": "Trump 2024"}'
```

### Method 3: From React Frontend

```typescript
// Add to your API service
export async function analyzeMarket(query: string) {
  const response = await fetch('http://localhost:8000/api/polymarket/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ market_query: query })
  });
  return await response.json();
}

// Use in component
const decision = await analyzeMarket("Trump 2024");
console.log(decision.final_recommendation);  // "YES", "NO", or "SKIP"
console.log(decision.suggested_bet_size);     // 8.5
```

---

## 🎨 Frontend Implementation Ideas

### 1. **Multi-Agent Dashboard**
Show each agent's decision in real-time:

```tsx
<div className="agents-grid">
  {decision.agent_decisions.map(agent => (
    <AgentCard
      name={agent.agent_name}
      recommendation={agent.recommendation}
      confidence={agent.confidence}
      reasoning={agent.reasoning}
    />
  ))}
</div>
```

### 2. **Consensus Meter**
Visual indicator of how much agents agree:

```tsx
<ConsensusMeter value={decision.consensus_level} />
// Shows 85% agreement with color gradient
```

### 3. **Decision Timeline**
Show the decision-making process:

```tsx
1. ✓ Data Collected
2. ✓ 4 Agents Analyzed
3. ✓ Votes: 3 YES, 1 NO
4. ✓ Final: YES (72% confidence)
```

### 4. **Risk Dashboard**
Display supporting vs risk factors:

```tsx
<div className="factors">
  <div className="supporting">
    ✅ Supporting: {decision.supporting_factors.length}
  </div>
  <div className="risks">
    ⚠️ Risks: {decision.risk_factors.length}
  </div>
</div>
```

---

## 🔧 Customization

### Add More Agents:

```python
class HistoricalAgent(BaseAgent):
    """Analyzes historical similar markets"""
    
    async def analyze(self, market_data):
        # Your logic here
        return AgentDecision(
            agent_name="Historical",
            confidence=0.8,
            recommendation="YES",
            reasoning="Similar markets resolved YES 80% of the time",
            key_factors=["Historical pattern match"]
        )

# Add to coordinator
coordinator.agents.append(HistoricalAgent())
```

### Adjust Agent Weights:

```python
# Give some agents more influence
def _aggregate_decisions(self, ...):
    # Weight certain agents higher
    weights = {
        "Odds Analyzer": 1.5,  # 1.5x weight
        "Data Collector": 1.0,
        "Sentiment": 0.7,      # 0.7x weight
    }
    # Apply weights when aggregating
```

### Change Decision Logic:

```python
# Require 75% consensus instead of simple majority
if consensus_level < 0.75:
    final_recommendation = "SKIP"
```

---

## 📈 Advanced Features

### 1. **Kelly Criterion Bet Sizing**
Already implemented! Suggests bet size based on:
- Edge (your confidence vs market price)
- Conservative formula: `bet_size = edge / 2`
- Capped at 20% of bankroll

### 2. **Expected Value Calculation**
```python
# TODO: Add this
expected_value = (win_probability * payout) - (lose_probability * stake)
```

### 3. **Agent Learning** (Future)
- Store all decisions in database
- Track which agents are most accurate
- Adjust weights based on performance

### 4. **Real-time Updates** (Future)
- Re-run agents every hour
- Alert when recommendation changes
- Track market movements

---

## 🎯 Example Workflow in Frontend

```tsx
function TradingDashboard() {
  const [analyzing, setAnalyzing] = useState(false);
  const [decision, setDecision] = useState(null);

  const analyzeMarket = async (query) => {
    setAnalyzing(true);
    
    // Call multi-agent system
    const result = await fetch('/api/polymarket/analyze', {
      method: 'POST',
      body: JSON.stringify({ market_query: query })
    });
    
    const decision = await result.json();
    setDecision(decision);
    setAnalyzing(false);
  };

  return (
    <div>
      {/* Input */}
      <input 
        placeholder="Enter market to analyze"
        onSubmit={(e) => analyzeMarket(e.target.value)}
      />
      
      {/* Agent Status */}
      {analyzing && <AgentProgress />}
      
      {/* Results */}
      {decision && (
        <div>
          <h2>Recommendation: {decision.final_recommendation}</h2>
          <p>Confidence: {decision.aggregate_confidence}%</p>
          <p>Bet Size: {decision.suggested_bet_size}%</p>
          
          {/* Agent Votes */}
          <AgentVotes decisions={decision.agent_decisions} />
          
          {/* Factors */}
          <Factors 
            supporting={decision.supporting_factors}
            risks={decision.risk_factors}
          />
        </div>
      )}
    </div>
  );
}
```

---

## 🧪 Testing

```bash
# Test with a real market
cd backend
source .venv/bin/activate
python multi_agent_decision.py

# Or via API
curl -X POST http://localhost:8000/api/polymarket/analyze \
  -H "Content-Type: application/json" \
  -d '{"market_query": "Trump 2024"}'
```

---

## 📊 Performance Optimization

### Fast Mode (2 agents, ~30 seconds):
```python
coordinator = DecisionCoordinator()
# Uses: DataCollector + OddsAnalyzer only
```

### Full Mode (4 agents, ~2 minutes):
```python
# Uncomment in multi_agent_decision.py:
# ResearchAgent(),
# SentimentAgent(),
```

---

## 🎉 Key Benefits

✅ **Reduces Bias** - Multiple perspectives  
✅ **Better Decisions** - Collective intelligence  
✅ **Risk Assessment** - Identifies concerns  
✅ **Transparency** - See each agent's reasoning  
✅ **Confidence Levels** - Know when to skip  
✅ **Automated Sizing** - Kelly Criterion  

---

## 🔮 Next Steps

1. ✅ Test the multi-agent system
2. ✅ Create frontend component to display agent decisions
3. ✅ Add more specialized agents (historical, technical, etc.)
4. ✅ Implement agent performance tracking
5. ✅ Build real-time monitoring dashboard

**You now have a sophisticated multi-agent trading system!** 🚀
