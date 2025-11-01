import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { 
  Loader2, 
  Brain, 
  TrendingUp, 
  TrendingDown, 
  Minus,
  CheckCircle2,
  XCircle,
  AlertCircle,
  Users
} from 'lucide-react';

/**
 * Multi-Agent Trading Decision Component
 * 
 * Shows AI agents working together to analyze Polymarket trades
 */

interface AgentDecision {
  agent_name: string;
  confidence: number;
  recommendation: string;
  reasoning: string;
  key_factors: string[];
}

interface CollectiveDecision {
  market_title: string;
  market_url: string;
  final_recommendation: string;
  aggregate_confidence: number;
  consensus_level: number;
  agent_decisions: AgentDecision[];
  supporting_factors: string[];
  risk_factors: string[];
  suggested_bet_size: number | null;
}

export function MultiAgentAnalysis() {
  const [marketQuery, setMarketQuery] = useState('Trump 2024');
  const [analyzing, setAnalyzing] = useState(false);
  const [decision, setDecision] = useState<CollectiveDecision | null>(null);
  const [error, setError] = useState<string | null>(null);

  const analyzeMarket = async () => {
    if (!marketQuery.trim()) return;

    setAnalyzing(true);
    setError(null);
    setDecision(null);

    try {
      const response = await fetch('http://localhost:8000/api/polymarket/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          market_query: marketQuery
        })
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();
      setDecision(data);
    } catch (err: any) {
      setError(err.message || 'Failed to analyze market');
    } finally {
      setAnalyzing(false);
    }
  };

  const getRecommendationColor = (rec: string) => {
    switch (rec) {
      case 'YES': return 'bg-green-500';
      case 'NO': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const getRecommendationIcon = (rec: string) => {
    switch (rec) {
      case 'YES': return <TrendingUp className="w-5 h-5" />;
      case 'NO': return <TrendingDown className="w-5 h-5" />;
      default: return <Minus className="w-5 h-5" />;
    }
  };

  return (
    <div className="space-y-6">
      
      {/* Header Card */}
      <Card className="border-border/40 bg-card/50 backdrop-blur">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="w-6 h-6 text-primary" />
            Multi-Agent Trading Analysis
          </CardTitle>
          <CardDescription>
            AI agents collaborate to analyze markets and provide trading recommendations
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          
          {/* Search Input */}
          <div className="flex gap-2">
            <Input
              value={marketQuery}
              onChange={(e) => setMarketQuery(e.target.value)}
              placeholder="Enter market to analyze (e.g., 'Trump 2024')"
              className="bg-background"
              disabled={analyzing}
              onKeyDown={(e) => e.key === 'Enter' && analyzeMarket()}
            />
            <Button
              onClick={analyzeMarket}
              disabled={analyzing || !marketQuery.trim()}
              className="min-w-32"
            >
              {analyzing ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Brain className="w-4 h-4 mr-2" />
                  Analyze
                </>
              )}
            </Button>
          </div>

          {/* Quick Examples */}
          <div className="flex gap-2 flex-wrap">
            <span className="text-sm text-muted-foreground">Quick:</span>
            {['Trump 2024', 'Bitcoin $100k', 'AI regulation'].map((example) => (
              <Button
                key={example}
                variant="outline"
                size="sm"
                onClick={() => setMarketQuery(example)}
                disabled={analyzing}
                className="text-xs"
              >
                {example}
              </Button>
            ))}
          </div>

        </CardContent>
      </Card>

      {/* Error */}
      {error && (
        <Card className="border-destructive/50 bg-destructive/5">
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 text-destructive">
              <XCircle className="w-5 h-5" />
              <span className="font-semibold">Error</span>
            </div>
            <p className="mt-2 text-sm">{error}</p>
          </CardContent>
        </Card>
      )}

      {/* Analysis in Progress */}
      {analyzing && (
        <Card className="border-border/40">
          <CardContent className="pt-6">
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                <Loader2 className="w-5 h-5 animate-spin text-primary" />
                <span className="font-medium">Running multi-agent analysis...</span>
              </div>
              <div className="space-y-2 text-sm text-muted-foreground">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-primary rounded-full animate-pulse" />
                  Collecting market data
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-primary rounded-full animate-pulse" />
                  Running specialized agents
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-primary rounded-full animate-pulse" />
                  Aggregating decisions
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Results */}
      {decision && (
        <>
          {/* Market Info & Final Decision */}
          <Card className="border-border/40 bg-gradient-to-br from-card to-card/50">
            <CardHeader>
              <CardTitle className="text-xl">{decision.market_title}</CardTitle>
              <CardDescription className="text-xs break-all">
                {decision.market_url}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              
              {/* Final Recommendation */}
              <div className="flex items-center justify-between p-6 bg-background/50 rounded-lg border border-border/40">
                <div className="space-y-1">
                  <p className="text-sm text-muted-foreground">Final Recommendation</p>
                  <div className="flex items-center gap-3">
                    <Badge className={`${getRecommendationColor(decision.final_recommendation)} text-white px-4 py-2 text-lg`}>
                      {getRecommendationIcon(decision.final_recommendation)}
                      <span className="ml-2">{decision.final_recommendation}</span>
                    </Badge>
                    <div className="text-2xl font-bold">
                      {(decision.aggregate_confidence * 100).toFixed(0)}%
                    </div>
                  </div>
                  <p className="text-xs text-muted-foreground">Confidence Level</p>
                </div>

                {decision.suggested_bet_size && decision.suggested_bet_size > 0 && (
                  <div className="text-right">
                    <p className="text-sm text-muted-foreground">Suggested Bet Size</p>
                    <div className="text-3xl font-bold text-primary">
                      {decision.suggested_bet_size.toFixed(1)}%
                    </div>
                    <p className="text-xs text-muted-foreground">of bankroll</p>
                  </div>
                )}
              </div>

              {/* Consensus Meter */}
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground flex items-center gap-2">
                    <Users className="w-4 h-4" />
                    Agent Consensus
                  </span>
                  <span className="font-semibold">
                    {(decision.consensus_level * 100).toFixed(0)}% Agreement
                  </span>
                </div>
                <Progress value={decision.consensus_level * 100} className="h-2" />
              </div>

            </CardContent>
          </Card>

          {/* Individual Agent Decisions */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {decision.agent_decisions.map((agent, idx) => (
              <Card key={idx} className="border-border/40">
                <CardHeader>
                  <CardTitle className="text-base flex items-center justify-between">
                    <span className="flex items-center gap-2">
                      <Brain className="w-4 h-4 text-primary" />
                      {agent.agent_name}
                    </span>
                    <Badge variant={
                      agent.recommendation === 'YES' ? 'default' : 
                      agent.recommendation === 'NO' ? 'destructive' : 
                      'secondary'
                    }>
                      {agent.recommendation}
                    </Badge>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="space-y-1">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Confidence</span>
                      <span className="font-semibold">{(agent.confidence * 100).toFixed(0)}%</span>
                    </div>
                    <Progress value={agent.confidence * 100} className="h-1.5" />
                  </div>

                  <div className="text-sm text-muted-foreground">
                    {agent.reasoning}
                  </div>

                  {agent.key_factors.length > 0 && (
                    <div className="space-y-1">
                      {agent.key_factors.map((factor, i) => (
                        <div key={i} className="text-xs flex items-start gap-2">
                          <span className="text-primary mt-0.5">•</span>
                          <span className="text-muted-foreground">{factor}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Supporting & Risk Factors */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            
            {/* Supporting Factors */}
            {decision.supporting_factors.length > 0 && (
              <Card className="border-green-500/20 bg-green-500/5">
                <CardHeader>
                  <CardTitle className="text-base flex items-center gap-2 text-green-600">
                    <CheckCircle2 className="w-4 h-4" />
                    Supporting Factors
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {decision.supporting_factors.map((factor, idx) => (
                      <li key={idx} className="text-sm flex items-start gap-2">
                        <CheckCircle2 className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                        <span>{factor}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            )}

            {/* Risk Factors */}
            {decision.risk_factors.length > 0 && (
              <Card className="border-yellow-500/20 bg-yellow-500/5">
                <CardHeader>
                  <CardTitle className="text-base flex items-center gap-2 text-yellow-600">
                    <AlertCircle className="w-4 h-4" />
                    Risk Factors
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {decision.risk_factors.map((factor, idx) => (
                      <li key={idx} className="text-sm flex items-start gap-2">
                        <AlertCircle className="w-4 h-4 text-yellow-500 mt-0.5 flex-shrink-0" />
                        <span>{factor}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            )}

          </div>
        </>
      )}

    </div>
  );
}
