import { useEffect, useMemo, useRef, useState } from "react";
import { wsUrl } from "../api";

export function useEvents() {
  const [connected, setConnected] = useState(false);
  const [tick, setTick] = useState(null);
  const [logs, setLogs] = useState([]);
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 5;
  const reconnectDelay = 3000; // 3 seconds

  const connect = () => {
    try {
      const url = wsUrl();
      console.log("Connecting to WebSocket:", url);
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log("WebSocket connected");
        setConnected(true);
        reconnectAttempts.current = 0;
      };

      ws.onclose = (event) => {
        console.log("WebSocket closed", event.code, event.reason);
        setConnected(false);
        
        // Attempt to reconnect if not a normal closure
        if (event.code !== 1000 && reconnectAttempts.current < maxReconnectAttempts) {
          reconnectAttempts.current += 1;
          console.log(`Reconnecting... Attempt ${reconnectAttempts.current}/${maxReconnectAttempts}`);
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, reconnectDelay);
        } else if (reconnectAttempts.current >= maxReconnectAttempts) {
          console.error("Max reconnection attempts reached");
        }
      };

      ws.onerror = (error) => {
        console.error("WebSocket error:", error);
        setConnected(false);
      };

      ws.onmessage = (ev) => {
        try {
          const msg = JSON.parse(ev.data);
          if (msg.type === "tick") {
            setTick(msg);
          } else if (msg.type === "logs") {
            // Handle real-time log events
            setLogs((prevLogs) => {
              // Add new log entries to the beginning (newest first)
              const newLogs = [...(msg.entries || []), ...prevLogs];
              // Keep only last 1000 entries to prevent memory issues
              return newLogs.slice(0, 1000);
            });
          } else if (msg.type === "hello") {
            console.log("WebSocket hello received");
            setConnected(true);
          } else if (msg.type === "ping") {
            // Respond to ping
            if (ws.readyState === WebSocket.OPEN) {
              ws.send(JSON.stringify({ type: "pong" }));
            }
          }
        } catch (err) {
          console.error("Error parsing WebSocket message:", err);
        }
      };
    } catch (error) {
      console.error("Failed to create WebSocket:", error);
      setConnected(false);
      
      // Retry connection
      if (reconnectAttempts.current < maxReconnectAttempts) {
        reconnectAttempts.current += 1;
        reconnectTimeoutRef.current = setTimeout(() => {
          connect();
        }, reconnectDelay);
      }
    }
  };

  useEffect(() => {
    connect();

    return () => {
      // Cleanup
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        try {
          wsRef.current.close(1000, "Component unmounting");
        } catch (error) {
          console.error("Error closing WebSocket:", error);
        }
      }
    };
  }, []);

  return { connected, tick, logs };
}
