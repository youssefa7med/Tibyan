# Settings Configuration Guide

## 📹 Camera/Video Source Settings

### Video Source Options

1. **Camera Index** (Default: `0`)
   - Use `0`, `1`, `2`, etc. for camera devices
   - `0` = First camera
   - `1` = Second camera
   - Test which camera index works on your system

2. **Video File Path**
   - Enter full path: `C:\Videos\test.mp4`
   - Or relative path: `videos/test.mp4`
   - Supported formats: `.mp4`, `.avi`, `.mov`, `.mkv`, `.flv`

3. **RTSP Stream**
   - Format: `rtsp://username:password@ip:port/stream`
   - Example: `rtsp://admin:password123@192.168.1.100:554/stream1`

4. **HTTP Stream**
   - Format: `http://ip:port/stream`
   - Example: `http://192.168.1.100:8080/video`

### Mode Selection

- **Demo Mode**: Uses simulated data (no camera needed)
- **Real Mode**: Processes actual video from source (requires camera/file/stream)

## 📱 Telegram Settings

### Setup Instructions

1. **Create Telegram Bot:**
   - Open Telegram and search for `@BotFather`
   - Send `/newbot` command
   - Follow instructions to create your bot
   - Copy the bot token (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

2. **Get Your Chat ID:**
   - Search for `@userinfobot` on Telegram
   - Send any message to it
   - It will reply with your chat ID (a number like `123456789`)

3. **Configure in Backend:**
   - Edit `backend/.env` file
   - Add these lines:
     ```env
     TELEGRAM_ENABLED=true
     TELEGRAM_TOKEN=your_bot_token_here
     TELEGRAM_CHAT_ID=your_chat_id_here
     TELEGRAM_COOLDOWN_SECONDS=30
     ```

4. **Enable in Settings:**
   - Go to Settings page
   - Enable "Enable Telegram" checkbox
   - Set cooldown time (seconds between messages)
   - Click "Save & Apply"
   - Click "Test Connection" to verify

### Telegram Settings Explained

- **Enable Telegram**: Turn on/off Telegram notifications
- **Cooldown (seconds)**: Minimum time between messages (prevents spam)
  - Recommended: 30-60 seconds
  - Range: 1-300 seconds

### Testing Telegram

1. Click "Test Connection" button in Settings
2. Check the result:
   - ✅ Green = Message sent successfully
   - ❌ Red = Check token, chat ID, or enable status
3. Check your Telegram - you should receive a test message

## 🎯 Detection Settings

### Unsafe Threshold
- **Default**: 3
- **Range**: 1-30
- **Meaning**: Number of consecutive frames before marking as UNSAFE
- **Lower** = Faster detection (may have false positives)
- **Higher** = More stable (may delay alerts)

### Anti-Flicker
- **Enabled by default**
- Prevents rapid status changes
- Stabilizes detection decisions

### History Size
- **Default**: 5
- **Range**: 1-30
- Number of frames to keep in history for anti-flicker

### Change Threshold
- **Default**: 3
- **Range**: 1-30
- Frames required to change status (prevents flickering)

## ⚙️ Advanced Settings

### Adaptive Confidence
- Auto-adjusts detection sensitivity based on scene conditions
- **Recommended**: Enabled

### EMA Temporal
- Uses Exponential Moving Average for smoother decisions
- **Recommended**: Enabled

### Occlusion Detection
- Handles overlapping persons intelligently
- **Recommended**: Enabled

### Scene Quality Analysis
- Adapts to lighting and blur conditions
- **Recommended**: Enabled

### PPE Memory
- Remembers last seen PPE during brief occlusions
- **Recommended**: Enabled

### Body Proportions
- Uses anthropometric data for smarter matching
- **Recommended**: Enabled

## 💾 Saving Settings

1. Configure all settings as needed
2. Click "Save & Apply" button
3. Settings are saved to backend
4. Changes take effect immediately (for most settings)
5. Some settings require restarting monitoring

## 🔄 Settings Persistence

- Settings are saved in backend memory
- To persist across restarts, also update `backend/.env` file
- Telegram token/chat_id must be in `.env` file (not in UI for security)

## ✅ Verification Checklist

After configuring settings:

- [ ] Video source configured (if using real mode)
- [ ] Mode selected (demo/real)
- [ ] Telegram token added to `.env`
- [ ] Telegram chat ID added to `.env`
- [ ] Telegram enabled in Settings
- [ ] Telegram test successful
- [ ] Detection thresholds set appropriately
- [ ] Advanced features enabled as needed
- [ ] Settings saved successfully

## 🆘 Troubleshooting

### Telegram Not Working

1. Check `.env` file has correct token and chat ID
2. Verify "Enable Telegram" is checked in Settings
3. Test connection - check error message
4. Check backend logs for Telegram errors
5. Verify bot token is correct (no extra spaces)
6. Verify chat ID is correct (numeric only)

### Camera Not Working

1. Check camera index (try 0, 1, 2, etc.)
2. Verify camera is not used by another application
3. Check file path is correct (if using video file)
4. Verify RTSP stream URL is correct (if using stream)
5. Check backend logs for camera errors

### Settings Not Saving

1. Check browser console for errors
2. Verify backend is running
3. Check backend logs for errors
4. Try refreshing page and checking settings again





