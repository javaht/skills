---
name: github-submit-sync
description: Use when the user asks to submit, commit, push, publish, or release code to GitHub, including Chinese requests like 提交到GitHub, 提交到 GitHub, 推送到GitHub, 发布到GitHub, 帮我提交代码, and English requests with GitHub, push, publish, or commit. Before committing or pushing, always sync the local branch with the latest remote code first.
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
   - Create the commit with an accurate message.
   - Push to the current branch's configured upstream unless the user names a different target.

## Stop Conditions

Stop and report the exact state instead of continuing when:

- The current branch has no upstream.
- The upstream branch or remote target is ambiguous.
- `git pull --rebase --autostash` reports conflicts or stops mid-rebase.
- The working tree contains unrelated changes that would make staging ambiguous.

Do not run `git reset --hard`, `git checkout --`, `git clean`, force push, or otherwise discard work unless the user explicitly asks for that operation.
