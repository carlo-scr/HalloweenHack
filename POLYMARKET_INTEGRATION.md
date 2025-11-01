# 🎲 Polymarket Integration Guide

## ✅ Yes! You CAN Get Polymarket Data from the Backend

Your project has a complete Polymarket data collector in `backend/Polymarket Agent/` that can:

### 📊 **What Data Can You Collect?**

From any Polymarket market, you can get:
- ✅ Market title/question
- ✅ All possible outcomes
- ✅ **Current prices** (probabilities) for each outcome
- ✅ **Total trading volume** in USD
- ✅ **Liquidity** amount
- ✅ Number of traders
- ✅ End date / time remaining
- ✅ Market status (active/resolved/closed)
- ✅ Market description
- ✅ Recent activity
- ✅ Additional research from Perplexity API (optional)

---

## 🚀 **How to Use It**

### **Method 1: Direct Python Script**

```bash
# Test if it works
python3 test_polymarket.py
```

```python
# In your code:
from polymarket_collector import collect_market_data

market_data = await collect_market_data(
    market_identifier="Trump 2024",
    method='search',  # or 'url' or 'id'
    headless=True
)

print(market_data.market_title)
print(market_data.current_prices)  # {"Yes": 0.65, "No": 0.35}
print(market_data.total_volume)     # 1234567.89
```

### **Method 2: Via API (Now Available!)**

I just added these endpoints to your backend:

#### **Get Specific Market Data**
```bash
# By URL
curl -X POST http://localhost:8000/api/polymarket/collect \
  -H "Content-Type: application/json" \
  -d '{"market_url": "https://polymarket.com/event/will-trump-win"}'

# By Search
curl -X POST http://localhost:8000/api/polymarket/collect \
  -H "Content-Type: application/json" \
  -d '{"search_query": "Biden 2024"}'

# By Market ID
curl -X POST http://localhost:8000/api/polymarket/collect \
  -H "Content-Type: application/json" \
  -d '{"market_id": "will-trump-win-2024"}'
```

#### **Get Trending Markets**
```bash
curl http://localhost:8000/api/polymarket/trending
```

### **Method 3: From React Frontend**

```typescript
// Add to your API service
export async function getPolymarketData(searchQuery: string) {
  const response = await fetch('http://localhost:8000/api/polymarket/collect', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ search_query: searchQuery })
  });
  return await response.json();
}

export async function getTrendingMarkets() {
  const response = await fetch('http://localhost:8000/api/polymarket/trending');
  return await response.json();
}
```

```tsx
// Use in a component
const [markets, setMarkets] = useState([]);

const fetchTrending = async () => {
  const data = await getTrendingMarkets();
  setMarkets(data.markets);
};
```

---

## 📦 **Example Response**

```json
{
  "market_id": "will-trump-win-2024",
  "market_url": "https://polymarket.com/event/will-trump-win-2024",
  "market_title": "Will Donald Trump win the 2024 Presidential Election?",
  "market_category": "Politics",
  "outcomes": ["Yes", "No"],
  "current_prices": {
    "Yes": 0.65,
    "No": 0.35
  },
  "total_volume": 12345678.90,
  "liquidity": 567890.12,
  "number_of_traders": 15234,
  "end_date": "2024-11-05T23:59:59Z",
  "time_remaining": "365 days",
  "status": "active",
  "description": "This market will resolve to Yes if...",
  "recent_activity": "Volume increased 23% in last 24h",
  "collected_at": "2025-11-01T12:30:00Z"
}
```

---

## 🎯 **Use Cases for Your Project**

### **1. Display Live Market Data**
Show current Polymarket prices on your dashboard

### **2. Track Market Changes**
Monitor price movements over time

### **3. Multi-Market Comparison**
Compare multiple markets side-by-side

### **4. Automated Trading Signals**
Use the `polymarket_decision_example.py` to analyze if a bet is good

### **5. Historical Analysis**
Collect data periodically and analyze trends

---

## 🔧 **Setup Requirements**

### **Required:**
- ✅ `BROWSER_USE_API_KEY` in `backend/.env` (you have this)

### **Optional (for enhanced research):**
- `PERPLEXITY_API_KEY` - Adds contextual research about markets
- `HYPERSPELL_API_KEY` - Enables learning/memory for decision-making

---

## 🧪 **Test It Now**

1. **Quick Test:**
```bash
python3 test_polymarket.py
```

2. **Start Backend with Polymarket endpoints:**
```bash
make stop
make start-backend
```

3. **Test the API:**
```bash
curl -X POST http://localhost:8000/api/polymarket/collect \
  -H "Content-Type: application/json" \
  -d '{"search_query": "Trump"}'
```

4. **Check trending markets:**
```bash
curl http://localhost:8000/api/polymarket/trending
```

---

## 📊 **New API Endpoints Added**

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/polymarket/collect` | POST | Get data from specific market |
| `/api/polymarket/trending` | GET | Get top trending markets |

---

## 💡 **Next Steps**

1. ✅ Test Polymarket collection works
2. ✅ Add Polymarket component to your React frontend
3. ✅ Display live market data
4. ✅ Build betting analysis features
5. ✅ Track multiple markets simultaneously

---

## ⚠️ **Important Notes**

- The collector uses browser automation, so it may take 10-30 seconds
- Set `headless: true` for faster execution
- Some markets may have different data structures
- Polymarket may change their UI (agent adapts automatically)
- Rate limit: Don't spam requests (browser automation is slower)

---

**Bottom Line:** Yes, you can absolutely get Polymarket data! The infrastructure is already there - just need to test it and connect it to your frontend. 🎉
