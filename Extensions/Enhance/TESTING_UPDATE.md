# Testing Asset Update Process

## Step-by-Step Testing Guide

### Step 1: Version Bump

✅ **Done**: Version bumped from `1.0.0` to `1.0.1` in `assets/version.json`

### Step 2: Commit and Push to GitLab

1. **Commit the changes:**
   ```bash
   cd /Users/joehome/dev/work/HEB/NetTools
   git add Extensions/Enhance/assets/version.json
   git commit -m "Bump asset version to 1.0.1"
   git push
   ```

2. **Verify files are in GitLab:**
   - Go to: https://gitlab.com/heath.joe/NetTools/-/blob/main/Extensions/Enhance/assets/version.json
   - Verify version shows `1.0.1`
   - Check raw URL: https://gitlab.com/heath.joe/NetTools/-/raw/main/Extensions/Enhance/assets/version.json

### Step 3: Test Extension Update

#### Option A: Wait for Automatic Poll (30 minutes default)

1. The extension will automatically check for updates every 30 minutes
2. Check extension popup to see when last fetch occurred
3. After poll interval, extension should detect new version and fetch updates

#### Option B: Manual Refresh (Immediate)

1. **Open extension popup:**
   - Click extension icon in browser toolbar
   - Check current version displayed

2. **Click "Refresh Assets" button:**
   - This manually triggers asset fetch
   - Extension should detect version `1.0.1` > `1.0.0`
   - Should fetch new assets and update cache

3. **Verify update:**
   - Check popup shows new version: `1.0.1`
   - Check "Last Fetch" time is updated
   - Visit target domain to verify new assets are injected

#### Option C: Check Service Worker Console

1. Go to `chrome://extensions/`
2. Find "Enhance" extension
3. Click "Service worker" link (opens console)
4. Look for:
   - `Fetching assets...`
   - `Assets fetched and cached successfully`
   - `New asset version available, re-fetching...` (if version changed)

### Step 4: Verify Assets Updated

1. **Check browser console on target page:**
   - Visit: `https://manage.mist.com/admin/`
   - Open console (F12)
   - Look for `[Enhance]` messages
   - Verify "Enhanced!" badge appears

2. **Check extension popup:**
   - Open popup
   - Verify "Asset Version" shows `1.0.1`
   - Verify "Last Fetch" time is recent

### Expected Behavior

1. **On "Refresh Assets":**
   - Extension fetches `version.json` from GitLab
   - Compares: `1.0.1` (remote) vs `1.0.0` (local)
   - Detects new version available
   - Fetches new `inject.css` and `inject.js`
   - Updates cache
   - Updates "Last Fetch" time

2. **On target page:**
   - Extension loads cached assets
   - Injects CSS and JS
   - Shows "Enhanced!" badge on Mist.com logo

### Troubleshooting

#### Assets Not Updating

1. **Check GitLab URL:**
   - Verify URL in `config.js` or Options page
   - Should be: `https://gitlab.com/heath.joe/NetTools/Extensions/Enhance/assets/`
   - Must end with `/`

2. **Check PAT (if private repo):**
   - Verify PAT is set in `config.js` or Options
   - Verify PAT has correct permissions

3. **Check Files in GitLab:**
   - Verify `version.json` shows `1.0.1`
   - Verify `inject.css` and `inject.js` exist
   - Test raw URLs directly in browser

4. **Check Service Worker:**
   - Open service worker console
   - Look for error messages
   - Check network requests

#### Version Not Detected

1. **Clear cache and retry:**
   - Open extension Options
   - Reset settings (if needed)
   - Click "Refresh Assets" again

2. **Check version comparison:**
   - Service worker console should show version comparison
   - Should log: `New asset version available`

3. **Manual version check:**
   - Visit: `${gitlabUrl}version.json` directly
   - Verify it returns JSON with version `1.0.1`

### Success Indicators

✅ Extension popup shows version `1.0.1`  
✅ "Last Fetch" time is recent  
✅ Target page shows "Enhanced!" badge  
✅ Console shows `[Enhance]` messages  
✅ Service worker console shows successful fetch  

### Next Steps After Testing

1. If update works: ✅ System is working correctly
2. If update fails: Check error messages in service worker console
3. For production: Set up proper versioning workflow

## Version Numbering

- **Patch** (1.0.0 → 1.0.1): Small changes, bug fixes
- **Minor** (1.0.0 → 1.1.0): New features, enhancements
- **Major** (1.0.0 → 2.0.0): Breaking changes

For this test, we're doing a patch bump (1.0.0 → 1.0.1).

