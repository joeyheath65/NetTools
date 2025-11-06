/**
 * Background service worker for Enhance extension
 * Handles asset fetching, version checking, caching, and alarms
 */

import { fetchAssetsWithFallback } from '../lib/fetcher.js';
import { checkAssetVersion, checkExtensionVersion, showUpdateNotification } from '../lib/versioning.js';
import { getConfigValue, getCachedAssets } from '../lib/storage.js';

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
    
    // Check if assets need update
    const assetVersionCheck = await checkAssetVersion();
    if (assetVersionCheck.needsUpdate) {
      console.log('New asset version available, re-fetching...');
      await fetchAssetsWithFallback();
    }
    
    // Check if extension needs update
    const extensionVersionCheck = await checkExtensionVersion();
    if (extensionVersionCheck.needsUpdate) {
      await showUpdateNotification(extensionVersionCheck);
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
    fetchAndCacheAssets();
  }
});

/**
 * Handle extension installation
 */
chrome.runtime.onInstalled.addListener(async () => {
  console.log('Enhance extension installed');
  
  // Fetch assets on install
  await fetchAndCacheAssets();
  
  // Setup periodic fetching
  await setupAlarm();
});

/**
 * Handle extension startup
 */
chrome.runtime.onStartup.addListener(async () => {
  console.log('Enhance extension started');
  
  // Fetch assets on startup
  await fetchAndCacheAssets();
  
  // Setup periodic fetching
  await setupAlarm();
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
    const { isTargetDomain } = await import('../lib/storage.js');
    const isTarget = await isTargetDomain(request.url);
    sendResponse({ isTarget });
    return true;
  }
});

/**
 * Handle notification clicks
 */
chrome.notifications.onClicked.addListener((notificationId) => {
  chrome.storage.local.get(['pendingUpdate'], (result) => {
    if (result.pendingUpdate && result.pendingUpdate.updateUrl) {
      chrome.tabs.create({ url: result.pendingUpdate.updateUrl });
    }
  });
  chrome.notifications.clear(notificationId);
});

// Initialize on service worker startup
(async () => {
  console.log('Enhance background service worker started');
  
  // Check if we have cached assets, if not, fetch them
  const cached = await getCachedAssets();
  if (!cached.css && !cached.js && !cached.version) {
    await fetchAndCacheAssets();
  }
  
  // Setup alarm
  await setupAlarm();
})();

