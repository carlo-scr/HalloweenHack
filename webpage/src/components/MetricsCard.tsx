import { Card } from "@/components/ui/card";
import { LucideIcon } from "lucide-react";

interface MetricsCardProps {
  title: string;
  value: string;
  change: string;
  icon: LucideIcon;
  trend: "up" | "down";
}

export const MetricsCard = ({ title, value, change, icon: Icon, trend }: MetricsCardProps) => {
  return (
    <Card className="glass glass-hover rounded-2xl p-5 shadow-glass">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xs font-mono text-muted-foreground uppercase tracking-wider">{title}</h3>
        <Icon className="h-4 w-4 text-muted-foreground" />
      </div>
      <div className="space-y-2">
        <p className="text-3xl font-mono font-bold tabular-nums">{value}</p>
        <p className={`text-sm font-mono tabular-nums ${
          trend === "up" ? "text-success" : "text-destructive"
        }`}>
          {trend === "up" ? "↑" : "↓"} {change}
        </p>
      </div>
    </Card>
  );
};
