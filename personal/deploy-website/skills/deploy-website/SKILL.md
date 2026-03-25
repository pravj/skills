---
name: deploy-website
description: Build the Hugo personal website and deploy to GitHub Pages. Use when the user has made changes to their website and wants to publish them. TRIGGER when: user mentions deploying website, publishing a post, updating their site, or pushing website changes.
user-invocable: true
allowed-tools:
  - Bash
  - Read
  - Glob
  - Grep
---

# Deploy Website to GitHub Pages

Build the Hugo site at `~/Projects/website/personal-website` and deploy the output to `~/Projects/website/pravj.github.io` (GitHub Pages repo for hackpravj.com).

## Step 1: Check for changes

```bash
cd ~/Projects/website/personal-website && git diff --stat && git status --short
```

Show the user a brief summary of what changed (new posts, modified layouts, config changes, etc.).

## Step 2: Build with Hugo

```bash
cd ~/Projects/website/personal-website && hugo
```

- Confirm the build succeeds with no errors.
- Note the number of pages generated and build time from Hugo's output.

## Step 3: Sync build output to GitHub Pages repo

```bash
rsync -av --delete --exclude='.git' --exclude='CNAME' ~/Projects/website/personal-website/public/ ~/Projects/website/pravj.github.io/
```

The `--exclude='.git'` preserves the git repo in the target. The `--exclude='CNAME'` preserves the custom domain config (`hackpravj.com`).

## Step 4: Show diff and confirm

```bash
cd ~/Projects/website/pravj.github.io && git status --short && git diff --stat
```

Show the user what files changed in the deploy repo. **Ask for confirmation before committing and pushing.**

## Step 5: Commit and push

After the user confirms:

```bash
cd ~/Projects/website/pravj.github.io
git add -A
git commit -m "site update: <brief description of changes>"
git push origin main
```

Derive the commit message from what changed in the Hugo source (e.g., "site update: new blog post on X" or "site update: layout and styling changes").

## Step 6: Confirm deployment

Tell the user the site should be live at https://hackpravj.com in a minute or two.

## Notes

- Hugo binary: `/opt/homebrew/bin/hugo`
- Hugo config: `hugo.toml` (baseURL: https://hackpravj.com/)
- The `public/` directory in personal-website is the build output
- The `pravj.github.io` repo is the GitHub Pages source — pushing to main triggers deployment
- Always preserve the `CNAME` file in pravj.github.io (contains `hackpravj.com`)
