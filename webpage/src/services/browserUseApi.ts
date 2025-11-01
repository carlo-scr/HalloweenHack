/**
 * Browser-Use API Service
 * 
 * Service layer for communicating with the Browser-Use Python backend.
 * Place this file in: src/services/browserUseApi.ts
 */

const API_BASE_URL = import.meta.env.VITE_BROWSER_USE_API_URL || 'http://localhost:8000';

// Type definitions
export interface BrowserTask {
  task: string;
  max_steps?: number;
  use_vision?: boolean;
  headless?: boolean;
}

export interface TaskResponse {
  success: boolean;
  message: string;
  task: string;
  steps_taken?: number;
  final_result?: string;
  urls_visited?: string[];
  error?: string;
}

export interface HealthResponse {
  status: string;
  browser_use_available: boolean;
  llm_configured: boolean;
}

export interface TaskExample {
  name: string;
  task: string;
  max_steps: number;
}

/**
 * Check if the backend is healthy and properly configured
 */
export async function checkHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE_URL}/health`);
  
  if (!response.ok) {
    throw new Error(`Health check failed: ${response.statusText}`);
  }
  
  return await response.json();
}

/**
 * Run a browser automation task
 */
export async function runBrowserTask(taskRequest: BrowserTask): Promise<TaskResponse> {
  const response = await fetch(`${API_BASE_URL}/api/run-task`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(taskRequest),
  });
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
  }
  
  return await response.json();
}

/**
 * Get example tasks
 */
export async function getExamples(): Promise<{ examples: TaskExample[] }> {
  const response = await fetch(`${API_BASE_URL}/api/examples`);
  
  if (!response.ok) {
    throw new Error(`Failed to fetch examples: ${response.statusText}`);
  }
  
  return await response.json();
}

/**
 * Error handler for API calls
 */
export function handleApiError(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }
  return 'An unknown error occurred';
}
