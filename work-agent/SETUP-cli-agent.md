# Setup: an agent CLI on your personal laptop (Path A)

This is the recommended path. You get full file access, automatic PDF generation, and a searchable case history, all on the AI subscription you already have.

## What you're installing

An agent CLI is a command-line AI assistant. You open a terminal, start the CLI, and it works inside a folder it can actually read and write files in. Any agent CLI that supports skill folders (a `SKILL.md` file with YAML frontmatter per skill) and headless `-p` mode will work. The commands below use `<cli>` as a placeholder for your CLI's command.

Works on Windows, macOS, and Linux. The instructions below assume Windows.

## Step 1: Install the CLI

Follow your CLI's own install instructions, then check it is on your PATH:

```bash
<cli> --version
```

If the terminal can't find it, close and reopen the terminal so it picks up the new PATH.

## Step 2: Sign in

```bash
<cli>
```

The first run opens a browser to sign in. Use the account that holds your subscription so usage comes out of your plan rather than API billing.

## Step 3: Put the work-agent folder somewhere permanent

Move the whole `work-agent/` folder (the one this file is in) to wherever you want it. Suggested:

- **Windows:** `C:\Users\Visal\work-agent\`
- **macOS:** `~/work-agent/`

## Step 4: Make the skills available

Most agent CLIs look for skills in a project-level skills folder or a global one in your home directory. Check your CLI's docs for the exact folder name; below it is shown as `<skills-dir>`.

**Easiest path: make them global** (available from any folder you're in):

**Windows:**
```powershell
mkdir <skills-dir> -Force
Copy-Item -Path .\skills\* -Destination <skills-dir> -Recurse
```

**macOS / Linux:**
```bash
mkdir -p <skills-dir>
cp -r ./skills/* <skills-dir>/
```

Global is the better choice. You want the agent available whenever you open a terminal, not only when you remember to cd into a specific folder.

## Step 5: Install the Python library for PDF generation

The troubleshooting-wizard skill generates PDFs using `reportlab`. Install it once:

```bash
pip install reportlab
```

If you don't have Python at all, install it from https://www.python.org/downloads/ first. Tick "Add Python to PATH" during install.

## Step 6: Test it

Open a new terminal window, start the CLI, then type:

> Pretend a client just called: their user can't sign in to Outlook after we reset her password. Start troubleshooting.

If the troubleshooting-wizard skill is loaded, the agent starts asking structured diagnostic questions. If it just gives generic advice, the skill isn't being seen. Check that the file sits at `<skills-dir>/troubleshooting-wizard/SKILL.md`, one folder deep.

## Daily use

Open a terminal and start the CLI. The three skills are always available. Try things like:

- *"Client says Teams calls are dropping after 60 seconds, help me troubleshoot."*
- *"Quick question: how do I check if a user has MFA enabled?"*
- *"Build me a study plan for Intune device compliance, 2 weeks, I want to be exam-ready for MD-102."*
- *"Have we seen any OneDrive sync issues before?"* (searches case-log/)

## Where things get saved

- **Case PDFs:** `work-agent/case-log/CASE-YYYY-NNNN-*.pdf`
- **Study plans:** `work-agent/study-plans/[topic].md`

To search past cases:
```bash
cd ~/work-agent
ls case-log/                                   # list all
grep -l "Conditional Access" case-log/*.pdf    # find by content (needs pdftotext)
```

Or ask the agent: *"List all my past cases involving OneDrive."*

## Troubleshooting the agent itself

**The skills aren't triggering.**
Use your CLI's command for listing loaded skills. If the three skills aren't listed, the path is wrong. They need to be at `<skills-dir>/[skill-name]/SKILL.md`, one folder deep, with the YAML frontmatter intact.

**PDF generation fails.**
Make sure `reportlab` is installed in the Python the CLI can see. Run `python -c "import reportlab; print(reportlab.__version__)"` to check.

**Hitting plan rate limits.**
Unlikely unless you use it for hours on end. If you do hit them, the agent will tell you to wait.

## Updating skills as you learn

The point is that these skills get better. After a week or two you'll notice patterns:

- A type of question the agent keeps fumbling → edit the SKILL.md description to mention that pattern
- A new Microsoft gotcha you learned → add it to `ms-stack-quickref/references/`
- A cert you're targeting → tell learning-planner to bias toward that cert's objectives

Open the SKILL.md files in any text editor. Changes take effect the next time the agent reads the skill.
