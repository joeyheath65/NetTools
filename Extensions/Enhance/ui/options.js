/**
 * Options page script for Enhance extension
 * Manages extension configuration
 */

import { getConfig, saveConfig, getConfigValue } from '../lib/storage.js';

/**
 * Load current configuration into form
 */
async function loadConfig() {
  try {
    const config = await getConfig();
    
    document.getElementById('gitlabUrl').value = config.gitlabUrl || '';
    document.getElementById('gitlabPat').value = config.gitlabPat || '';
    document.getElementById('pollInterval').value = config.pollInterval || 30;
    document.getElementById('targetDomains').value = (config.targetDomains || []).join('\n');
  } catch (error) {
    console.error('Error loading config:', error);
    showStatus('Error loading configuration', 'error');
  }
}

/**
 * Save configuration from form
 */
async function saveConfiguration(event) {
  event.preventDefault();
  
  try {
    const gitlabUrl = document.getElementById('gitlabUrl').value.trim();
    const gitlabPat = document.getElementById('gitlabPat').value.trim();
    const pollInterval = parseInt(document.getElementById('pollInterval').value, 10);
    const targetDomainsText = document.getElementById('targetDomains').value.trim();
    
    // Validate inputs
    if (!gitlabUrl) {
      throw new Error('GitLab URL is required');
    }
    
    if (pollInterval < 1 || pollInterval > 1440) {
      throw new Error('Poll interval must be between 1 and 1440 minutes');
    }
    
    // Parse target domains (one per line)
    const targetDomains = targetDomainsText
      .split('\n')
      .map(line => line.trim())
      .filter(line => line.length > 0);
    
    if (targetDomains.length === 0) {
      throw new Error('At least one target domain is required');
    }
    
    // Get existing config to preserve other values
    const existingConfig = await getConfig();
    
    // Update configuration
    const config = {
      ...existingConfig,
      gitlabUrl,
      gitlabPat,
      pollInterval,
      targetDomains
    };
    
    await saveConfig(config);
    
    // Notify background script to update alarm
    chrome.runtime.sendMessage({ action: 'configUpdated' });
    
    showStatus('Settings saved successfully!', 'success');
    
    // Trigger asset fetch if URL changed
    if (existingConfig.gitlabUrl !== gitlabUrl) {
      chrome.runtime.sendMessage({ action: 'fetchAssets' });
    }
  } catch (error) {
    console.error('Error saving config:', error);
    showStatus(error.message, 'error');
  }
}

/**
 * Reset configuration to defaults
 */
async function resetConfig() {
  if (!confirm('Are you sure you want to reset all settings to defaults?')) {
    return;
  }
  
  try {
    const { DEFAULT_CONFIG } = await import('../lib/storage.js');
    await saveConfig(DEFAULT_CONFIG);
    await loadConfig();
    showStatus('Settings reset to defaults', 'success');
  } catch (error) {
    console.error('Error resetting config:', error);
    showStatus('Error resetting configuration', 'error');
  }
}

/**
 * Show status message
 * @param {string} message - Status message
 * @param {string} type - Message type: 'success' or 'error'
 */
function showStatus(message, type) {
  const statusEl = document.getElementById('saveStatus');
  statusEl.textContent = message;
  statusEl.className = `status-message ${type}`;
  statusEl.style.display = 'block';
  
  // Hide after 3 seconds for success messages
  if (type === 'success') {
    setTimeout(() => {
      statusEl.style.display = 'none';
    }, 3000);
  }
}

// Initialize options page
document.addEventListener('DOMContentLoaded', async () => {
  await loadConfig();
  
  document.getElementById('optionsForm').addEventListener('submit', saveConfiguration);
  document.getElementById('resetBtn').addEventListener('click', resetConfig);
});

