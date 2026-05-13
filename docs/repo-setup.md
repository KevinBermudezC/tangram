# GitHub repository setup

This document lists the GitHub-side configuration that lives outside the repo — branch rulesets, CODEOWNERS enforcement, repo settings — and the rationale behind each choice.

If you fork Tangram, you do not need to replicate any of this; it only applies to the upstream maintainers' configuration of `KevinBermudezC/tangram`.

## Branch ruleset — `main`

Create the ruleset under **Settings → Rules → Rulesets → New branch ruleset**.

| Field | Value |
| --- | --- |
| Ruleset name | `main protection` |
| Enforcement status | **Active** |
| Bypass list | While the project is solo-maintained, the owner SHOULD be in the bypass list with **mode: Pull request only**. This lets the owner merge their own PRs without a second approver (no one else exists), but still blocks direct pushes to `main` and still requires external contributor PRs to be approved. **Remove the owner from the bypass list once a second maintainer joins.** |
| Target branches | Include `main` |

### Rules to enable

| Rule | State | Why |
| --- | --- | --- |
| **Restrict deletions** | On | `main` should never be deletable. |
| **Block force pushes** | On | History must be immutable. |
| **Require linear history** | On | No merge commits — keeps the log readable. Squash-and-merge becomes the default merge strategy. |
| **Require a pull request before merging** | On | All changes flow through PRs. |
| └ Required approvals | **1** | Smallest viable for a 2-person team. Increase to 2 when team grows. |
| └ Dismiss stale pull request approvals when new commits are pushed | On | Re-review after substantive changes. |
| └ Require review from Code Owners | On | Pairs with `.github/CODEOWNERS`. Only listed owners can satisfy the required approval for a given path. |
| └ Require approval of the most recent reviewable push | On | The last commit must be approved, not just the original PR. |
| └ Require conversation resolution before merging | On | All inline review comments must be resolved or explicitly accepted. |
| **Require status checks to pass** | On (after CI lands — roadmap item #4) | Will require: `lint`, `tests`, `openspec validate`. |
| └ Require branches to be up to date before merging | On (when CI is on) | Prevents merging stale branches. |
| **Require signed commits** | Off (for now) | Adds friction for first-time contributors. Reconsider in Phase 2/3 if supply-chain becomes a concern. |
| **Block creations** | Off | We want contributors to be able to create branches. |

### What this gives you

- Nobody (including the repo owner, under normal use) can push directly to `main`.
- Every change goes through a PR, gets at least one approval, and ideally from a Code Owner for the touched paths.
- The `main` history is linear (no merge commits) — `git log` reads top-to-bottom like a story.
- Once CI lands, broken PRs cannot land in `main` even with approvals.

## Repository settings — general

Under **Settings → General**:

| Setting | Recommended value |
| --- | --- |
| Default branch | `main` |
| Pull Requests → Allow merge commits | **Off** |
| Pull Requests → Allow squash merging | **On**, with "Default to PR title and description" |
| Pull Requests → Allow rebase merging | **On** (optional, useful for clean histories) |
| Pull Requests → Always suggest updating PR branches | **On** |
| Pull Requests → Automatically delete head branches | **On** |
| Issues → Templates | (see `.github/ISSUE_TEMPLATE/` — to be added in a future proposal) |

## Repository settings — collaboration

Under **Settings → Collaborators**:

- Add co-maintainers with the **Maintain** role (not Admin) — they can manage issues and PRs but not delete the repo or change ruleset.
- Reserve **Admin** for the project owner.

## Repository settings — security

Under **Settings → Code security**:

| Feature | Recommended |
| --- | --- |
| Dependabot alerts | **On** |
| Dependabot security updates | **On** |
| Code scanning (CodeQL) | **On** once CI lands |
| Secret scanning | **On** |
| Push protection for secrets | **On** |

These are zero-friction wins for an OSS project.

## CODEOWNERS

The file at `.github/CODEOWNERS` defines who must review which paths. Pair it with the ruleset's "Require review from Code Owners" rule for enforcement.

Update the file whenever:
- A new maintainer joins the team.
- A subsystem grows large enough to deserve its own owner (e.g. once `patterns/` has dozens of files, you might want a "patterns librarian" as a dedicated reviewer for it).

## Ruleset as JSON (advanced, optional)

If you prefer to manage the ruleset via GitHub API or sync between repos, the equivalent JSON is below. Apply with:

```bash
gh api repos/KevinBermudezC/tangram/rulesets --input ruleset.json
```

```json
{
  "name": "main protection",
  "target": "branch",
  "enforcement": "active",
  "conditions": {
    "ref_name": {
      "include": ["refs/heads/main"],
      "exclude": []
    }
  },
  "rules": [
    { "type": "deletion" },
    { "type": "non_fast_forward" },
    { "type": "required_linear_history" },
    {
      "type": "pull_request",
      "parameters": {
        "required_approving_review_count": 1,
        "dismiss_stale_reviews_on_push": true,
        "require_code_owner_review": true,
        "require_last_push_approval": true,
        "required_review_thread_resolution": true
      }
    }
  ]
}
```

Once CI lands and we have named status checks, add a `required_status_checks` rule with the check names.

## Open questions

- **Should we require 2 approvals once we have 3+ maintainers?** Yes, and update this doc when that happens.
- **Should the partner maintainer be added to CODEOWNERS with admin or maintain role?** Maintain is enough for daily work; admin only for the project owner.
- **Should we require signed commits?** Not in MVP — friction outweighs benefit at our scale. Revisit in Phase 2.
