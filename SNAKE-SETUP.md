# 🐍 Snake Animation Setup Guide

## ✅ Fixed the Workflow!

The snake workflow has been updated with proper permissions. No need to create a Personal Access Token!

## 📝 Setup Steps:

### 1. Push Files to GitHub
```bash
cd Github/AtharvM02222
git add .
git commit -m "Add snake animation workflow"
git push
```

### 2. Enable Workflow Permissions
1. Go to your repo: `https://github.com/AtharvM02222/AtharvM02222`
2. Click **Settings** tab
3. Click **Actions** → **General** (left sidebar)
4. Scroll to **Workflow permissions**
5. Select **"Read and write permissions"**
6. Check **"Allow GitHub Actions to create and approve pull requests"**
7. Click **Save**

### 3. Run the Workflow
1. Go to **Actions** tab
2. Click **"Generate Snake Animation"** in the left sidebar
3. Click **"Run workflow"** button (top right)
4. Select branch: **main**
5. Click green **"Run workflow"** button
6. Wait 1-2 minutes for completion ✅

### 4. Check Results
- Workflow should complete successfully
- An `output` branch will be created automatically
- Snake animation will appear in your README!

## 🔧 What Was Fixed:

1. ✅ Added `permissions: contents: write` to workflow
2. ✅ Added checkout step to clone the repo first
3. ✅ Workflow now has permission to push to `output` branch

## ⚠️ Troubleshooting:

### If workflow still fails:
1. Make sure you enabled "Read and write permissions" in Settings
2. Check the Actions tab for error messages
3. Try running the workflow again

### If snake doesn't appear:
1. Check if `output` branch was created (look in branches dropdown)
2. Wait 5 minutes and refresh the page
3. Clear browser cache
4. Try incognito mode

## 🎯 Expected Result:

Once the workflow runs successfully:
- ✅ `output` branch created
- ✅ Snake SVG files generated
- ✅ Snake animation appears in README
- ✅ Auto-updates every 12 hours

---

**The workflow is ready to go! Just push and run it!** 🚀
