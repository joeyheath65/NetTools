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
    const updateSection = document.getElementById('updateSection');
    if (pendingUpdate && pendingUpdate.timestamp) {
      updateSection.classList.remove('hidden');
      
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
    } else {
      updateSection.classList.add('hidden');
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
  showStatus(message, 'error');
}

/**
 * Hide error message
 */
function hideError() {
  const errorSection = document.getElementById('errorSection');
  errorSection.classList.add('hidden');
}

/**
 * Refresh assets from GitLab
 */
async function refreshAssets() {
  const refreshBtn = document.getElementById('refreshAssetsBtn');
  
  try {
    hideError();
    refreshBtn.disabled = true;
    refreshBtn.textContent = 'Refreshing...';
    
    // Send message and wait for response
    const response = await new Promise((resolve, reject) => {
      chrome.runtime.sendMessage({ action: 'fetchAssets' }, (response) => {
        if (chrome.runtime.lastError) {
          reject(new Error(chrome.runtime.lastError.message));
        } else {
          resolve(response);
        }
      });
    });
    
    if (response && response.success) {
      // Wait a moment for assets to be cached
      await new Promise(resolve => setTimeout(resolve, 500));
      // Update status after refresh
      await updateStatus();
      showStatus('Assets refreshed successfully!', 'success');
    } else {
      throw new Error(response?.error || 'Failed to refresh assets');
    }
  } catch (error) {
    console.error('Error refreshing assets:', error);
    showError(error.message || 'Failed to refresh assets. Check console for details.');
  } finally {
    refreshBtn.disabled = false;
    refreshBtn.textContent = 'Refresh Assets';
  }
}

/**
 * Show success message (temporary, similar to error message)
 */
function showStatus(message, type) {
  const errorSection = document.getElementById('errorSection');
  const errorMessage = document.getElementById('errorMessage');
  
  if (type === 'success') {
    errorMessage.style.background = '#d4edda';
    errorMessage.style.color = '#155724';
    errorMessage.style.border = '1px solid #c3e6cb';
  } else {
    errorMessage.style.background = '#fee';
    errorMessage.style.color = '#c33';
    errorMessage.style.border = '1px solid #fcc';
  }
  
  errorMessage.textContent = message;
  errorSection.classList.remove('hidden');
  
  // Auto-hide success messages after 3 seconds
  if (type === 'success') {
    setTimeout(() => {
      errorSection.classList.add('hidden');
    }, 3000);
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

