# Configuration Guide

## Overview

The Enhance extension supports two ways to configure GitLab endpoints:

1. **Hardcoded defaults in `config.js`** (recommended for internal deployments)
2. **Options page** (for user-configurable deployments)

## Method 1: Hardcode Defaults in `config.js`

This is the recommended approach for internal/production deployments where you want to pre-configure the extension.

### Steps

1. Edit `lib/config.js`:
   ```javascript
   export const DEFAULT_GITLAB_CONFIG = {
     gitlabUrl: 'https://gitlab.yourcompany.com/group/project/-/raw/main/',
     gitlabPat: '', // Optional: only if repo is private
     pollInterval: 30,
     targetDomains: [
       'https://manage.mist.com/admin/*',
       'https://manage.mist.com/admin/?org_id=*#!dashboard/insights/*'
     ]
   };
   ```

2. Build/deploy the extension with these defaults
3. The extension will use these values automatically
4. Users can still override in Options page if needed

### Advantages

- ✅ No user configuration required
- ✅ Consistent deployment across users
- ✅ Works immediately after installation
- ✅ Can be version-controlled

### Security Considerations

- ⚠️ **PAT tokens in code**: If you set `gitlabPat` in `config.js`, it will be visible in the extension code
- ✅ **Recommendation**: For private repos, either:
  - Leave PAT empty and require users to set it in Options
  - Use enterprise policy to set PAT
  - Use a read-only token with minimal permissions

## Method 2: Options Page Configuration

This approach allows users to configure the extension themselves.

### Steps

1. Leave `config.js` defaults empty (or set minimal defaults)
2. Users open extension Options page
3. Users enter GitLab URL and other settings
4. Settings are saved in `chrome.storage.local`

### Advantages

- ✅ No hardcoded credentials
- ✅ Users can configure their own endpoints
- ✅ More flexible for different environments

## Hybrid Approach

You can combine both methods:

1. Set defaults in `config.js` for common settings (URL, poll interval, target domains)
2. Leave PAT empty in `config.js`
3. Users configure PAT in Options page if needed

This gives you:
- Pre-configured defaults for easy deployment
- Security for sensitive tokens (PAT)

## Environment-Specific Builds

For different environments (dev, staging, production), you can:

1. Create multiple `config.js` files:
   - `config.dev.js`
   - `config.prod.js`
   - `config.staging.js`

2. Use a build script to copy the appropriate file to `config.js`

3. Or use a simple script:
   ```bash
   # For production
   cp lib/config.prod.js lib/config.js
   
   # For development
   cp lib/config.dev.js lib/config.js
   ```

## Example Configurations

### Internal Company Deployment

```javascript
export const DEFAULT_GITLAB_CONFIG = {
  gitlabUrl: 'https://gitlab.company.com/it/enhance-assets/-/raw/main/',
  gitlabPat: '', // Users set this in Options
  pollInterval: 30,
  targetDomains: [
    'https://manage.mist.com/admin/*',
    'https://manage.mist.com/admin/?org_id=*#!dashboard/insights/*'
  ]
};
```

### Public Repository

```javascript
export const DEFAULT_GITLAB_CONFIG = {
  gitlabUrl: 'https://gitlab.com/your-org/enhance-assets/-/raw/main/',
  gitlabPat: '', // Not needed for public repos
  pollInterval: 30,
  targetDomains: [
    'https://manage.mist.com/admin/*'
  ]
};
```

### Development/Testing

```javascript
export const DEFAULT_GITLAB_CONFIG = {
  gitlabUrl: '', // Configure via Options
  gitlabPat: '',
  pollInterval: 5, // Faster polling for testing
  targetDomains: [
    'https://manage.mist.com/admin/*'
  ]
};
```

## Priority Order

The extension uses configuration in this priority order:

1. **User settings in Options page** (highest priority)
2. **Defaults from `config.js`** (fallback)
3. **Built-in defaults** (last resort)

This means:
- If user sets a value in Options, it overrides `config.js`
- If `config.js` has a value and Options is empty, `config.js` is used
- If both are empty, built-in defaults are used

## Troubleshooting

### Extension not fetching assets

1. Check if GitLab URL is set:
   - Open Options page
   - Check if URL field has a value
   - If empty, check `config.js` for defaults

2. Check browser console:
   - Look for `[Enhance]` messages
   - Check for fetch errors

3. Verify GitLab URL format:
   - Must end with `/`
   - Must be a raw file URL
   - Example: `https://gitlab.com/group/project/-/raw/main/`

### PAT not working

1. Verify PAT has correct permissions:
   - `read_api` scope minimum
   - `read_repository` if repo is private

2. Check if PAT is set:
   - Options page → GitLab PAT field
   - Or in `config.js` (less secure)

3. Test PAT manually:
   ```bash
   curl -H "Authorization: Bearer YOUR_PAT" \
     https://gitlab.com/api/v4/projects/YOUR_PROJECT_ID
   ```

## Best Practices

1. **For Internal Deployments**:
   - Set GitLab URL in `config.js`
   - Leave PAT empty (users configure)
   - Set appropriate target domains

2. **For Public Distribution**:
   - Leave all defaults empty
   - Require users to configure via Options

3. **For Security**:
   - Never commit PAT tokens to version control
   - Use read-only tokens with minimal permissions
   - Consider using enterprise policy for PAT distribution

4. **For Development**:
   - Use fast poll intervals (5-10 minutes)
   - Test with local GitLab instance if possible
   - Use Options page for quick iteration

