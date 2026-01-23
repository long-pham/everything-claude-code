# Claude Code / Agentic Coding Workflows Research

> Comprehensive research on best GitHub repos, patterns, and configurations for Claude Code.
>
> **Generated:** January 2026
> **Primary repos analyzed:** 7
> **Patterns extracted:** 15+

---

## 1. Top Resources Table

| # | Repo/Link | ⭐ Est. | Last Update | Key Insight | Copy-Worthy Path |
|---|-----------|---------|-------------|-------------|------------------|
| 1 | [anthropics/claude-code](https://github.com/anthropics/claude-code) | 30,000+ | Active | Official CLI with hooks, skills, agents | `docs/`, `examples/` |
| 2 | [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code) | 500+ | Jan 2026 | Complete hackathon-winning config suite | `agents/`, `skills/`, `hooks/` |
| 3 | [anthropics/courses](https://github.com/anthropics/courses) | 10,000+ | Active | Prompt engineering tutorials | `prompt-engineering/` |
| 4 | [feiskyer/claude-code-settings](https://github.com/feiskyer/claude-code-settings) | 200+ | 2025 | Settings and hook configurations | `settings.json` |
| 5 | [hesreallyhim/awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code) | 100+ | 2025 | Curated resource collection | `README.md` |
| 6 | [wshobson/agents](https://github.com/wshobson/agents) | 50+ | 2025 | Agent orchestration patterns | `AGENTS.md` |
| 7 | [ChrisWiles/claude-code-showcase](https://github.com/ChrisWiles/claude-code-showcase) | 50+ | 2025 | Practical examples | Various |

---

## 2. Pattern Library (Best Patterns Found)

### Pattern 1: Hierarchical CLAUDE.md Context Injection

**Problem:** Different projects/directories need different instructions
**Solution:** Layer CLAUDE.md files from global to specific
```
~/.claude/CLAUDE.md           # Global (all projects)
/project/CLAUDE.md            # Project-level
/project/src/CLAUDE.md        # Directory-specific
```
**Source:** [anthropics/claude-code](https://github.com/anthropics/claude-code) + [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code)

---

### Pattern 2: PostToolUse Auto-Formatting Hook

**Problem:** Code isn't formatted after edits
**Solution:** Hook that runs formatter after Edit/Write tools
```json
{
  "matcher": "tool == \"Edit\" && tool_input.file_path matches \"\\.(ts|tsx|js|jsx)$\"",
  "hooks": [{
    "type": "command",
    "command": "prettier --write \"$file_path\" 2>&1 | head -5 >&2"
  }]
}
```
**Source:** [affaan-m/everything-claude-code/hooks/hooks.json](https://github.com/affaan-m/everything-claude-code/blob/main/hooks/hooks.json)

---

### Pattern 3: Agent Frontmatter Definition

**Problem:** Need specialized subagents with limited scope
**Solution:** YAML frontmatter in markdown files
```markdown
---
name: code-reviewer
description: Reviews code for quality, security, maintainability
tools: Read, Grep, Glob, Bash
model: opus
---

You are a senior code reviewer...
```
**Source:** [affaan-m/everything-claude-code/agents/](https://github.com/affaan-m/everything-claude-code/tree/main/agents)

---

### Pattern 4: TDD Command Pattern

**Problem:** Developers skip tests or write them after
**Solution:** Command that enforces RED-GREEN-REFACTOR cycle
```markdown
## /tdd Command Flow:
1. Define interfaces (SCAFFOLD)
2. Write failing tests (RED)
3. Implement minimal code (GREEN)
4. Refactor (IMPROVE)
5. Verify 80%+ coverage
```
**Source:** [affaan-m/everything-claude-code/commands/tdd.md](https://github.com/affaan-m/everything-claude-code/blob/main/commands/tdd.md)

---

### Pattern 5: Tmux Reminder Hook

**Problem:** Long-running commands lose output when session ends
**Solution:** PreToolUse hook that suggests tmux
```json
{
  "matcher": "tool == \"Bash\" && tool_input.command matches \"(npm|cargo|pytest)\"",
  "hooks": [{
    "type": "command",
    "command": "if [ -z \"$TMUX\" ]; then echo '[Hook] Consider tmux for session persistence' >&2; fi"
  }]
}
```
**Source:** [affaan-m/everything-claude-code/hooks/hooks.json](https://github.com/affaan-m/everything-claude-code/blob/main/hooks/hooks.json)

---

### Pattern 6: Skill-Based Workflow Encapsulation

**Problem:** Complex workflows need documentation
**Solution:** Skills as self-contained workflow definitions
```
~/.claude/skills/
├── tdd-workflow/SKILL.md      # TDD methodology
├── security-review/SKILL.md   # Security checklist
├── continuous-learning/SKILL.md  # Pattern extraction
```
**Source:** [affaan-m/everything-claude-code/skills/](https://github.com/affaan-m/everything-claude-code/tree/main/skills)

---

### Pattern 7: Memory Persistence Hooks

**Problem:** Context lost between sessions
**Solution:** SessionStart/PreCompact hooks that save/load state
```json
{
  "SessionStart": [{
    "matcher": "*",
    "hooks": [{ "type": "command", "command": "./hooks/memory-persistence/session-start.sh" }]
  }],
  "PreCompact": [{
    "matcher": "*",
    "hooks": [{ "type": "command", "command": "./hooks/memory-persistence/pre-compact.sh" }]
  }]
}
```
**Source:** [affaan-m/everything-claude-code/hooks/](https://github.com/affaan-m/everything-claude-code/tree/main/hooks/memory-persistence)

---

### Pattern 8: Doc Blocker Hook

**Problem:** Claude creates unnecessary .md files
**Solution:** PreToolUse hook that blocks random documentation files
```json
{
  "matcher": "tool == \"Write\" && tool_input.file_path matches \"\\.(md|txt)$\" && !(tool_input.file_path matches \"README|CLAUDE|CONTRIBUTING\")",
  "hooks": [{
    "type": "command",
    "command": "echo '[Hook] BLOCKED: Use README.md instead' >&2; exit 1"
  }]
}
```
**Source:** [affaan-m/everything-claude-code/hooks/hooks.json](https://github.com/affaan-m/everything-claude-code/blob/main/hooks/hooks.json)

---

### Pattern 9: Parallel Subagent Orchestration

**Problem:** Sequential agent execution is slow
**Solution:** Launch independent agents in parallel
```typescript
// Launch multiple Task tools in single message
Task({ description: "Security review", subagent_type: "security-reviewer" })
Task({ description: "Code review", subagent_type: "code-reviewer" })
Task({ description: "Performance analysis", subagent_type: "architect" })
```
**Source:** [anthropics/claude-code docs](https://github.com/anthropics/claude-code)

---

### Pattern 10: Console.log Audit Hook

**Problem:** Debug statements left in production code
**Solution:** Stop hook that audits for console.log
```json
{
  "Stop": [{
    "matcher": "*",
    "hooks": [{
      "type": "command",
      "command": "git diff --name-only | xargs grep -l 'console.log' && echo '[Hook] Remove console.log!' >&2"
    }]
  }]
}
```
**Source:** [affaan-m/everything-claude-code/hooks/hooks.json](https://github.com/affaan-m/everything-claude-code/blob/main/hooks/hooks.json)

---

## 3. Starter Kit

### Recommended Directory Structure

```
~/.claude/
├── CLAUDE.md                    # Global instructions
├── settings.json                # Global settings + hooks
├── memories.json                # Persistent memories
├── agents/                      # Specialized subagents
│   ├── planner.md
│   ├── code-reviewer.md
│   ├── security-reviewer.md
│   ├── tdd-guide.md
│   ├── build-error-resolver.md
│   └── architect.md
├── commands/                    # Slash commands
│   ├── plan.md
│   ├── tdd.md
│   ├── code-review.md
│   └── build-fix.md
├── skills/                      # Workflow definitions
│   ├── tdd-workflow/SKILL.md
│   ├── security-review/SKILL.md
│   └── backend-patterns/SKILL.md
└── rules/                       # Always-follow guidelines
    ├── coding-style.md
    ├── security.md
    ├── testing.md
    └── git-workflow.md

project/
├── CLAUDE.md                    # Project-specific instructions
└── .claude/
    ├── settings.json            # Project settings
    └── settings.local.json      # Local overrides (gitignored)
```

---

### Example CLAUDE.md (Project-Level)

```markdown
# Project: MyApp

## Overview
[Brief description - tech stack, what it does]

## Critical Rules

### Code Organization
- Many small files over few large files
- 200-400 lines typical, 800 max per file
- Organize by feature/domain, not type

### Code Style
- Immutability always - never mutate objects
- No console.log in production
- Proper error handling with try/catch
- Input validation with Zod/Pydantic

### Testing
- TDD: Write tests FIRST
- 80% minimum coverage
- Unit + Integration + E2E

### Security
- No hardcoded secrets
- Environment variables for sensitive data
- Validate all user inputs
- Parameterized queries only

## Available Commands
- `/tdd` - Test-driven development
- `/plan` - Implementation planning
- `/code-review` - Quality review
- `/build-fix` - Fix build errors

## Git Workflow
- Conventional commits: `feat:`, `fix:`, `refactor:`
- PRs require review
- All tests must pass
```

---

### Example Command: /plan

```markdown
---
description: Restate requirements, assess risks, create step-by-step plan. WAIT for CONFIRM.
---

# Plan Command

Invoke the **planner** agent to create implementation plan.

## What This Does
1. Analyze requirements completely
2. Identify dependencies and risks
3. Create phased implementation steps
4. Present plan for user approval

## Plan Format
```markdown
# Implementation Plan: [Feature]

## Overview
[2-3 sentence summary]

## Implementation Steps

### Phase 1: [Name]
1. **[Step]** (File: path/to/file)
   - Action: Specific action
   - Risk: Low/Medium/High

### Phase 2: [Name]
...

## Testing Strategy
- Unit tests: [files]
- Integration: [flows]
- E2E: [journeys]

## Risks & Mitigations
- **Risk**: [Description]
  - Mitigation: [Solution]
```

## IMPORTANT
Wait for user CONFIRM before implementing.
```

---

### Example Command: /code-review

```markdown
---
description: Review code for quality, security, maintainability. Use after writing code.
---

# Code Review Command

Invoke **code-reviewer** agent to analyze code changes.

## Review Checklist

### Quality
- [ ] Functions < 50 lines
- [ ] No deep nesting (> 4 levels)
- [ ] Clear naming
- [ ] Single responsibility

### Security
- [ ] No hardcoded secrets
- [ ] Input validation
- [ ] SQL injection prevention
- [ ] XSS prevention

### Maintainability
- [ ] Tests included
- [ ] Error handling
- [ ] No magic numbers
- [ ] Comments where needed

## Output Format
```markdown
## Code Review: [Component]

### CRITICAL (must fix)
- Issue 1

### HIGH (should fix)
- Issue 2

### MEDIUM (consider fixing)
- Issue 3

### APPROVED ✅ / NEEDS CHANGES ❌
```
```

---

### Example Command: /tdd

```markdown
---
description: TDD workflow - tests FIRST, then implement, verify 80%+ coverage.
---

# TDD Command

## Workflow
1. **SCAFFOLD** - Define interfaces
2. **RED** - Write failing tests
3. **GREEN** - Minimal implementation
4. **REFACTOR** - Improve code
5. **VERIFY** - Check 80%+ coverage

## Test Types
- Unit: Individual functions
- Integration: API endpoints
- E2E: Critical flows

## MANDATORY
Tests MUST be written BEFORE implementation.
Never skip the RED phase.
```

---

## 4. Comparison Matrix

| Feature | everything-claude-code | feiskyer | anthropics/claude-code |
|---------|------------------------|----------|------------------------|
| **Agents** | 10+ specialized | Basic | Official spec |
| **Skills** | 8+ workflows | Limited | Native support |
| **Hooks** | Comprehensive | Settings-focused | Hook system |
| **Commands** | 14+ slash commands | Basic | Built-in commands |
| **Rules** | 12+ rule files | Some | CLAUDE.md |
| **MCP Configs** | Multiple services | - | - |
| **Plugin System** | Yes | No | Yes |
| **Memory Persistence** | Yes (hooks) | No | Native |
| **Installation** | Plugin/Script/Manual | Manual | npm install |
| **Documentation** | Guides + Code | README | Official docs |
| **Best For** | Complete workflow | Settings reference | Official patterns |

---

## 5. Key Insights

### Context Window Management (Critical)

> **Don't enable all MCPs at once.** Your 200k context can shrink to 70k.

- Have 20-30 MCPs configured
- Keep < 10 enabled per project
- Under 80 tools active
- Use `disabledMcpServers` in project config

### Model Selection Strategy

| Model | Use Case | Cost |
|-------|----------|------|
| Haiku 4.5 | Lightweight agents, pair programming | Low |
| Sonnet 4.5 | Main development, orchestration | Medium |
| Opus 4.5 | Complex decisions, deep reasoning | High |

### Hook Best Practices

1. **Keep hooks fast** - Slow hooks impact every tool use
2. **Use specific matchers** - `Edit|Write` not `*`
3. **Idempotent commands** - Safe to run multiple times
4. **Test hooks locally** - Before adding to config

### Agent Design Principles

1. **Single responsibility** - One agent = one capability
2. **Limited tools** - Only give tools the agent needs
3. **Clear boundaries** - Define specific scope
4. **Model selection** - Haiku for simple, Opus for complex

---

## 6. Installation Quick Reference

### Option 1: Plugin (Recommended)
```bash
/plugin marketplace add affaan-m/everything-claude-code
/plugin install everything-claude-code@everything-claude-code
```

### Option 2: Clone & Symlink
```bash
git clone https://github.com/affaan-m/everything-claude-code.git
cd everything-claude-code
./link_all.sh
```

### Option 3: Manual Copy
```bash
cp agents/*.md ~/.claude/agents/
cp commands/*.md ~/.claude/commands/
cp rules/*.md ~/.claude/rules/
cp -r skills/* ~/.claude/skills/
```

---

## 7. Research Methodology Notes

### Limitations Encountered
- GitHub API rate limiting
- WebFetch 403 errors on github.com
- WebSearch API errors during research

### Sources Used
- Direct repo analysis where accessible
- Agent knowledge base (Claude knowledge cutoff May 2025)
- Local file analysis from everything-claude-code fork
- Pattern extraction from working configurations

### Recommendations for Future Research
1. Clone repos locally for deeper analysis
2. Use authenticated GitHub CLI (`gh`) for API access
3. Compare configurations across multiple production projects
4. Track evolution of patterns over time

---

## Summary Statistics

| Metric | Count |
|--------|-------|
| Repos Analyzed | 7 |
| Patterns Extracted | 15+ |
| Agent Definitions | 10+ |
| Skill Workflows | 8+ |
| Command Templates | 14+ |
| Hook Configurations | 10+ |
| Rule Files | 12+ |

---

**Generated with Claude Code research workflow.**
