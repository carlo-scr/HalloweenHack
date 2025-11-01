import { Card } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";

const activeBets = [
  { id: 1, market: "2024 Presidential Election", position: "TRUMP", size: "$125,000", probability: "62%", pnl: "+$8,450", status: "winning" },
  { id: 2, market: "Fed Rate Decision Dec", position: "No", size: "$87,500", probability: "41%", pnl: "-$2,100", status: "losing" },
  { id: 3, market: "AI Regulation Q1 2025", position: "PASS", size: "$156,000", probability: "78%", pnl: "+$15,200", status: "winning" },
  { id: 4, market: "Bitcoin $100K by EOY", position: "YES", size: "$92,000", probability: "54%", pnl: "+$4,800", status: "winning" },
  { id: 5, market: "Tech Layoffs Continue", position: "YES", size: "$68,500", probability: "71%", pnl: "+$6,320", status: "winning" },
  { id: 6, market: "Fed Pivot in Q1 2025", position: "NO", size: "$112,000", probability: "38%", pnl: "-$3,450", status: "losing" },
  { id: 7, market: "AI Safety Bill Passes", position: "PASS", size: "$84,000", probability: "66%", pnl: "+$5,120", status: "winning" },
  { id: 8, market: "Inflation Below 2%", position: "NO", size: "$97,500", probability: "45%", pnl: "+$2,890", status: "winning" },
];

export const ActiveBetsTable = () => {
  return (
    <Card className="rounded-2xl p-5 overflow-hidden border-white/[0.08]">
      <h2 className="text-base font-mono font-bold mb-5 uppercase tracking-wider">
        Active Positions
      </h2>
      <div className="overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow className="border-border hover:bg-transparent">
              <TableHead className="font-mono text-xs">Market</TableHead>
              <TableHead className="font-mono text-xs">Position</TableHead>
              <TableHead className="font-mono text-xs">Size</TableHead>
              <TableHead className="font-mono text-xs">Probability</TableHead>
              <TableHead className="font-mono text-xs text-right">P&L</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {activeBets.map((bet) => (
              <TableRow key={bet.id} className="border-white/[0.05] hover:border-white/[0.08] transition-colors">
                <TableCell className="font-mono text-xs">{bet.market}</TableCell>
                <TableCell>
                  <Badge variant="default" className="font-mono text-[10px] px-2 py-0">
                    {bet.position.toUpperCase()}
                  </Badge>
                </TableCell>
                <TableCell className="font-mono text-xs text-muted-foreground">{bet.size}</TableCell>
                <TableCell>
                  <span className="font-mono text-xs text-primary">{bet.probability}</span>
                </TableCell>
                <TableCell className="text-right">
                  <span className={`font-mono text-xs font-semibold ${bet.status === "winning" ? "text-success" : "text-destructive"}`}>
                    {bet.pnl}
                  </span>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </Card>
  );
};
