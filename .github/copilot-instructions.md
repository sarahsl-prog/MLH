## Purpose

These instructions help an AI coding agent become productive in this repository. They are intentionally concise and action-focused. If this file already exists, merge your changes preserving any human-written guidance.

## Current repo snapshot

During analysis no source files or README were found in the workspace root. That means the repository may be empty or the workspace view is limited. Follow the "first steps" below to discover project structure before making changes.

## First steps (what to run / inspect)

- List top-level files and common manifests: check for `package.json`, `pyproject.toml`, `requirements.txt`, `setup.py`, `Pipfile`, `go.mod`, `Cargo.toml`, `Makefile`, `Dockerfile` and `.github/workflows`.
- Look for typical source dirs: `src/`, `app/`, `lib/`, `server/`, `web/`, `packages/`, `cmd/`.
- If none of the above exist, ask the human: "Is this repo intentionally empty or am I looking at the wrong folder?"

Commands (run in repository root):

Windows (cmd.exe):

  dir /b

Look for common manifests manually after listing files.

## How to discover the big-picture architecture

- If you find `README.md`, start there. Look for an "architecture" or "overview" section.
- If you find multiple subfolders (for example `api/`, `worker/`, `ui/`), treat them as service boundaries. Open each service's manifest (package.json, pyproject.toml, etc.) to learn its runtime and dependencies.
- If there is a `docker-compose.yml` or `Dockerfile`, inspect it to infer runtime ports, service names, and environment variables.

## Developer workflows to try (project-specific)

Because this workspace currently contains no source files, there are no project-specific build or test commands to document. When files are present, prefer the following discovery order rather than assuming commands:

1. Find and read `README.md` and any `docs/` or `docs/*.md` files.
2. Inspect package manifests (see list above) and use the scripts there (e.g., `npm run`, `poetry run`, `make`).
3. Check `.github/workflows` for CI commands which often show canonical build/test steps.

Example: if `package.json` exists, use `npm ci` then `npm test` rather than `npm install` when CI-like reproducibility is desired.

## Project-specific conventions & patterns to detect

- Mono-repo layout: presence of `packages/` or `workspace` keys in package manifests usually means multiple packages. Treat each package as independently buildable.
- Feature flags/environment config: prefer reading `.env.example`, `config/`, or `env.*` files to learn runtime configuration names.
- Database migrations: look for `migrations/`, `alembic/`, or `prisma/` directories and reference them when making schema changes.

## Integration points & external dependencies

- Search for references to external services in environment variables (e.g., `REDIS_URL`, `DATABASE_URL`, `SENTRY_DSN`, `AWS_`) and prefer to run code with safe local mocks or test containers.
- If CI config references cloud providers or secrets, do not attempt network actions—ask maintainers for credentials or a reproducible test harness.

## When editing or creating files

- Keep changes minimal and focused. If adding new code, include a small README and a test that demonstrates the behavior.
- Add/update manifests (package.json, requirements) to allow reproducible installs; include pinned versions when creating manifests.

## Examples and patterns to extract (for future merges)

- If you later find `server/index.js` and `web/src/index.tsx`, treat `server` as backend and `web` as frontend. Look for shared types in `shared/` or `packages/common`.
- If `Makefile` contains targets `build`, `test`, `lint`, prefer calling those targets.

## Merge guidance

- If `.github/copilot-instructions.md` already exists, append a short dated note with the agent's additions and keep any human-written bullet points intact. Do not delete or rewrite human guidance.

## Questions for maintainers (when repo is empty)

1. Is this the intended repository root? If not, where is the main project folder?
2. Are there any private submodules or files excluded from this workspace that I should be aware of?

If you receive no reply within a reasonable time, create a short PR with exploratory README and a placeholder `src/` showing how you propose to structure the project, and include CI-free, non-destructive tests.

---
If anything here is unclear or you want agent behaviour tuned (for example, prefer TypeScript-first changes, or always run tests in Docker), tell me and I'll update this instruction file.
