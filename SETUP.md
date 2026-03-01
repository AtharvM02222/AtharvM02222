# 🚀 GitHub Profile README Setup Guide

This guide will help you set up all the dynamic features in your GitHub profile README.

## 📋 Prerequisites

- GitHub account (AtharvM02222)
- Repository named `AtharvM02222` (same as your username)
- Repository must be public

## ✅ Setup Steps

### 1. Enable GitHub Actions

1. Go to your repository: `https://github.com/AtharvM02222/AtharvM02222`
2. Click on **Settings** tab
3. Navigate to **Actions** → **General**
4. Under "Workflow permissions", select **Read and write permissions**
5. Check **Allow GitHub Actions to create and approve pull requests**
6. Click **Save**

### 2. Activate Snake Animation

The snake animation workflow is already set up in `.github/workflows/snake.yml`

To trigger it manually:
1. Go to **Actions** tab
2. Click on **Generate Snake Animation** workflow
3. Click **Run workflow** → **Run workflow**
4. Wait for it to complete (creates an `output` branch)

The animation will auto-update every 12 hours!

### 3. Activate Recent Activity

The activity updater is set up in `.github/workflows/update-activity.yml`

To trigger it manually:
1. Go to **Actions** tab
2. Click on **Update Recent Activity** workflow
3. Click **Run workflow** → **Run workflow**

This will auto-update every 6 hours!

### 4. Fix Trophy Display

The trophies should display automatically. If they don't:
- Clear your browser cache
- Wait a few minutes for GitHub's CDN to update
- Try accessing in incognito mode

### 5. Upload Assets to Certi-Mailer Repo

Make sure these files are in your `Certi-Mailer` repository:
- `particles-bg.gif` ✅ (already there)
- `nyrc-title.gif` ✅ (already there)

These are used in the README for animations!

## 🎨 Customization

### Change Theme Colors

Edit the badge colors in `README.md`:
- `color=00d9ff` - Change to any hex color
- `theme=tokyonight` - Try: `algolia`, `react-dark`, `github-dark`, `radical`

### Add More Projects

Edit the Featured Projects section in `README.md` to add your latest work!

### Update Bio Information

Edit the Python class in the "About Me" section with your latest info.

## 🔧 Troubleshooting

### Snake Animation Not Showing
- Make sure the workflow ran successfully
- Check if `output` branch was created
- Wait 5-10 minutes after first run

### Activity Not Updating
- Ensure workflow permissions are set correctly
- Check Actions tab for any errors
- Manually trigger the workflow

### Trophies Not Loading
- This is a third-party service - sometimes it takes time
- Try: `theme=algolia` or `theme=radical` if one doesn't work
- Clear cache and refresh

### Stats Not Showing
- GitHub stats API can be slow
- Try adding `&cache_seconds=1800` to the URL
- Use incognito mode to see fresh version

## 📊 What's Included

✅ Animated typing header
✅ Particle background GIF
✅ Profile view counter
✅ GitHub followers/stars badges
✅ Collapsible tech stack sections
✅ GitHub statistics (4 different cards)
✅ Trophy showcase
✅ Featured projects with real data
✅ Contribution activity graph
✅ Snake contribution animation
✅ Recent activity auto-update
✅ Random dev quotes
✅ Social links
✅ Visitor counter

## 🎯 Next Steps

1. Push all changes to GitHub
2. Enable GitHub Actions
3. Run both workflows manually
4. Wait for them to complete
5. Refresh your profile!

## 💡 Tips

- Star your own repositories to increase your GitHub stars count
- Contribute regularly to keep the contribution graph active
- Update the README with new projects as you build them
- Engage with the community to grow your followers

---

Made with 💙 by Atharv Mandlavdiya
