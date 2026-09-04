# Rule: docs lifecycle — specs shrink as code ships

`spec.md` (an untracked, local planning file — see `.gitignore`) describes what does **not**
exist yet. Once a section is implemented, that section stops being a spec and becomes a fact
about the codebase — so it belongs in the live docs, not in `spec.md`.

## The rule

When a PR implements a `spec.md` section, that same PR must:

1. **Delete** the implemented content from `spec.md` (the whole section, or the specific
   subsections that are now shipped).
2. **Add** the equivalent, "what actually exists" description to the live docs:
   - `README.md` for user-facing usage, inputs/outputs, and examples;
   - `docs/template-override-guide.md` for custom-template-pack behavior;
   - `DEVELOPER.md` for local-dev workflow and QA commands.

This is a **move**, not a copy. After the PR, the information exists in exactly one place —
the live docs — and `spec.md` is smaller. `spec.md` trends toward empty as features ship.

## What "move" means

- Do not leave the section in `spec.md` with a "✅ implemented" marker. Remove it.
- Do not duplicate the same table/flow in both `spec.md` and the live doc. One home.
- If only part of a section shipped, split it: the shipped part moves to live docs, the
  unshipped part stays in `spec.md`.
- Cross-references that pointed at the moved `spec.md` section must be repointed to its new
  home in the same PR (keep `link-check` green).

## When spec.md is empty

When the local planning file has no remaining unimplemented content, delete it (or leave it
absent — it is gitignored and not part of the committed tree either way). A spec with
nothing prospective in it is drift waiting to happen.
