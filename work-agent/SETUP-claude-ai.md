# Setup: Claude.ai Projects on a locked-down work laptop (Path B)

Use this if your company laptop won't let you install software. You'll lose the automatic PDF generation and case-log search, but the conversational behaviour is identical and you still use your Max plan.

## What you're building

Three Projects in Claude.ai, one per skill. Each project has the skill markdown pasted into the "Project instructions" field, which acts like a permanent system prompt for that project.

## Step 1: Create three Projects

In Claude.ai (https://claude.ai), click **Projects** in the left sidebar, then **+ New Project**.

Create three projects with these names:

1. `Troubleshooting Wizard`
2. `MS Stack Quickref`
3. `Learning Planner`

## Step 2: Paste the skill instructions

For each project, click the project name to open it, then click **Set instructions** (or "Edit instructions" if you've already set them).

**For Troubleshooting Wizard:**
Open `skills/troubleshooting-wizard/SKILL.md` in any text editor. Copy everything BELOW the second `---` line (don't copy the YAML frontmatter at the top). Paste into the project instructions.

Add this line at the very top of the instructions, since Claude.ai can't auto-save PDFs:

> **Note:** This is running in Claude.ai (not Claude Code), so when the user wants a case PDF, generate one using the Code Execution feature (it's available in this conversation) and present it as a download. Don't try to save to a case-log folder.

**For MS Stack Quickref:**
Same process. Copy the body of `skills/ms-stack-quickref/SKILL.md` (everything below the YAML frontmatter) into project instructions.

Also paste the contents of both reference files at the end of the instructions, under a heading "## Reference Material". They are:
- `skills/ms-stack-quickref/references/powershell-modules.md`
- `skills/ms-stack-quickref/references/admin-centres.md`

**For Learning Planner:**
Same process. Body of `skills/learning-planner/SKILL.md` into project instructions.

## Step 3: Enable Code Execution in each project

For the Troubleshooting Wizard project especially, you want PDF generation to work. In any conversation in that project:

1. Click the **+** button next to the chat input
2. Make sure **Code interpreter** (or "Code Execution") is enabled

You may need to toggle this on per-conversation depending on Claude.ai settings at the time you read this. PDFs will then be generated in the chat as downloadable files.

## Step 4: Test each project

**Troubleshooting Wizard test:**
Open the project, start a new chat, type:

> A client says their user can't send external email. Outlook desktop. Help me troubleshoot.

Expect: structured diagnostic questions, not a generic answer dump.

**MS Stack Quickref test:**

> Quick question — what's the command to convert a user mailbox to a shared mailbox?

Expect: short, direct answer with the cmdlet, in the format from the SKILL.md examples.

**Learning Planner test:**

> Build me a 2-week plan to learn Conditional Access. I want hands-on labs.

Expect: structured plan with concept map, labs in your free dev tenant, real-world scenarios, and a tracking checklist at the end.

## Daily use

Pin all three projects to your sidebar in Claude.ai. When a ticket comes in, open the right project and start a chat.

**On mobile too:** The Claude app on your phone has access to the same projects. Useful when you're onsite and don't have the laptop open.

## What you lose vs Path A

- **Auto-saved PDFs.** You'll generate them but download manually and file them somewhere yourself (OneDrive folder, etc).
- **Case-log search across past tickets.** You can search past Claude.ai chats from within the app, but it's not the same as grepping a folder of PDFs.
- **Direct file editing of the skills.** Updates mean editing the project instructions in the web UI, not a markdown file.

## What you keep

- All three skill behaviours work identically in conversation
- Your Max plan covers it, no extra cost
- Works from any browser (handy if you switch between work laptop, personal laptop, and phone)
- Project instructions persist forever, no setup repeating

## If you later switch to Path A

Easy. Your skill markdown files are already in this pack. Just follow `SETUP-claude-code.md` when you get a laptop you can install on. You don't lose any work.
