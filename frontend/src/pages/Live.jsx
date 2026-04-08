import { useEffect, useRef, useState } from "react";
import { StatusBadge } from "../components/StatusBadge";
import { postJSON, getJSON } from "../api";

// Get API base URL for video stream
const getApiBase = () => {
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }
  const hostname = window.location.hostname;
  const isLocalhost = hostname === 'localhost' || hostname === '127.0.0.1' || hostname === '';
  if (isLocalhost) {
    return 'http://localhost:8000';
  }
  return `${window.location.protocol}//${hostname}:8000`;
};

export default function Live({ tick }) {
  const people = tick?.people || [];
  const counts = tick?.counts || { total: 0, safe: 0, check: 0, unsafe: 0 };
  const [running, setRunning] = useState(false);
  const [config, setConfig] = useState(null);
  const canvasRef = useRef(null);
  const videoRef = useRef(null);
  const imgRef = useRef(null);
  const [videoError, setVideoError] = useState("");
  const [useVideoStream, setUseVideoStream] = useState(false);

  useEffect(() => {
    getJSON("/api/config").then(setConfig);
  }, []);

  // Continuous redraw loop
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    let animationFrameId;
    
    const draw = () => {
      const ctx = canvas.getContext("2d");
      const width = canvas.width;
      const height = canvas.height;

    // Clear canvas with dark gray background (not pure black)
    ctx.fillStyle = "#0a0a0a";
    ctx.fillRect(0, 0, width, height);

    // Draw brighter grid pattern for visual feedback
    ctx.strokeStyle = "#2a2a2a";
    ctx.lineWidth = 1;
    for (let x = 0; x < width; x += 40) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, height);
      ctx.stroke();
    }
    for (let y = 0; y < height; y += 40) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
      ctx.stroke();
    }

    // Draw center message with better visibility
    ctx.fillStyle = "#888888";
    ctx.font = "bold 18px Arial";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    
    if (!running) {
      ctx.fillStyle = "#aaaaaa";
      ctx.fillText("Click 'Start' to begin monitoring", width / 2, height / 2 - 30);
      ctx.fillStyle = "#666666";
      ctx.font = "14px Arial";
      ctx.fillText("Video will appear here when processing", width / 2, height / 2 + 10);
    } else {
      ctx.fillStyle = "#00ff00";
      ctx.font = "bold 20px Arial";
      ctx.fillText("✓ Monitoring Active", width / 2, height / 2 - 30);
      ctx.fillStyle = "#888888";
      ctx.font = "14px Arial";
      ctx.fillText(`Mode: ${config?.mode || "demo"} | FPS: ${tick?.fps?.toFixed(1) || "0.0"} | Frame: ${tick?.frame_id || 0}`, width / 2, height / 2 + 10);
      
      // Draw animated pulse effect when running
      const time = Date.now() / 1000;
      const pulse = Math.sin(time * 2) * 0.1 + 0.9;
      ctx.fillStyle = `rgba(0, 255, 0, ${0.1 * pulse})`;
      ctx.fillRect(0, 0, width, height);
    }

    // Draw bounding boxes for detected people
    if (people && people.length > 0) {
      people.forEach(p => {
        const [x1, y1, x2, y2] = p.box || [0, 0, 0, 0];
        
        // Skip if box is invalid
        if (!x1 && !y1 && !x2 && !y2) return;
        
        // Scale coordinates to canvas size (assuming 1280x720 source)
        const scaleX = width / 1280;
        const scaleY = height / 720;
        
        const sx1 = x1 * scaleX;
        const sy1 = y1 * scaleY;
        const sw = (x2 - x1) * scaleX;
        const sh = (y2 - y1) * scaleY;

        // Skip if dimensions are invalid
        if (sw <= 0 || sh <= 0) return;

        // Choose color based on status
        let color = "#00ff00"; // Green for SAFE
        if (p.status === "CHECK") color = "#ffa500"; // Orange for CHECK
        if (p.status === "UNSAFE") color = "#ff0000"; // Red for UNSAFE

        // Draw bounding box with shadow
        ctx.shadowColor = color;
        ctx.shadowBlur = 10;
        ctx.strokeStyle = color;
        ctx.lineWidth = 3;
        ctx.strokeRect(sx1, sy1, sw, sh);
        ctx.shadowBlur = 0;

        // Draw label background
        const label = `ID ${p.id} • ${p.status}`;
        ctx.font = "bold 14px Arial";
        const metrics = ctx.measureText(label);
        const labelWidth = metrics.width + 10;
        const labelHeight = 20;

        ctx.fillStyle = "rgba(0, 0, 0, 0.8)";
        ctx.fillRect(sx1, sy1 - labelHeight, labelWidth, labelHeight);

        // Draw label text
        ctx.fillStyle = color;
        ctx.textAlign = "left";
        ctx.textBaseline = "top";
        ctx.fillText(label, sx1 + 5, sy1 - labelHeight + 3);

        // Draw PPE indicators
        if (!p.helmet || !p.vest) {
          ctx.fillStyle = "rgba(255, 0, 0, 0.2)";
          ctx.fillRect(sx1, sy1, sw, sh);
        }
      });
    }
    
    // Continue animation loop (always, not conditionally)
    animationFrameId = requestAnimationFrame(draw);
  };

    // Start the animation loop
    draw();

    // Cleanup
    return () => {
      if (animationFrameId) {
        cancelAnimationFrame(animationFrameId);
      }
    };
  }, [people, running, tick, config]);

  const handleStart = async () => {
    try {
      const result = await postJSON("/api/monitor/start");
      setRunning(true);
      setVideoError("");
      
      // Enable video stream if in real mode
      if (config?.mode === "real") {
        setUseVideoStream(true);
      }
    } catch (error) {
      setVideoError("Failed to start monitoring: " + error.message);
      setRunning(false);
    }
  };

  const handleStop = async () => {
    try {
      await postJSON("/api/monitor/stop");
      setRunning(false);
      setUseVideoStream(false);
    } catch (error) {
      setVideoError("Failed to stop monitoring: " + error.message);
    }
  };
  
  // Update video stream URL when running state changes
  useEffect(() => {
    if (running && config?.mode === "real") {
      setUseVideoStream(true);
    } else {
      setUseVideoStream(false);
    }
  }, [running, config]);

  // Update running state from tick
  useEffect(() => {
    if (tick?.config?.mode) {
      // Check if monitoring is actually running
      getJSON("/api/stats").then(stats => {
        setRunning(stats.running || false);
      });
    }
  }, [tick]);

  return (
    <div className="w-screen h-screen flex flex-col">
      {/* Header */}
      <div className="flex-none px-3 md:px-4 py-3 md:py-4 border-b border-white/10 bg-ink-900/50">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
          <div>
            <div className="text-white font-bold text-lg md:text-xl">Live Monitor</div>
            <div className="text-white/60 text-xs md:text-sm">
              {config?.mode === "real" ? "Live video processing" : "Demo mode - Simulated monitoring"}
            </div>
          </div>
          <div className="flex gap-2 flex-wrap">
            <button 
              onClick={handleStart} 
              disabled={running}
              className={`px-3 md:px-4 py-2 rounded-xl font-bold text-sm transition-all ${
                running 
                  ? "bg-gray-500/50 text-gray-300 cursor-not-allowed" 
                  : "bg-brand-500 text-black hover:bg-brand-400"
              }`}
            >
              {running ? "Running..." : "Start"}
            </button>
            <button 
              onClick={handleStop}
              disabled={!running}
              className={`px-3 md:px-4 py-2 rounded-xl font-semibold text-sm border transition-all ${
                !running
                  ? "bg-gray-500/50 text-gray-300 border-gray-500/50 cursor-not-allowed"
                  : "bg-white/10 text-white border-white/10 hover:bg-white/20"
              }`}
            >
              Stop
            </button>
          </div>
        </div>

        {videoError && (
          <div className="card p-2 md:p-3 bg-red-500/10 border-red-500/30 mt-3">
            <div className="text-red-300 font-semibold text-xs md:text-sm">{videoError}</div>
          </div>
        )}
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-hidden flex flex-col lg:flex-row px-3 md:px-4 py-3 md:py-4 gap-3 md:gap-4">
        {/* Video Feed */}
        <div className="flex-1 min-w-0 min-h-0 flex flex-col">
          <div className="flex-1 card p-2 md:p-3 relative rounded-2xl overflow-hidden border border-white/10 bg-gray-900">
            {/* Video stream for real mode */}
            {useVideoStream && config?.mode === "real" && running ? (
              <img
                ref={imgRef}
                src={`${getApiBase()}/api/video/stream`}
                alt="Video Stream"
                className="w-full h-full object-contain"
                style={{ 
                  display: "block"
                }}
                onError={(e) => {
                  console.error("Video stream error");
                  setUseVideoStream(false);
                  setVideoError("Failed to load video stream. Check camera connection and ensure OpenCV is installed.");
                }}
              />
            ) : (
              /* Canvas for demo mode or when video not available */
              <canvas
                ref={canvasRef}
                width={1280}
                height={720}
                className="w-full h-full object-contain bg-gray-900"
                style={{ 
                  display: "block",
                  backgroundColor: "#0a0a0a"
                }}
              />
            )}

            {/* Stats overlay */}
            <div className="absolute top-3 left-3 card px-3 py-2 bg-black/70 backdrop-blur">
              <div className="text-white text-sm font-bold">Live Stats</div>
              <div className="text-white/70 text-xs mt-1 space-y-1">
                <div>Total: {counts.total} • Safe: <span className="text-green-400">{counts.safe}</span> • Check: <span className="text-yellow-400">{counts.check}</span> • Unsafe: <span className="text-red-400">{counts.unsafe}</span></div>
                <div>FPS: {tick?.fps?.toFixed(1) || "0.0"} • Frame: {tick?.frame_id || 0}</div>
                <div>Mode: {config?.mode || "demo"} • Status: {running ? "🟢 Active" : "⚪ Stopped"}</div>
              </div>
            </div>

            {/* Video source info */}
            {config && (
              <div className="absolute bottom-3 left-3 card px-3 py-2 bg-black/70 backdrop-blur">
                <div className="text-white/70 text-xs">
                  Source: <span className="text-white font-semibold">{config.video_source || "0"}</span>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Persons Panel */}
        <div className="flex-none lg:flex-1 xl:w-80 min-h-0 flex flex-col card p-2 md:p-4">
          <div className="text-white font-bold mb-1 md:mb-2 text-sm md:text-base">Tracked Persons</div>
          <div className="text-white/60 text-xs mb-2 md:mb-3">ID • Helmet • Vest • Status</div>
          <div className="flex-1 overflow-y-auto space-y-2 pr-1 min-h-0">
            {people.length > 0 ? (
              people.map(p => (
                <div key={p.id} className="rounded-xl bg-white/5 border border-white/10 p-3 hover:bg-white/10 transition-all">
                  <div className="flex items-center justify-between">
                    <div className="text-white font-bold">Worker #{p.id}</div>
                    <StatusBadge status={p.status} />
                  </div>
                  <div className="text-white/70 text-sm mt-2 space-y-1">
                    <div>
                      Helmet: <span className={p.helmet ? "text-green-300 font-semibold" : "text-red-300 font-semibold"}>
                        {p.helmet ? "✓ Yes" : "✗ No"}
                      </span>
                    </div>
                    <div>
                      Vest: <span className={p.vest ? "text-green-300 font-semibold" : "text-red-300 font-semibold"}>
                        {p.vest ? "✓ Yes" : "✗ No"}
                      </span>
                    </div>
                    <div className="text-white/50 text-xs mt-1">
                      Unsafe counter: {p.unsafe_counter || 0}
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-white/50 text-center py-8">
                {running ? (
                  <>
                    <div className="text-4xl mb-2">👀</div>
                    <div>No persons detected yet</div>
                    <div className="text-xs mt-2">Waiting for detections...</div>
                  </>
                ) : (
                  <>
                    <div className="text-4xl mb-2">▶️</div>
                    <div>Click Start to begin</div>
                    <div className="text-xs mt-2">Monitoring will begin when started</div>
                  </>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
