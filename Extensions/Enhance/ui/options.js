/**
 * Options page script for Enhance extension
 * Manages extension configuration
 */

import { getConfig, saveConfig, getConfigValue } from '../lib/storage.js';
import { DEFAULT_GITLAB_CONFIG } from '../lib/config.js';

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
    // If no URL provided, check if there's a default in config.js
    if (!gitlabUrl && !DEFAULT_GITLAB_CONFIG.gitlabUrl) {
      throw new Error('GitLab URL is required (either set in config.js or enter here)');
    }
    
    // Use default from config.js if not provided
    const finalGitlabUrl = gitlabUrl || DEFAULT_GITLAB_CONFIG.gitlabUrl;
    
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
    // Use provided values, or fall back to defaults from config.js
    const config = {
      ...existingConfig,
      gitlabUrl: finalGitlabUrl,
      gitlabPat: gitlabPat || DEFAULT_GITLAB_CONFIG.gitlabPat || '',
      pollInterval: pollInterval || DEFAULT_GITLAB_CONFIG.pollInterval || 30,
      targetDomains: targetDomains.length > 0 ? targetDomains : DEFAULT_GITLAB_CONFIG.targetDomains
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
 * Load default values from config.js into form (without saving)
 * Useful for seeing what the hardcoded defaults are
 */
function showDefaults() {
  document.getElementById('gitlabUrl').placeholder = DEFAULT_GITLAB_CONFIG.gitlabUrl || 'Enter GitLab Raw URL';
  if (DEFAULT_GITLAB_CONFIG.gitlabUrl) {
    // Show a hint that there's a default value
    const urlInput = document.getElementById('gitlabUrl');
    urlInput.title = `Default: ${DEFAULT_GITLAB_CONFIG.gitlabUrl}`;
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
  showDefaults();
  
  document.getElementById('optionsForm').addEventListener('submit', saveConfiguration);
  document.getElementById('resetBtn').addEventListener('click', resetConfig);
});

