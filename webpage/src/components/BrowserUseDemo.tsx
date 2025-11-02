import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Loader2, Check, X } from 'lucide-react';
import { runBrowserTask, checkHealth, getExamples, handleApiError } from '@/services/browserUseApi';
import type { TaskResponse, TaskExample } from '@/services/browserUseApi';

/**
 * Example component showing how to use the Browser-Use backend from React
 * 
 * Usage: Import this component anywhere in your app
 */
export function BrowserUseDemo() {
  const [task, setTask] = useState('');
  const [result, setResult] = useState<TaskResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [backendHealthy, setBackendHealthy] = useState<boolean | null>(null);
  const [examples, setExamples] = useState<TaskExample[]>([]);

  // Check backend health on mount
  useEffect(() => {
    checkHealth()
      .then(() => setBackendHealthy(true))
      .catch(() => setBackendHealthy(false));
    
    getExamples()
      .then(data => setExamples(data.examples))
      .catch(console.error);
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!task.trim()) {
      setError('Please enter a task');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await runBrowserTask({
        task: task,
        max_steps: 10,
        use_vision: true,
        headless: false
      });
      
      setResult(response);
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setLoading(false);
    }
  };

  const loadExample = (exampleTask: string) => {
    setTask(exampleTask);
    setResult(null);
    setError(null);
  };

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Browser-Use Integration Demo</CardTitle>
          <CardDescription>
            Control browser automation from your React app
          </CardDescription>
          {backendHealthy !== null && (
            <Badge variant={backendHealthy ? "default" : "destructive"}>
              {backendHealthy ? (
                <><Check className="w-3 h-3 mr-1" /> Backend Connected</>
              ) : (
                <><X className="w-3 h-3 mr-1" /> Backend Offline</>
              )}
            </Badge>
          )}
        </CardHeader>
        <CardContent className="space-y-4">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Input
                type="text"
                placeholder="Enter a browser task (e.g., 'Go to Hacker News and find the top post')"
                value={task}
                onChange={(e) => setTask(e.target.value)}
                disabled={loading}
                className="w-full"
              />
            </div>
            
            <Button 
              type="submit" 
              disabled={loading || !backendHealthy}
              className="w-full"
            >
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Running Task...
                </>
              ) : (
                'Run Browser Task'
              )}
            </Button>
          </form>

          {examples.length > 0 && (
            <div className="space-y-2">
              <p className="text-sm text-muted-foreground">Quick Examples:</p>
              <div className="flex flex-wrap gap-2">
                {examples.map((example, idx) => (
                  <Button
                    key={idx}
                    variant="outline"
                    size="sm"
                    onClick={() => loadExample(example.task)}
                    disabled={loading}
                  >
                    {example.name}
                  </Button>
                ))}
              </div>
            </div>
          )}

          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {result && (
            <Card className={result.success ? 'border-green-500' : 'border-red-500'}>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  {result.success ? (
                    <><Check className="w-5 h-5 text-green-500" /> Success</>
                  ) : (
                    <><X className="w-5 h-5 text-red-500" /> Failed</>
                  )}
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <p className="text-sm font-medium">Message:</p>
                  <p className="text-sm text-muted-foreground">{result.message}</p>
                </div>
                
                {result.steps_taken && (
                  <div>
                    <p className="text-sm font-medium">Steps Taken:</p>
                    <p className="text-sm text-muted-foreground">{result.steps_taken}</p>
                  </div>
                )}
                
                {result.final_result && (
                  <div>
                    <p className="text-sm font-medium">Result:</p>
                    <p className="text-sm text-muted-foreground">{result.final_result}</p>
                  </div>
                )}
                
                {result.urls_visited && result.urls_visited.length > 0 && (
                  <div>
                    <p className="text-sm font-medium">URLs Visited:</p>
                    <ul className="text-sm text-muted-foreground list-disc list-inside">
                      {result.urls_visited.map((url, idx) => (
                        <li key={idx} className="truncate">{url}</li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {result.error && (
                  <div>
                    <p className="text-sm font-medium text-red-500">Error:</p>
                    <p className="text-sm text-red-400">{result.error}</p>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </CardContent>
      </Card>

      {!backendHealthy && (
        <Alert>
          <AlertDescription>
            <strong>Backend not running.</strong> Start it with:
            <code className="block mt-2 p-2 bg-muted rounded">
              cd browser-use-backend && python main.py
            </code>
          </AlertDescription>
        </Alert>
      )}
    </div>
  );
}
