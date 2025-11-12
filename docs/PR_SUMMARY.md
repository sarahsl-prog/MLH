PR update — docs added

This PR now includes a full `docs/` directory with:

- `docs/index.md`, `docs/installation.md`, `docs/usage.md`, `docs/testing.md`, `docs/integration.md`, `docs/development.md`
- `mkdocs.yml` to configure site generation (Material theme)
- `requirements.txt` updated to include `mkdocs` and `mkdocs-material`
- GitHub Actions workflow at `.github/workflows/mkdocs.yml` to build and deploy the site to GitHub Pages on pushes to `main`.

What to review in this PR
- The documentation content in `docs/` (accuracy and wording)
- The `mkdocs.yml` configuration and the GitHub Actions workflow
- Whether you want the site automatically published on `main` pushes or via manual dispatch only

If you'd like, I can tweak the workflow to deploy from the `APITest` branch (for preview) or add a preview step using `actions-gh-pages` with a branch-specific publish target.
