# Live Inject Assets

This directory contains the **live/production** inject code that gets uploaded to your GitLab repository and fetched by the extension.

## Purpose

- **`assets/`** - Live production code (this directory)
  - Upload these files to your GitLab repository
  - These are the actual files the extension fetches and uses
  - Edit these files when you want to update the live enhancements

- **`examples/`** - Example/template files
  - Reference implementations and documentation
  - Show how to structure your code
  - Used for learning and development

## Files

- **`inject.css`** - CSS styles injected into target domains
- **`inject.js`** - JavaScript code injected into target domains  
- **`version.json`** - Version information and update URLs

**Important:** `version.json` does NOT contain the GitLab URL. The GitLab URL is configured in `lib/config.js` or the Options page. See `GITLAB_URL_CONFIG.md` for details.

## Workflow

1. **Edit files in `assets/`** - Make your changes to the live code
2. **Upload to GitLab** - Push these files to your GitLab repository
3. **Extension fetches** - The extension automatically fetches from GitLab
4. **Version update** - Update `version.json` version number to trigger update

## Deployment

### Initial Setup

1. Create a GitLab repository (or use existing)
2. Upload these three files to the repository root:
   - `inject.css`
   - `inject.js`
   - `version.json`
3. Get the raw URL for the files:
   - Go to a file in GitLab
   - Click "Raw" button
   - Copy the base URL (everything up to the filename)
   - Example: `https://gitlab.com/group/project/-/raw/main/`
4. Configure extension:
   - Open extension Options
   - Paste the base URL into "GitLab Raw URL"
   - Save settings

### Updating Live Code

1. Edit files in `assets/` directory
2. Update version in `version.json`:
   ```json
   {
     "version": "1.0.1",
     ...
   }
   ```
3. Upload/commit changes to GitLab
4. Extension will automatically detect the new version and fetch updates

## Version Management

The `version.json` file controls versioning:

```json
{
  "version": "1.0.0",              // Asset version (CSS/JS)
  "extensionVersion": "1.0.0",     // Required extension version
  "updateUrl": "...",              // URL for "Update Now" button
  "changelogUrl": "..."            // URL for "Changelog" button
}
```

- **`version`**: Increment this when you update CSS/JS files
- **`extensionVersion`**: Set this if you require a specific extension version
- **`updateUrl`**: Link to extension update/download page
- **`changelogUrl`**: Link to changelog documentation

## Best Practices

1. **Version Control**: Keep `assets/` files in version control
2. **Test Locally**: Test changes locally before uploading
3. **Increment Versions**: Always increment version in `version.json` when updating
4. **Document Changes**: Update changelog when making significant changes
5. **Backup**: Keep backups of working versions

## Development Workflow

```
1. Edit assets/inject.js or assets/inject.css
2. Test locally (if possible)
3. Update assets/version.json version
4. Commit and push to GitLab
5. Extension auto-updates (within poll interval)
```

## Notes

- Files in `assets/` are what gets deployed to GitLab
- Files in `examples/` are for reference only
- The extension fetches from GitLab, not from local `assets/` directory
- Always update `version.json` when making changes to trigger updates

