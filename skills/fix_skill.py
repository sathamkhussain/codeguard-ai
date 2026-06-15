"""
AutoFixSkill — takes vulnerable code and returns a fully corrected, safe version
with inline comments explaining every change made.
"""

from .base import BaseSkill


class AutoFixSkill(BaseSkill):
    """
    Skill: Automatic Vulnerability Fixer

    Input  — original vulnerable code + list of vulnerabilities found
    Output — fully corrected code with inline comments on every fix applied
    """

    system_prompt = """You are an expert secure code reviewer. Your job is to take \
vulnerable code and return a fully fixed, production-safe version.

## Rules
- Return the COMPLETE fixed code — never partial snippets
- Add a short inline comment on every line you changed explaining WHY
- Do not change logic that is not related to the security fix
- After the fixed code, include a ## Changes Made section listing every fix applied
- Use the same programming language as the input
- If the code has multiple vulnerabilities, fix ALL of them in one pass
- Format the fixed code in a proper markdown code block with the language specified

## Output format

## Fixed Code
```<language>
# fixed code here with inline comments
```

## Changes Made
1. **[Vulnerability name]** — what was changed and why
2. ...
"""

    max_tokens = 3000

    def fix(self, vulnerable_code: str, vulnerabilities: str, language: str = "auto") -> str:
        prompt = f"""Fix all security vulnerabilities in this {language} code.

**Vulnerabilities found:**
{vulnerabilities}

**Vulnerable code:**
```{language}
{vulnerable_code}
```

Return the complete fixed code with inline comments and a Changes Made section."""
        return self.run(prompt)

    def fix_stream(self, vulnerable_code: str, vulnerabilities: str, language: str = "auto"):
        prompt = f"""Fix all security vulnerabilities in this {language} code.

**Vulnerabilities found:**
{vulnerabilities}

**Vulnerable code:**
```{language}
{vulnerable_code}
```

Return the complete fixed code with inline comments and a Changes Made section."""
        return self.stream(prompt)
