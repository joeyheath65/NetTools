/**
 * Options page script for Enhance extension
 * Manages extension configuration
 */

import { getConfig, saveConfig } from '../lib/storage.js';
import { DEFAULT_GITLAB_CONFIG } from '../lib/config.js';

/**
 * Load current configuration into form
 */
async function loadConfig() {
  try {
    const config = await getConfig();
    
    document.getElementById('gitlabUrl').value = config.gitlabUrl || '';
    document.getElementById('gitlabPat').value = config.gitlabPat || '';
    document.getElementById('githubUrl').value = config.githubUrl || '';
    document.getElementById('githubPat').value = config.githubPat || '';
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
    const githubUrl = document.getElementById('githubUrl').value.trim();
    const githubPat = document.getElementById('githubPat').value.trim();
    const pollInterval = parseInt(document.getElementById('pollInterval').value, 10);
    const targetDomainsText = document.getElementById('targetDomains').value.trim();
    
    // Determine primary and fallback URLs
    const finalGitlabUrl = gitlabUrl || DEFAULT_GITLAB_CONFIG.gitlabUrl || '';
    const finalGithubUrl = githubUrl || DEFAULT_GITLAB_CONFIG.githubUrl || '';

    if (!finalGitlabUrl && !finalGithubUrl) {
      throw new Error('At least one asset source URL (GitLab or GitHub) must be provided.');
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
    // Use provided values, or fall back to defaults from config.js
    const config = {
      ...existingConfig,
      gitlabUrl: finalGitlabUrl,
      gitlabPat: gitlabPat || DEFAULT_GITLAB_CONFIG.gitlabPat || '',
      githubUrl: finalGithubUrl,
      githubPat: githubPat || DEFAULT_GITLAB_CONFIG.githubPat || '',
      pollInterval: pollInterval || DEFAULT_GITLAB_CONFIG.pollInterval || 30,
      targetDomains: targetDomains.length > 0 ? targetDomains : DEFAULT_GITLAB_CONFIG.targetDomains
    };
    
    await saveConfig(config);
    
    // Notify background script to update alarm
    chrome.runtime.sendMessage({ action: 'configUpdated' }, (response) => {
      if (chrome.runtime.lastError) {
        console.warn('Error notifying background script:', chrome.runtime.lastError);
      }
    });
    
    showStatus('Settings saved successfully!', 'success');
    
    // Trigger asset fetch if URL changed or if this is first time setting URL
    const urlChanged = existingConfig.gitlabUrl !== finalGitlabUrl;
    const githubChanged = existingConfig.githubUrl !== finalGithubUrl;
    if (
      urlChanged || githubChanged ||
      ((!existingConfig.gitlabUrl && finalGitlabUrl) || (!existingConfig.githubUrl && finalGithubUrl))
    ) {
      chrome.runtime.sendMessage({ action: 'fetchAssets' }, (response) => {
        if (chrome.runtime.lastError) {
          console.warn('Error fetching assets:', chrome.runtime.lastError);
        } else if (response && !response.success) {
          console.warn('Asset fetch warning:', response.error);
        }
      });
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
  const urlInput = document.getElementById('gitlabUrl');
  const patInput = document.getElementById('gitlabPat');
  const githubUrlInput = document.getElementById('githubUrl');
  const githubPatInput = document.getElementById('githubPat');
  const pollInput = document.getElementById('pollInterval');
  const domainsInput = document.getElementById('targetDomains');
  
  // Set placeholders based on defaults
  urlInput.placeholder = DEFAULT_GITLAB_CONFIG.gitlabUrl || 'Enter GitLab Raw URL (e.g., https://gitlab.com/group/project/-/raw/main/assets/)';
  githubUrlInput.placeholder = DEFAULT_GITLAB_CONFIG.githubUrl || 'Enter GitHub Raw URL (e.g., https://raw.githubusercontent.com/org/project/main/assets/)';
  
  if (DEFAULT_GITLAB_CONFIG.gitlabUrl) {
    urlInput.title = `Default from config.js: ${DEFAULT_GITLAB_CONFIG.gitlabUrl}`;
  }
  
  if (DEFAULT_GITLAB_CONFIG.githubUrl) {
    githubUrlInput.title = `Default from config.js: ${DEFAULT_GITLAB_CONFIG.githubUrl}`;
  }
  
  if (DEFAULT_GITLAB_CONFIG.gitlabPat) {
    patInput.title = 'Default GitLab PAT is set in config.js';
  }

  if (DEFAULT_GITLAB_CONFIG.githubPat) {
    githubPatInput.title = 'Default GitHub PAT is set in config.js';
  }
  
  if (DEFAULT_GITLAB_CONFIG.pollInterval) {
    pollInput.title = `Default from config.js: ${DEFAULT_GITLAB_CONFIG.pollInterval} minutes`;
  }
  
  if (DEFAULT_GITLAB_CONFIG.targetDomains && DEFAULT_GITLAB_CONFIG.targetDomains.length > 0) {
    domainsInput.title = `Default from config.js: ${DEFAULT_GITLAB_CONFIG.targetDomains.join(', ')}`;
  }
  
  // Note: Helper text would be nice but could cause duplicate inserts
  // Users can see defaults in the placeholder/title tooltips instead
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

