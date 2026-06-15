"""Demo mode — realistic mock responses without an API key."""

import time

SQL_RESPONSE = """## 🔍 Scan Complete — 2 Vulnerabilities Found

---

### 🔴 CRITICAL — SQL Injection
**Line 1:** `query = "SELECT * FROM users WHERE id = " + user_id`

**Why it's dangerous:**
An attacker can input `1 OR 1=1` to return all users, or `1; DROP TABLE users;` to destroy your database. No authentication required.

**Fixed version:**
```python
# Use parameterised queries
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
```

---

### 🔴 CRITICAL — SQL Injection
**Line 2:** `db.execute(query)`

Executing a dynamically built string directly into the database driver with no sanitisation.

**Fixed version:**
```python
cursor.execute("SELECT * FROM users WHERE id = ?", [user_id])
```

---

## 📊 Security Score: 12 / 100

**Verdict:** ⛔ Critical risk — this code is vulnerable to database compromise. Do not deploy.

**Next steps:**
1. Replace all string-concatenated queries with parameterised statements
2. Add input validation at the API boundary
3. Run OWASP ZAP or sqlmap in a safe environment to verify the fix"""

SECRET_RESPONSE = """## 🔍 Scan Complete — 2 Vulnerabilities Found

---

### 🔴 CRITICAL — Hardcoded API Key
**Line 1:** `API_KEY = "sk-1234567890abcdef"`

**Why it's dangerous:**
Anyone with read access to this file (teammates, CI logs, git history) has your API key. Even if you delete it later, it lives forever in git history.

**Fixed version:**
```python
import os
API_KEY = os.getenv("API_KEY")  # Store in .env file, never commit it
```

---

### 🔴 CRITICAL — Hardcoded Password
**Line 2:** `password = "admin123"`

Plain-text password in source code. Visible to every developer, in every git clone, forever.

**Fixed version:**
```python
import os
password = os.getenv("DB_PASSWORD")
```

---

## 📊 Security Score: 5 / 100

**Verdict:** ⛔ Critical risk — secrets in source code are a breach waiting to happen.

**Immediate actions:**
1. Rotate the exposed API key right now
2. Move all secrets to environment variables or a secrets manager (e.g. AWS Secrets Manager, Vault)
3. Add `.env` to `.gitignore` before your next commit
4. Run `git filter-branch` or `git-secrets` to audit your history"""

XSS_RESPONSE = """## 🔍 Scan Complete — 2 Vulnerabilities Found

---

### 🟠 HIGH — Cross-Site Scripting (XSS)
**Line 1:** `document.getElementById("output").innerHTML = userInput`

**Why it's dangerous:**
If `userInput` is `<script>document.cookie</script>`, attackers steal session cookies. Your users' accounts get hijacked.

**Fixed version:**
```javascript
// Use textContent instead — it never executes scripts
document.getElementById("output").textContent = userInput

// Or sanitise with DOMPurify if you need HTML
import DOMPurify from 'dompurify'
element.innerHTML = DOMPurify.sanitize(userInput)
```

---

### 🔴 CRITICAL — eval() with User Input
**Line 2:** `eval(userInput)`

This executes arbitrary JavaScript from user input. Full remote code execution in the browser.

**Fixed version:**
```javascript
// Never eval user input. Use JSON.parse if you need to parse data:
const data = JSON.parse(userInput)
```

---

## 📊 Security Score: 18 / 100

**Verdict:** ⛔ High risk — XSS vulnerabilities can lead to full account takeover."""

INSECURE_RESPONSE = """## 🔍 Scan Complete — 2 Vulnerabilities Found

---

### 🔴 CRITICAL — Insecure Deserialization
**Line 1:** `data = pickle.loads(user_data)`

**Why it's dangerous:**
`pickle.loads` executes arbitrary Python code during deserialization. An attacker crafting a malicious payload gains full code execution on your server.

**Fixed version:**
```python
import json
data = json.loads(user_data)  # Use JSON for untrusted data
```

---

### 🔴 CRITICAL — OS Command Injection
**Line 2:** `os.system("rm -rf " + path)`

String concatenation into a shell command. Input `/ --no-preserve-root` and your server is gone.

**Fixed version:**
```python
import subprocess
# Use a list — never string concatenation
subprocess.run(["rm", "-rf", path], check=True)
# Better: validate path first
import pathlib
safe_path = pathlib.Path(path).resolve()
```

---

## 📊 Security Score: 8 / 100

**Verdict:** ⛔ Critical risk — remote code execution vulnerabilities. Patch immediately."""

DEFAULT_RESPONSE = """## 🔍 Scan Complete

I'm running in **Demo Mode** — paste one of the example snippets from the sidebar to see a full vulnerability report.

**What I can detect in Live Mode:**
- 🔴 SQL Injection
- 🟠 Cross-Site Scripting (XSS)
- 🔴 Hardcoded Secrets & API Keys
- 🟠 Dangerous Functions (eval, exec, pickle)
- 🟡 Authentication Flaws

Add your `ANTHROPIC_API_KEY` to `.env` to enable real Claude-powered scanning."""


def _pick(message: str) -> str:
    msg = message.lower()
    if "sql" in msg or "select" in msg or "query" in msg:
        return SQL_RESPONSE
    if "secret" in msg or "api_key" in msg or "password" in msg:
        return SECRET_RESPONSE
    if "xss" in msg or "innerhtml" in msg or "eval" in msg:
        return XSS_RESPONSE
    if "pickle" in msg or "os.system" in msg or "exec" in msg or "insecure" in msg:
        return INSECURE_RESPONSE
    return DEFAULT_RESPONSE


class MockCodeGuardAgent:
    def chat(self, user_message: str, history: list, image_data: dict = None, deep_analysis: bool = False) -> str:
        time.sleep(1.2)
        if image_data:
            return SQL_RESPONSE
        return _pick(user_message)

    def stream_chat(self, user_message: str, history: list, image_data=None):
        response = _pick(user_message)
        for word in response.split(" "):
            yield word + " "
            time.sleep(0.015)
