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

    function buildAlertsUrl(orgId, siteId) {
      if (!orgId) {
        return null;
      }

      if (siteId) {
        return `https://manage.mist.com/admin/?org_id=${orgId}#!alerts/${siteId}`;
      }

      return `https://manage.mist.com/admin/?org_id=${orgId}#!alerts`;
    }

    async function updateAlarmSummary(panel, orgId, siteId) {
      const valueEl = panel.querySelector('[data-enhance-alarm-count]');
      const linkEl = panel.querySelector('[data-enhance-alarm-link]');

      if (linkEl) {
        const alertsUrl = buildAlertsUrl(orgId, siteId);
        if (alertsUrl) {
          linkEl.href = alertsUrl;
          linkEl.classList.remove('is-disabled');
          linkEl.title = 'View site alarms';
        } else {
          linkEl.removeAttribute('href');
          linkEl.classList.add('is-disabled');
          linkEl.title = 'Alerts URL unavailable';
        }
      }

      if (!valueEl) {
        return;
      }

      if (!siteId) {
        valueEl.textContent = 'N/A';
        return;
      }

      if (panel.dataset.enhanceAlarmSiteId === siteId) {
        return;
      }

      panel.dataset.enhanceAlarmSiteId = siteId;
      valueEl.textContent = '...';

      try {
        const response = await fetch(`https://api.mist.com/api/v1/sites/${siteId}/alarms/count`, {
          credentials: 'include'
        });

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();
        let total = 0;

        if (typeof data.total === 'number') {
          total = data.total;
        } else if (Array.isArray(data.results)) {
          total = data.results.reduce((sum, item) => sum + (item.count || 0), 0);
        }

        valueEl.textContent = total;
      } catch (error) {
        console.warn('[Enhance] Failed to load alarm summary:', error);
        valueEl.textContent = '—';
        if (linkEl) {
          linkEl.title = `Failed to load alarm count: ${error.message}`;
        }
      }
    }

    function buildMarvisMiniUrl(orgId, siteId, rawHref = null) {
      if (!orgId) {
        return null;
      }

      if (rawHref) {
        const cleaned = rawHref.trim();
        if (/^https?:\/\//i.test(cleaned)) {
          return cleaned;
        }
        const fragment = cleaned.startsWith('#') ? cleaned : `#!${cleaned.replace(/^!+/, '')}`;
        return `https://manage.mist.com/admin/?org_id=${orgId}${fragment}`;
      }

      if (!siteId) {
        return null;
      }

      const params = new URLSearchParams({
        scopeType: 'site',
        scopeId: siteId,
        site: siteId,
        shortName: 'today'
      });

      return `https://manage.mist.com/admin/?org_id=${orgId}#!marvisMiniSLE?${params.toString()}`;
    }

    function extractMarvisMiniMetric() {
      const links = Array.from(document.querySelectorAll('a[href*="marvisMiniSLE"]'));

      for (const link of links) {
        if (/Network Services/i.test(link.textContent || '')) {
          const cell = link.closest('.css-table-cell') || link.parentElement;
          let valueText = null;

          if (cell) {
            const valueEl = cell.querySelector('.metricValue .value');
            if (valueEl) {
              valueText = valueEl.textContent.trim();
            }
          }

          return {
            valueText,
            href: link.getAttribute('href') || null
          };
        }
      }

      return null;
    }

    function updateMarvisSummary(panel, orgId, siteId) {
      const linkEl = panel.querySelector('[data-enhance-marvis-link]');
      const valueEl = panel.querySelector('[data-enhance-marvis-value]');

      if (!linkEl || !valueEl) {
        return;
      }

      const metric = extractMarvisMiniMetric();

      if (metric) {
        valueEl.textContent = metric.valueText || '—';
        const resolvedUrl = buildMarvisMiniUrl(orgId, siteId, metric.href);
        if (resolvedUrl) {
          linkEl.href = resolvedUrl;
          linkEl.classList.remove('is-disabled');
          linkEl.title = 'View Marvis Minis SLE details';
        } else {
          linkEl.removeAttribute('href');
          linkEl.classList.add('is-disabled');
          linkEl.title = 'Marvis Minis SLE link unavailable';
        }
      } else {
        valueEl.textContent = '—';
        const fallbackUrl = buildMarvisMiniUrl(orgId, siteId);
        if (fallbackUrl) {
          linkEl.href = fallbackUrl;
          linkEl.classList.remove('is-disabled');
          linkEl.title = 'View Marvis Minis SLE details';
        } else {
          linkEl.removeAttribute('href');
          linkEl.classList.add('is-disabled');
          linkEl.title = 'Marvis Minis SLE link unavailable';
        }
      }

      panel.dataset.enhanceMarvisSiteId = siteId || '';
    }

    function enhanceSiteOverviewPanel() {
      const section = document.querySelector('section.section-wrapper');
      if (!section) {
        return false;
      }

      const mapWrap = section.querySelector('.map-wrap');
      const mapContent = section.querySelector('.map-content');

      if (!mapWrap || !mapContent) {
        return false;
      }

      section.classList.add('enhance-map-layout');
      mapWrap.classList.add('enhance-map-container');
      mapContent.classList.add('enhance-site-panel');

      let insightsList = mapContent.querySelector('[data-enhance-insights-list]');
      if (!insightsList) {
        insightsList = document.createElement('div');
        insightsList.className = 'enhance-insights-list';
        insightsList.setAttribute('data-enhance-insights-list', 'true');
        mapContent.appendChild(insightsList);
      }

      let alarmRow = mapContent.querySelector('[data-enhance-alarm-link]');
      if (!alarmRow) {
        alarmRow = document.createElement('a');
        alarmRow.className = 'enhance-insight-row';
        alarmRow.setAttribute('data-enhance-alarm-link', '');
        alarmRow.innerHTML = `
          <span class="enhance-insight-label">Alarms</span>
          <span class="enhance-insight-value" data-enhance-alarm-count>—</span>
        `;
        insightsList.appendChild(alarmRow);
      }

      let marvisRow = mapContent.querySelector('[data-enhance-marvis-link]');
      if (!marvisRow) {
        marvisRow = document.createElement('a');
        marvisRow.className = 'enhance-insight-row';
        marvisRow.setAttribute('data-enhance-marvis-link', '');
        marvisRow.innerHTML = `
          <span class="enhance-insight-label">Marvis Minis SLE</span>
          <span class="enhance-insight-value" data-enhance-marvis-value>—</span>
        `;
        insightsList.appendChild(marvisRow);
      }

      const { orgId, siteId } = getOrgAndSiteIds();
      updateAlarmSummary(mapContent, orgId, siteId);
      updateMarvisSummary(mapContent, orgId, siteId);

      const summaryElement = mapContent.querySelector('.map-summary');
      if (summaryElement && !summaryElement.dataset.enhanceSummaryObserved) {
        const summaryObserver = new MutationObserver(() => {
          const ids = getOrgAndSiteIds();
          updateMarvisSummary(mapContent, ids.orgId, ids.siteId);
        });

        summaryObserver.observe(summaryElement, {
          childList: true,
          subtree: true
        });

        summaryElement.dataset.enhanceSummaryObserved = 'true';
      }

      return true;
    }

    // Initialize Mist.com enhancements
    function initMistEnhancements() {
      const currentUrl = window.location.href;
      addSiteConfigNavButton();
      enhanceSiteOverviewPanel();
      
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
        enhanceSiteOverviewPanel();
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
        enhanceSiteOverviewPanel();
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
      enhanceSiteOverviewPanel();

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
      enhanceSiteOverviewPanel();
    });
    
    contentObserver.observe(document.body, {
      childList: true,
      subtree: true
    });
    
  })();
  /* end-domain */
  
})();

