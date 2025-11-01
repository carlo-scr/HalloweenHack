import { useState } from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { Button } from "@/components/ui/button";

const formatDate = (date: Date, timeframe: number) => {
  if (timeframe === 1) {
    // 1D: time only
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
  } else if (timeframe <= 90) {
    // 1W, 1M, 3M: day and month
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  } else {
    // 1Y, ALL: month and year
    return date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
  }
};

const generateData = (days: number) => {
  const data = [];
  const now = Date.now();
  const startPnL = days === 730 ? 0 : 100000; // Start at 0 for ALL
  let pnl = startPnL;
  
  for (let i = days; i >= 0; i--) {
    const date = new Date(now - i * 24 * 60 * 60 * 1000);
    pnl += (Math.random() - 0.45) * 2000;
    data.push({
      date: date,
      dateFormatted: formatDate(date, days),
      pnl: Math.round(pnl),
    });
  }
  return data;
};

const timeframes = [
  { label: "1D", days: 1 },
  { label: "1W", days: 7 },
  { label: "1M", days: 30 },
  { label: "3M", days: 90 },
  { label: "1Y", days: 365 },
  { label: "ALL", days: 730 },
];

export const PnLChart = () => {
  const [selectedTimeframe, setSelectedTimeframe] = useState(730);
  const data = generateData(selectedTimeframe);
  
  const currentPnL = data[data.length - 1]?.pnl || 0;
  const startPnL = data[0]?.pnl || 0;
  const change = currentPnL - startPnL;
  const changePercent = ((change / startPnL) * 100).toFixed(2);
  const isPositive = change >= 0;

  const getTickCount = () => {
    if (selectedTimeframe === 1) return 12; // 1D
    if (selectedTimeframe === 7) return 7;  // 1W
    return 12; // 1M, 3M, 1Y, ALL
  };

  return (
    <div className="space-y-8">
      <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-6">
        <div>
          <div className="text-xs text-muted-foreground font-medium uppercase tracking-wider mb-2 font-sans">Realized PnL</div>
          <div className={`text-5xl md:text-6xl font-bold mb-2 ${isPositive ? 'text-success' : 'text-destructive'}`}>
            ${currentPnL.toLocaleString()}
          </div>
          <div className="flex items-center gap-3">
            <div className={`text-lg font-semibold ${isPositive ? 'text-success' : 'text-destructive'}`}>
              {isPositive ? '↗' : '↘'} {isPositive ? '+' : ''}{change.toLocaleString()}
            </div>
            <div className={`px-3 py-1 rounded-full text-sm font-medium ${isPositive ? 'bg-success/20 text-success' : 'bg-destructive/20 text-destructive'}`}>
              {isPositive ? '+' : ''}{changePercent}%
            </div>
          </div>
        </div>
        
        <div className="flex gap-2 flex-wrap">
          {timeframes.map((tf) => (
            <Button
              key={tf.label}
              variant={selectedTimeframe === tf.days ? "default" : "outline"}
              size="sm"
              onClick={() => setSelectedTimeframe(tf.days)}
              className={`font-mono text-xs transition-all ${
                selectedTimeframe === tf.days 
                  ? 'shadow-lg shadow-primary/20' 
                  : 'hover:border-primary/50'
              }`}
            >
              {tf.label}
            </Button>
          ))}
        </div>
      </div>

      <div className="rounded-2xl bg-muted/30 p-4 backdrop-blur-sm">
        <ResponsiveContainer width="100%" height={450}>
          <LineChart data={data}>
            <defs>
              <linearGradient id="colorGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={isPositive ? '#34d399' : '#f87171'} stopOpacity={0.3}/>
                <stop offset="95%" stopColor={isPositive ? '#34d399' : '#f87171'} stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" opacity={0.3} />
            <XAxis 
              dataKey="dateFormatted" 
              stroke="hsl(var(--muted-foreground))"
              style={{ fontSize: '11px', fontFamily: 'monospace' }}
              tickCount={getTickCount()}
            />
            <YAxis 
              stroke="hsl(var(--muted-foreground))"
              style={{ fontSize: '11px', fontFamily: 'monospace' }}
              tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`}
            />
            <Tooltip 
              contentStyle={{
                backgroundColor: 'hsl(var(--popover))',
                border: '1px solid hsl(var(--border))',
                borderRadius: '12px',
                fontSize: '12px',
                fontFamily: 'monospace',
                padding: '12px'
              }}
              formatter={(value: number) => [`$${value.toLocaleString()}`, 'PnL']}
              labelFormatter={(label, payload) => {
                if (payload && payload[0]) {
                  const date = payload[0].payload.date;
                  return date.toLocaleDateString('en-US', { 
                    month: 'short', 
                    day: 'numeric', 
                    year: 'numeric',
                    hour: selectedTimeframe === 1 ? '2-digit' : undefined,
                    minute: selectedTimeframe === 1 ? '2-digit' : undefined
                  });
                }
                return label;
              }}
            />
            <Line 
              type="monotone" 
              dataKey="pnl" 
              stroke={isPositive ? '#34d399' : '#f87171'}
              strokeWidth={3}
              dot={false}
              fill="url(#colorGradient)"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
