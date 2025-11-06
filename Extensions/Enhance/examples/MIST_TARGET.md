# Mist.com Target Configuration

## Target Domains

The extension is configured to target the following Mist.com admin pages:

1. **Base Admin URL**: `https://manage.mist.com/admin/*`
   - Matches all pages under the admin section

2. **Dashboard Insights Page**: `https://manage.mist.com/admin/?org_id=*#!dashboard/insights/*`
   - Specifically targets the dashboard insights page
   - `org_id` query parameter is wildcarded (any organization ID)
   - Site ID in the hash is wildcarded (any site ID)

## URL Pattern Examples

The following URLs will match and have assets injected:

- `https://manage.mist.com/admin/`
- `https://manage.mist.com/admin/?org_id=abc123`
- `https://manage.mist.com/admin/?org_id=abc123#!dashboard/insights/site-001`
- `https://manage.mist.com/admin/?org_id=xyz789#!dashboard/insights/site-456`
- `https://manage.mist.com/admin/settings`
- `https://manage.mist.com/admin/devices`

## Domain-Specific Enhancements

The example `inject.js` file includes domain-specific code for Mist.com that:

1. **Detects Dashboard Insights Page**: Checks if the current URL matches the insights dashboard pattern
2. **Extracts Site ID**: Parses the site ID from the URL hash for use in enhancements
3. **Enhances Metrics**: Adds hover effects and styling to metric cards
4. **Enhances Charts**: Improves chart container styling
5. **Adds Keyboard Shortcuts**: Provides quick search functionality (Ctrl/Cmd + K)
6. **Improves Tables**: Adds sticky headers to data tables
7. **Handles SPA Navigation**: Watches for hash changes and re-initializes enhancements

## Usage in inject.js

The Mist.com specific code is wrapped in domain-specific blocks:

```javascript
/* domain:manage.mist.com */
// Mist.com specific code here
/* end-domain */
```

This ensures the code only runs on Mist.com pages, not on other target domains.

## Testing

To test the enhancements:

1. Load the extension in your browser
2. Configure the GitLab URL in extension options
3. Navigate to `https://manage.mist.com/admin/`
4. Open browser DevTools console
5. Look for `[Enhance]` log messages
6. Navigate to a dashboard insights page: `https://manage.mist.com/admin/?org_id=YOUR_ORG#!dashboard/insights/YOUR_SITE_ID`
7. Verify enhancements are applied (hover over metric cards, check table headers, etc.)

## Customization

You can customize the enhancements by modifying the functions in the `inject.js` file:

- `initDashboardInsights()`: Main initialization for insights page
- `enhanceDashboardMetrics()`: Enhancements for metric cards
- `enhanceDashboardCharts()`: Enhancements for charts
- `initAdminEnhancements()`: General admin page enhancements

Add your own custom logic based on your specific needs for the Mist.com dashboard.

