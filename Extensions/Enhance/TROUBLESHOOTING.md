# Troubleshooting Guide

## Target Domain Pattern Matching Issues

### Problem: Extension Not Injecting on Target Pages

If the extension isn't injecting assets on your target pages, check the following:

#### 1. Verify Target Domain Pattern

Check that your URL pattern matches the actual URL format.

**Actual URL:**
```
https://manage.mist.com/admin/?org_id=9a9d648b-610b-40fb-bf16-1231f682ff51#!dashboard/insights/
```

**Pattern Options:**

✅ **Option 1: Match any insights page (with or without site ID)**
```
https://manage.mist.com/admin/?org_id=*#!dashboard/insights*
```

✅ **Option 2: Match specific pattern**
```
https://manage.mist.com/admin/?org_id=*#!dashboard/insights/*
```

✅ **Option 3: Match all admin pages**
```
https://manage.mist.com/admin/*
```

#### 2. Common Pattern Matching Issues

**Issue: Trailing slash mismatch**
- Pattern: `https://example.com/page/*`
- URL: `https://example.com/page/`
- Solution: Use `*` which matches empty strings too

**Issue: Hash fragment matching**
- Pattern: `https://example.com/page#section`
- URL: `https://example.com/page#section/`
- Solution: Use `*` at the end: `https://example.com/page#section*`

**Issue: Query parameter order**
- Pattern: `https://example.com/?id=*&page=*`
- URL: `https://example.com/?page=1&id=123`
- Solution: Match just the base URL: `https://example.com/?*`

#### 3. Debug Pattern Matching

Add debug logging to see what's happening:

1. Open browser console (F12)
2. Look for `[Enhance]` messages
3. Check if you see: `URL matched pattern: ...`

If you don't see match messages, the pattern isn't matching.

#### 4. Test Your Pattern

You can test patterns manually:

```javascript
// In browser console on target page
const pattern = 'https://manage.mist.com/admin/?org_id=*#!dashboard/insights*';
const url = window.location.href;
const escaped = pattern
  .replace(/[.+^${}()|[\]\\]/g, '\\$&')
  .replace(/\*/g, '.*')
  .replace(/\\\?/g, '\\?')
  .replace(/\\#/g, '\\#');
const regex = new RegExp('^' + escaped + '$');
console.log('Pattern:', pattern);
console.log('URL:', url);
console.log('Matches:', regex.test(url));
console.log('Regex:', regex);
```

### Solution: Update Pattern

For your specific case, update the pattern in `lib/config.js`:

```javascript
targetDomains: [
  'https://manage.mist.com/admin/*',
  'https://manage.mist.com/admin/?org_id=*#!dashboard/insights*'  // Note: * at end, not /*
]
```

The `*` at the end matches:
- `#!dashboard/insights/` (with trailing slash)
- `#!dashboard/insights/site-123` (with site ID)
- `#!dashboard/insights` (no trailing slash)

### Verify Configuration

1. **Check config.js:**
   ```javascript
   targetDomains: [
     'https://manage.mist.com/admin/*',
     'https://manage.mist.com/admin/?org_id=*#!dashboard/insights*'
   ]
   ```

2. **Or check Options page:**
   - Open extension Options
   - Verify target domains list
   - Make sure pattern ends with `*` (not `/*`)

3. **Reload extension:**
   - Go to `chrome://extensions/`
   - Click reload on the extension
   - Refresh the target page

4. **Check console:**
   - Open browser console (F12)
   - Look for `[Enhance]` messages
   - Should see: `URL matched pattern: ...`

## Other Common Issues

### Assets Not Loading

1. **Check GitLab URL:**
   - Verify URL in `config.js` or Options page
   - Must end with `/`
   - Must point to directory containing files

2. **Check Files Exist:**
   - Visit: `${gitlabUrl}inject.css`
   - Visit: `${gitlabUrl}inject.js`
   - Visit: `${gitlabUrl}version.json`
   - All should return content

3. **Check PAT (if private repo):**
   - Verify PAT is set in Options page
   - Verify PAT has correct permissions

### Extension Not Working

1. **Check Extension is Loaded:**
   - Go to `chrome://extensions/`
   - Verify extension is enabled
   - Check for errors

2. **Check Service Worker:**
   - Go to `chrome://extensions/`
   - Click "Service worker" link
   - Check console for errors

3. **Check Content Script:**
   - Open target page
   - Open browser console (F12)
   - Look for `[Enhance]` messages
   - Should see: `Extension loaded`

### Version Not Updating

1. **Check version.json:**
   - Verify version is incremented
   - Upload to GitLab
   - Wait for poll interval (default 30 min)

2. **Manual Refresh:**
   - Open extension popup
   - Click "Refresh Assets"
   - Check if new version is fetched

## Debug Mode

To enable more detailed logging, check browser console for:

- `[Enhance]` messages - Extension activity
- `URL matched pattern` - Pattern matching results
- `Assets fetched` - Asset loading status
- `Error` messages - Any errors

## Still Not Working?

1. Check browser console for errors
2. Verify all configuration is correct
3. Test with a simpler pattern first (e.g., `https://manage.mist.com/admin/*`)
4. Check extension permissions in manifest.json
5. Verify target domains are in the correct format

