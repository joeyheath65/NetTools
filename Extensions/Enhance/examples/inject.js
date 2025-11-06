/**
 * Enhance Extension - Global JavaScript
 * This file contains JavaScript that will be injected into all target domains
 * 
 * Note: This code runs in the page context, not in an isolated world.
 * Be careful with variable names to avoid conflicts with page scripts.
 */

(function() {
  'use strict';
  
  // Global code for all domains
  console.log('[Enhance] Extension loaded');
  
  // Example: Add a global utility function
  window.Enhance = window.Enhance || {};
  window.Enhance.version = '1.0.0';
  window.Enhance.utils = {
    log: function(message) {
      console.log('[Enhance]', message);
    }
  };
  
  // Domain-specific code for manage.mist.com
  /* domain:manage.mist.com */
  (function() {
    console.log('[Enhance] Mist.com enhancements loaded');
    
    // Example: Wait for page to be ready
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', initMistEnhancements);
    } else {
      initMistEnhancements();
    }
    
    function initMistEnhancements() {
      // Add your Mist.com specific enhancements here
      // Example: Modify dashboard elements
      // const dashboard = document.querySelector('.dashboard');
      // if (dashboard) {
      //   dashboard.style.backgroundColor = '#f5f5f5';
      // }
    }
  })();
  /* end-domain */
  
  // Domain-specific code for example.com
  /* domain:example.com */
  (function() {
    console.log('[Enhance] Example.com enhancements loaded');
    
    // Add your example.com specific enhancements here
  })();
  /* end-domain */
  
})();

