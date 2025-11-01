import { User, LogOut } from "lucide-react";
import { ActiveBetsTable } from "@/components/ActiveBetsTable";
import { AgentStatusGrid } from "@/components/AgentStatusGrid";
import { ActivityFeed } from "@/components/ActivityFeed";
import { useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";
import logo from "@/assets/logo.svg";

const Index = () => {
  const navigate = useNavigate();
  const [isScrolled, setIsScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20);
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <div className="min-h-screen">
      {/* Header */}
      <section className={`sticky top-0 z-50 transition-all duration-300 ${
        isScrolled ? 'backdrop-blur-xl bg-background/50' : ''
      }`}>
        <div className="container mx-auto px-4 py-6 flex items-center justify-between">
          <img src={logo} alt="Agentic Swarms" className="h-6 w-auto" />
          
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="flex items-center gap-2 text-white/70 hover:text-white hover:bg-white/5 font-sans">
                <span className="text-sm">Max</span>
                <User className="h-5 w-5" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-48 bg-popover border-border font-sans">
              <DropdownMenuItem className="cursor-pointer text-popover-foreground hover:bg-muted focus:bg-muted">
                <LogOut className="mr-2 h-4 w-4" />
                Logout
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </section>

      {/* Dashboard */}
      <section className="container mx-auto px-4 pb-12">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <ActiveBetsTable />
            <AgentStatusGrid />
          </div>
          <div>
            <ActivityFeed />
          </div>
        </div>
      </section>
    </div>
  );
};

export default Index;
