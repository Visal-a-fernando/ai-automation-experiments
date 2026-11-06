# Setup: web assistant Projects on a locked-down work laptop (Path B)

Use this if your company laptop won't let you install software. You lose automatic PDF saving and case-log search, but the conversational behaviour is the same and it still runs on your existing subscription.

This path needs an AI assistant web app with **Projects** (or workspaces) that have their own custom instructions, plus a code execution or file creation feature for PDFs.

## What you're building

Three Projects, one per skill. Each Project has the skill markdown pasted into its instructions field, which acts like a permanent system prompt for that Project.

## Step 1: Create three Projects

In your assistant's web app, open Projects and create three:

1. `Troubleshooting Wizard`
2. `MS Stack Quickref`
3. `Learning Planner`

## Step 2: Paste the skill instructions

For each Project, open it and edit its instructions.

**For Troubleshooting Wizard:**
Open `skills/troubleshooting-wizard/SKILL.md` in any text editor. Copy everything BELOW the second `---` line (skip the YAML frontmatter at the top). Paste into the Project instructions.

Add this line at the very top of the instructions, since the web app can't save files to your disk:

> **Note:** This is running in a web chat, not an agent CLI, so when the user wants a case PDF, generate one with the code execution feature and present it as a download. Don't try to save to a case-log folder.

**For MS Stack Quickref:**
Same process. Copy the body of `skills/ms-stack-quickref/SKILL.md` (everything below the YAML frontmatter) into the Project instructions.

Also paste the contents of both reference files at the end of the instructions, under a heading "## Reference Material":
- `skills/ms-stack-quickref/references/powershell-modules.md`
- `skills/ms-stack-quickref/references/admin-centres.md`

**For Learning Planner:**
Same process. Body of `skills/learning-planner/SKILL.md` into the Project instructions.

## Step 3: Turn on code execution

For the Troubleshooting Wizard Project especially, you want PDF generation to work. Turn on the app's code execution or file creation feature in that Project's chats. Depending on the app, this may be a per-chat toggle. PDFs then appear in the chat as downloads.

## Step 4: Test each Project

**Troubleshooting Wizard test:**

> A client says their user can't send external email. Outlook desktop. Help me troubleshoot.

Expect: structured diagnostic questions, not a generic answer dump.

**MS Stack Quickref test:**

> Quick question: what's the command to convert a user mailbox to a shared mailbox?

Expect: a short, direct answer with the cmdlet, in the format from the SKILL.md examples.

**Learning Planner test:**

> Build me a 2-week plan to learn Conditional Access. I want hands-on labs.

Expect: a structured plan with a concept map, labs in your free dev tenant, real-world scenarios, and a tracking checklist at the end.

## Daily use

Pin all three Projects in the app. When a ticket comes in, open the right Project and start a chat.

**On mobile too:** if the app has a phone version, the same Projects are usually there. Useful when you're onsite without the laptop.

## What you lose vs Path A

- **Auto-saved PDFs.** You generate them but download and file them yourself (OneDrive folder, etc).
- **Case-log search across past tickets.** Searching past chats in the app isn't the same as searching a folder of PDFs.
- **Direct file editing of the skills.** Updates mean editing the Project instructions in the web UI, not a markdown file.

## What you keep

- All three skill behaviours work the same in conversation
- Runs on your existing subscription, no extra cost
- Works from any browser (handy when switching between work laptop, personal laptop, and phone)
- Project instructions persist, no repeated setup

## If you later switch to Path A

Your skill markdown files are already in this pack. Follow `SETUP-cli-agent.md` when you get a laptop you can install on. You don't lose any work.
