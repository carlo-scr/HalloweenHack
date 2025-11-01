import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Loader2, PlayCircle, CheckCircle2, XCircle, Globe } from 'lucide-react';
import logo from "@/assets/logo.svg";

/**
 * Simple Browser Automation Test Page
 * Shows how frontend connects to backend
 */
const BrowserTest = () => {
  const [task, setTask] = useState('Go to example.com and get the page title');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  // This is how you call the backend!
  const runAutomation = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      // Call your Python backend API
      const response = await fetch('http://localhost:8000/api/run-task', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          task: task,
          max_steps: 5,
          headless: true,
          use_vision: true
        })
      });

      const data = await response.json();
      
      if (response.ok) {
        setResult(data);
      } else {
        setError(data.error || 'Task failed');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to connect to backend');
    } finally {
      setLoading(false);
    }
  };

  const quickTests = [
    'Go to example.com and get the page title',
    'Go to Hacker News and find the top post title',
    'Search Google for "browser automation" and get first result',
  ];

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="border-b border-border/40">
        <div className="container mx-auto px-4 py-6">
          <img src={logo} alt="Logo" className="h-6 w-auto" />
        </div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-12">
        <div className="max-w-3xl mx-auto space-y-8">
          
          {/* Title */}
          <div className="text-center space-y-2">
            <h1 className="text-4xl font-bold bg-gradient-to-r from-primary to-purple-500 bg-clip-text text-transparent">
              Browser Automation Test
            </h1>
            <p className="text-muted-foreground">
              Frontend → Backend → Browser Agent → Result
            </p>
          </div>

          {/* Main Card */}
          <Card className="border-border/40">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Globe className="w-5 h-5" />
                Test Browser Task
              </CardTitle>
              <CardDescription>
                Enter a task in plain English and watch the AI browser agent do it
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              
              {/* Task Input */}
              <div className="space-y-2">
                <label className="text-sm font-medium">Task Description</label>
                <Input
                  value={task}
                  onChange={(e) => setTask(e.target.value)}
                  placeholder="What should the browser do?"
                  className="bg-background"
                  disabled={loading}
                />
              </div>

              {/* Quick Test Buttons */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-muted-foreground">Quick Tests:</label>
                <div className="flex flex-wrap gap-2">
                  {quickTests.map((quickTask, idx) => (
                    <Button
                      key={idx}
                      variant="outline"
                      size="sm"
                      onClick={() => setTask(quickTask)}
                      disabled={loading}
                      className="text-xs"
                    >
                      {quickTask.substring(0, 30)}...
                    </Button>
                  ))}
                </div>
              </div>

              {/* Run Button */}
              <Button
                onClick={runAutomation}
                disabled={loading || !task}
                className="w-full"
                size="lg"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Running automation...
                  </>
                ) : (
                  <>
                    <PlayCircle className="w-4 h-4 mr-2" />
                    Run Browser Task
                  </>
                )}
              </Button>

              {/* Results */}
              {result && (
                <div className="space-y-3 p-4 bg-muted/50 rounded-lg border border-border/40">
                  <div className="flex items-center gap-2">
                    {result.success ? (
                      <CheckCircle2 className="w-5 h-5 text-green-500" />
                    ) : (
                      <XCircle className="w-5 h-5 text-red-500" />
                    )}
                    <span className="font-semibold">
                      {result.success ? 'Success!' : 'Failed'}
                    </span>
                  </div>

                  {result.final_result && (
                    <div className="space-y-1">
                      <div className="text-sm font-medium text-muted-foreground">Result:</div>
                      <div className="p-3 bg-background rounded border border-border/40">
                        {result.final_result}
                      </div>
                    </div>
                  )}

                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-muted-foreground">Steps taken:</span>
                      <div className="font-mono">{result.steps_taken}</div>
                    </div>
                    <div>
                      <span className="text-muted-foreground">URLs visited:</span>
                      <div className="font-mono">{result.urls_visited?.length || 0}</div>
                    </div>
                  </div>

                  {result.urls_visited && result.urls_visited.length > 0 && (
                    <div className="space-y-1">
                      <div className="text-sm font-medium text-muted-foreground">Visited:</div>
                      <div className="space-y-1">
                        {result.urls_visited.map((url: string, idx: number) => (
                          <div key={idx} className="text-xs font-mono text-muted-foreground">
                            {url}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Error */}
              {error && (
                <div className="p-4 bg-destructive/10 border border-destructive/20 rounded-lg">
                  <div className="flex items-center gap-2 text-destructive">
                    <XCircle className="w-4 h-4" />
                    <span className="font-semibold">Error</span>
                  </div>
                  <p className="text-sm mt-2 text-destructive/80">{error}</p>
                </div>
              )}

              {/* How it works */}
              <div className="pt-4 border-t border-border/40">
                <details className="text-sm text-muted-foreground">
                  <summary className="cursor-pointer font-medium hover:text-foreground">
                    🔍 How does this work?
                  </summary>
                  <div className="mt-3 space-y-2 pl-4">
                    <p>1. <strong>React Frontend</strong> sends HTTP POST request to backend</p>
                    <p>2. <strong>Python Backend</strong> receives task at <code>localhost:8000</code></p>
                    <p>3. <strong>AI Agent</strong> plans steps to complete the task</p>
                    <p>4. <strong>Browser</strong> executes actions (navigate, click, extract data)</p>
                    <p>5. <strong>Backend</strong> returns JSON result to frontend</p>
                    <p>6. <strong>React</strong> displays the result!</p>
                  </div>
                </details>
              </div>

            </CardContent>
          </Card>

          {/* Code Example */}
          <Card className="border-border/40">
            <CardHeader>
              <CardTitle className="text-base">💻 Code Example</CardTitle>
            </CardHeader>
            <CardContent>
              <pre className="text-xs bg-muted p-4 rounded overflow-x-auto">
{`// Call the backend from any React component:
const response = await fetch('http://localhost:8000/api/run-task', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    task: 'Go to example.com',
    max_steps: 5,
    headless: true
  })
});

const result = await response.json();
console.log(result.final_result);`}
              </pre>
            </CardContent>
          </Card>

        </div>
      </div>
    </div>
  );
};

export default BrowserTest;
