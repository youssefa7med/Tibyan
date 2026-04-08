import { useEffect, useState } from "react";
import { getJSON, postJSON } from "../api";

export default function Settings() {
  const [cfg, setCfg] = useState(null);
  const [saving, setSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState("");
  const [telegramTestResult, setTelegramTestResult] = useState(null);

  useEffect(() => {
    getJSON("/api/config").then(setCfg);
  }, []);

  if (!cfg) return <div className="max-w-6xl mx-auto px-4 py-6 text-white/70">Loading...</div>;

  async function save() {
    setSaving(true);
    setSaveMessage("");
    try {
      const result = await postJSON("/api/config", cfg);
      setSaveMessage("Settings saved successfully!");
      setTimeout(() => setSaveMessage(""), 3000);
    } catch (error) {
      setSaveMessage("Error saving settings: " + error.message);
    } finally {
      setSaving(false);
    }
  }

  async function testTelegram() {
    setTelegramTestResult(null);
    try {
      const result = await postJSON("/api/alerts/test-telegram");
      setTelegramTestResult({
        success: result.telegram_sent,
        message: result.telegram_sent
          ? "Test message sent successfully!"
          : "Telegram not enabled or configuration invalid",
        preview: result.message_preview
      });
    } catch (error) {
      setTelegramTestResult({
        success: false,
        message: "Error testing Telegram: " + error.message
      });
    }
  }

  function set(k, v) {
    setCfg(prev => ({ ...prev, [k]: v }));
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-6 pb-12">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6">
        <div>
          <div className="text-white font-bold text-xl">Settings</div>
          <div className="text-white/60 text-sm">Configure camera, Telegram, and system parameters</div>
        </div>
        <div className="flex gap-2">
          <button
            onClick={save}
            className="px-6 py-2 rounded-xl bg-brand-500 text-black font-bold hover:bg-brand-400 transition-all"
            disabled={saving}
          >
            {saving ? "Saving..." : "Save & Apply"}
          </button>
        </div>
      </div>

      <div className="space-y-6 overflow-y-auto" style={{ maxHeight: 'calc(100vh - 280px)' }}>
        {saveMessage && (
          <div className={`card p-4 ${saveMessage.includes("Error") ? "bg-red-500/10 border-red-500/30" : "bg-green-500/10 border-green-500/30"}`}>
            <div className={`font-semibold ${saveMessage.includes("Error") ? "text-red-300" : "text-green-300"}`}>
              {saveMessage}
            </div>
          </div>
        )}

        {/* Camera/Video Source Section */}
        <div className="card p-6">
          <div className="flex items-center gap-3 mb-4">
            <span className="text-3xl">📹</span>
            <div>
              <div className="text-white font-bold text-lg">Camera & Video Source</div>
              <div className="text-white/60 text-sm">Configure video input source</div>
            </div>
          </div>

          <div className="mb-4 p-4 rounded-xl bg-blue-500/10 border border-blue-500/30">
            <div className="text-blue-300 font-semibold text-sm mb-2 flex items-center gap-2">
              <span>💡</span> What This Does
            </div>
            <div className="text-white/70 text-xs space-y-1">
              <div>• <strong>Video Source:</strong> Specifies where the system gets video input for PPE detection</div>
              <div>• <strong>Mode:</strong> Demo uses simulated data, Real processes actual video from your camera/stream</div>
              <div>• <strong>Confidence:</strong> How certain the AI must be before detecting PPE (helmet/vest)</div>
            </div>
            <div className="mt-3 pt-3 border-t border-blue-500/20">
              <div className="text-blue-200 font-semibold text-xs mb-1">✅ Recommended Settings:</div>
              <div className="text-white/60 text-xs space-y-1">
                <div>• <strong>For Testing:</strong> Use Demo mode with confidence 0.30</div>
                <div>• <strong>For Production:</strong> Use Real mode with confidence 0.40-0.50 (higher = fewer false positives)</div>
                <div>• <strong>Video Source:</strong> Start with "0" for default camera, or use RTSP URL for IP cameras</div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="md:col-span-2">
              <label className="text-white/70 text-sm font-semibold">Video Source</label>
              <input
                value={cfg.video_source || "0"}
                onChange={e => set("video_source", e.target.value)}
                className="mt-2 w-full rounded-xl bg-white/5 border border-white/10 px-4 py-3 text-white focus:outline-none focus:border-brand-500"
                placeholder="0, 1, 2 (camera index) or /path/to/video.mp4 or rtsp://..."
              />
              <div className="text-white/50 text-xs mt-2 space-y-1">
                <div>• <strong>Camera:</strong> Use 0, 1, 2, etc. for camera index</div>
                <div>• <strong>Video File:</strong> Enter full path like C:\videos\test.mp4</div>
                <div>• <strong>RTSP Stream:</strong> Enter rtsp://username:password@ip:port/stream</div>
                <div>• <strong>HTTP Stream:</strong> Enter http://ip:port/stream</div>
              </div>
            </div>

            <div className="md:col-span-2">
              <label className="text-white/70 text-sm font-semibold">📍 Camera Location/Name</label>
              <input
                value={cfg.camera_location || "Camera 1"}
                onChange={e => set("camera_location", e.target.value)}
                className="mt-2 w-full rounded-xl bg-white/5 border border-white/10 px-4 py-3 text-white focus:outline-none focus:border-brand-500"
                placeholder="e.g., Main Entrance, Warehouse A, Loading Dock..."
              />
              <div className="text-white/50 text-xs mt-2">
                This location name will be displayed on the Live Monitor page for camera identification.
              </div>
            </div>

            <div>
              <label className="text-white/70 text-sm font-semibold">Mode</label>
              <select
                value={cfg.mode || "demo"}
                onChange={e => set("mode", e.target.value)}
                className="mt-2 w-full rounded-xl bg-white/5 border border-white/10 px-4 py-3 text-white focus:outline-none focus:border-brand-500"
              >
                <option value="demo">Demo Mode (Simulated Data)</option>
                <option value="real">Real Mode (Live Video Processing)</option>
              </select>
              <div className="text-white/50 text-xs mt-2">
                Demo mode uses simulated data. Real mode processes actual video.
              </div>
            </div>

            <div>
              <label className="text-white/70 text-sm font-semibold">
                Confidence Threshold: {cfg.confidence?.toFixed(2) || "0.30"}
              </label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.01"
                value={cfg.confidence || 0.3}
                onChange={e => set("confidence", Number(e.target.value))}
                className="mt-2 w-full"
              />
              <div className="text-white/50 text-xs mt-2">
                Detection confidence threshold (0.0 - 1.0). Lower = more detections, Higher = more accurate.
              </div>
            </div>
          </div>
        </div>

        {/* Telegram Settings Section */}
        <div className="card p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <span className="text-3xl">📱</span>
              <div>
                <div className="text-white font-bold text-lg">Telegram Notifications</div>
                <div className="text-white/60 text-sm">Configure Telegram bot for safety alerts</div>
              </div>
            </div>
            <button
              onClick={testTelegram}
              className="px-4 py-2 rounded-xl bg-blue-500/20 text-blue-300 border border-blue-500/30 hover:bg-blue-500/30 transition-all text-sm font-semibold"
            >
              Test Connection
            </button>
          </div>

          {telegramTestResult && (
            <div className={`mb-4 p-4 rounded-xl ${telegramTestResult.success ? "bg-green-500/10 border border-green-500/30" : "bg-red-500/10 border border-red-500/30"}`}>
              <div className={`font-semibold ${telegramTestResult.success ? "text-green-300" : "text-red-300"}`}>
                {telegramTestResult.message}
              </div>
              {telegramTestResult.preview && (
                <div className="text-white/70 text-xs mt-2 font-mono bg-black/30 p-2 rounded">
                  {telegramTestResult.preview}
                </div>
              )}
            </div>
          )}

          <div className="mb-4 p-4 rounded-xl bg-blue-500/10 border border-blue-500/30">
            <div className="text-blue-300 font-semibold text-sm mb-2 flex items-center gap-2">
              <span>💡</span> What This Does
            </div>
            <div className="text-white/70 text-xs space-y-1">
              <div>• <strong>Telegram Notifications:</strong> Sends instant alerts to your phone/computer via Telegram when safety violations are detected</div>
              <div>• <strong>Cooldown:</strong> Prevents spam by limiting how often messages are sent (e.g., 30 seconds = max 1 message per 30 seconds)</div>
              <div>• <strong>Use Case:</strong> Get real-time alerts when workers are detected without helmets or vests</div>
            </div>
            <div className="mt-3 pt-3 border-t border-blue-500/20">
              <div className="text-blue-200 font-semibold text-xs mb-1">✅ Recommended Settings:</div>
              <div className="text-white/60 text-xs space-y-1">
                <div>• <strong>Enable:</strong> Yes, if you want instant mobile notifications</div>
                <div>• <strong>Cooldown:</strong> 30-60 seconds (prevents message flooding)</div>
                <div>• <strong>Setup Required:</strong> You must configure TELEGRAM_TOKEN and TELEGRAM_CHAT_ID in backend/.env file first</div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="flex items-center justify-between rounded-xl bg-white/5 border border-white/10 p-4">
              <div>
                <div className="text-white font-semibold">Enable Telegram</div>
                <div className="text-white/50 text-xs">Send alerts to Telegram</div>
              </div>
              <input
                type="checkbox"
                checked={cfg.telegram_enabled || false}
                onChange={e => set("telegram_enabled", e.target.checked)}
                className="w-5 h-5"
              />
            </div>

            <div>
              <label className="text-white/70 text-sm font-semibold">Cooldown (seconds)</label>
              <input
                type="number"
                min="1"
                max="300"
                value={cfg.telegram_cooldown_seconds || 30}
                onChange={e => set("telegram_cooldown_seconds", Number(e.target.value))}
                className="mt-2 w-full rounded-xl bg-white/5 border border-white/10 px-4 py-3 text-white focus:outline-none focus:border-brand-500"
              />
              <div className="text-white/50 text-xs mt-2">
                Minimum time between Telegram messages (prevents spam)
              </div>
            </div>
          </div>

          <div className="mt-4 p-4 rounded-xl bg-yellow-500/10 border border-yellow-500/30">
            <div className="text-yellow-300 font-semibold text-sm mb-2">⚠️ Telegram Configuration</div>
            <div className="text-white/70 text-xs space-y-1">
              <div><strong>To use Telegram notifications:</strong></div>
              <div>1. Create a bot with @BotFather on Telegram</div>
              <div>2. Get your bot token</div>
              <div>3. Get your chat ID (use @userinfobot or send a message and check API)</div>
              <div>4. Add to <code className="bg-black/30 px-1 rounded">backend/.env</code>:</div>
              <div className="ml-4 font-mono text-xs">
                TELEGRAM_ENABLED=true<br />
                TELEGRAM_TOKEN=your_bot_token<br />
                TELEGRAM_CHAT_ID=your_chat_id
              </div>
              <div className="mt-2 text-yellow-300">Note: Settings here enable/disable Telegram. Token and Chat ID must be in .env file.</div>
            </div>
          </div>
        </div>

        {/* Detection Settings */}
        <div className="card p-6">
          <div className="flex items-center gap-3 mb-4">
            <span className="text-3xl">🎯</span>
            <div>
              <div className="text-white font-bold text-lg">Detection Settings</div>
              <div className="text-white/60 text-sm">Configure detection parameters</div>
            </div>
          </div>

          <div className="mb-4 p-4 rounded-xl bg-blue-500/10 border border-blue-500/30">
            <div className="text-blue-300 font-semibold text-sm mb-2 flex items-center gap-2">
              <span>💡</span> What This Does
            </div>
            <div className="text-white/70 text-xs space-y-1">
              <div>• <strong>Unsafe Threshold:</strong> How many consecutive frames a person must be missing PPE before marked as UNSAFE</div>
              <div>• <strong>Anti-Flicker:</strong> Prevents status from rapidly changing (SAFE→UNSAFE→SAFE) due to detection errors</div>
              <div>• <strong>History Size:</strong> Number of past frames to remember for smoothing decisions</div>
              <div>• <strong>Change Threshold:</strong> How many frames needed to confirm a status change</div>
            </div>
            <div className="mt-3 pt-3 border-t border-blue-500/20">
              <div className="text-blue-200 font-semibold text-xs mb-1">✅ Recommended Settings:</div>
              <div className="text-white/60 text-xs space-y-1">
                <div>• <strong>Unsafe Threshold:</strong> 3-5 frames (too low = false alarms, too high = delayed detection)</div>
                <div>• <strong>Anti-Flicker:</strong> ON (recommended for stable, reliable detection)</div>
                <div>• <strong>History Size:</strong> 5-7 frames (balances responsiveness and stability)</div>
                <div>• <strong>Change Threshold:</strong> 3 frames (prevents flickering status changes)</div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-white/70 text-sm font-semibold">Unsafe Threshold</label>
              <input
                type="number"
                min="1"
                max="30"
                value={cfg.unsafe_threshold || 3}
                onChange={e => set("unsafe_threshold", Number(e.target.value))}
                className="mt-2 w-full rounded-xl bg-white/5 border border-white/10 px-4 py-3 text-white focus:outline-none focus:border-brand-500"
              />
              <div className="text-white/50 text-xs mt-2">
                Consecutive frames before marking as UNSAFE (1-30)
              </div>
            </div>

            <div className="flex items-center justify-between rounded-xl bg-white/5 border border-white/10 p-4">
              <div>
                <div className="text-white font-semibold">Anti-Flicker</div>
                <div className="text-white/50 text-xs">Stabilize status decisions</div>
              </div>
              <input
                type="checkbox"
                checked={cfg.anti_flicker_enabled !== false}
                onChange={e => set("anti_flicker_enabled", e.target.checked)}
                className="w-5 h-5"
              />
            </div>

            <div>
              <label className="text-white/70 text-sm font-semibold">History Size</label>
              <input
                type="number"
                min="1"
                max="30"
                value={cfg.status_history_size || 5}
                onChange={e => set("status_history_size", Number(e.target.value))}
                className="mt-2 w-full rounded-xl bg-white/5 border border-white/10 px-4 py-3 text-white focus:outline-none focus:border-brand-500"
              />
              <div className="text-white/50 text-xs mt-2">
                Number of frames to keep in history for anti-flicker
              </div>
            </div>

            <div>
              <label className="text-white/70 text-sm font-semibold">Change Threshold</label>
              <input
                type="number"
                min="1"
                max="30"
                value={cfg.status_change_threshold || 3}
                onChange={e => set("status_change_threshold", Number(e.target.value))}
                className="mt-2 w-full rounded-xl bg-white/5 border border-white/10 px-4 py-3 text-white focus:outline-none focus:border-brand-500"
              />
              <div className="text-white/50 text-xs mt-2">
                Frames required to change status
              </div>
            </div>
          </div>
        </div>

        {/* Advanced Settings (Collapsible) */}
        <div className="card p-6">
          <div className="flex items-center gap-3 mb-4">
            <span className="text-3xl">⚙️</span>
            <div>
              <div className="text-white font-bold text-lg">Advanced Settings</div>
              <div className="text-white/60 text-sm">Fine-tune detection algorithms</div>
            </div>
          </div>

          <div className="mb-4 p-4 rounded-xl bg-purple-500/10 border border-purple-500/30">
            <div className="text-purple-300 font-semibold text-sm mb-2 flex items-center gap-2">
              <span>🧠</span> What These AI Features Do
            </div>
            <div className="text-white/70 text-xs space-y-2">
              <div>
                <strong className="text-purple-200">• Adaptive Confidence:</strong>
                <div className="ml-4 mt-1">Automatically adjusts detection sensitivity based on lighting and scene conditions. Helps maintain accuracy in varying environments.</div>
              </div>
              <div>
                <strong className="text-purple-200">• EMA Temporal:</strong>
                <div className="ml-4 mt-1">Uses Exponential Moving Average to smooth detection over time. Reduces jitter and creates more stable status decisions.</div>
              </div>
              <div>
                <strong className="text-purple-200">• Occlusion Detection:</strong>
                <div className="ml-4 mt-1">Detects when workers overlap or block each other. Prevents false negatives when PPE is temporarily hidden.</div>
              </div>
              <div>
                <strong className="text-purple-200">• Scene Quality Analysis:</strong>
                <div className="ml-4 mt-1">Analyzes video quality (brightness, blur, contrast). Adapts detection to poor lighting or low-quality cameras.</div>
              </div>
              <div>
                <strong className="text-purple-200">• PPE Memory:</strong>
                <div className="ml-4 mt-1">Remembers last seen PPE for each person. If helmet briefly disappears (e.g., turned away), assumes still wearing it.</div>
              </div>
              <div>
                <strong className="text-purple-200">• Body Proportions:</strong>
                <div className="ml-4 mt-1">Uses human body ratios to better match helmets and vests to correct person. Improves accuracy in crowded scenes.</div>
              </div>
            </div>
            <div className="mt-3 pt-3 border-t border-purple-500/20">
              <div className="text-purple-200 font-semibold text-xs mb-1">✅ Recommended Settings:</div>
              <div className="text-white/60 text-xs space-y-1">
                <div>• <strong>For Best Accuracy:</strong> Enable ALL features (recommended for production)</div>
                <div>• <strong>For Performance:</strong> Disable Occlusion Detection and Scene Quality (faster processing)</div>
                <div>• <strong>For Crowded Areas:</strong> Keep Body Proportions and Occlusion Detection ON</div>
                <div>• <strong>For Poor Lighting:</strong> Keep Adaptive Confidence and Scene Quality ON</div>
                <div>• <strong>For Simple Setups:</strong> Just enable Anti-Flicker and PPE Memory (basic but effective)</div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="flex items-center justify-between rounded-xl bg-white/5 border border-white/10 p-4">
              <div>
                <div className="text-white font-semibold">Adaptive Confidence</div>
                <div className="text-white/50 text-xs">Auto-adjust detection sensitivity</div>
              </div>
              <input
                type="checkbox"
                checked={cfg.adaptive_confidence_enabled !== false}
                onChange={e => set("adaptive_confidence_enabled", e.target.checked)}
                className="w-5 h-5"
              />
            </div>

            <div className="flex items-center justify-between rounded-xl bg-white/5 border border-white/10 p-4">
              <div>
                <div className="text-white font-semibold">EMA Temporal</div>
                <div className="text-white/50 text-xs">Smooth status decisions</div>
              </div>
              <input
                type="checkbox"
                checked={cfg.use_ema_temporal !== false}
                onChange={e => set("use_ema_temporal", e.target.checked)}
                className="w-5 h-5"
              />
            </div>

            <div className="flex items-center justify-between rounded-xl bg-white/5 border border-white/10 p-4">
              <div>
                <div className="text-white font-semibold">Occlusion Detection</div>
                <div className="text-white/50 text-xs">Handle overlapping persons</div>
              </div>
              <input
                type="checkbox"
                checked={cfg.occlusion_detection_enabled !== false}
                onChange={e => set("occlusion_detection_enabled", e.target.checked)}
                className="w-5 h-5"
              />
            </div>

            <div className="flex items-center justify-between rounded-xl bg-white/5 border border-white/10 p-4">
              <div>
                <div className="text-white font-semibold">Scene Quality Analysis</div>
                <div className="text-white/50 text-xs">Adapt to lighting conditions</div>
              </div>
              <input
                type="checkbox"
                checked={cfg.scene_quality_enabled !== false}
                onChange={e => set("scene_quality_enabled", e.target.checked)}
                className="w-5 h-5"
              />
            </div>

            <div className="flex items-center justify-between rounded-xl bg-white/5 border border-white/10 p-4">
              <div>
                <div className="text-white font-semibold">PPE Memory</div>
                <div className="text-white/50 text-xs">Remember last seen PPE</div>
              </div>
              <input
                type="checkbox"
                checked={cfg.ppe_memory_enabled !== false}
                onChange={e => set("ppe_memory_enabled", e.target.checked)}
                className="w-5 h-5"
              />
            </div>

            <div className="flex items-center justify-between rounded-xl bg-white/5 border border-white/10 p-4">
              <div>
                <div className="text-white font-semibold">Body Proportions</div>
                <div className="text-white/50 text-xs">Use anthropometric matching</div>
              </div>
              <input
                type="checkbox"
                checked={cfg.use_body_proportions !== false}
                onChange={e => set("use_body_proportions", e.target.checked)}
                className="w-5 h-5"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
