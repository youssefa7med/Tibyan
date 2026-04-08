// API Configuration for Local On-Premises Deployment
// Automatically detects if running locally or on network
const getApiBase = () => {
  // Check for explicit environment variable
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }
  
  // For local on-premises: use localhost or current host
  const hostname = window.location.hostname;
  const isLocalhost = hostname === 'localhost' || hostname === '127.0.0.1' || hostname === '';
  
  if (isLocalhost) {
    return 'http://localhost:8000';
  }
  
  // For network access: use current host with port 8000
  return `${window.location.protocol}//${hostname}:8000`;
};

const getWsBase = () => {
  // Check for explicit environment variable
  if (import.meta.env.VITE_WS_URL) {
    return import.meta.env.VITE_WS_URL;
  }
  
  // For local on-premises: use localhost or current host
  const hostname = window.location.hostname;
  const isLocalhost = hostname === 'localhost' || hostname === '127.0.0.1' || hostname === '';
  
  if (isLocalhost) {
    return 'ws://localhost:8000';
  }
  
  // For network access: use ws/wss based on protocol
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  return `${protocol}//${hostname}:8000`;
};

const API = getApiBase();
const WS = getWsBase();

export async function getJSON(path) {
  const url = path.startsWith('http') ? path : `${API}${path}`;
  const r = await fetch(url);
  if (!r.ok) throw new Error(`HTTP ${r.status}`);
  return r.json();
}

export async function postJSON(path, body) {
  const url = path.startsWith('http') ? path : `${API}${path}`;
  const r = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body ?? {}),
  });
  if (!r.ok) throw new Error(`HTTP ${r.status}`);
  return r.json();
}

export function wsUrl() {
  return `${WS}/ws/events`;
}
