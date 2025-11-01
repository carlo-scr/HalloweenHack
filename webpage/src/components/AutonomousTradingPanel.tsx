import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { 
  Play, 
  Square, 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  Activity,
  Bot,
  RefreshCw,
  Settings
} from "lucide-react";
import { useToast } from "@/hooks/use-toast";

const API_BASE_URL = "http://localhost:8000";

interface Position {
  trade_id: string;
  market_title: string;
  action: string;
  outcome: string;
  price: number;
  size: number;
  shares: number;
  confidence: number;
  consensus: number;
  executed_at: string;
  status: string;
  pnl?: number;
}

interface Portfolio {
  total_value: number;
  cash: number;
  active_positions: Position[];
  closed_positions: Position[];
  total_pnl: number;
  win_rate: number;
  total_trades: number;
  winning_trades: number;
  last_updated: string;
}

interface TradingStatus {
  running: boolean;
  portfolio: Portfolio;
  markets_monitored?: string[];
  config?: {
    check_interval: number;
    min_confidence: number;
    min_consensus: number;
    max_position_size: number;
  };
}

export const AutonomousTradingPanel = () => {
  const [status, setStatus] = useState<TradingStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const { toast } = useToast();

  const fetchStatus = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/trading/status`);
      const data = await response.json();
      setStatus(data);
      setLoading(false);
    } catch (error) {
      console.error("Error fetching status:", error);
      toast({
        title: "Error",
        description: "Failed to fetch trading status",
        variant: "destructive",
      });
      setLoading(false);
    }
  };

  const startTrading = async () => {
    setActionLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/trading/start`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          markets: ["Trump 2024", "Bitcoin $100k by 2025"],
          check_interval: 300,
          min_confidence: 0.7,
          min_consensus: 0.6,
          max_position_size: 500
        })
      });
      
      const data = await response.json();
      
      if (data.success) {
        toast({
          title: "Trading Started",
          description: "Autonomous trading agent is now running",
        });
        await fetchStatus();
      } else {
        toast({
          title: "Already Running",
          description: data.message,
        });
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to start trading",
        variant: "destructive",
      });
    }
    setActionLoading(false);
  };

  const stopTrading = async () => {
    setActionLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/trading/stop`, {
        method: "POST",
      });
      
      const data = await response.json();
      
      toast({
        title: "Trading Stopped",
        description: "Autonomous trading agent has been stopped",
      });
      await fetchStatus();
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to stop trading",
        variant: "destructive",
      });
    }
    setActionLoading(false);
  };

  useEffect(() => {
    fetchStatus();
    
    // Auto-refresh every 20 seconds
    const interval = setInterval(fetchStatus, 20000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bot className="h-5 w-5" />
            Autonomous Trading Agent
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center p-8">
            <RefreshCw className="h-6 w-6 animate-spin text-muted-foreground" />
          </div>
        </CardContent>
      </Card>
    );
  }

  const portfolio = status?.portfolio;
  const isRunning = status?.running || false;
  const pnlPositive = (portfolio?.total_pnl || 0) >= 0;

  return (
    <div className="space-y-6">
      {/* Agent Control */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Bot className="h-5 w-5" />
              <CardTitle>Autonomous Trading Agent</CardTitle>
              <Badge variant={isRunning ? "default" : "secondary"}>
                {isRunning ? "Running" : "Stopped"}
              </Badge>
            </div>
            <div className="flex gap-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={fetchStatus}
                disabled={actionLoading}
              >
                <RefreshCw className={`h-4 w-4 ${actionLoading ? 'animate-spin' : ''}`} />
              </Button>
              {isRunning ? (
                <Button
                  variant="destructive"
                  size="sm"
                  onClick={stopTrading}
                  disabled={actionLoading}
                >
                  <Square className="h-4 w-4 mr-2" />
                  Stop
                </Button>
              ) : (
                <Button
                  variant="default"
                  size="sm"
                  onClick={startTrading}
                  disabled={actionLoading}
                >
                  <Play className="h-4 w-4 mr-2" />
                  Start
                </Button>
              )}
            </div>
          </div>
          <CardDescription>
            AI agents autonomously analyze markets and execute trades (updates every 20s)
          </CardDescription>
        </CardHeader>
        
        {status?.config && (
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <div className="text-muted-foreground">Check Interval</div>
                <div className="font-semibold">{status.config.check_interval}s</div>
              </div>
              <div>
                <div className="text-muted-foreground">Min Confidence</div>
                <div className="font-semibold">{(status.config.min_confidence * 100).toFixed(0)}%</div>
              </div>
              <div>
                <div className="text-muted-foreground">Min Consensus</div>
                <div className="font-semibold">{(status.config.min_consensus * 100).toFixed(0)}%</div>
              </div>
              <div>
                <div className="text-muted-foreground">Max Position</div>
                <div className="font-semibold">${status.config.max_position_size}</div>
              </div>
            </div>
            
            {status.markets_monitored && status.markets_monitored.length > 0 && (
              <div className="mt-4">
                <div className="text-sm text-muted-foreground mb-2">Monitoring</div>
                <div className="flex flex-wrap gap-2">
                  {status.markets_monitored.map((market, i) => (
                    <Badge key={i} variant="outline">{market}</Badge>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        )}
      </Card>

      {/* Portfolio Overview */}
      {portfolio && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Total Value
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  ${portfolio.total_value.toFixed(2)}
                </div>
                <Progress 
                  value={(portfolio.total_value / 10000) * 100} 
                  className="mt-2"
                />
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Available Cash
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold flex items-center gap-2">
                  <DollarSign className="h-5 w-5 text-green-500" />
                  ${portfolio.cash.toFixed(2)}
                </div>
                <div className="text-xs text-muted-foreground mt-1">
                  {((portfolio.cash / portfolio.total_value) * 100).toFixed(1)}% of portfolio
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Total P&L
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className={`text-2xl font-bold flex items-center gap-2 ${pnlPositive ? 'text-green-500' : 'text-red-500'}`}>
                  {pnlPositive ? (
                    <TrendingUp className="h-5 w-5" />
                  ) : (
                    <TrendingDown className="h-5 w-5" />
                  )}
                  ${portfolio.total_pnl.toFixed(2)}
                </div>
                <div className="text-xs text-muted-foreground mt-1">
                  {((portfolio.total_pnl / 10000) * 100).toFixed(2)}% return
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Win Rate
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold flex items-center gap-2">
                  <Activity className="h-5 w-5 text-blue-500" />
                  {(portfolio.win_rate * 100).toFixed(1)}%
                </div>
                <div className="text-xs text-muted-foreground mt-1">
                  {portfolio.winning_trades}/{portfolio.total_trades} trades
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Active Positions */}
          <Card>
            <CardHeader>
              <CardTitle>Active Positions</CardTitle>
              <CardDescription>
                Currently held positions ({portfolio.active_positions.length})
              </CardDescription>
            </CardHeader>
            <CardContent>
              {portfolio.active_positions.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  No active positions
                </div>
              ) : (
                <div className="space-y-4">
                  {portfolio.active_positions.map((position) => (
                    <div
                      key={position.trade_id}
                      className="border rounded-lg p-4 space-y-2"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="font-semibold">{position.market_title}</div>
                          <div className="text-sm text-muted-foreground">
                            {position.action.toUpperCase()} {position.outcome}
                          </div>
                        </div>
                        <Badge variant={position.action === "buy" ? "default" : "secondary"}>
                          {position.action.toUpperCase()}
                        </Badge>
                      </div>
                      
                      <div className="grid grid-cols-4 gap-4 text-sm">
                        <div>
                          <div className="text-muted-foreground">Size</div>
                          <div className="font-semibold">${position.size.toFixed(2)}</div>
                        </div>
                        <div>
                          <div className="text-muted-foreground">Price</div>
                          <div className="font-semibold">${position.price.toFixed(2)}</div>
                        </div>
                        <div>
                          <div className="text-muted-foreground">Confidence</div>
                          <div className="font-semibold">{(position.confidence * 100).toFixed(0)}%</div>
                        </div>
                        <div>
                          <div className="text-muted-foreground">Consensus</div>
                          <div className="font-semibold">{(position.consensus * 100).toFixed(0)}%</div>
                        </div>
                      </div>
                      
                      <div className="text-xs text-muted-foreground">
                        Executed: {new Date(position.executed_at).toLocaleString()}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
};
