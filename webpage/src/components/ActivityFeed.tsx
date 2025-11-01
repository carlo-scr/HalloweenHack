import { Card } from "@/components/ui/card";
import { ArrowUpRight, ArrowDownRight, AlertCircle, TrendingUp, Brain, Activity } from "lucide-react";
import { useEffect, useState } from "react";

interface TradeActivity {
  trade_id: string;
  market_title: string;
  action: string;
  outcome: string;
  price: number;
  size: number;
  confidence: number;
  executed_at: string;
}

interface AgentStatus {
  running: boolean;
  markets_monitored: string[];
}

interface ActivityItem {
  id: string;
  type: 'trade' | 'analysis' | 'system';
  message: string;
  market?: string;
  time: string;
  icon: any;
  color: string;
  details?: string;
}

export const ActivityFeed = () => {
  const [activities, setActivities] = useState<ActivityItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const formatTimeAgo = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);
    
    if (seconds < 60) return 'Just now';
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    return `${Math.floor(seconds / 86400)}d ago`;
  };

  const fetchActivity = async () => {
    try {
      // Fetch portfolio history (trades)
      const historyRes = await fetch('http://localhost:8000/api/portfolio/history');
      const historyData = await historyRes.json();
      
      // Fetch trading status
      const statusRes = await fetch('http://localhost:8000/api/trading/status');
      const statusData: AgentStatus = await statusRes.json();
      
      // Fetch active positions
      const positionsRes = await fetch('http://localhost:8000/api/portfolio/positions');
      const positionsData = await positionsRes.json();

      const activityItems: ActivityItem[] = [];

      // Add system status
      if (statusData.running) {
        activityItems.push({
          id: 'system-running',
          type: 'system',
          message: 'Autonomous agent active',
          market: `Monitoring ${statusData.markets_monitored?.length || 0} markets`,
          time: 'Active',
          icon: Activity,
          color: 'text-green-400',
        });
      }

      // Add recent trades from history
      if (historyData && Array.isArray(historyData)) {
        historyData.slice(0, 10).forEach((trade: TradeActivity) => {
          const isBuy = trade.action.toLowerCase() === 'buy';
          activityItems.push({
            id: trade.trade_id,
            type: 'trade',
            message: `${isBuy ? 'Bought' : 'Sold'} ${trade.outcome}`,
            market: trade.market_title,
            time: formatTimeAgo(trade.executed_at),
            icon: isBuy ? ArrowUpRight : ArrowDownRight,
            color: isBuy ? 'text-green-400' : 'text-orange-400',
            details: `$${trade.size.toFixed(2)} @ ${(trade.price * 100).toFixed(1)}% (${(trade.confidence * 100).toFixed(0)}% confidence)`,
          });
        });
      }

      // Add active positions
      if (positionsData && Array.isArray(positionsData)) {
        positionsData.forEach((position: TradeActivity) => {
          activityItems.push({
            id: `active-${position.trade_id}`,
            type: 'analysis',
            message: `Holding ${position.outcome} position`,
            market: position.market_title,
            time: formatTimeAgo(position.executed_at),
            icon: TrendingUp,
            color: 'text-blue-400',
            details: `$${position.size.toFixed(2)} @ ${(position.price * 100).toFixed(1)}%`,
          });
        });
      }

      setActivities(activityItems);
      setIsLoading(false);
    } catch (error) {
      console.error('Error fetching activity:', error);
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchActivity();
    const interval = setInterval(fetchActivity, 5000); // Update every 5 seconds
    return () => clearInterval(interval);
  }, []);

  return (
    <Card className="rounded-2xl p-5 h-full border-white/[0.08]">
      <div className="flex items-center justify-between mb-5">
        <h2 className="text-base font-mono font-bold uppercase tracking-wider">
          Activity Feed
        </h2>
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
          <span className="text-xs font-mono text-muted-foreground">Live</span>
        </div>
      </div>
      
      <div className="space-y-3 max-h-[600px] overflow-y-auto pr-2">
        {isLoading ? (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
          </div>
        ) : activities.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground font-mono text-sm">
            No activity yet. Waiting for trades...
          </div>
        ) : (
          activities.map((activity) => (
            <div
              key={activity.id}
              className="flex gap-3 p-4 border border-white/[0.08] rounded-xl hover:border-white/[0.12] transition-all duration-300 hover:bg-white/[0.02]"
            >
              <div className={`flex-shrink-0 ${activity.color}`}>
                <activity.icon className="h-4 w-4" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-mono text-xs mb-1 font-semibold">{activity.message}</p>
                {activity.market && (
                  <p className="font-mono text-xs text-muted-foreground truncate">{activity.market}</p>
                )}
                {activity.details && (
                  <p className="font-mono text-xs text-muted-foreground mt-1">{activity.details}</p>
                )}
                <p className="font-mono text-xs text-muted-foreground mt-1">{activity.time}</p>
              </div>
            </div>
          ))
        )}
      </div>
    </Card>
  );
};
