# AI / Automation Experiments

Two working experiments in putting an LLM behind a deterministic control loop - letting the model *think* at a few well-defined points while ordinary code stays
in charge of everything that has to be reliable.

Both are powered by a headless LLM CLI (the `the LLM CLI` command), invoked
in-process. There are no model API keys in these projects - auth rides on the
CLI's own login.

## 1. `work-agent/` - a Telegram-driven IT support assistant

A personal Level-1 IT engineer's assistant. You message a Telegram bot; each
message is forwarded to the LLM CLI running in a working folder it can read and
write, and the reply comes back on your phone. It ships with three **skills**:

- **troubleshooting-wizard** - structured ticket triage that produces a fillable
  case PDF
- **ms-stack-quickref** - fast M365 / Azure / PowerShell reference
- **learning-planner** - study plans with hands-on labs

Setup guides for both a full local install and a locked-down work-laptop
fallback are in `work-agent/`. Real support tickets and inbox images are **not**
committed - those folders are runtime placeholders.

## 2. `pinflow/` - a dropshipping orchestrator

A deterministic, debuggable "spine" for an automated storefront. The control
flow lives in ordinary Python; the LLM is called at exactly three points - score
product candidates, write listing copy, write an SEO blog post. It runs today as
a dry loop (research/publish are stubs, state is a local JSON file), ready to
swap in Supabase + Shopify + a real research source once the spine is solid.

The design principle it demonstrates: **treat the model as one bounded evaluator,
never as the thing that pulls the trigger.**

## Setup

Each subproject has its own `.env.example`. Copy it to `.env`, fill in your
values locally, and never commit the `.env`. Both expect the `the LLM CLI` CLI on
your `PATH` (`npm install -g @anthropic-ai/the LLM CLI-code`, then `the LLM CLI login`).

## License

MIT - see `LICENSE`.
