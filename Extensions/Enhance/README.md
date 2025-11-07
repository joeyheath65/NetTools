# Enhance Extension

Internal Chrome/Firefox Manifest V3 extension for enhancing network infrastructure management portals and dashboards.

## Overview

Enhance is a wrapper extension that injects custom CSS and JavaScript into specific target domains (such as network management portals). It fetches assets from a GitLab repository and caches them locally, with automatic updates and version checking.

## Features

- **Dynamic Asset Loading**: Fetches `inject.css`, `inject.js`, and `version.json` from GitLab on startup and every 30 minutes (configurable)
- **Multi-Domain Support**: Supports multiple target domains with domain-specific CSS/JS injection
- **Version Management**: Compares local vs remote versions and handles updates automatically
- **Caching**: Caches assets in `chrome.storage.local` for offline use
- **Configurable**: All settings (GitLab URL, PAT, poll interval, target domains) stored in Options page
- **Update Notifications**: Shows notifications when new extension versions are available
- **Graceful Fallback**: Falls back to cached assets if fetch fails

## Installation

### For Internal Use (Unpacked Extension)

1. Open Chrome/Edge: `chrome://extensions/` or Edge: `edge://extensions/`
2. Enable "Developer mode" (toggle in top right)
3. Click "Load unpacked"
4. Select the `Extensions/Enhance` directory
5. The extension will be installed and ready to use

### For Firefox

1. Open Firefox: `about:debugging#/runtime/this-firefox`
2. Click "Load Temporary Add-on"
3. Select the `manifest.json` file in the `Extensions/Enhance` directory

## Setup

### Step 1: Prepare Inject Assets

1. Edit files in `assets/` directory:
   - `assets/inject.css` - CSS to inject
   - `assets/inject.js` - JavaScript to inject
   - `assets/version.json` - Version information

2. Upload these files to your GitLab repository (root or subdirectory)

3. Get the raw URL:
   - Navigate to a file in GitLab
   - Click "Raw" button
   - Copy the base URL (everything up to the filename)
   - Example: `https://gitlab.com/group/project/-/raw/main/`

### Step 2: Configure Extension

#### Option 1: Hardcode Defaults in `config.js` (Recommended for Internal Deployments)

1. Edit `lib/config.js` and set your GitLab URL and other defaults:
   ```javascript
   export const DEFAULT_GITLAB_CONFIG = {
     gitlabUrl: 'https://gitlab.yourcompany.com/group/project/-/raw/main/',
     gitlabPat: '', // Optional: set PAT for private repos
     pollInterval: 30,
     targetDomains: [
       'https://manage.mist.com/admin/*',
       'https://manage.mist.com/admin/?org_id=*#!dashboard/insights/*'
     ]
   };
   ```

2. These defaults will be used automatically
3. Users can still override in Options page if needed

#### Option 2: Configure via Options Page

1. Click the extension icon in your browser toolbar
2. Click "Options" button
3. Configure the following settings:

   - **GitLab Raw URL**: Base URL for fetching assets (e.g., `https://gitlab.com/group/project/-/raw/main/`)
   - **GitLab PAT** (Optional): Personal Access Token if repository is private
   - **Poll Interval**: How often to check for updates (default: 30 minutes)
   - **Target Domains**: Domain patterns to inject assets into (one per line, use `*` as wildcard)

4. Click "Save Settings"

**Note**: If `config.js` has defaults set, those will be used if Options page fields are left empty.

## Directory Structure

- **`assets/`** - Live production inject code (upload to GitLab)
- **`examples/`** - Example/template files for reference

## Usage

### Domain-Specific CSS/JS

**Yes, you add all domains to the same inject files!** The extension supports multiple target domains in the same `inject.css` and `inject.js` files using domain-specific code blocks.

#### How It Works

- ✅ **Same files** for all domains (`inject.css` and `inject.js`)
- ✅ **Domain blocks** to separate code (`/* domain:example.com */ ... /* end-domain */`)
- ✅ **Global code** outside blocks applies to all domains
- ✅ **Automatic extraction** - extension only injects relevant code per domain

#### Example: Multiple Domains in Same Files

```css
/* Global styles for all domains */
body {
  font-family: Arial, sans-serif;
}

/* Domain-specific styles for manage.mist.com */
/* domain:manage.mist.com */
.mist-dashboard {
  background-color: #f5f5f5;
}
/* end-domain */

/* Domain-specific styles for example.com */
/* domain:example.com */
.example-class {
  color: blue;
}
/* end-domain */
```

```javascript
// Global JavaScript for all domains
console.log('[Enhance] Extension loaded');

// Domain-specific JavaScript for manage.mist.com
/* domain:manage.mist.com */
(function() {
  console.log('[Enhance] Mist.com enhancements loaded');
  // Mist.com specific code here
})();
/* end-domain */

// Domain-specific JavaScript for example.com
/* domain:example.com */
(function() {
  console.log('[Enhance] Example.com enhancements loaded');
  // Example.com specific code here
})();
/* end-domain */
```

#### Adding a New Domain

1. **Add domain to target domains** (in `config.js` or Options page)
2. **Add domain block** to `inject.css` and/or `inject.js`
3. **Update version** in `version.json`
4. **Upload to GitLab** - extension will automatically fetch updates

See `assets/MULTI_DOMAIN_GUIDE.md` for detailed guide on managing multiple domains.

### Version.json Format

The `version.json` file should follow this format:

```json
{
  "version": "1.0.0",
  "extensionVersion": "1.0.0",
  "updateUrl": "https://gitlab.com/group/project/-/releases",
  "changelogUrl": "https://gitlab.com/group/project/-/blob/main/CHANGELOG.md"
}
```

- `version`: Version of the assets (CSS/JS)
- `extensionVersion`: Required extension version (triggers update notification if newer)
- `updateUrl`: URL to open when user clicks "Update Now"
- `changelogUrl`: URL to open when user clicks "Changelog"

## Architecture

### Directory Structure

```
Enhance/
├── manifest.json              # Extension manifest
├── background/
│   └── background.js          # Service worker for fetching, caching, versioning
├── content/
│   └── content_loader.js      # Content script for CSS/JS injection
├── assets/                    # Live inject code (upload to GitLab)
│   ├── inject.css            # Production CSS
│   ├── inject.js             # Production JavaScript
│   ├── version.json          # Version information
│   └── README.md             # Assets directory documentation
├── examples/                  # Example/template files
│   ├── inject.css            # Example CSS template
│   ├── inject.js             # Example JavaScript template
│   ├── version.json          # Example version file
│   └── README.md             # Examples documentation
├── lib/
│   ├── config.js              # Default configuration (edit for hardcoded defaults)
│   ├── config.example.js      # Example config file
│   ├── defaultAssets.js       # Built-in default assets
│   ├── storage.js             # Storage utilities
│   ├── fetcher.js             # GitLab fetching utilities
│   └── versioning.js          # Version comparison and update logic
├── ui/
│   ├── popup.html             # Extension popup UI
│   ├── popup.js               # Popup logic
│   ├── popup.css              # Popup styles
│   ├── options.html           # Options page
│   ├── options.js             # Options page logic
│   └── options.css            # Options page styles
└── icons/                     # Extension icons (16x16, 48x48, 128x128)
```

### Key Components

- **Background Service Worker**: Handles asset fetching, version checking, caching, and alarms
- **Content Script**: Injects CSS and JS into target domains based on URL matching
- **Storage Module**: Manages all configuration and cached assets in `chrome.storage.local`
- **Fetcher Module**: Handles authenticated requests to GitLab
- **Versioning Module**: Compares versions and triggers update notifications

## Permissions

- `storage`: Store configuration and cached assets
- `scripting`: Inject CSS and JS into pages
- `alarms`: Schedule periodic asset fetching
- `notifications`: Show update notifications
- `activeTab`: Access current tab information
- `host_permissions`: Fetch assets from GitLab

## Future Enhancements

- Remote code execution (Python, JavaScript, etc.)
- Integration with Grafana, ServiceNow, and other data sources
- Advanced domain matching rules
- Asset versioning per domain
- Custom injection timing options

## Development

### Testing

1. Load the extension in developer mode
2. Configure GitLab URL and target domains in Options
3. Visit a target domain to verify injection
4. Check browser console for extension logs
5. Use popup to verify status and refresh assets

### Debugging

- Background service worker: Check `chrome://extensions/` → "Service worker" link
- Content script: Check browser DevTools console on target pages
- Popup: Right-click extension icon → "Inspect popup"

## Security Notes

- All configuration is stored locally in `chrome.storage.local`
- GitLab PAT is stored locally and only sent to GitLab for authentication
- Extension is for internal use only and not published to any store
- Content scripts run in isolated context and cannot access page JavaScript directly

## License

Internal use only.

