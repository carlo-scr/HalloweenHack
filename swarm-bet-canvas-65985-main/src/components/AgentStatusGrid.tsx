import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

const agents = [
  { id: "AGT-001", name: "Quantum Trader", status: "active", tasks: 12, accuracy: "94%" },
  { id: "AGT-002", name: "Neural Prophet", status: "active", tasks: 8, accuracy: "87%" },
  { id: "AGT-003", name: "Shadow Strategist", status: "idle", tasks: 0, accuracy: "91%" },
  { id: "AGT-004", name: "Velocity Vanguard", status: "active", tasks: 15, accuracy: "89%" },
];

export const AgentStatusGrid = () => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "bg-success/20 text-success border-success/50";
      case "idle":
        return "bg-muted text-muted-foreground border-border";
      case "maintenance":
        return "bg-destructive/20 text-destructive border-destructive/50";
      default:
        return "bg-muted";
    }
  };

  return (
    <Card className="rounded-2xl p-5 border-white/[0.08]">
      <h2 className="text-base font-mono font-bold mb-5 uppercase tracking-wider">
        Agent Status
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {agents.map((agent) => (
          <div
            key={agent.id}
            className="backdrop-blur-sm border border-white/[0.08] rounded-xl p-4 hover:border-white/[0.12] transition-all duration-300"
          >
            <div className="flex items-center justify-between mb-2">
              <div>
                <p className="font-mono text-xs text-muted-foreground">{agent.id}</p>
                <h3 className="font-mono text-sm font-bold">{agent.name}</h3>
              </div>
              <Badge className={`${getStatusColor(agent.status)} font-mono text-xs`}>
                {agent.status}
              </Badge>
            </div>
            <div className="flex items-center justify-between text-xs font-mono">
              <span className="text-muted-foreground">Tasks: <span className="text-foreground">{agent.tasks}</span></span>
              <span className="text-muted-foreground">Accuracy: <span className="text-foreground">{agent.accuracy}</span></span>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
};
