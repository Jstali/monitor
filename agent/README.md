# 📦 Employee Monitoring Agent - Installation Package

## For Employees

### What is this?
This is the Employee Monitoring Agent that captures screenshots and tracks activity on your work computer. It works together with the web dashboard.

---

## 🚀 Quick Installation (3 Steps)

### Step 1: Download
You received this package from your organization. Extract it to a folder on your computer (e.g., Desktop).

### Step 2: Install
**On macOS/Linux:**
```bash
cd path/to/agent
./install.sh
```

**On Windows:**
```cmd
cd path\to\agent
install.bat
```

### Step 3: Login
When prompted, enter:
- Your work email
- Your work password

A desktop shortcut will be created automatically.

---

## 📱 Daily Usage

### Starting Monitoring:
1. **Double-click** the desktop shortcut (`StartMonitoring`)
2. Your web dashboard opens automatically
3. **Login** to the dashboard
4. **Click "Start Monitoring"** button
5. Work normally - the agent runs in the background

### Stopping Monitoring:
1. Go to the web dashboard
2. **Click "Stop Monitoring"**
3. Close the terminal/command window

---

## ✅ What Gets Monitored?

- ✅ Screenshots (every 60 seconds by default)
- ✅ Active applications
- ✅ Websites visited
- ✅ Work time tracking

**Privacy Note:** Monitoring only happens when you click "Start Monitoring" in the dashboard. You have full control.

---

## 🔧 System Requirements

- **Operating System:** macOS 10.14+, Windows 10+, or Linux (Ubuntu 18.04+)
- **Python:** 3.8 or higher (installer will check)
- **Internet:** Required for uploading data
- **Disk Space:** ~10 MB

---

## 🆘 Troubleshooting

### "Python not found"
Install Python from: https://www.python.org/downloads/

### "Permission denied" (macOS)
1. System Preferences → Security & Privacy → Privacy
2. Enable **Screen Recording** for Terminal
3. Enable **Accessibility** for Terminal

### "Module not found"
Run the installer again: `./install.sh`

### Token expired
Run: `python3 get_token.py` and enter your credentials again

---

## 📞 Support

For technical support, contact your IT department or system administrator.

---

## 🔒 Security & Privacy

- All data is encrypted during transmission
- Screenshots are stored securely on company servers
- You control when monitoring starts and stops
- Your credentials are never stored in plain text

---

**Version:** 1.0  
**Last Updated:** 2025-11-26
