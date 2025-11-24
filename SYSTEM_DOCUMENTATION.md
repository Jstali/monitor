# Employee Monitoring System - Complete Functionality & API Documentation

**Generated:** 2025-11-22 18:34:09  
**Status:** ✅ Operational

---

## 📊 SYSTEM OVERVIEW

### Core Features
1. ✅ **Selective Monitoring** - Only tracks allowlisted applications/websites
2. ✅ **Screenshot Capture** - Organized in folders by activity
3. ✅ **Activity Logging** - Tracks window titles, URLs, and actions
4. ✅ **Process Mining** - Interactive workflow diagrams
5. ✅ **OCR Extraction** - Analyzes screenshot content
6. ✅ **Step-by-Step Activity Log** - Detailed employee actions

---

## 🔐 AUTHENTICATION ENDPOINTS

### 1. Login
- **Endpoint:** `POST /api/auth/login`
- **Status:** ✅ Working
- **Body:** `{ "email": "user@example.com", "password": "password" }`
- **Response:** `{ "access_token": "...", "employee": {...} }`

### 2. Get Current User
- **Endpoint:** `GET /api/auth/me`
- **Status:** ✅ Working
- **Headers:** `Authorization: Bearer <token>`
- **Response:** Employee details

---

## 🏢 ORGANIZATION ENDPOINTS

### 1. List Organizations
- **Endpoint:** `GET /api/organizations`
- **Status:** ⚠️ Requires Admin Access
- **Access:** Super Admin only

### 2. Get Organization Details
- **Endpoint:** `GET /api/organizations/{id}`
- **Status:** ⚠️ Requires Admin Access
- **Access:** Admin of that organization

---

## 👥 EMPLOYEE ENDPOINTS

### 1. List Employees
- **Endpoint:** `GET /api/employees`
- **Status:** ❌ Not Found (404)
- **Note:** Endpoint may not be implemented

### 2. Employee Statistics
- **Endpoint:** `GET /api/employees/stats`
- **Status:** ❌ Not Found (404)
- **Note:** Endpoint may not be implemented

---

## ⚙️ MONITORING CONFIGURATION ENDPOINTS

### 1. Get Monitoring Config (Allowlist)
- **Endpoint:** `GET /api/monitoring-config`
- **Status:** ✅ Working
- **Response:** List of allowlisted applications and URLs
- **Example:**
  ```json
  [
    {
      "id": 1,
      "config_type": "application",
      "pattern": "cursor",
      "folder_name": "cursor",
      "is_active": true
    },
    {
      "id": 2,
      "config_type": "url",
      "pattern": "https://chatgpt.com",
      "folder_name": "chatgpt",
      "is_active": true
    }
  ]
  ```

### 2. Get Employee Config
- **Endpoint:** `GET /api/monitoring-config/employee`
- **Status:** ❌ Not Found (404)

---

## 📹 MONITORING SESSION ENDPOINTS

### 1. Start Session
- **Endpoint:** `POST /api/monitoring/sessions/start`
- **Status:** ✅ Working (via agent)
- **Body:** `{ "screenshot_interval": 10 }`

### 2. Stop Session
- **Endpoint:** `POST /api/monitoring/sessions/stop`
- **Status:** ✅ Working (via agent)

### 3. Get All Sessions
- **Endpoint:** `GET /api/monitoring/sessions`
- **Status:** ✅ Working
- **Response:** List of all monitoring sessions
- **Example:**
  ```json
  [
    {
      "id": 46,
      "employee_id": 6,
      "start_time": "2025-11-22T12:00:00",
      "end_time": "2025-11-22T14:30:00",
      "is_active": false,
      "screenshot_interval": 10
    }
  ]
  ```

### 4. Get Current Session
- **Endpoint:** `GET /api/monitoring/sessions/current`
- **Status:** ✅ Working
- **Response:** Currently active session or null

---

## 📝 ACTIVITY ENDPOINTS

### 1. Log Activity
- **Endpoint:** `POST /api/monitoring/activities`
- **Status:** ✅ Working (via agent)
- **Body:**
  ```json
  {
    "session_id": 46,
    "application_name": "Cursor",
    "window_title": "ProcessMiningModal.jsx",
    "activity_type": "application"
  }
  ```

### 2. Get Activities
- **Endpoint:** `GET /api/monitoring/activities?session_id={id}`
- **Status:** ✅ Working
- **Response:** List of activities for a session
- **Example:**
  ```json
  [
    {
      "id": 1234,
      "session_id": 46,
      "application_name": "Cursor",
      "window_title": "ProcessMiningModal.jsx",
      "activity_type": "application",
      "timestamp": "2025-11-22T12:05:30"
    }
  ]
  ```

---

## 📸 SCREENSHOT ENDPOINTS

### 1. Upload Screenshot
- **Endpoint:** `POST /api/screenshots/upload`
- **Status:** ✅ Working (via agent)
- **Body:** Multipart form data with file and metadata

### 2. Get Session Screenshots
- **Endpoint:** `GET /api/screenshots/session/{session_id}`
- **Status:** ✅ Working
- **Response:** List of screenshots for a session

### 3. Get Screenshot Details
- **Endpoint:** `GET /api/screenshots/{id}`
- **Status:** ✅ Working
- **Response:** Screenshot metadata including extraction data

### 4. Download Screenshot File
- **Endpoint:** `GET /api/screenshots/{id}/file?token={token}`
- **Status:** ✅ Working
- **Response:** PNG image file

### 5. Extract Screenshot Data (Single)
- **Endpoint:** `POST /api/screenshots/{id}/extract`
- **Status:** ✅ Working
- **Response:** Extracted text and structured data

### 6. Extract Batch
- **Endpoint:** `POST /api/screenshots/extract/batch`
- **Status:** ✅ Working
- **Body:** `{ "screenshot_ids": [1, 2, 3, ...] }`
- **Limit:** Max 50 screenshots per batch
- **Response:**
  ```json
  {
    "message": "Batch processing completed",
    "processed_count": 50,
    "failed_count": 0
  }
  ```

---

## 📊 WORKFLOW & PROCESS MINING ENDPOINTS

### 1. Get Process Map (JSON)
- **Endpoint:** `GET /api/workflow/session/{id}/process-map?format=json`
- **Status:** ✅ Working
- **Response:** Process mining statistics and transitions
- **Example:**
  ```json
  {
    "statistics": {
      "total_activities": 134,
      "unique_activities": 3,
      "total_transitions": 2,
      "activity_distribution": {
        "cursor": 53,
        "https://chatgpt.com": 47,
        "Electron": 34
      },
      "top_transitions": [
        [["Electron", "cursor"], 1],
        [["cursor", "https://chatgpt.com"], 1]
      ]
    }
  }
  ```

### 2. Get Process Map (PNG)
- **Endpoint:** `GET /api/workflow/session/{id}/process-map?format=png&token={token}`
- **Status:** ✅ Working
- **Response:** PNG diagram image

### 3. Get Process Map (CSV)
- **Endpoint:** `GET /api/workflow/session/{id}/process-map?format=csv`
- **Status:** ✅ Working
- **Response:** Event log in CSV format

### 4. Get Workflow Diagram (JSON)
- **Endpoint:** `GET /api/workflow/session/{id}/diagram?format=json`
- **Status:** ✅ Working
- **Response:** Workflow analysis and summary

---

## 🎯 KEY FUNCTIONALITIES

### 1. Selective Monitoring ✅
**How it works:**
- Manager configures allowlist (applications + websites)
- Agent only captures screenshots for allowlisted items
- Non-allowlisted activities are ignored

**Allowlist Items:**
- ✅ Cursor → `cursor/` folder
- ✅ ChatGPT (https://chatgpt.com) → `chatgpt/` folder
- ✅ VS Code/Electron → `vs_code/` folder

### 2. Screenshot Organization ✅
**Folder Structure:**
```
screenshots/
├── cursor/      (53 screenshots)
├── chatgpt/     (47 screenshots)
└── vs_code/     (34 screenshots)
```

### 3. Process Mining Diagram ✅
**Features:**
- Interactive network visualization
- Click on nodes to see details
- Curved edges with frequency counts
- Color-coded by activity frequency
- START and END nodes

### 4. Step-by-Step Activity Log ✅
**When clicking on an activity node:**
- Shows chronological list of actions
- Displays extracted text from screenshots
- Shows app, action, context, and details
- Timeline with timestamps

### 5. OCR Extraction ✅
**Methods:**
- **Primary:** Mistral AI OCR (reads screenshot text)
- **Fallback:** Activity log data (window title, URL)

**Extraction Data Structure:**
```json
{
  "app": "Cursor",
  "action": "Coding",
  "context": "ProcessMiningModal.jsx",
  "details": "User was editing code in Cursor",
  "confidence": 0.90,
  "source": "activity_log_fallback"
}
```

---

## ⚠️ KNOWN ISSUES

### 1. Employee Endpoints (404)
- `/api/employees` - Not implemented
- `/api/employees/stats` - Not implemented
- **Impact:** Low - Not critical for core functionality

### 2. Organization Access (403)
- Requires admin/super admin role
- **Impact:** Low - Expected behavior for security

### 3. OCR Fallback Usage
- Currently using activity log fallback instead of real OCR
- **Reason:** OCR may be timing out or failing
- **Impact:** Medium - Shows generic descriptions instead of actual screenshot text

---

## 🚀 AGENT FUNCTIONALITY

### Monitoring Agent Features
1. ✅ Auto-login and authentication
2. ✅ Loads allowlist from backend
3. ✅ Monitors active window
4. ✅ Checks against allowlist
5. ✅ Captures screenshots every 10 seconds
6. ✅ Logs activities to backend
7. ✅ Organizes screenshots in folders
8. ✅ Handles session start/stop

### Agent Logs Example
```
✓ Logged in as Stalin
✓ Loaded 4 allowlist items:
  - application: cursor → cursor/
  - url: https://chatgpt.com → chatgpt/
  - application: Visual Studio Code → vs_code/
  - application: Electron → vs_code/

✓ Active session detected (ID: 46)
  Screenshot interval: 10 seconds
  Starting capture...
  
  Activity: Cursor - ProcessMiningModal.jsx
  [18:33:41] Screenshot captured → cursor/
  [18:33:54] Screenshot captured → cursor/
  
  Activity: Google Chrome - https://chatgpt.com/ - ChatGPT
  [18:35:59] Screenshot captured → chatgpt/
```

---

## 📈 STATISTICS

### Current Session (ID: 46)
- **Total Screenshots:** 134
- **Activities:**
  - Cursor: 53 screenshots
  - ChatGPT: 47 screenshots
  - VS Code/Electron: 34 screenshots
- **Transitions:** 2 unique transitions
- **Duration:** ~22 minutes

---

## ✅ SYSTEM STATUS

| Component | Status | Notes |
|-----------|--------|-------|
| Backend API | ✅ Running | Port 5001 |
| Frontend | ✅ Running | Port 5173 |
| Agent | ✅ Running | Monitoring active |
| Database | ✅ Connected | PostgreSQL |
| Authentication | ✅ Working | JWT tokens |
| Screenshot Capture | ✅ Working | Folder-organized |
| Process Mining | ✅ Working | Interactive diagram |
| OCR Extraction | ⚠️ Fallback | Using activity data |
| Batch Processing | ✅ Working | Max 50 per batch |

---

## 🎯 RECOMMENDATIONS

1. **Improve OCR:** Investigate why Mistral OCR is falling back to activity data
2. **Implement Missing Endpoints:** Add `/api/employees` and `/api/employees/stats`
3. **Increase Batch Limit:** Consider increasing from 50 to 100 for faster processing
4. **Add Real-time Updates:** WebSocket support for live monitoring
5. **Export Features:** Add PDF/Excel export for reports

---

**End of Documentation**
