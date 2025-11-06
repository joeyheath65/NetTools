# Example Files for GitLab Repository

These are example files that should be hosted in your GitLab repository at the raw URL you configure in the extension options.

## Files Required

1. **version.json** - Version information and update URLs
2. **inject.css** - CSS to inject into target domains
3. **inject.js** - JavaScript to inject into target domains

## Setup Instructions

1. Create a GitLab repository (or use an existing one)
2. Upload these three files to the repository root (or a subdirectory)
3. Get the raw URL for the files:
   - Go to the file in GitLab
   - Click "Raw" button
   - Copy the base URL (everything up to and including the filename)
   - Remove the filename to get the base URL
   - Example: `https://gitlab.com/group/project/-/raw/main/` (note the trailing slash)
4. Configure the extension:
   - Open extension Options
   - Paste the base URL into "GitLab Raw URL"
   - If the repository is private, add your Personal Access Token
   - Save settings

## File Format

### version.json

```json
{
  "version": "1.0.0",           // Version of the assets (CSS/JS)
  "extensionVersion": "1.0.0",  // Required extension version (triggers update notification)
  "updateUrl": "...",           // URL for "Update Now" button
  "changelogUrl": "..."         // URL for "Changelog" button
}
```

### inject.css

- Global CSS applies to all target domains
- Domain-specific CSS uses the format:
  ```css
  /* domain:example.com */
  .example-class { ... }
  /* end-domain */
  ```

### inject.js

- Global JavaScript applies to all target domains
- Domain-specific JavaScript uses the format:
  ```javascript
  /* domain:example.com */
  // Domain-specific code here
  /* end-domain */
  ```

## Version Management

- When you update `inject.css` or `inject.js`, increment the `version` field in `version.json`
- The extension will automatically detect the new version and re-fetch assets
- When you require a new extension version, increment `extensionVersion` in `version.json`
- Users will see an update notification with links to update and changelog

## Security Notes

- These files are fetched and executed in the browser
- Only include trusted code
- Use domain-specific blocks to limit code execution to intended domains
- Consider code minification for production use

