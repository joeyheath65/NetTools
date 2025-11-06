/**
 * Popup script for Enhance extension
 * Displays status and provides controls
 */

import { getConfigValue, getCachedAssets } from '../lib/storage.js';
import { getExtensionVersion } from '../lib/versioning.js';

/**
 * Format timestamp to readable date
 * @param {number} timestamp - Unix timestamp in milliseconds
 * @returns {string} Formatted date string
 */
function formatDate(timestamp) {
  if (!timestamp) return 'Never';
  const date = new Date(timestamp);
  return date.toLocaleString();
}

/**
 * Update popup UI with current status
 */
async function updateStatus() {
  try {
    // Get extension version
    const extVersion = getExtensionVersion();
    document.getElementById('extensionVersion').textContent = `v${extVersion}`;
    document.getElementById('extVersion').textContent = `v${extVersion}`;
    
    // Get last fetch time
    const lastFetchTime = await getConfigValue('lastFetchTime');
    document.getElementById('lastFetchTime').textContent = formatDate(lastFetchTime);
    
    // Get asset version
    const assets = await getCachedAssets();
    const assetVersion = assets.version?.version || 'Unknown';
    document.getElementById('assetVersion').textContent = assetVersion;
    
    // Check for pending update
    const pendingUpdate = await getConfigValue('pendingUpdate');
    if (pendingUpdate && pendingUpdate.timestamp) {
      const updateSection = document.getElementById('updateSection');
      updateSection.style.display = 'block';
      
      document.getElementById('updateNowBtn').onclick = () => {
        if (pendingUpdate.updateUrl) {
          chrome.tabs.create({ url: pendingUpdate.updateUrl });
        }
      };
      
      document.getElementById('changelogBtn').onclick = () => {
        if (pendingUpdate.changelogUrl) {
          chrome.tabs.create({ url: pendingUpdate.changelogUrl });
        }
      };
    }
  } catch (error) {
    console.error('Error updating status:', error);
    showError(error.message);
  }
}

/**
 * Show error message
 * @param {string} message - Error message
 */
function showError(message) {
  const errorSection = document.getElementById('errorSection');
  const errorMessage = document.getElementById('errorMessage');
  errorMessage.textContent = message;
  errorSection.style.display = 'block';
}

/**
 * Hide error message
 */
function hideError() {
  document.getElementById('errorSection').style.display = 'none';
}

/**
 * Refresh assets from GitLab
 */
async function refreshAssets() {
  try {
    hideError();
    const refreshBtn = document.getElementById('refreshAssetsBtn');
    refreshBtn.disabled = true;
    refreshBtn.textContent = 'Refreshing...';
    
    const response = await chrome.runtime.sendMessage({ action: 'fetchAssets' });
    
    if (response && response.success) {
      // Update status after refresh
      await updateStatus();
      refreshBtn.textContent = 'Refresh Assets';
    } else {
      throw new Error(response?.error || 'Failed to refresh assets');
    }
  } catch (error) {
    console.error('Error refreshing assets:', error);
    showError(error.message);
  } finally {
    const refreshBtn = document.getElementById('refreshAssetsBtn');
    refreshBtn.disabled = false;
    refreshBtn.textContent = 'Refresh Assets';
  }
}

// Initialize popup
document.addEventListener('DOMContentLoaded', async () => {
  await updateStatus();
  
  // Setup button handlers
  document.getElementById('refreshAssetsBtn').addEventListener('click', refreshAssets);
  document.getElementById('optionsBtn').addEventListener('click', () => {
    chrome.runtime.openOptionsPage();
  });
});

