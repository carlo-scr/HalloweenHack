import { Card } from "@/components/ui/card";
import { ArrowUpRight, ArrowDownRight, AlertCircle, CheckCircle } from "lucide-react";

const activities = [
  {
    id: 1,
    type: "entry",
    message: "New position opened",
    market: "AI Regulation Q1",
    time: "1 day ago",
    icon: ArrowUpRight,
    color: "text-success",
  },
  {
    id: 2,
    type: "alert",
    message: "High volatility detected",
    market: "Crypto ETF",
    time: "2 days ago",
    icon: AlertCircle,
    color: "text-destructive",
  },
  {
    id: 3,
    type: "success",
    message: "Target hit +12%",
    market: "Tech Stock Rally",
    time: "3 days ago",
    icon: CheckCircle,
    color: "text-success",
  },
  {
    id: 4,
    type: "exit",
    message: "Position closed",
    market: "Fed Rate Decision",
    time: "4 days ago",
    icon: ArrowDownRight,
    color: "text-muted-foreground",
  },
  {
    id: 5,
    type: "entry",
    message: "New position opened",
    market: "Bitcoin $100K",
    time: "5 days ago",
    icon: ArrowUpRight,
    color: "text-success",
  },
  {
    id: 6,
    type: "success",
    message: "Stop loss triggered",
    market: "Fed Pivot Q1",
    time: "6 days ago",
    icon: AlertCircle,
    color: "text-destructive",
  },
  {
    id: 7,
    type: "entry",
    message: "Market threshold reached",
    market: "Inflation Below 2%",
    time: "7 days ago",
    icon: CheckCircle,
    color: "text-success",
  },
  {
    id: 8,
    type: "alert",
    message: "Price movement detected",
    market: "Tech Layoffs",
    time: "8 days ago",
    icon: AlertCircle,
    color: "text-primary",
  },
];

export const ActivityFeed = () => {
  return (
    <Card className="rounded-2xl p-5 h-full border-white/[0.08]">
      <h2 className="text-base font-mono font-bold mb-5 uppercase tracking-wider">
        Activity
      </h2>
      <div className="space-y-3">
        {activities.map((activity) => (
          <div
            key={activity.id}
            className="flex gap-3 p-4 border border-white/[0.08] rounded-xl hover:border-white/[0.12] transition-all duration-300"
          >
            <div className={`flex-shrink-0 ${activity.color}`}>
              <activity.icon className="h-4 w-4" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="font-mono text-xs mb-1">{activity.message}</p>
              <p className="font-mono text-xs text-muted-foreground truncate">{activity.market}</p>
              <p className="font-mono text-xs text-muted-foreground mt-1">{activity.time}</p>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
};
