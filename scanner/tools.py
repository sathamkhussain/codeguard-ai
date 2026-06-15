import re
from typing import List, Dict

TOOLS = [
    {
        "name": "scan_sql_injection",
        "description": (
            "Scan code for SQL Injection vulnerabilities — string concatenation in queries, "
            "unparameterised inputs, raw SQL construction from user data."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "The full code snippet to scan"},
                "language": {"type": "string", "description": "Programming language (python, javascript, php, java, etc.)"}
            },
            "required": ["code"]
        }
    },
    {
        "name": "scan_xss",
        "description": (
            "Scan code for Cross-Site Scripting (XSS) vulnerabilities — unescaped user input "
            "rendered in HTML, dangerous DOM manipulation, eval usage."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "The full code snippet to scan"},
                "language": {"type": "string", "description": "Programming language"}
            },
            "required": ["code"]
        }
    },
    {
        "name": "scan_hardcoded_secrets",
        "description": (
            "Scan code for hardcoded secrets — API keys, passwords, tokens, private keys, "
            "connection strings, credentials embedded directly in source code."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "The full code snippet to scan"}
            },
            "required": ["code"]
        }
    },
    {
        "name": "scan_insecure_functions",
        "description": (
            "Scan for dangerous function usage — eval, exec, os.system, shell_exec, "
            "pickle.loads, subprocess with shell=True, unsafe deserialization."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "The full code snippet to scan"},
                "language": {"type": "string", "description": "Programming language"}
            },
            "required": ["code"]
        }
    },
    {
        "name": "scan_auth_flaws",
        "description": (
            "Scan for authentication and authorisation flaws — missing auth checks, "
            "weak password hashing, insecure session tokens, broken access control."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "The full code snippet to scan"}
            },
            "required": ["code"]
        }
    }
]


def execute_tool(name: str, inputs: dict) -> dict:
    dispatch = {
        "scan_sql_injection":    _scan_sql_injection,
        "scan_xss":              _scan_xss,
        "scan_hardcoded_secrets": _scan_hardcoded_secrets,
        "scan_insecure_functions": _scan_insecure_functions,
        "scan_auth_flaws":       _scan_auth_flaws,
    }
    fn = dispatch.get(name)
    if fn is None:
        return {"error": f"Unknown tool: {name}"}
    return fn(**inputs)


def _find_matches(code: str, patterns: List[str], flags=re.IGNORECASE) -> List[Dict]:
    findings = []
    lines = code.split("\n")
    for i, line in enumerate(lines, 1):
        for pattern in patterns:
            if re.search(pattern, line, flags):
                findings.append({"line": i, "snippet": line.strip(), "pattern": pattern})
                break
    return findings


def _scan_sql_injection(code: str, language: str = "auto") -> dict:
    patterns = [
        r'(SELECT|INSERT|UPDATE|DELETE|FROM|WHERE).*["\'].*\+',
        r'(query|sql|cursor\.execute|db\.execute)\s*\(.*\+',
        r'f["\'].*SELECT.*\{',
        r'%s.*%.*(?:user|input|request|param|data)',
        r'String\.format\(.*SELECT',
        # Swift — string interpolation in SQL
        r'(SELECT|INSERT|UPDATE|DELETE).*\\\(.*\)',
        r'db\.execute\s*\(["\'].*\\\(',
    ]
    findings = _find_matches(code, patterns)
    severity = "Critical" if findings else "None"
    return {
        "vulnerability": "SQL Injection",
        "severity": severity,
        "findings": findings,
        "count": len(findings),
        "description": "User input concatenated directly into SQL queries allows attackers to manipulate database operations."
    }


def _scan_xss(code: str, language: str = "auto") -> dict:
    patterns = [
        r'innerHTML\s*=\s*(?![\"\']<)',
        r'document\.write\s*\(',
        r'eval\s*\(',
        r'outerHTML\s*=',
        r'\$\(.*\)\.html\(',
        r'dangerouslySetInnerHTML',
        r'v-html\s*=',
        # Swift WKWebView — loading unvalidated HTML
        r'loadHTMLString\s*\(.*\\\(',
        r'evaluateJavaScript\s*\(.*\\\(',
    ]
    findings = _find_matches(code, patterns)
    severity = "High" if findings else "None"
    return {
        "vulnerability": "Cross-Site Scripting (XSS)",
        "severity": severity,
        "findings": findings,
        "count": len(findings),
        "description": "Unescaped user input rendered in the DOM allows attackers to inject malicious scripts."
    }


def _scan_hardcoded_secrets(code: str) -> dict:
    patterns = [
        r'(?:api_key|apikey|api_secret|secret_key)\s*[=:]\s*["\'][a-zA-Z0-9\-_]{8,}["\']',
        r'(?:password|passwd|pwd)\s*[=:]\s*["\'][^"\']{4,}["\']',
        r'(?:token|access_token|auth_token)\s*[=:]\s*["\'][a-zA-Z0-9\-_\.]{10,}["\']',
        r'sk-[a-zA-Z0-9]{20,}',
        r'(?:private_key|privatekey)\s*[=:]\s*["\']',
        r'(?:BEGIN\s+(?:RSA|EC|OPENSSH)\s+PRIVATE\s+KEY)',
        r'(?:mongodb|mysql|postgresql|redis):\/\/[^"\'>\s]+:[^"\'>\s]+@',
        # Swift — let/var constant secrets
        r'(?:let|var)\s+\w*(?:key|token|secret|password|apiKey|api_key)\w*\s*=\s*"[a-zA-Z0-9\-_]{8,}"',
        r'(?:let|var)\s+\w*(?:password|passwd)\w*\s*=\s*"[^"]{4,}"',
    ]
    findings = _find_matches(code, patterns, flags=re.IGNORECASE)
    severity = "Critical" if findings else "None"
    return {
        "vulnerability": "Hardcoded Secrets",
        "severity": severity,
        "findings": findings,
        "count": len(findings),
        "description": "Credentials and keys embedded in source code are exposed in version control and logs."
    }


def _scan_insecure_functions(code: str, language: str = "auto") -> dict:
    patterns = [
        r'\beval\s*\(',
        r'\bexec\s*\(',
        r'os\.system\s*\(',
        r'subprocess\.[a-z]+\(.*shell\s*=\s*True',
        r'pickle\.loads?\s*\(',
        r'shell_exec\s*\(',
        r'system\s*\(',
        r'passthru\s*\(',
        r'__import__\s*\(',
        r'compile\s*\(.*exec',
        # Swift — insecure patterns
        r'NSLog\s*\(.*(?:password|token|key|secret)',
        r'print\s*\(.*(?:password|token|secret|apiKey)',
        r'allowsAnyHTTPSCertificate\s*=\s*true',
        r'kCFStreamSSLValidatesCertificateChain.*false',
        r'URLCredential\(.*\.forSession\)',
    ]
    findings = _find_matches(code, patterns)
    severity = "High" if findings else "None"
    return {
        "vulnerability": "Insecure Function Usage",
        "severity": severity,
        "findings": findings,
        "count": len(findings),
        "description": "Dangerous functions that execute arbitrary code, log secrets, or disable security checks."
    }


def _scan_auth_flaws(code: str) -> dict:
    patterns = [
        r'md5\s*\(',
        r'sha1\s*\(',
        r'(?:password|passwd)\s*==\s*["\']',
        r'random\.\w+\(\).*(?:token|session|key)',
        r'verify\s*=\s*False',
        r'SSL_VERIFY\s*=\s*False',
        r'checkPassword\s*=\s*False',
        # Swift — insecure data storage & auth
        r'UserDefaults\.standard\.set\s*\(.*(?:password|token|key|secret)',
        r'kSecAttrAccessible.*Always[^W]',
        r'SecItemAdd\s*\(.*nil\)',
        r'\.allowsExpiredCertificates\s*=\s*true',
        r'\.allowsSelfSignedCertificates\s*=\s*true',
    ]
    findings = _find_matches(code, patterns)
    severity = "High" if findings else "None"
    return {
        "vulnerability": "Authentication & Storage Flaws",
        "severity": severity,
        "findings": findings,
        "count": len(findings),
        "description": "Weak hashing, insecure Keychain usage, UserDefaults storing secrets, or disabled certificate checks."
    }
