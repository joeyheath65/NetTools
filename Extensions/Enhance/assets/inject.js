/**
 * Enhance Extension - Live JavaScript
 * This file contains JavaScript that will be injected into target domains
 * 
 * This is the LIVE version - upload this to your GitLab repository
 * The examples/ directory contains example/template files
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
  window.Enhance.version = '1.0.1';
  window.Enhance.utils = {
    log: function(message) {
      console.log('[Enhance]', message);
    }
  };
  
  // Domain-specific code for manage.mist.com
  /* domain:manage.mist.com */
  (function() {
    'use strict';
    
    console.log('[Enhance] Mist.com enhancements loaded');

    function getOrgAndSiteIds() {
      let orgId = null;
      let siteId = null;

      try {
        const url = new URL(window.location.href);
        orgId = url.searchParams.get('org_id');
      } catch (error) {
        console.warn('[Enhance] Unable to parse org_id from URL:', error);
      }

      const hashMatch = window.location.hash.match(/dashboard\/insights\/([^\/]+)/);
      if (hashMatch) {
        siteId = hashMatch[1];
      }

      if (!siteId) {
        const bodySiteId = document.body.getAttribute('data-mist-site-id');
        if (bodySiteId) {
          siteId = bodySiteId;
        }
      }

      return { orgId, siteId };
    }

    function createSiteConfigButton(targetUrl) {
      const buttonItem = document.createElement('li');
      buttonItem.className = 'comp-navbarBtn';
      buttonItem.setAttribute('data-enhance-site-config', 'button');
      buttonItem.setAttribute('role', 'button');
      buttonItem.tabIndex = 0;
      buttonItem.style.cursor = 'pointer';

      const label = document.createElement('div');
      label.className = 'comp-navbarBtn-text';
      label.textContent = 'Site Config';

      buttonItem.appendChild(label);

      const navigate = () => {
        window.location.href = targetUrl;
      };

      buttonItem.addEventListener('click', navigate);
      buttonItem.addEventListener('keydown', (event) => {
        if (event.key === 'Enter' || event.key === ' ') {
          event.preventDefault();
          navigate();
        }
      });

      return buttonItem;
    }

    function addSiteConfigNavButton() {
      const { orgId, siteId } = getOrgAndSiteIds();

      if (!orgId || !siteId) {
        return false;
      }

      const navList = document.querySelector('.comp-navigationBar-list');
      if (!navList) {
        return false;
      }

      if (navList.querySelector('[data-enhance-site-config="button"]')) {
        return true;
      }

      const dividerItem = document.createElement('li');
      dividerItem.setAttribute('data-enhance-site-config', 'divider');
      dividerItem.style.width = '100%';
      dividerItem.style.padding = '4px 12px';

      const hr = document.createElement('hr');
      hr.style.border = 'none';
      hr.style.borderTop = '1px solid rgba(255, 255, 255, 0.25)';
      hr.style.margin = '6px 0';
      dividerItem.appendChild(hr);

      const targetUrl = `https://manage.mist.com/admin/?org_id=${orgId}#!configuration/${siteId}`;
      const buttonItem = createSiteConfigButton(targetUrl);

      navList.appendChild(dividerItem);
      navList.appendChild(buttonItem);

      console.log('[Enhance] Added Site Config button to navbar', { orgId, siteId });
      return true;
    }

    function watchNavigationBar() {
      const navList = document.querySelector('.comp-navigationBar-list');

      if (!navList) {
        setTimeout(watchNavigationBar, 500);
        return false;
      }

      if (!navList.dataset.enhanceNavObserved) {
        const navObserver = new MutationObserver(() => {
          addSiteConfigNavButton();
        });

        navObserver.observe(navList, {
          childList: true,
          subtree: false
        });

        navList.dataset.enhanceNavObserved = 'true';
      }

      return addSiteConfigNavButton();
    }

    // Initialize Mist.com enhancements
    function initMistEnhancements() {
      const currentUrl = window.location.href;
      addSiteConfigNavButton();
      
      // Check if we're on the dashboard insights page
      if (currentUrl.includes('/admin/') && currentUrl.includes('#!dashboard/insights/')) {
        initDashboardInsights();
      }
      
      // General admin page enhancements
      if (currentUrl.includes('/admin/')) {
        initAdminEnhancements();
      }
    }
    
    // Enhancements for dashboard insights page
    function initDashboardInsights() {
      console.log('[Enhance] Initializing Mist.com Dashboard Insights enhancements');
      
      // Extract site ID from URL hash
      const hashMatch = window.location.hash.match(/dashboard\/insights\/([^\/]+)/);
      const siteId = hashMatch ? hashMatch[1] : null;
      
      if (siteId) {
        console.log('[Enhance] Site ID detected:', siteId);
        
        // Add custom data attribute for easy identification
        document.body.setAttribute('data-mist-site-id', siteId);
      }
      
      // Wait for dashboard to load (Mist.com uses dynamic loading)
      const observer = new MutationObserver((mutations, obs) => {
        const dashboard = document.querySelector('[class*="dashboard"], [class*="insights"]');
        if (dashboard) {
          enhanceDashboardMetrics();
          enhanceDashboardCharts();
          obs.disconnect();
        }
      });
      
      observer.observe(document.body, {
        childList: true,
        subtree: true
      });
      
      // Also try immediately in case page is already loaded
      setTimeout(() => {
        enhanceDashboardMetrics();
        enhanceDashboardCharts();
        addSiteConfigNavButton();
      }, 1000);
    }
    
    // Add "Enhanced!" indicator to Mist.com logo
    function addEnhancementIndicator() {
      const logoLink = document.querySelector('a.comp-navbarLogo');
      if (!logoLink) {
        return false;
      }
      
      // Check if already enhanced
      if (logoLink.hasAttribute('data-enhance-indicator')) {
        return true;
      }
      
      // Create "Enhanced!" text element
      const enhancedText = document.createElement('span');
      enhancedText.textContent = 'Enhanced!';
      enhancedText.style.cssText = `
        display: inline-block;
        margin-left: 8px;
        padding: 2px 8px;
        background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
        color: white;
        font-size: 11px;
        font-weight: 600;
        border-radius: 4px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        box-shadow: 0 2px 4px rgba(0, 123, 255, 0.3);
        vertical-align: middle;
        line-height: 1.4;
      `;
      
      // Add to logo link
      logoLink.appendChild(enhancedText);
      logoLink.setAttribute('data-enhance-indicator', 'true');
      
      console.log('[Enhance] Added "Enhanced!" indicator to logo');
      return true;
    }
    
    // Enhance dashboard metrics display
    function enhanceDashboardMetrics() {
      // Find metric cards and enhance them
      const metricCards = document.querySelectorAll('[class*="metric"], [class*="card"]');
      metricCards.forEach((card, index) => {
        if (!card.hasAttribute('data-enhance-processed')) {
          card.setAttribute('data-enhance-processed', 'true');
          
          // Add hover effect
          card.style.transition = 'transform 0.2s, box-shadow 0.2s';
          card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
            this.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.1)';
          });
          card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '';
          });
        }
      });
    }
    function addSuccessPercentageColumn() {
      const networkServersSection = document.querySelector('section.section-wrapper.status-section.network-servers-section');
  
      if (networkServersSection) {
          console.log('Network Servers section found:', networkServersSection);
          const table = networkServersSection.querySelector('table');
          if (table) {
              const thead = table.querySelector('thead tr');
              const tbody = table.querySelector('tbody');
  
              // Add a new column header if it doesn't already exist
              if (!thead.querySelector('.hdr-successPercentage')) {
                  const newHeader = document.createElement('th');
                  newHeader.className = 'hdr-successPercentage';
                  newHeader.innerHTML = '<span class="sort-heading">Success Percentage</span>';
                  thead.appendChild(newHeader);
              }
              const rows = tbody.querySelectorAll('tr');
              rows.forEach(row => {
                  const goodAttemptsCell = row.querySelector('.row-goodAttempts');
                  const badAttemptsCell = row.querySelector('.row-badAttempts');
                  const goodAttempts = parseInt(goodAttemptsCell.textContent.trim(), 10) || 0;
                  const badAttempts = parseInt(badAttemptsCell.textContent.trim(), 10) || 0;
                  const totalAttempts = goodAttempts + badAttempts;
                  const successPercentage = totalAttempts === 0 ? 0 : (goodAttempts / totalAttempts * 100).toFixed(2);
  
                  let percentageCell = row.querySelector('.row-successPercentage');
                  if (!percentageCell) {
                      percentageCell = document.createElement('td');
                      percentageCell.className = 'row-successPercentage';
                      row.appendChild(percentageCell);
                  }
                  percentageCell.textContent = `${successPercentage}%`;
              });
          } else {
              console.log('Table not found in Network Servers section');
          }
      } else {
          console.log('Network Servers section not found');
      }
  }
  function observeForSection() {
      const observer = new MutationObserver((mutations, me) => {
          const networkServersSection = document.querySelector('section.section-wrapper.status-section.network-servers-section');
          if (networkServersSection) {
              addSuccessPercentageColumn();
              me.disconnect();
              observeTabChanges();
          }
      });
  
      observer.observe(document, {
          childList: true,
          subtree: true
      });
  }
  
  function observeTabChanges() {
      const tabs = document.querySelectorAll('.section-wrapper.status-section.network-servers-section .tab-menu-item');
      tabs.forEach(tab => {
          tab.addEventListener('click', () => {
              setTimeout(addSuccessPercentageColumn, 100);
          });
      });
  }
  
  window.addEventListener('load', observeForSection);
  
    
    // Enhance dashboard charts
    function enhanceDashboardCharts() {
      // Find chart containers and add enhancements
      const charts = document.querySelectorAll('[class*="chart"], canvas, svg');
      charts.forEach((chart) => {
        if (!chart.hasAttribute('data-enhance-processed')) {
          chart.setAttribute('data-enhance-processed', 'true');
          
          // Add container styling if needed
          const container = chart.closest('[class*="container"], [class*="wrapper"]');
          if (container) {
            container.style.borderRadius = '8px';
            container.style.overflow = 'hidden';
          }
        }
      });
    }
    
    // General admin page enhancements
    function initAdminEnhancements() {
      console.log('[Enhance] Initializing Mist.com Admin page enhancements');
      
      // Add "Enhanced!" indicator to logo (try multiple times as page loads)
      let attempts = 0;
      const maxAttempts = 10;
      const tryAddIndicator = setInterval(() => {
        attempts++;
        if (addEnhancementIndicator() || attempts >= maxAttempts) {
          clearInterval(tryAddIndicator);
        }
      }, 500);
      
      // Also try immediately
      addEnhancementIndicator();
      
      // Watch for logo element if it's not present yet
      const logoObserver = new MutationObserver(() => {
        if (addEnhancementIndicator()) {
          logoObserver.disconnect();
        }
      });
      
      logoObserver.observe(document.body, {
        childList: true,
        subtree: true
      });
      
      watchNavigationBar();

      // Add keyboard shortcuts helper
      document.addEventListener('keydown', function(e) {
        // Example: Ctrl/Cmd + K for quick search (if not already handled)
        if ((e.ctrlKey || e.metaKey) && e.key === 'k' && !e.target.matches('input, textarea')) {
          const searchInput = document.querySelector('input[type="search"], input[placeholder*="search" i]');
          if (searchInput) {
            e.preventDefault();
            searchInput.focus();
            searchInput.select();
          }
        }
      });
      
      // Enhance data tables
      const tables = document.querySelectorAll('table');
      tables.forEach((table) => {
        if (!table.hasAttribute('data-enhance-processed')) {
          table.setAttribute('data-enhance-processed', 'true');
          
          // Add sticky header if not already present
          const thead = table.querySelector('thead');
          if (thead) {
            thead.style.position = 'sticky';
            thead.style.top = '0';
            thead.style.zIndex = '10';
            thead.style.backgroundColor = '#fff';
          }
        }
      });
    }
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', initMistEnhancements);
    } else {
      initMistEnhancements();
    }
    
    // Re-initialize on hash change (SPA navigation)
    let lastHash = window.location.hash;
    window.addEventListener('hashchange', function() {
      if (window.location.hash !== lastHash) {
        lastHash = window.location.hash;
        setTimeout(() => {
          initMistEnhancements();
          addSiteConfigNavButton();
        }, 500); // Wait for SPA to update
      }
    });
    
    // Also watch for dynamic content loading
    const contentObserver = new MutationObserver(() => {
      initMistEnhancements();
      addSiteConfigNavButton();
    });
    
    contentObserver.observe(document.body, {
      childList: true,
      subtree: true
    });
    
  })();
  /* end-domain */
  
})();

