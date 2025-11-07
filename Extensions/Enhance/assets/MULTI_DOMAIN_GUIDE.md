# Multi-Domain Guide

## Overview

All target domains share the same `inject.css` and `inject.js` files. You use domain-specific code blocks to separate code for different domains. The extension automatically extracts and injects only the relevant code for each domain.

## How It Works

1. **Single Files**: All domains use the same `inject.css` and `inject.js` files
2. **Domain Blocks**: Use domain-specific blocks to separate code for each domain
3. **Automatic Extraction**: The extension extracts only the relevant code for the current domain
4. **Global Code**: Code outside domain blocks applies to all domains

## CSS Format

```css
/* Global CSS - applies to ALL domains */
body {
  font-family: Arial, sans-serif;
}

/* Domain-specific CSS for manage.mist.com */
/* domain:manage.mist.com */
.mist-dashboard {
  background-color: #f5f5f5;
}
/* end-domain */

/* Domain-specific CSS for example.com */
/* domain:example.com */
.example-widget {
  border: 2px solid blue;
}
/* end-domain */
```

## JavaScript Format

```javascript
// Global JavaScript - applies to ALL domains
console.log('[Enhance] Extension loaded');

// Domain-specific JavaScript for manage.mist.com
/* domain:manage.mist.com */
(function() {
  console.log('[Enhance] Mist.com enhancements');
  // Mist.com specific code here
})();
/* end-domain */

// Domain-specific JavaScript for example.com
/* domain:example.com */
(function() {
  console.log('[Enhance] Example.com enhancements');
  // Example.com specific code here
})();
/* end-domain */
```

## Adding a New Target Domain

### Step 1: Add Domain to Target Domains List

**Option A: In `lib/config.js`**
```javascript
export const DEFAULT_GITLAB_CONFIG = {
  // ...
  targetDomains: [
    'https://manage.mist.com/admin/*',
    'https://example.com/*',  // ← Add new domain
    'https://another-site.com/dashboard/*'
  ]
};
```

**Option B: In Options Page**
- Open extension Options
- Add domain pattern to "Target Domains" field (one per line)

### Step 2: Add Domain-Specific Code

Edit `assets/inject.css` and/or `assets/inject.js`:

```css
/* assets/inject.css */

/* Existing domains... */

/* Domain-specific CSS for newdomain.com */
/* domain:newdomain.com */
.newdomain-custom-class {
  color: red;
}
/* end-domain */
```

```javascript
// assets/inject.js

// Existing domains...

// Domain-specific JavaScript for newdomain.com
/* domain:newdomain.com */
(function() {
  console.log('[Enhance] NewDomain.com enhancements loaded');
  
  // Your newdomain.com specific code here
  function initNewDomain() {
    // Custom enhancements
  }
  
  // Initialize when page loads
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initNewDomain);
  } else {
    initNewDomain();
  }
})();
/* end-domain */
```

### Step 3: Update Version and Deploy

1. Update version in `assets/version.json`:
   ```json
   {
     "version": "1.0.1"  // Increment version
   }
   ```

2. Upload files to GitLab

3. Extension will automatically fetch and apply updates

## Domain Matching

The extension matches domains by hostname:

- `https://manage.mist.com/admin/` → matches `domain:manage.mist.com`
- `https://www.example.com/` → matches `domain:example.com`
- `https://example.com/` → matches `domain:example.com`

**Note**: The `www.` prefix is automatically removed when matching.

## Best Practices

### 1. Use Global Code for Common Features

```javascript
// Global code - runs on all domains
window.Enhance = window.Enhance || {};
window.Enhance.utils = {
  log: function(msg) { console.log('[Enhance]', msg); }
};
```

### 2. Keep Domain Code Isolated

```javascript
/* domain:example.com */
(function() {
  'use strict';  // Use IIFE to avoid conflicts
  // Domain-specific code
})();
/* end-domain */
```

### 3. Use Descriptive Comments

```javascript
/* domain:manage.mist.com */
// Mist.com Admin Dashboard Enhancements
// - Adds "Enhanced!" badge to logo
// - Enhances metric cards with hover effects
// - Improves table readability
(function() {
  // Code here
})();
/* end-domain */
```

### 4. Test Each Domain Separately

1. Visit the target domain
2. Check browser console for `[Enhance]` messages
3. Verify domain-specific features work
4. Check that other domains are not affected

## Example: Multiple Domains

```javascript
// assets/inject.js

// Global code
console.log('[Enhance] Extension loaded');

// Mist.com enhancements
/* domain:manage.mist.com */
(function() {
  console.log('[Enhance] Mist.com loaded');
  // Mist.com code
})();
/* end-domain */

// ServiceNow enhancements
/* domain:servicenow.com */
(function() {
  console.log('[Enhance] ServiceNow loaded');
  // ServiceNow code
})();
/* end-domain */

// Grafana enhancements
/* domain:grafana.com */
(function() {
  console.log('[Enhance] Grafana loaded');
  // Grafana code
})();
/* end-domain */
```

## Troubleshooting

### Code Not Running for a Domain

1. **Check domain pattern**: Verify the domain is in target domains list
2. **Check domain block format**: Ensure `/* domain:example.com */` matches the hostname exactly
3. **Check console**: Look for `[Enhance]` messages in browser console
4. **Verify URL matching**: The extension logs which domains match

### Code Running on Wrong Domain

1. **Check domain block syntax**: Ensure `/* end-domain */` is present
2. **Check for typos**: Domain name in block must match hostname exactly
3. **Check global code**: Code outside blocks runs on all domains

### Conflicts Between Domains

1. **Use IIFE**: Wrap domain code in immediately invoked function expressions
2. **Use unique variable names**: Prefix variables with domain name
3. **Check for global pollution**: Avoid modifying global objects unnecessarily

## Summary

- ✅ **Same files** for all domains (`inject.css` and `inject.js`)
- ✅ **Domain blocks** to separate code (`/* domain:example.com */ ... /* end-domain */`)
- ✅ **Global code** outside blocks applies to all domains
- ✅ **Automatic extraction** - extension only injects relevant code
- ✅ **Easy to add** - just add new domain block and update target domains list

