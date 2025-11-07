# GitLab URL Configuration Examples

## How the URL Works

The GitLab URL in `config.js` should point to the **directory** containing your asset files. The extension automatically appends the filenames (`inject.css`, `inject.js`, `version.json`).

## Examples

### Files in Repository Root

If your files are in the root of your GitLab repository:
```
Repository: https://gitlab.com/group/project
Files:
  - inject.css
  - inject.js
  - version.json
```

**Config:**
```javascript
gitlabUrl: 'https://gitlab.com/group/project/-/raw/main/'
```

The extension will fetch:
- `https://gitlab.com/group/project/-/raw/main/inject.css`
- `https://gitlab.com/group/project/-/raw/main/inject.js`
- `https://gitlab.com/group/project/-/raw/main/version.json`

### Files in `assets/` Subdirectory

If your files are in an `assets/` subdirectory:
```
Repository: https://gitlab.com/group/project
Files:
  - assets/inject.css
  - assets/inject.js
  - assets/version.json
```

**Config:**
```javascript
gitlabUrl: 'https://gitlab.com/group/project/-/raw/main/assets/'
```

The extension will fetch:
- `https://gitlab.com/group/project/-/raw/main/assets/inject.css`
- `https://gitlab.com/group/project/-/raw/main/assets/inject.js`
- `https://gitlab.com/group/project/-/raw/main/assets/version.json`

### Files in Custom Directory

If your files are in a custom directory like `extension-assets/`:
```
Repository: https://gitlab.com/group/project
Files:
  - extension-assets/inject.css
  - extension-assets/inject.js
  - extension-assets/version.json
```

**Config:**
```javascript
gitlabUrl: 'https://gitlab.com/group/project/-/raw/main/extension-assets/'
```

### Different Branch

If your files are in a different branch:
```
Repository: https://gitlab.com/group/project
Branch: production
Files:
  - inject.css
  - inject.js
  - version.json
```

**Config:**
```javascript
gitlabUrl: 'https://gitlab.com/group/project/-/raw/production/'
```

### Self-Hosted GitLab

If using self-hosted GitLab:
```
Repository: https://gitlab.yourcompany.com/group/project
Files:
  - assets/inject.css
  - assets/inject.js
  - assets/version.json
```

**Config:**
```javascript
gitlabUrl: 'https://gitlab.yourcompany.com/group/project/-/raw/main/assets/'
```

## How to Get the Correct URL

### Method 1: From GitLab Web Interface

1. Navigate to your repository in GitLab
2. Go to the directory containing your files
3. Click on one of the files (e.g., `inject.css`)
4. Click the "Raw" button
5. Copy the URL
6. Remove the filename from the end
7. Ensure it ends with `/`

**Example:**
- Raw file URL: `https://gitlab.com/group/project/-/raw/main/assets/inject.css`
- Base URL: `https://gitlab.com/group/project/-/raw/main/assets/`

### Method 2: Manual Construction

The format is:
```
https://[gitlab-host]/[group]/[project]/-/raw/[branch]/[path]/
```

**Components:**
- `[gitlab-host]` - `gitlab.com` or your self-hosted GitLab
- `[group]` - Your GitLab group/organization
- `[project]` - Your project name
- `[branch]` - Branch name (usually `main` or `master`)
- `[path]` - Directory path (leave empty if files are in root)

## Important Rules

1. ✅ **Must end with `/`** - The extension adds filenames, so the URL must end with a forward slash
2. ✅ **Use raw file URLs** - Must use the `/-/raw/` path, not regular file view
3. ✅ **Point to directory** - URL should point to the directory containing the files, not a specific file
4. ✅ **Match branch** - Ensure the branch name matches where your files are located

## Common Mistakes

### ❌ Wrong: Missing trailing slash
```javascript
gitlabUrl: 'https://gitlab.com/group/project/-/raw/main/assets'
// Missing / at the end
```

### ✅ Correct
```javascript
gitlabUrl: 'https://gitlab.com/group/project/-/raw/main/assets/'
```

### ❌ Wrong: Including filename
```javascript
gitlabUrl: 'https://gitlab.com/group/project/-/raw/main/inject.css'
// Includes filename - extension will append it again
```

### ✅ Correct
```javascript
gitlabUrl: 'https://gitlab.com/group/project/-/raw/main/'
```

### ❌ Wrong: Using non-raw URL
```javascript
gitlabUrl: 'https://gitlab.com/group/project/blob/main/assets/'
// Missing /-/raw/ path
```

### ✅ Correct
```javascript
gitlabUrl: 'https://gitlab.com/group/project/-/raw/main/assets/'
```

## Verification

After setting the URL, you can verify it's correct by:

1. Opening extension Options page
2. Clicking "Refresh Assets" in the popup
3. Checking browser console for errors
4. Verifying the extension fetches assets successfully

If there are errors, check:
- URL format is correct
- Files exist at that location
- Branch name is correct
- PAT is set if repository is private

## Summary

- **Point to the directory** containing your files (not a specific file)
- **Include the full path** if files are in a subdirectory
- **End with `/`** - required for URL construction
- **Use raw file URLs** - must include `/-/raw/` in the path
- **Match your branch** - use the correct branch name

