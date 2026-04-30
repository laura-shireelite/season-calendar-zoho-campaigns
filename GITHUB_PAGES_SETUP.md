# GitHub Pages Setup for Campaign HTML Hosting

## Overview

The skill now generates HTML campaign files and saves them to `docs/campaigns/`. These files are served publicly via GitHub Pages, and the public URLs are passed to Zoho Campaigns' `content_url` parameter for full automation.

**Result:** Campaigns created with content immediately visible in Zoho, no manual copy/paste needed.

---

## Setup Steps

### Step 1: Verify Your GitHub Username and Repo Name

Get your GitHub username and repo name ready:

```bash
# In your terminal, find your GitHub username
git config --global user.name
# Output: Laura Garrett (or your name)

# Get your GitHub username from GitHub.com account settings
# Typical format: firstname-lastname, or your preferred GitHub handle
```

### Step 2: Set Environment Variables

Add these to your `config.txt`:

```bash
# GitHub Pages configuration
export GITHUB_USERNAME="your-github-username"
export GITHUB_REPO="zoho-gym-campaigns"
```

Example:
```bash
export GITHUB_USERNAME="laura-garrett"
export GITHUB_REPO="zoho-gym-campaigns"
```

Then reload config:
```bash
source config.txt
```

### Step 3: Create GitHub Repository (if needed)

If you don't have this repo on GitHub yet:

1. Go to https://github.com/new
2. Repository name: `zoho-gym-campaigns`
3. Description: "Automated gym email campaigns via Zoho"
4. Public (required for Pages)
5. Click Create Repository
6. Follow the instructions to push your local code

### Step 4: Enable GitHub Pages

1. Go to your repo on GitHub
2. Settings → Pages
3. Under "Build and deployment":
   - Source: Deploy from a branch
   - Branch: `main` (or `master`)
   - Folder: `/docs`
4. Click Save

GitHub will show you the URL where your site will be published:
```
https://your-github-username.github.io/zoho-gym-campaigns/campaigns/
```

⏳ **Wait 1-2 minutes** for GitHub Pages to build and publish.

### Step 5: Verify GitHub Pages is Working

Check if the site is live:

```bash
curl https://your-github-username.github.io/zoho-gym-campaigns/
```

Or open it in your browser. You should see a blank page or 404 (that's fine - no files yet).

### Step 6: Commit and Push the Docs Directory

```bash
cd /Users/lauragarrett/Documents/zoho-gym-campaigns

git add docs/
git commit -m "Add docs directory for GitHub Pages campaign HTML hosting"
git push origin main
```

### Step 7: Test the Skill

Run the skill:

```bash
source config.txt
python3 main.py
```

Watch the output for:
```
💾 Saved HTML: term-overview-term-2-2026.html
🌐 Public URL: https://your-github-username.github.io/zoho-gym-campaigns/campaigns/term-overview-term-2-2026.html
```

If you see the Public URL, the HTML was saved successfully! ✅

### Step 8: Check Zoho Campaigns

1. Log into Zoho Campaigns
2. Find the newly created draft campaign
3. Look at the CONTENT section
4. **The HTML should be there!** 🎉

---

## Troubleshooting

### Issue: `content_url parameter with data URIs` error

**This is expected and OK.** We switched from data URIs to real public URLs.

### Issue: "GitHub Pages is not live yet"

GitHub Pages takes 1-2 minutes to publish. Wait a bit and try again:

```bash
# Check if the site is live
curl -I https://your-github-username.github.io/zoho-gym-campaigns/
```

Should return `200 OK` when ready.

### Issue: URL returns 404

1. Verify Settings → Pages is set to `/docs` branch `main`
2. Run the skill to generate HTML files
3. Commit and push the generated HTML:
   ```bash
   git add docs/campaigns/
   git commit -m "Generated campaign HTML"
   git push
   ```
4. Wait 1-2 minutes for GitHub to rebuild
5. Test the URL again

### Issue: Campaigns created but content is empty

1. Check the skill output for the generated public URL
2. Verify the URL is correct in Zoho's campaign details
3. Test the URL in your browser - it should show the HTML
4. If the URL works but Zoho shows no content:
   - Zoho might be caching - try refreshing
   - Contact Zoho support about content_url support

---

## How It Works

1. **Skill runs** (3x per year, automatically)
2. **Campaign generator creates HTML** files
3. **Files saved to** `docs/campaigns/`
4. **Files committed to GitHub** (or pushed by CI/CD)
5. **GitHub Pages publishes** them publicly
6. **Campaign generator returns** public URL
7. **Zoho API called** with `content_url` pointing to the hosted HTML
8. **Zoho imports** the HTML and creates campaign with content ✅

---

## Next Steps

Once verified:
1. Commit the updated code:
   ```bash
   git add campaign_generator.py zoho_campaigns_client.py config.txt
   git commit -m "Implement GitHub Pages hosting for campaign HTML"
   git push
   ```

2. Schedule the skill to run automatically:
   - May 15 (Term 2 start)
   - Sept 30 (Term 3 start)  
   - Jan 15 (Term 1 start)

3. Done! Campaigns will be created with content fully automated 🚀

---

## Reference

- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [Zoho Campaigns API - content_url](https://www.zoho.com/campaigns/help/api/campaign-content.html)
- [Your Generated Campaign Files](https://github.com/YOUR_USERNAME/zoho-gym-campaigns/tree/main/docs/campaigns)
