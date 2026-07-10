# Setup: Claude Code on your personal laptop (Path A)

This is the recommended path. You get full file access, automatic PDF generation, and a searchable case history. Uses your existing Claude Max plan, no extra cost.

## What you're installing

Claude Code is a command-line tool. You open your terminal, type `claude`, and it's like having Claude.ai but inside a folder it can actually read and write files in.

Works on Windows, macOS, and Linux. The instructions below assume Windows since that's most likely your situation.

## Step 1: Install Claude Code

The native installer is the easiest path. No Node.js required, no npm headaches.

**Windows (PowerShell, run as your normal user — not admin):**

```powershell
irm https://claude.ai/install.ps1 | iex
```

**macOS / Linux:**

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

Verify the install:

```bash
claude --version
```

If it can't find `claude`, close and reopen your terminal so it picks up the new PATH.

## Step 2: Sign in with your Max plan

```bash
claude
```

First run, it'll open a browser. Sign in with the same email you use for Claude Max. Claude Code will use your Max plan limits, not API billing.

## Step 3: Put the work-agent folder somewhere permanent

Move the whole `work-agent/` folder (the one this README is in) to wherever you want it. Suggested:

- **Windows:** `C:\Users\Visal\work-agent\`
- **macOS:** `~/work-agent/`

## Step 4: Tell Claude Code about the skills

Claude Code looks for skills in two places: a project-level `.claude/skills/` folder, or a global `~/.claude/skills/` folder.

**Easiest path — make them global** (available from any folder you're in):

**Windows:**
```powershell
# Open the skills folder in your home directory
mkdir $HOME\.claude\skills -Force
# Copy the three skill folders there
Copy-Item -Path .\skills\* -Destination $HOME\.claude\skills\ -Recurse
```

**macOS / Linux:**
```bash
mkdir -p ~/.claude/skills
cp -r ./skills/* ~/.claude/skills/
```

Alternative — keep them project-scoped (only loads when you `cd` into work-agent/):
```bash
# Just stay where you are
mkdir -p .claude
mv skills .claude/skills
```

I'd go with global. You want the agent available whenever you open a terminal, not only when you remember to cd into a specific folder.

## Step 5: Install the Python library for PDF generation

The troubleshooting-wizard skill generates PDFs using `reportlab`. Install it once:

```bash
pip install reportlab
```

If you don't have Python at all, install it from https://www.python.org/downloads/ first. Tick "Add Python to PATH" during install.

## Step 6: Test it

Open a new terminal window. Type:

```bash
claude
```

Then type:

> Pretend a client just called: their user can't sign in to Outlook after we reset her password. Start troubleshooting.

If the troubleshooting-wizard skill is loaded right, Claude will start asking you the structured diagnostic questions. If it just gives generic advice, the skill isn't being seen — check that the files are in `~/.claude/skills/troubleshooting-wizard/SKILL.md` (not nested deeper).

## Daily use

From now on, just open a terminal and type `claude`. The three skills are always available. Try things like:

- *"Client says Teams calls are dropping after 60 seconds, help me troubleshoot."*
- *"Quick question — how do I check if a user has MFA enabled?"*
- *"Build me a study plan for Intune device compliance, 2 weeks, I want to be exam-ready for MD-102."*
- *"Have we seen any OneDrive sync issues before?"* (searches case-log/)

## Where things get saved

- **Case PDFs:** `work-agent/case-log/CASE-YYYY-NNNN-*.pdf`
- **Study plans:** `work-agent/study-plans/[topic].md`
- **Claude Code conversations:** `~/.claude/projects/` (auto-managed)

To search past cases:
```bash
cd ~/work-agent
ls case-log/                    # list all
grep -l "Conditional Access" case-log/*.pdf   # find by content (needs pdftotext)
```

Or just ask Claude in the terminal: *"List all my past cases involving OneDrive."*

## Troubleshooting the agent itself

**The skills aren't triggering.**
Run `claude` then type `/skills` to see what's loaded. If your three skills aren't listed, the path is wrong. They need to be at `~/.claude/skills/[skill-name]/SKILL.md` — one folder deep, with the YAML frontmatter intact.

**PDF generation fails.**
Make sure `reportlab` is installed in the Python that `claude` can see. Run `python -c "import reportlab; print(reportlab.__version__)"` to verify.

**Hitting Max plan rate limits.**
You shouldn't unless you're hammering it for hours. Max gives generous limits for Claude Code use. If you do hit them, the agent will tell you to wait.

## Updating skills as you learn

The whole point is these skills get better. After a week or two, you'll notice patterns:

- A type of question the agent keeps fumbling → edit the SKILL.md description to mention that pattern
- A new MS gotcha you learned → add it to `ms-stack-quickref/references/`
- A cert you're targeting → tell learning-planner to bias toward that cert's objectives

Just open the SKILL.md files in any text editor (VS Code, Notepad, whatever). Changes take effect immediately the next time Claude reads the skill.
