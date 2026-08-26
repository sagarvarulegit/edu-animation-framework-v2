# AI Agent Handoff Guide

This repository is designed for multiple AI coding agents.

## First action

Read:

1. `AGENTS.md`
2. `README.md`

Then inspect the current repository.

## Never assume

Do not assume:

- Blender is the only renderer;
- every lesson needs Blender;
- every object needs a new model;
- a generated scene is visually correct;
- scientific details can be inferred;
- the previous agent implemented the ideal architecture.

## Before editing

Answer internally:

- What is the current architecture?
- Which files own this behavior?
- Can an existing primitive be reused?
- Is this lesson-specific or framework-level?
- Does this change affect other renderers?

## After editing

Run appropriate validation and document:

- what changed;
- what was tested;
- what was visually inspected;
- known limitations;
- what should happen next.

## If blocked

Do not invent a workaround that silently changes educational meaning.

Document the blocker and propose alternatives.

## If replacing an implementation

Preserve behavior unless the task explicitly changes behavior.

Do not perform unrelated refactors.

## Visual work

For visual changes, code execution is insufficient.

Generate a preview if possible and inspect:

- composition;
- framing;
- readability;
- scientific interpretation;
- animation timing;
- materials;
- lighting.

## Scientific work

When a lesson involves:

- equations;
- reactions;
- measurements;
- physical laws;
- biological processes;

validate the content against reliable sources where necessary.

If a simplification is used, document it.

## Handoff format

```text
Completed:
- ...

Changed:
- ...

Validation:
- ...

Visual QA:
- ...

Known limitations:
- ...

Next:
- ...
```
