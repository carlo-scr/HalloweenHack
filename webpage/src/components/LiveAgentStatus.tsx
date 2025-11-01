import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Brain, TrendingUp, Search, MessageSquare, Database, RefreshCw } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

const API_BASE_URL = "http://localhost:8000";

interface AgentDecision {
  agent_name: string;
  recommendation: "BUY" | "SELL" | "HOLD";
  confidence: number;
  reasoning: string;
  supporting_factors: string[];
  risk_factors: string[];
}

interface TradingStatus {
  running: boolean;
  markets_monitored?: string[];
  config?: {
    check_interval: number;
    min_confidence: number;
    min_consensus: number;
  };
}

const AGENT_ICONS: Record<string, any> = {
  "Data Collector": Database,
  "Odds Analyzer": TrendingUp,
  "Research Agent": Search,
  "Sentiment Agent": MessageSquare,
};

const AGENT_DESCRIPTIONS: Record<string, string> = {
  "Data Collector": "Validates market data quality, volume, and liquidity",
  "Odds Analyzer": "Calculates value bets and analyzes market margins",
  "Research Agent": "Performs web research and gathers market context",
  "Sentiment Agent": "Analyzes social media sentiment and crowd psychology",
};

export const LiveAgentStatus = () => {
  const [status, setStatus] = useState<TradingStatus | null>(null);
  const [lastCheck, setLastCheck] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const { toast } = useToast();

  const fetchStatus = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/trading/status`);
      const data = await response.json();
      setStatus(data);
      setLastCheck(new Date().toLocaleTimeString());
      setLoading(false);
    } catch (error) {
      console.error("Error fetching agent status:", error);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
    
    // Update every 20 seconds
    const interval = setInterval(fetchStatus, 20000);
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (isRunning: boolean) => {
    return isRunning
      ? "bg-green-500/20 text-green-500 border-green-500/50"
      : "bg-muted text-muted-foreground border-border";
  };

  const getRecommendationColor = (recommendation: string) => {
    switch (recommendation) {
      case "BUY":
        return "bg-green-500/20 text-green-500 border-green-500/50";
      case "SELL":
        return "bg-red-500/20 text-red-500 border-red-500/50";
      case "HOLD":
        return "bg-yellow-500/20 text-yellow-500 border-yellow-500/50";
      default:
        return "bg-muted text-muted-foreground border-border";
    }
  };

  const agents = [
    "Data Collector",
    "Odds Analyzer",
    "Research Agent",
    "Sentiment Agent",
  ];

  const isRunning = status?.running || false;

  return (
    <Card className="rounded-2xl p-5 border-white/[0.08]">
      <div className="flex items-center justify-between mb-5">
        <div className="flex items-center gap-2">
          <Brain className="h-5 w-5 text-primary" />
          <h2 className="text-base font-mono font-bold uppercase tracking-wider">
            Multi-Agent System
          </h2>
          <Badge className={`${getStatusColor(isRunning)} font-mono text-xs ml-2`}>
            {isRunning ? "ACTIVE" : "IDLE"}
          </Badge>
        </div>
        <div className="flex items-center gap-2 text-xs text-muted-foreground font-mono">
          <RefreshCw className="h-3 w-3" />
          {lastCheck && `Updated: ${lastCheck}`}
        </div>
      </div>

      {/* Agent Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        {agents.map((agentName) => {
          const Icon = AGENT_ICONS[agentName] || Brain;
          const description = AGENT_DESCRIPTIONS[agentName];
          
          return (
            <div
              key={agentName}
              className="backdrop-blur-sm border border-white/[0.08] rounded-xl p-4 hover:border-white/[0.12] transition-all duration-300"
            >
              <div className="flex items-start gap-3 mb-2">
                <div className={`p-2 rounded-lg ${isRunning ? 'bg-primary/20' : 'bg-muted'}`}>
                  <Icon className={`h-4 w-4 ${isRunning ? 'text-primary' : 'text-muted-foreground'}`} />
                </div>
                <div className="flex-1">
                  <h3 className="font-mono text-sm font-bold mb-1">{agentName}</h3>
                  <p className="text-xs text-muted-foreground leading-relaxed">
                    {description}
                  </p>
                </div>
              </div>
              
              <div className="flex items-center justify-between mt-3 pt-3 border-t border-white/[0.08]">
                <span className="text-xs font-mono text-muted-foreground">
                  Status
                </span>
                <Badge 
                  variant={isRunning ? "default" : "secondary"} 
                  className="font-mono text-xs"
                >
                  {isRunning ? "Monitoring" : "Standby"}
                </Badge>
              </div>
            </div>
          );
        })}
      </div>

      {/* System Info */}
      {status?.config && isRunning && (
        <div className="mt-4 p-3 bg-white/[0.02] rounded-lg border border-white/[0.08]">
          <div className="grid grid-cols-3 gap-4 text-xs font-mono">
            <div>
              <div className="text-muted-foreground mb-1">Check Interval</div>
              <div className="font-semibold">{status.config.check_interval}s</div>
            </div>
            <div>
              <div className="text-muted-foreground mb-1">Min Confidence</div>
              <div className="font-semibold">{(status.config.min_confidence * 100).toFixed(0)}%</div>
            </div>
            <div>
              <div className="text-muted-foreground mb-1">Min Consensus</div>
              <div className="font-semibold">{(status.config.min_consensus * 100).toFixed(0)}%</div>
            </div>
          </div>
          
          {status.markets_monitored && status.markets_monitored.length > 0 && (
            <div className="mt-3 pt-3 border-t border-white/[0.08]">
              <div className="text-muted-foreground text-xs mb-2">Monitoring Markets</div>
              <div className="flex flex-wrap gap-2">
                {status.markets_monitored.map((market, i) => (
                  <Badge key={i} variant="outline" className="font-mono text-xs">
                    {market}
                  </Badge>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {!isRunning && (
        <div className="text-center py-6 text-muted-foreground text-sm">
          <Brain className="h-8 w-8 mx-auto mb-2 opacity-50" />
          <p>Agents are on standby. Start autonomous trading to activate.</p>
        </div>
      )}
    </Card>
  );
};
