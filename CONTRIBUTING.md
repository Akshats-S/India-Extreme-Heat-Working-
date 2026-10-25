# Contributing

This is a small university research group project. The workflow below keeps `main` stable and every change reviewable.

## Ground rules

1. **Do not push directly to `main`.** All changes go through a pull request (PR) reviewed by at least one teammate. A repository rule enforces the PR requirement.
2. **Work from an Issue.** Each task is tracked as a GitHub Issue. Comment on the Issue (or ask to be assigned) before starting so work is not duplicated.
3. **Never commit raw IMD data** or anything under `data/raw/` (see `data/README.md`). Also never commit credentials, tokens or personal files.
4. **AI tools are allowed.** The course instructor has confirmed full freedom to use AI/LLM tools. You remain responsible for everything you commit: read and verify AI-generated code and text, and never commit fabricated data or results.

## Branches

1. Update your local `main`:

   ```bash
   git checkout main
   git pull origin main
   ```

2. Create a branch from `main`. Proposed naming: `<type>/<issue-number>-<short-description>`, for example:
   - `data/3-validate-missing-values`
   - `docs/7-finalize-readme`
   - `feature/5-build-clean-dataset`
   - `fix/12-date-parsing`
3. Keep branches small and focused on one Issue.

## Commits

- Write short, imperative messages (e.g. `Add duplicate check for city-date pairs`).
- Commit logically related changes together; avoid mixing unrelated edits.
- Reference the Issue where relevant (`Refs #3`).

## Pull requests

1. Push your branch and open a PR into `main` (a PR template with a checklist will appear).
2. In the description, state what changed, link the Issue (`Closes #N` when the PR fully completes it), and note how a reviewer can check it.
3. Request a review from at least one teammate. Address comments with follow-up commits.
4. Confirm before requesting review: no data files or secrets are included, scripts run from a clean checkout as far as implemented, and documentation reflects what is actually done (mark unfinished items as pending).
5. Merge once approved. Delete the branch after merging.

## Code and documentation conventions (proposed)

- Python 3; keep reusable code in `src/` and exploration in `notebooks/`.
- The final pipeline must run end to end with no manual steps (course requirement).
- Record any data-processing decision in `docs/methodology.md` when it is made.
- Keep `requirements.txt` up to date when adding dependencies.
- Distinguish clearly between completed and planned work in all documentation.
- Log human verification of each step in `docs/verification-log.md`; the instructors review the code.

## Using AI assistants

- Point your assistant at [AGENTS.md](AGENTS.md) first; it contains the project context, the data schema and the rules above.
- AI tools may be used for any part of the work (code, analysis, writing).
- You remain responsible for everything you commit. Review AI-written code before opening a pull request, and do not paste raw IMD data or credentials into an AI tool or into the repository (IMD's redistribution terms are unconfirmed).

## Branch protection

`main` is protected by a repository rule: changes must arrive through a pull request, and force-pushes and deletion of `main` are blocked. Required approvals are currently 0; the team may raise this to 1 once all members have joined.

## Questions

Open a GitHub Issue or discuss in your team channel.
