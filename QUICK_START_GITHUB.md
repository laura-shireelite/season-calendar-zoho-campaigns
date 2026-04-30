# Quick Start - Push to GitHub

Your GitHub username is now set to `laura-shireelite`. Follow these steps to push your code to GitHub.

## Step 1: Create Repository on GitHub

Go to https://github.com/new and create a new repo:

- **Repository name:** `zoho-gym-campaigns`
- **Description:** Automated gym email campaigns via Zoho
- **Public** (required for GitHub Pages)
- Click **Create repository**

## Step 2: Copy-Paste These Commands in Your Terminal

Replace `<token>` with a GitHub Personal Access Token (see Step 3 below).

```bash
cd /Users/lauragarrett/Documents/zoho-gym-campaigns

git init
git add .
git commit -m "Initial commit: Zoho Campaigns automation with GitHub Pages"
git branch -M main
git remote add origin https://github.com/laura-shireelite/zoho-gym-campaigns.git
git push -u origin main
```

If you get an authentication error, you need a Personal Access Token (see Step 3).

## Step 3: Create GitHub Personal Access Token (if needed)

If `git push` asks for a password:

1. Go to https://github.com/settings/tokens
2. Click **Generate new token** (classic)
3. Name it: `zoho-campaigns`
4. Check: `repo` (Full control of private repositories)
5. Click **Generate token**
6. **Copy the token** (you won't see it again!)
7. When git asks for password, paste the token

Then retry the `git push` command above.

## Step 4: Enable GitHub Pages

1. Go to https://github.com/laura-shireelite/zoho-gym-campaigns/settings/pages
2. Under "Build and deployment":
   - **Source:** Deploy from a branch
   - **Branch:** main
   - **Folder:** /docs
3. Click **Save**

Wait 1-2 minutes for it to deploy.

## Step 5: Verify GitHub Pages is Live

```bash
curl https://laura-shireelite.github.io/zoho-gym-campaigns/
```

Should return a page (might be blank - that's OK).

## Done!

Once you see the GitHub Pages URL working, run the skill:

```bash
source config.txt
python3 main.py
```

You should see generated HTML files and public URLs! 🎉
