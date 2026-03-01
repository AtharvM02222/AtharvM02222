# 🔑 Personal Access Token Setup

To count lines across ALL your repositories (public + private), you need to create a Personal Access Token (PAT).

## Quick Setup (5 minutes):

### Step 1: Create a Personal Access Token

1. Go to: **https://github.com/settings/tokens**
2. Click **"Generate new token"** → **"Generate new token (classic)"**
3. Give it a name: `Line Counter Token`
4. Set expiration: **"No expiration"** (or choose 90 days and renew later)
5. Check this scope:
   - ✅ **`repo`** (Full control of private repositories)
6. Scroll down and click **"Generate token"**
7. **COPY THE TOKEN** - you won't see it again! (looks like: `ghp_xxxxxxxxxxxx`)

### Step 2: Add Token to Your Repository

1. Go to: **https://github.com/AtharvM02222/AtharvM02222/settings/secrets/actions**
2. Click **"New repository secret"**
3. Name: `PAT_TOKEN`
4. Value: Paste your token from Step 1
5. Click **"Add secret"**

### Step 3: Run the Workflow

1. Go to: **https://github.com/AtharvM02222/AtharvM02222/actions**
2. Click **"Count Lines of Code"** workflow
3. Click **"Run workflow"** → **"Run workflow"**
4. Wait 2-5 minutes
5. Check your README - it will show lines from ALL your repos!

---

## What This Does:

✅ Counts lines in ALL your repositories (public + private)  
✅ Shows total lines of code  
✅ Shows number of repositories counted  
✅ Updates automatically every Sunday  
✅ Can be triggered manually anytime  

---

## Without PAT (Current):

❌ Only counts PUBLIC repositories  
❌ Shows "1 repository" (just your profile repo)  

## With PAT:

✅ Counts ALL repositories (public + private)  
✅ Shows accurate total across all your code  

---

## Security:

- The PAT is stored securely in GitHub Secrets
- Only this workflow can access it
- It's never exposed in logs
- You can revoke it anytime from: https://github.com/settings/tokens

---

## Need Help?

If the workflow fails after adding the PAT:
1. Make sure the secret name is exactly `PAT_TOKEN`
2. Verify the token has `repo` scope checked
3. Check the Actions tab for error messages

---

**That's it! Once set up, your README will show the total lines of code across all your repositories!** 🚀
