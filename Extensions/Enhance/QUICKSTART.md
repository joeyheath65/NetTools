# Enhance Extension - Quick Start Guide

## Installation

1. **Load Extension**:
   - Chrome/Edge: Go to `chrome://extensions/` → Enable "Developer mode" → "Load unpacked" → Select `Extensions/Enhance` folder
   - Firefox: Go to `about:debugging#/runtime/this-firefox` → "Load Temporary Add-on" → Select `manifest.json`

2. **Configure Extension**:
   - Click extension icon → "Options"
   - Enter GitLab Raw URL (e.g., `https://gitlab.com/group/project/-/raw/main/`)
   - (Optional) Enter GitLab Personal Access Token if repository is private
   - Set poll interval (default: 30 minutes)
   - Add target domains (one per line, e.g., `https://manage.mist.com/*`)
   - Click "Save Settings"

3. **Verify Setup**:
   - Click extension icon to see status
   - Check "Last Fetch" time
   - Visit a target domain to verify injection
   - Check browser console for `[Enhance]` logs

## File Structure

```
Enhance/
├── manifest.json              # Extension manifest (Manifest V3)
├── background/
│   └── background.js          # Service worker (fetching, caching, versioning)
├── content/
│   └── content_loader.js      # Content script (CSS/JS injection)
├── lib/
│   ├── storage.js             # Storage utilities
│   ├── fetcher.js             # GitLab fetching
│   └── versioning.js          # Version comparison
├── ui/
│   ├── popup.html/js/css      # Extension popup
│   └── options.html/js/css    # Options page
├── icons/                     # Extension icons (create 16x16, 48x48, 128x128 PNGs)
└── examples/                  # Example files for GitLab repo
    ├── version.json
    ├── inject.css
    └── inject.js
```

## Key Features

✅ **Automatic Updates**: Fetches assets on startup and every 30 minutes (configurable)  
✅ **Multi-Domain Support**: Different CSS/JS per domain using domain-specific blocks  
✅ **Version Management**: Compares versions and shows update notifications  
✅ **Offline Support**: Falls back to cached assets if fetch fails  
✅ **Secure**: All config stored locally, PAT only sent to GitLab  

## Domain-Specific Injection

Use domain-specific blocks in your CSS/JS files:

**CSS:**
```css
/* domain:manage.mist.com */
.mist-class { color: blue; }
/* end-domain */
```

**JavaScript:**
```javascript
/* domain:manage.mist.com */
console.log('Mist.com loaded');
/* end-domain */
```

## Troubleshooting

- **Assets not loading**: Check GitLab URL and PAT in Options
- **No injection on page**: Verify domain matches target patterns in Options
- **Version check fails**: Ensure `version.json` is accessible at GitLab URL
- **Console errors**: Check browser console and extension service worker logs

## Next Steps

1. Create extension icons (see `icons/README.md`)
2. Set up GitLab repository with `inject.css`, `inject.js`, and `version.json`
3. Configure extension with your GitLab URL
4. Test on target domains
5. Customize CSS/JS for your needs

