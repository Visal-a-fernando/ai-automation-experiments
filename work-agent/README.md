# Visal's Work Agent — Starter Pack

A personal AI assistant for your Level 1 IT engineer role. Three skills, two ways to use them, your existing Claude Max subscription powers everything.

## What's in here

```
work-agent/
├── skills/
│   ├── troubleshooting-wizard/    ← structured ticket triage + fillable PDF
│   ├── ms-stack-quickref/         ← fast answers for M365 / Azure questions
│   └── learning-planner/          ← study plans with hands-on labs
├── case-log/                       ← past tickets as PDFs (search later)
├── study-plans/                    ← saved learning plans
├── README.md                       ← this file
├── SETUP-claude-code.md            ← personal laptop path (RECOMMENDED)
└── SETUP-claude-ai.md              ← locked-down work laptop fallback
```

## Two ways to deploy this

### Path A — Claude Code on your personal laptop (recommended)

Full power. Skills load automatically when relevant. PDFs save to your filesystem. Your case-log becomes a searchable knowledge base over time. Uses your Max plan, $0 extra cost.

→ Follow **SETUP-claude-code.md**

### Path B — Claude.ai Projects on a locked-down work laptop (fallback)

If you can't install software on the company laptop, you can paste the skill markdown into a Claude.ai Project's "instructions" field. You lose automatic file saving (PDFs come out as downloads instead of auto-saved to case-log), but the conversational behaviour is identical.

→ Follow **SETUP-claude-ai.md**

## Day one of your new job

Once set up, here's what your first week looks like:

**Monday morning, first ticket arrives:**
> "Hey Claude, just got a ticket — client says SharePoint search isn't returning recent documents."

→ troubleshooting-wizard kicks in, asks diagnostic questions, walks you through it, generates a PDF when done.

**Tuesday, between tickets:**
> "Quick question — what's the cmdlet to see who's a global admin?"

→ ms-stack-quickref answers in 3 lines.

**Wednesday evening at home, planning study:**
> "I want to learn Conditional Access. Where do I start?"

→ learning-planner builds you a 2-week plan with labs in your free dev tenant.

**Friday afternoon:**
> "Have I seen anything like this OneDrive sync issue before?"

→ Claude grep's your case-log/ folder and surfaces prior cases.

## Customising

The skills are markdown files. Edit them as you go. After a month you'll know:
- Which gotchas keep biting you → add them to the ms-stack-quickref references/
- Which question types your skill keeps getting wrong → tighten the SKILL.md description
- New topics you're studying → save the plans, tick the checklists

Treat the agent like a junior version of yourself that gets smarter every month.

## A few rules of the road

1. **Never paste client-identifying info into the agent unnecessarily.** Use "the client" or initials in case PDFs if you'll share them. Real client names only in PDFs that stay on your machine.
2. **Don't run cmdlets the agent suggests without reading them first.** Especially anything with `Remove-`, `Set-`, or `-Force`. Senior engineers check, even when they're 99% sure.
3. **The PDFs are working documents, not official records.** Your company has its own ticketing system. The case-log is your personal learning archive.
4. **If you're ever unsure whether to escalate, escalate.** The agent will tell you the same thing.

Good luck with the new role.
