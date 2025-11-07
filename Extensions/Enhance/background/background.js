/**
 * Background service worker for Enhance extension
 * Handles asset fetching, version checking, caching, and alarms
 */

import { fetchAssetsWithFallback } from '../lib/fetcher.js';
import { checkAssetVersion, checkExtensionVersion, showUpdateNotification } from '../lib/versioning.js';
import { getConfigValue, getCachedAssets, isTargetDomain, saveCachedAssets } from '../lib/storage.js';
import { getDefaultAssets } from '../lib/defaultAssets.js';

const ALARM_NAME = 'fetchAssets';
const ALARM_INTERVAL = 30; // minutes

/**
 * Fetch and cache assets from GitLab
 */
async function fetchAndCacheAssets() {
  try {
    console.log('Fetching assets...');
    const assets = await fetchAssetsWithFallback();
    console.log('Assets fetched and cached successfully');
    
    // Check if assets need update (non-blocking)
    try {
      const assetVersionCheck = await checkAssetVersion();
      if (assetVersionCheck.needsUpdate && !assetVersionCheck.error) {
        console.log('New asset version available, re-fetching...');
        await fetchAssetsWithFallback();
      }
    } catch (error) {
      console.warn('Error checking asset version (non-critical):', error);
    }
    
    // Check if extension needs update (non-blocking)
    try {
      const extensionVersionCheck = await checkExtensionVersion();
      if (extensionVersionCheck.needsUpdate && !extensionVersionCheck.error) {
        await showUpdateNotification(extensionVersionCheck);
      }
    } catch (error) {
      console.warn('Error checking extension version (non-critical):', error);
    }
  } catch (error) {
    console.error('Error fetching assets:', error);
    // Fallback to cached assets is handled in fetchAssetsWithFallback
  }
}

/**
 * Setup alarm for periodic asset fetching
 */
async function setupAlarm() {
  const pollInterval = await getConfigValue('pollInterval');
  const intervalMinutes = pollInterval || ALARM_INTERVAL;
  
  // Clear existing alarm
  chrome.alarms.clear(ALARM_NAME);
  
  // Create new alarm
  chrome.alarms.create(ALARM_NAME, {
    periodInMinutes: intervalMinutes
  });
  
  console.log(`Alarm set for ${intervalMinutes} minutes`);
}

/**
 * Handle alarm trigger
 */
chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === ALARM_NAME) {
    fetchAndCacheAssets().catch((error) => {
      console.error('Error fetching assets from alarm:', error);
    });
  }
});

/**
 * Handle extension installation
 */
chrome.runtime.onInstalled.addListener(async () => {
  try {
    console.log('Enhance extension installed');
    
    // Fetch assets on install
    await fetchAndCacheAssets();
    
    // Setup periodic fetching
    await setupAlarm();
  } catch (error) {
    console.error('Error during extension installation:', error);
  }
});

/**
 * Handle extension startup
 */
chrome.runtime.onStartup.addListener(async () => {
  try {
    console.log('Enhance extension started');
    
    // Fetch assets on startup
    await fetchAndCacheAssets();
    
    // Setup periodic fetching
    await setupAlarm();
  } catch (error) {
    console.error('Error during extension startup:', error);
  }
});

/**
 * Handle messages from content scripts or popup
 */
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'fetchAssets') {
    fetchAndCacheAssets().then(() => {
      sendResponse({ success: true });
    }).catch((error) => {
      sendResponse({ success: false, error: error.message });
    });
    return true; // Keep channel open for async response
  }
  
  if (request.action === 'getCachedAssets') {
    getCachedAssets().then((assets) => {
      sendResponse({ success: true, assets });
    }).catch((error) => {
      sendResponse({ success: false, error: error.message });
    });
    return true;
  }
  
  if (request.action === 'checkVersions') {
    Promise.all([
      checkAssetVersion(),
      checkExtensionVersion()
    ]).then(([assetCheck, extensionCheck]) => {
      sendResponse({ success: true, assetCheck, extensionCheck });
    }).catch((error) => {
      sendResponse({ success: false, error: error.message });
    });
    return true;
  }
  
  if (request.action === 'configUpdated') {
    setupAlarm().then(() => {
      sendResponse({ success: true });
    }).catch((error) => {
      sendResponse({ success: false, error: error.message });
    });
    return true;
  }
  
  if (request.action === 'isTargetDomain') {
    (async () => {
      try {
        const isTarget = await isTargetDomain(request.url);
        sendResponse({ isTarget });
      } catch (error) {
        console.error('Error checking target domain:', error);
        sendResponse({ isTarget: false, error: error.message });
      }
    })();
    return true; // Keep channel open for async response
  }
  
  // Return false for unhandled messages
  return false;
});

/**
 * Handle notification clicks
 */
chrome.notifications.onClicked.addListener((notificationId) => {
  try {
    chrome.storage.local.get(['pendingUpdate'], (result) => {
      try {
        if (result.pendingUpdate && result.pendingUpdate.updateUrl) {
          chrome.tabs.create({ url: result.pendingUpdate.updateUrl });
        }
      } catch (error) {
        console.error('Error handling notification click:', error);
      }
    });
    chrome.notifications.clear(notificationId);
  } catch (error) {
    console.error('Error in notification click handler:', error);
  }
});

// Initialize on service worker startup
(async () => {
  try {
    console.log('Enhance background service worker started');
    
    // Check if we have cached assets, if not, initialize with defaults
    try {
      const cached = await getCachedAssets();
      if (!cached.css && !cached.js && !cached.version) {
        // Try to fetch from GitLab, but fall back to defaults if not configured
        try {
          const gitlabUrl = await getConfigValue('gitlabUrl');
          if (gitlabUrl) {
            // GitLab URL is configured, try to fetch
            await fetchAndCacheAssets();
          } else {
            // No GitLab URL configured, use default assets
            console.log('No GitLab URL configured, using default built-in assets');
            const defaultAssets = getDefaultAssets();
            await saveCachedAssets(defaultAssets);
          }
        } catch (error) {
          console.error('Error initializing assets:', error);
          // Fallback to default assets on error
          try {
            const defaultAssets = getDefaultAssets();
            await saveCachedAssets(defaultAssets);
          } catch (fallbackError) {
            console.error('Error loading default assets:', fallbackError);
          }
        }
      }
    } catch (error) {
      console.error('Error checking cached assets:', error);
    }
    
    // Setup alarm
    try {
      await setupAlarm();
    } catch (error) {
      console.error('Error setting up alarm:', error);
    }
  } catch (error) {
    console.error('Fatal error in service worker initialization:', error);
  }
})();

