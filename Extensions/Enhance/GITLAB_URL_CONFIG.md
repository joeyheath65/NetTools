# GitLab URL Configuration Guide

## Important: GitLab URL is NOT in version.json

The `version.json` file is **fetched FROM GitLab**, but it does **NOT contain** the GitLab URL itself.

## Where to Configure GitLab URL

You need to configure the GitLab URL in one of these places:

### Option 1: Hardcode in `lib/config.js` (Recommended for Internal Deployments)

Edit `lib/config.js`:

```javascript
export const DEFAULT_GITLAB_CONFIG = {
  gitlabUrl: 'https://gitlab.yourcompany.com/group/project/-/raw/main/',
  // ... other config
};
```

**Pros:**
- Pre-configured for all users
- No user setup required
- Consistent across deployments

**Cons:**
- Hardcoded in extension code
- Requires rebuild to change

### Option 2: Configure via Options Page (User-Configurable)

1. Open extension Options page
2. Enter GitLab URL in "GitLab Raw URL" field
3. Click "Save Settings"

**Pros:**
- Flexible - users can configure their own URL
- No rebuild needed
- Good for different environments

**Cons:**
- Users must configure manually
- Different users may use different URLs

### Option 3: Hybrid (Recommended)

1. Set default in `lib/config.js`:
   ```javascript
   gitlabUrl: 'https://gitlab.yourcompany.com/group/project/-/raw/main/',
   ```

2. Users can override in Options page if needed

**Best of both worlds:**
- Default URL for easy deployment
- Flexibility to override if needed

## Priority Order

The extension uses GitLab URL in this order:

1. **User setting in Options page** (highest priority)
2. **Default in `lib/config.js`** (fallback)
3. **Error if neither is set**

## What's in version.json?

The `version.json` file (which is fetched FROM GitLab) contains:

```json
{
  "version": "1.0.0",              // Asset version (CSS/JS)
  "extensionVersion": "1.0.0",     // Required extension version
  "updateUrl": "...",              // URL for "Update Now" button (optional)
  "changelogUrl": "..."            // URL for "Changelog" button (optional)
}
```

**It does NOT contain:**
- ❌ GitLab URL (that's configured separately)
- ❌ GitLab PAT (that's configured separately)

## Complete Setup Flow

### 1. Configure GitLab URL

**Method A: In `lib/config.js`**
```javascript
gitlabUrl: 'https://gitlab.com/group/project/-/raw/main/',
```

**Method B: In Options Page**
- Open extension Options
- Enter GitLab URL
- Save

### 2. Upload Assets to GitLab

Upload these files to your GitLab repository:
- `inject.css`
- `inject.js`
- `version.json`

### 3. Extension Fetches Assets

The extension will:
1. Use GitLab URL from config/options
2. Fetch `${gitlabUrl}inject.css`
3. Fetch `${gitlabUrl}inject.js`
4. Fetch `${gitlabUrl}version.json`

### 4. Update version.json

When you update assets:
1. Edit `inject.css` or `inject.js`
2. Update `version` in `version.json`:
   ```json
   {
     "version": "1.0.1"  // Increment this
   }
   ```
3. Upload to GitLab
4. Extension detects new version and fetches updates

## Example Configuration

### lib/config.js
```javascript
export const DEFAULT_GITLAB_CONFIG = {
  gitlabUrl: 'https://gitlab.yourcompany.com/it/enhance-assets/-/raw/main/',
  gitlabPat: '',  // Users set in Options if repo is private
  pollInterval: 30,
  targetDomains: [
    'https://manage.mist.com/admin/*'
  ]
};
```

### version.json (uploaded to GitLab)
```json
{
  "version": "1.0.0",
  "extensionVersion": "1.0.0",
  "updateUrl": "https://gitlab.yourcompany.com/it/enhance-assets/-/releases",
  "changelogUrl": "https://gitlab.yourcompany.com/it/enhance-assets/-/blob/main/CHANGELOG.md"
}
```

**Note:** The `updateUrl` and `changelogUrl` in `version.json` are optional and can point to any URL (not necessarily GitLab).

## Summary

| Location | Contains GitLab URL? | Purpose |
|----------|---------------------|---------|
| `lib/config.js` | ✅ Yes (default) | Hardcoded default URL |
| Options Page | ✅ Yes (user setting) | User-configurable URL |
| `version.json` | ❌ No | Version info only |
| `chrome.storage.local` | ✅ Yes (stored) | Where user settings are saved |

**Key Point:** GitLab URL is configured in the extension code/options, NOT in the `version.json` file that's fetched from GitLab.

