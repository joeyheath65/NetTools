/**
 * Content script for injecting CSS and JS into target domains
 * Injects assets based on domain matching and supports multiple domains
 */

// Note: Content scripts use messaging to communicate with background script
// to avoid direct storage access and maintain security boundaries

const INJECTION_TAG = 'data-ld-proxy';
const INJECTED_FLAG = 'enhance-injected';

/**
 * Check if assets have already been injected
 * @returns {boolean} True if already injected
 */
function isAlreadyInjected() {
  return document.documentElement.hasAttribute(INJECTED_FLAG);
}

/**
 * Mark document as injected
 */
function markAsInjected() {
  document.documentElement.setAttribute(INJECTED_FLAG, 'true');
}

/**
 * Inject CSS into the page
 * @param {string} css - CSS content to inject
 * @param {string} domain - Current domain for domain-specific CSS
 */
function injectCSS(css, domain) {
  if (!css) return;
  
  // Remove existing injected styles
  const existing = document.querySelector(`style[${INJECTION_TAG}]`);
  if (existing) {
    existing.remove();
  }
  
  // Create new style element
  const style = document.createElement('style');
  style.setAttribute(INJECTION_TAG, 'true');
  style.textContent = css;
  
  // Inject at the start of head for priority
  if (document.head) {
    document.head.insertBefore(style, document.head.firstChild);
  } else {
    // If head doesn't exist yet, wait for it
    const observer = new MutationObserver((mutations, obs) => {
      if (document.head) {
        document.head.insertBefore(style, document.head.firstChild);
        obs.disconnect();
      }
    });
    observer.observe(document.documentElement, { childList: true });
  }
}

/**
 * Inject JS into the page
 * @param {string} js - JavaScript content to inject
 * @param {string} domain - Current domain for domain-specific JS
 */
function injectJS(js, domain) {
  if (!js) return;
  
  // Remove existing injected scripts
  const existing = document.querySelector(`script[${INJECTION_TAG}]`);
  if (existing) {
    existing.remove();
  }
  
  // Create blob URL for script
  const blob = new Blob([js], { type: 'application/javascript' });
  const url = URL.createObjectURL(blob);
  
  // Create script element
  const script = document.createElement('script');
  script.setAttribute(INJECTION_TAG, 'true');
  script.src = url;
  script.async = false;
  
  // Clean up blob URL after script loads
  script.onload = () => {
    URL.revokeObjectURL(url);
  };
  
  // Inject script
  if (document.head) {
    document.head.appendChild(script);
  } else {
    // If head doesn't exist yet, wait for it
    const observer = new MutationObserver((mutations, obs) => {
      if (document.head) {
        document.head.appendChild(script);
        obs.disconnect();
      }
    });
    observer.observe(document.documentElement, { childList: true });
  }
}

/**
 * Get domain-specific assets from cached assets
 * Supports format: / * domain:example.com * / ... / * end-domain * /
 * @param {string} content - CSS or JS content
 * @param {string} domain - Current domain
 * @returns {string} Domain-specific content
 */
function getDomainSpecificContent(content, domain) {
  if (!content) return '';
  
  // Extract domain name from URL
  const domainName = new URL(domain).hostname.replace(/^www\./, '');
  
  // Look for domain-specific blocks
  const domainRegex = new RegExp(
    `/\\*\\s*domain:${domainName}\\s*\\*/([\\s\\S]*?)/\\*\\s*end-domain\\s*\\*/`,
    'g'
  );
  
  let domainContent = '';
  let match;
  while ((match = domainRegex.exec(content)) !== null) {
    domainContent += match[1] + '\n';
  }
  
  // If no domain-specific content found, return all content (global)
  // Remove all domain-specific blocks from global content
  const globalContent = content.replace(
    /\/\*\s*domain:[^*]+\s*\*\/[\s\S]*?\/\*\s*end-domain\s*\*\//g,
    ''
  );
  
  return domainContent || globalContent;
}

/**
 * Check if current URL matches target domains
 * @param {string} url - URL to check
 * @returns {Promise<boolean>} True if URL matches a target domain
 */
async function isTargetDomain(url) {
  return new Promise((resolve) => {
    chrome.runtime.sendMessage({ action: 'isTargetDomain', url }, (response) => {
      resolve(response?.isTarget || false);
    });
  });
}

/**
 * Load and inject assets for current domain
 */
async function loadAndInjectAssets() {
  try {
    const currentUrl = window.location.href;
    const targetCheck = await new Promise((resolve) => {
      chrome.runtime.sendMessage({ action: 'isTargetDomain', url: currentUrl }, (response) => {
        resolve(response?.isTarget || false);
      });
    });
    
    if (!targetCheck) {
      return; // Not a target domain, skip injection
    }
    
    if (isAlreadyInjected()) {
      return; // Already injected, skip
    }
    
    // Get cached assets from background
    const response = await new Promise((resolve) => {
      chrome.runtime.sendMessage({ action: 'getCachedAssets' }, (response) => {
        resolve(response);
      });
    });
    
    if (!response || !response.success || !response.assets) {
      console.warn('Enhance: No cached assets available');
      return;
    }
    
    const assets = response.assets;
    
    // Get domain-specific content
    const css = getDomainSpecificContent(assets.css, currentUrl);
    const js = getDomainSpecificContent(assets.js, currentUrl);
    
    // Inject CSS
    if (css) {
      injectCSS(css, currentUrl);
    }
    
    // Inject JS
    if (js) {
      // Wait for DOM to be ready for JS injection
      if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
          injectJS(js, currentUrl);
        });
      } else {
        injectJS(js, currentUrl);
      }
    }
    
    markAsInjected();
    console.log('Enhance: Assets injected successfully');
  } catch (error) {
    console.error('Enhance: Error loading assets:', error);
  }
}

// Run injection
// Use different strategies based on document state
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', loadAndInjectAssets);
} else {
  // DOM already loaded, inject immediately
  loadAndInjectAssets();
}

// Also listen for navigation in SPAs
let lastUrl = location.href;
new MutationObserver(() => {
  const url = location.href;
  if (url !== lastUrl) {
    lastUrl = url;
    // Reset injection flag and reload assets
    document.documentElement.removeAttribute(INJECTED_FLAG);
    loadAndInjectAssets();
  }
}).observe(document, { subtree: true, childList: true });

