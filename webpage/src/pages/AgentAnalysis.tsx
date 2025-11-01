import { MultiAgentAnalysis } from '@/components/MultiAgentAnalysis';
import logo from "@/assets/logo.svg";
import { Button } from "@/components/ui/button";
import { ArrowLeft } from "lucide-react";
import { useNavigate } from "react-router-dom";

const AgentAnalysis = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="border-b border-border/40">
        <div className="container mx-auto px-4 py-6 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button 
              variant="ghost" 
              size="sm"
              onClick={() => navigate('/')}
              className="gap-2"
            >
              <ArrowLeft className="w-4 h-4" />
              Back
            </Button>
            <img src={logo} alt="Logo" className="h-6 w-auto" />
          </div>
          <div className="text-sm text-muted-foreground">
            AI Trading Advisor
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto space-y-6">
          
          {/* Title */}
          <div className="space-y-2">
            <h1 className="text-4xl font-bold bg-gradient-to-r from-primary to-purple-500 bg-clip-text text-transparent">
              Multi-Agent Trading Advisor
            </h1>
            <p className="text-muted-foreground">
              Multiple AI agents analyze markets together to provide collective intelligence and trading recommendations
            </p>
          </div>

          {/* How it Works */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-center">
            <div className="p-4 bg-card/50 rounded-lg border border-border/40">
              <div className="text-3xl mb-2">🔍</div>
              <div className="font-semibold text-sm">Data Collection</div>
              <div className="text-xs text-muted-foreground mt-1">Gathers market data</div>
            </div>
            <div className="p-4 bg-card/50 rounded-lg border border-border/40">
              <div className="text-3xl mb-2">🤖</div>
              <div className="font-semibold text-sm">Agents Analyze</div>
              <div className="text-xs text-muted-foreground mt-1">Multiple perspectives</div>
            </div>
            <div className="p-4 bg-card/50 rounded-lg border border-border/40">
              <div className="text-3xl mb-2">🗳️</div>
              <div className="font-semibold text-sm">Vote & Aggregate</div>
              <div className="text-xs text-muted-foreground mt-1">Collective decision</div>
            </div>
            <div className="p-4 bg-card/50 rounded-lg border border-border/40">
              <div className="text-3xl mb-2">💡</div>
              <div className="font-semibold text-sm">Recommendation</div>
              <div className="text-xs text-muted-foreground mt-1">Final verdict + sizing</div>
            </div>
          </div>

          {/* Multi-Agent Component */}
          <MultiAgentAnalysis />

        </div>
      </div>
    </div>
  );
};

export default AgentAnalysis;
