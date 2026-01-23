# Claude Code Patterns Research

**Research Date:** 2026-01-22
**Primary Source:** [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code)
**Scope:** Agent orchestration, skills, hooks, commands, rules, and MCP configurations for Claude Code

---

## 1. Top Resources Table

| # | Repo/Resource | Key Insight | Copy-Worthy Path | Notes |
|---|---------------|-------------|------------------|-------|
| 1 | [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code) | Complete production-ready config from Anthropic hackathon winner | `agents/`, `skills/`, `hooks/`, `commands/` | 10+ months battle-tested |
| 2 | Shorthand Guide | Foundation - what each config type does | [X Thread](https://x.com/affaanmustafa/status/2012378465664745795) | Start here |
| 3 | Longform Guide | Advanced - token optimization, memory persistence, evals | [X Thread](https://x.com/affaanmustafa/status/2014040193557471352) | Deep techniques |
| 4 | Plugin System | Claude Code plugins for easy installation | `.claude-plugin/plugin.json` | `/plugin install` |
| 5 | Orchestrate Command | Sequential multi-agent workflows | `commands/orchestrate.md` | Handoff patterns |
| 6 | TDD Workflow Skill | Complete TDD with 80%+ coverage | `skills/tdd-workflow/SKILL.md` | pytest + httpx |
| 7 | Security Reviewer | OWASP Top 10 + financial security | `agents/security-reviewer.md` | Proactive review |
| 8 | Continuous Learning | Auto-extract patterns from sessions | `skills/continuous-learning/` | Stop hook |
| 9 | Strategic Compact | Manual compaction at logical boundaries | `skills/strategic-compact/` | Token optimization |
| 10 | Memory Persistence | Session state across compactions | `hooks/memory-persistence/` | PreCompact hook |
| 11 | MCP Configs | 14 pre-configured MCP servers | `mcp-configs/mcp-servers.json` | GitHub, Supabase, Vercel |
| 12 | Rules Library | 18 modular rule files | `rules/*.md` | Python + TypeScript |
| 13 | Context Injection | Dynamic system prompts | `contexts/dev.md`, `review.md` | Mode-based contexts |
| 14 | Example CLAUDE.md | Project-level config template | `examples/CLAUDE.md` | Copy and customize |
| 15 | Hooks System | PreToolUse, PostToolUse, Stop hooks | `hooks/hooks.json` | Auto-format, warnings |

---

## 2. Pattern Library (10 Best Ideas)

### Pattern 1: Agent Frontmatter

**Problem:** Agents need metadata (name, description, tools, model) in a structured way.

**Solution:**
```markdown
---
name: code-reviewer
description: Expert code review specialist. Use immediately after writing code.
tools: Read, Grep, Glob, Bash
model: opus
---

You are a senior code reviewer...
```

**Source:** `agents/code-reviewer.md:1-6`

---

### Pattern 2: Orchestrated Agent Workflows

**Problem:** Complex tasks need multiple specialized agents in sequence.

**Solution:**
```
/orchestrate feature "Add user authentication"

Executes: planner -> tdd-guide -> code-reviewer -> security-reviewer

Handoff Document Format:
## HANDOFF: [previous-agent] -> [next-agent]
### Context
### Findings
### Files Modified
### Open Questions
### Recommendations
```

**Source:** `commands/orchestrate.md`

---

### Pattern 3: Pre-Compact Memory Persistence

**Problem:** Context compaction loses important state.

**Solution:**
```bash
#!/bin/bash
# PreCompact Hook - Save state before context compaction
SESSIONS_DIR="${HOME}/.claude/sessions"
mkdir -p "$SESSIONS_DIR"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Context compaction triggered" >> "$COMPACTION_LOG"

ACTIVE_SESSION=$(ls -t "$SESSIONS_DIR"/*.tmp 2>/dev/null | head -1)
if [ -n "$ACTIVE_SESSION" ]; then
  echo "---" >> "$ACTIVE_SESSION"
  echo "**[Compaction occurred at $(date '+%H:%M')]**" >> "$ACTIVE_SESSION"
fi
```

**Source:** `hooks/memory-persistence/pre-compact.sh`

---

### Pattern 4: Continuous Learning via Stop Hook

**Problem:** Valuable patterns from sessions are lost.

**Solution:**
```json
{
  "hooks": {
    "Stop": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "~/.claude/skills/continuous-learning/evaluate-session.sh"
      }]
    }]
  }
}
```

Pattern detection types: `error_resolution`, `user_corrections`, `workarounds`, `debugging_techniques`, `project_specific`

**Source:** `skills/continuous-learning/SKILL.md`

---

### Pattern 5: Strategic Compaction at Logical Boundaries

**Problem:** Auto-compaction triggers mid-task at arbitrary points.

**Solution:**
```json
{
  "PreToolUse": [{
    "matcher": "tool == \"Edit\" || tool == \"Write\"",
    "hooks": [{
      "type": "command",
      "command": "~/.claude/skills/strategic-compact/suggest-compact.sh"
    }]
  }]
}
```

When to compact:
- After exploration, before execution
- After completing a milestone
- Before major context shifts

**Source:** `skills/strategic-compact/SKILL.md`

---

### Pattern 6: Hook-Based Auto-Formatting

**Problem:** Code needs formatting after edits.

**Solution:**
```json
{
  "matcher": "tool == \"Edit\" && tool_input.file_path matches \"\\\\.(ts|tsx|js|jsx)$\"",
  "hooks": [{
    "type": "command",
    "command": "#!/bin/bash\nfile_path=$(echo \"$input\" | jq -r '.tool_input.file_path')\nprettier --write \"$file_path\" 2>&1 | head -5 >&2"
  }]
}
```

**Source:** `hooks/hooks.json:92-100`

---

### Pattern 7: Dev Server Tmux Enforcement

**Problem:** Dev servers run outside tmux lose log access.

**Solution:**
```json
{
  "matcher": "tool == \"Bash\" && tool_input.command matches \"(npm run dev|pnpm dev|yarn dev)\"",
  "hooks": [{
    "type": "command",
    "command": "#!/bin/bash\necho '[Hook] BLOCKED: Dev server must run in tmux' >&2\necho 'Use: tmux new-session -d -s dev \"npm run dev\"' >&2\nexit 1"
  }]
}
```

**Source:** `hooks/hooks.json:4-14`

---

### Pattern 8: Security Review Checklist per Context

**Problem:** Different code needs different security checks.

**Solution:**
```markdown
## Financial Security (for payment code):
- [ ] All trades are atomic transactions
- [ ] Balance checks before withdrawal
- [ ] Rate limiting on financial endpoints
- [ ] No floating-point arithmetic for money

## Blockchain Security (for crypto code):
- [ ] Wallet signatures validated
- [ ] Private keys never logged
- [ ] Slippage protection
```

**Source:** `agents/security-reviewer.md:126-180`

---

### Pattern 9: TDD Test-Before-Code Enforcement

**Problem:** Developers skip tests or write them after.

**Solution:**
```markdown
## TDD Workflow Steps

1. Write User Journeys
2. Generate Test Cases (RED)
3. Run Tests (They Should Fail)
4. Implement Code (GREEN)
5. Run Tests Again (Pass)
6. Refactor (IMPROVE)
7. Verify Coverage (80%+)
```

**Source:** `skills/tdd-workflow/SKILL.md:48-118`

---

### Pattern 10: MCP Server Context Management

**Problem:** Too many MCPs shrink context window from 200k to 70k.

**Solution:**
```markdown
Rule of thumb:
- Have 20-30 MCPs configured
- Keep under 10 enabled per project
- Under 80 tools active

Use `disabledMcpServers` in project config:
```json
{
  "disabledMcpServers": ["cloudflare-docs", "railway"]
}
```

**Source:** `README.md:330-340`, `mcp-configs/mcp-servers.json:86-90`

---

## 3. Starter Kit

### Directory Structure

```
~/.claude/
├── agents/
│   ├── planner.md
│   ├── code-reviewer.md
│   ├── security-reviewer.md
│   ├── tdd-guide.md
│   └── architect.md
├── commands/
│   ├── plan.md
│   ├── tdd.md
│   ├── code-review.md
│   ├── orchestrate.md
│   └── learn.md
├── skills/
│   ├── tdd-workflow/
│   │   └── SKILL.md
│   ├── continuous-learning/
│   │   ├── SKILL.md
│   │   └── evaluate-session.sh
│   └── security-review/
│       └── SKILL.md
├── hooks/
│   ├── hooks.json
│   └── memory-persistence/
│       ├── pre-compact.sh
│       └── session-start.sh
├── rules/
│   ├── security.md
│   ├── testing.md
│   ├── coding-style.md
│   └── agents.md
└── settings.json
```

### Example CLAUDE.md (Project Root)

```markdown
# Project CLAUDE.md

## Project Overview
[Brief description - what it does, tech stack]

## Critical Rules

### 1. Code Organization
- Many small files over few large files
- 200-400 lines typical, 800 max per file
- Organize by feature/domain

### 2. Code Style
- Immutability always - never mutate objects
- No console.log in production
- Proper error handling with try/catch
- Input validation with Zod

### 3. Testing
- TDD: Write tests first
- 80% minimum coverage
- Unit + Integration + E2E

### 4. Security
- No hardcoded secrets
- Environment variables for sensitive data
- Validate all user inputs

## Key Patterns

### API Response Format
```typescript
interface ApiResponse<T> {
  success: boolean
  data?: T
  error?: string
}
```

## Available Commands
- `/plan` - Create implementation plan
- `/tdd` - Test-driven development
- `/code-review` - Review code quality
- `/orchestrate feature <desc>` - Full feature workflow

## Git Workflow
- Conventional commits: feat:, fix:, refactor:
- PRs require review
- All tests must pass before merge
```

### Example Command: /plan

```markdown
# /plan

Restate requirements, assess risks, and create step-by-step implementation plan.
WAIT for user CONFIRM before touching any code.

## Process

1. **Understand Requirements**
   - Ask clarifying questions if needed
   - Identify success criteria
   - List assumptions and constraints

2. **Architecture Review**
   - Analyze existing codebase
   - Identify affected components
   - Consider reusable patterns

3. **Create Plan**
   - Break into phases
   - Each step: file path, action, why, risk level
   - Include testing strategy

4. **Request Approval**
   - Present plan to user
   - Wait for explicit confirmation
   - Do NOT implement until approved
```

### Example Command: /tdd

```markdown
# /tdd

Enforce test-driven development workflow.
Scaffold interfaces, generate tests FIRST, then implement minimal code to pass.
Ensure 80%+ coverage.

## Steps

1. **Define Interfaces**
   - Create type definitions
   - Document expected behavior

2. **Write Tests (RED)**
   ```bash
   uv run pytest --tb=short
   # Tests should FAIL - not implemented yet
   ```

3. **Implement (GREEN)**
   - Write minimal code to pass tests
   - No extra features

4. **Refactor (IMPROVE)**
   - Clean up code
   - Keep tests green

5. **Verify Coverage**
   ```bash
   uv run pytest --cov=src --cov-report=html
   # Must be 80%+
   ```
```

### Example Command: /code-review

```markdown
# /code-review

Review code for quality, security, and maintainability.

## Automatic Triggers
- After any file is written or edited
- Before git commit

## Checklist

### CRITICAL (Must Fix)
- [ ] No hardcoded secrets
- [ ] No SQL injection
- [ ] No XSS vulnerabilities
- [ ] Authentication on all routes

### HIGH (Should Fix)
- [ ] Functions under 50 lines
- [ ] Files under 800 lines
- [ ] No console.log statements
- [ ] Proper error handling

### MEDIUM (Consider)
- [ ] Test coverage adequate
- [ ] Documentation updated
- [ ] No TODO without ticket

## Output Format
```
[CRITICAL] Hardcoded API key
File: src/api/client.ts:42
Issue: API key exposed in source
Fix: Move to environment variable

const apiKey = "sk-abc123";  // BAD
const apiKey = process.env.API_KEY;  // GOOD
```
```

---

## 4. Comparison Matrix

| Feature | everything-claude-code | Notes |
|---------|------------------------|-------|
| **Agents** | 9 specialized agents | planner, architect, tdd-guide, code-reviewer, security-reviewer, build-error-resolver, e2e-runner, refactor-cleaner, doc-updater |
| **Commands** | 14 slash commands | plan, tdd, code-review, e2e, build-fix, refactor-clean, checkpoint, verify, learn, orchestrate, etc. |
| **Skills** | 12 skill definitions | TDD workflow, coding standards, backend/frontend patterns, security review, continuous learning, strategic compact, etc. |
| **Hooks** | 6 hook categories | PreToolUse (5), PostToolUse (4), Stop (3), PreCompact (1), SessionStart (1) |
| **Rules** | 18 rule files | Python + TypeScript versions for security, testing, coding style, git workflow, performance |
| **MCP Configs** | 14 servers | GitHub, Supabase, Vercel, Railway, Cloudflare, ClickHouse, Memory, etc. |
| **Examples** | 3 templates | CLAUDE.md, user-CLAUDE.md, statusline.json |
| **Installation** | 3 methods | Plugin install, link_all.sh script, manual copy |

---

## 5. Key Concepts Summary

### Configuration Hierarchy

1. **~/.claude.json** - Global settings, MCP servers
2. **~/.claude/settings.json** - Hooks, enabledPlugins
3. **~/.claude/rules/** - Always-follow guidelines
4. **Project CLAUDE.md** - Project-specific instructions
5. **~/.claude/commands/** - Slash commands
6. **~/.claude/skills/** - Workflow definitions
7. **~/.claude/agents/** - Specialized subagents

### Hook Types

| Type | Trigger | Use Case |
|------|---------|----------|
| PreToolUse | Before tool execution | Block unsafe commands, add warnings |
| PostToolUse | After tool execution | Auto-format, type check, warn about issues |
| Stop | Session ends | Audit, persist state, extract patterns |
| PreCompact | Before compaction | Save state that might be lost |
| SessionStart | New session | Load previous context |

### Model Selection Strategy

| Model | Use Case | Cost |
|-------|----------|------|
| Haiku 4.5 | Lightweight agents, frequent invocation | Lowest |
| Sonnet 4.5 | Main development, orchestration | Medium |
| Opus 4.5 | Complex architecture, deep reasoning | Highest |

---

## 6. Implementation Recommendations

### Quick Start (5 minutes)

```bash
# Clone and run setup
git clone https://github.com/affaan-m/everything-claude-code.git
cd everything-claude-code
./link_all.sh
```

### Gradual Adoption

1. **Week 1:** Copy `rules/` for consistent coding standards
2. **Week 2:** Add `agents/code-reviewer.md` and `agents/planner.md`
3. **Week 3:** Configure `hooks/hooks.json` for auto-formatting
4. **Week 4:** Add TDD workflow and orchestration commands

### Must-Have Components

1. `agents/code-reviewer.md` - Catch issues before commit
2. `agents/security-reviewer.md` - Security audit
3. `rules/security.md` - No hardcoded secrets
4. `hooks.json` with Prettier auto-format
5. Example `CLAUDE.md` for each project

---

## 7. Research Statistics

- **Files Analyzed:** 40+
- **Patterns Extracted:** 10 major, 20+ minor
- **Total Lines of Config:** ~4,000
- **Primary Source:** affaan-m/everything-claude-code
- **External Sources Blocked:** GitHub sandbox restrictions prevented analysis of other repos

---

## 8. Sources

- [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code) - Primary source
- [Shorthand Guide](https://x.com/affaanmustafa/status/2012378465664745795) - Foundation concepts
- [Longform Guide](https://x.com/affaanmustafa/status/2014040193557471352) - Advanced techniques

---

*Research compiled by Claude Code research session, 2026-01-22*
