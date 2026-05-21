---
name: github-submit-sync
description: Use when the user asks to submit, commit, push, publish, or release code to GitHub, including Chinese requests like 提交到GitHub, 提交到 GitHub, 推送到GitHub, 发布到GitHub, 帮我提交代码, and English requests with GitHub, push, publish, or commit. Before committing or pushing, always sync the local branch with the latest remote code first and ensure commit metadata uses only the human author's identity, never Claude Code or any AI assistant identity.
---

# GitHub Submit Sync

When the user asks to submit code to GitHub, publish to GitHub, push changes, or otherwise commit and push work, treat remote freshness as part of the default workflow.

## Required Flow

1. Inspect the repository before staging anything:
   ```bash
   git status --short --branch
   git branch --show-current
   git rev-parse --abbrev-ref --symbolic-full-name @{u}
   ```

2. Sync latest remote code before creating the commit or pushing:
   ```bash
   git fetch --all --prune
   git pull --rebase --autostash
   ```

3. Continue the normal submit flow only after the sync succeeds:
   - Stage only changes related to the user's request.
   - Confirm the commit identity before committing:
     ```bash
     git config --get user.name
     git config --get user.email
     git var GIT_AUTHOR_IDENT
     git var GIT_COMMITTER_IDENT
     env | rg '^(GIT_AUTHOR|GIT_COMMITTER)_(NAME|EMAIL)=' || true
     ```
   - Create the commit with an accurate message and only the human author's identity in the author and committer metadata.
   - Do not include `Claude Code`, `Codex`, `OpenAI`, `Anthropic`, known agent names, or any other AI assistant identity in the commit author, committer, or commit-message trailers such as `Co-authored-by`.
   - Verify the newly created commit before pushing:
     ```bash
     git show -s --format=fuller HEAD
     ```
   - Push to the current branch's configured upstream unless the user names a different target.

## Stop Conditions

Stop and report the exact state instead of continuing when:

- The current branch has no upstream.
- The upstream branch or remote target is ambiguous.
- `git pull --rebase --autostash` reports conflicts or stops mid-rebase.
- The working tree contains unrelated changes that would make staging ambiguous.
- The correct human author identity is unknown or cannot be verified.
- The configured author, committer, environment overrides, or newly created commit metadata contains Claude Code, Codex, OpenAI, Anthropic, known agent names, or any non-human assistant identity.

Do not run `git reset --hard`, `git checkout --`, `git clean`, force push, or otherwise discard work unless the user explicitly asks for that operation.
