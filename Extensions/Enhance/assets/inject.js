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

    // Cache for site stats data
    const siteStatsCache = new Map();

    async function fetchSiteStats(siteId) {
      if (!siteId) {
        return null;
      }

      // Return cached data if available and recent (less than 30 seconds old)
      const cached = siteStatsCache.get(siteId);
      if (cached && (Date.now() - cached.timestamp < 30000)) {
        console.log('[Enhance] Using cached site stats for', siteId);
        return cached.data;
      }

      try {
        console.log('[Enhance] Fetching site stats for', siteId);
        const response = await fetch(`https://api.mist.com/api/v1/sites/${siteId}/stats`, {
          credentials: 'include'
        });

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();
        
        // Cache the data
        siteStatsCache.set(siteId, {
          data: data,
          timestamp: Date.now()
        });

        console.log('[Enhance] Site stats fetched and cached:', {
          totalAPs: data.num_ap,
          onlineAPs: data.num_ap_connected
        });

        return data;
      } catch (error) {
        console.warn('[Enhance] Failed to fetch site stats:', error);
        return null;
      }
    }

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
      // Add gear icon before the text
      label.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" style="position:relative;top:2px;margin-right:6px;" width="16" height="16" fill="currentColor" viewBox="0 0 20 20"><path d="M13.562 2.661c-.563-1.209-2.562-1.209-3.124 0-.225.483-.689.812-1.233.889-1.364.188-2.293 1.303-1.996 2.63.07.301.027.617-.154.867-.688.981-2.08 1.058-2.428-.004-.244-.714-.962-1.302-1.784-1.382C2.36 6.451 2 7.428 2 8.25c0 1.051.858 2.003 1.889 2.004C4.82 10.255 6.09 9.732 6.291 9.026c.162-.528.755-.818 1.264-.641.39.132.831-.012 1.04-.385.208-.37.753-.455 1.138-.213.292.185.648.215.962.068 1.063-.514 2.293.294 2.167 1.466-.042.398.22.761.616.828.972.159 2.064-.442 2.064-1.432 0-.764-.436-1.523-1.294-1.738-.598-.15-1.081-.687-1.115-1.301-.043-.775-1.147-.894-1.325-.147zm-3.68 4.554a3 3 0 1 1 5.237 0l.5-.865c.277-.48.945-.59 1.27-.211a3 3 0 0 1 0 3.382c-.285.382-.528.813-.666 1.288.081.345.317.642.654.757a3 3 0 0 1 0 1.683c-.337.115-.573.412-.654.757.139.475.381.906.666 1.288a3 3 0 0 1 0 3.382c-.325.38-.993.27-1.27-.21l-.5-.866a3 3 0 1 1-5.237 0l-.5.866c-.277.48-.945.59-1.27.21a3 3 0 0 1 0-3.382c.285-.382.527-.813.666-1.288-.08-.345-.317-.642-.654-.757a3 3 0 0 1 0-1.683c.337-.115.573-.412.654-.757-.139-.475-.381-.906-.666-1.288a3 3 0 0 1 0-3.382c.325-.38.993-.27 1.27.211l.5.865zm2.118.785a2 2 0 1 0 0 4.001 2 2 0 0 0 0-4.001z"/></svg>Site Config`;

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
      const rowEl = linkEl;

      if (linkEl) {
        const alertsUrl = buildAlertsUrl(orgId, siteId);
        if (alertsUrl) {
          linkEl.href = alertsUrl;
          linkEl.classList.remove('is-disabled');
          linkEl.title = 'View site alarms';
          linkEl.dataset.enhanceState = 'loading';
        } else {
          linkEl.removeAttribute('href');
          linkEl.classList.add('is-disabled');
          linkEl.title = 'Alerts URL unavailable';
          linkEl.dataset.enhanceState = 'idle';
        }
      }

      if (!valueEl) {
        if (rowEl) {
          rowEl.dataset.enhanceState = 'idle';
        }
        return;
      }

      if (!siteId) {
        valueEl.textContent = 'N/A';
        if (rowEl) {
          rowEl.dataset.enhanceState = 'idle';
        }
        return;
      }

      if (panel.dataset.enhanceAlarmSiteId === siteId) {
        return;
      }

      panel.dataset.enhanceAlarmSiteId = siteId;
      valueEl.textContent = 'Loading...';

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
        if (rowEl) {
          rowEl.dataset.enhanceState = total > 0 ? 'alert' : 'ready';
          rowEl.title = total > 0 ? `${total} active alarm${total === 1 ? '' : 's'}` : 'No active alarms';
        }
      } catch (error) {
        console.warn('[Enhance] Failed to load alarm summary:', error);
        valueEl.textContent = '—';
        if (linkEl) {
          linkEl.title = `Failed to load alarm count: ${error.message}`;
        }
        if (rowEl) {
          rowEl.dataset.enhanceState = 'error';
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

      if (!siteId) {
        valueEl.textContent = 'N/A';
        linkEl.removeAttribute('href');
        linkEl.classList.add('is-disabled');
        linkEl.title = 'Site context required';
        linkEl.dataset.enhanceState = 'idle';
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
          linkEl.dataset.enhanceState = 'ready';
        } else {
          linkEl.removeAttribute('href');
          linkEl.classList.add('is-disabled');
          linkEl.title = 'Marvis Minis SLE link unavailable';
          linkEl.dataset.enhanceState = 'idle';
        }
      } else {
        valueEl.textContent = '—';
        const fallbackUrl = buildMarvisMiniUrl(orgId, siteId);
        if (fallbackUrl) {
          linkEl.href = fallbackUrl;
          linkEl.classList.remove('is-disabled');
          linkEl.title = 'View Marvis Minis SLE details';
          linkEl.dataset.enhanceState = 'ready';
        } else {
          linkEl.removeAttribute('href');
          linkEl.classList.add('is-disabled');
          linkEl.title = 'Marvis Minis SLE link unavailable';
          linkEl.dataset.enhanceState = 'idle';
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
      const originalContent = section.querySelector('.map-content');

      if (!mapWrap || !originalContent) {
        return false;
      }

      if (!originalContent.dataset.enhanceHidden) {
        originalContent.dataset.enhanceHidden = 'true';
        originalContent.style.display = 'none';
      }

      section.classList.add('enhance-map-layout');
      mapWrap.classList.add('enhance-map-container');

      let panel = section.querySelector('[data-enhance-site-panel]');
      if (!panel) {
        panel = document.createElement('div');
        panel.className = 'enhance-site-panel';
        panel.setAttribute('data-enhance-site-panel', 'true');
        if (mapWrap.nextSibling) {
          section.insertBefore(panel, mapWrap.nextSibling);
        } else {
          section.appendChild(panel);
        }
      }

      let titleEl = panel.querySelector('.map-name');
      if (!titleEl) {
        titleEl = document.createElement('div');
        titleEl.className = 'map-name';
        panel.appendChild(titleEl);
      }

      const sourceName = originalContent.querySelector('.map-name');
      if (sourceName) {
        titleEl.textContent = sourceName.textContent;
        titleEl.setAttribute('title', sourceName.getAttribute('title') || sourceName.textContent);
      }

      let summaryEl = panel.querySelector('.map-summary');
      if (!summaryEl) {
        summaryEl = document.createElement('div');
        summaryEl.className = 'map-summary';
        summaryEl.setAttribute('data-enhance-summary', 'true');
        panel.appendChild(summaryEl);
      }

      const sourceSummary = originalContent.querySelector('.map-summary');
      if (sourceSummary) {
        summaryEl.innerHTML = sourceSummary.innerHTML;
      } else {
        summaryEl.innerHTML = '';
      }

      let insightsList = panel.querySelector('[data-enhance-insights-list]');
      if (!insightsList) {
        insightsList = document.createElement('div');
        insightsList.className = 'enhance-insights-list';
        insightsList.setAttribute('data-enhance-insights-list', 'true');
        panel.appendChild(insightsList);
      }

      let alarmRow = panel.querySelector('[data-enhance-alarm-link]');
      if (!alarmRow) {
        alarmRow = document.createElement('a');
        alarmRow.className = 'enhance-insight-row';
        alarmRow.setAttribute('data-enhance-alarm-link', '');
        alarmRow.dataset.enhanceState = 'loading';
        alarmRow.innerHTML = `
          <div class="enhance-insight-leading">
            <span class="enhance-insight-icon" aria-hidden="true">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <path d="M12 9v4"></path>
                <path d="M12 17h.01"></path>
                <path d="M10.29 3.86 1.82 18a1.5 1.5 0 0 0 1.29 2.25h17.78A1.5 1.5 0 0 0 22.18 18L13.71 3.86a1.5 1.5 0 0 0-2.42 0z"></path>
              </svg>
            </span>
            <div class="enhance-insight-content">
              <span class="enhance-insight-label">Alarms</span>
              <span class="enhance-insight-subLabel">Active alerts for this site</span>
            </div>
          </div>
          <span class="enhance-insight-value" data-enhance-alarm-count>Loading...</span>
        `;
        insightsList.appendChild(alarmRow);
      }

      let marvisRow = panel.querySelector('[data-enhance-marvis-link]');
      if (!marvisRow) {
        marvisRow = document.createElement('a');
        marvisRow.className = 'enhance-insight-row';
        marvisRow.setAttribute('data-enhance-marvis-link', '');
        marvisRow.dataset.enhanceState = 'loading';
        marvisRow.innerHTML = `
          <div class="enhance-insight-leading">
            <span class="enhance-insight-icon" aria-hidden="true">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="7" width="18" height="12" rx="2"></rect>
                <circle cx="9" cy="13" r="1"></circle>
                <circle cx="15" cy="13" r="1"></circle>
                <path d="M9 3v2"></path>
                <path d="M15 3v2"></path>
                <path d="M5 7V5"></path>
                <path d="M19 7V5"></path>
              </svg>
            </span>
            <div class="enhance-insight-content">
              <span class="enhance-insight-label">Marvis Minis SLE</span>
              <span class="enhance-insight-subLabel">Session insight (past 24h)</span>
            </div>
          </div>
          <span class="enhance-insight-value" data-enhance-marvis-value>Loading...</span>
        `;
        insightsList.appendChild(marvisRow);
      }

      const { orgId, siteId } = getOrgAndSiteIds();
      updateAlarmSummary(panel, orgId, siteId);
      updateMarvisSummary(panel, orgId, siteId);

      // Process the summary table to add site health percentage
      // Use setTimeout to ensure DOM is fully parsed after innerHTML assignment
      // Try multiple times in case content loads asynchronously
      let retryCount = 0;
      const maxRetries = 10;
      const tryEnhance = async () => {
        // Try enhancing summaryEl
        const success = await enhanceMapSummaryTable(summaryEl, sourceSummary);
        if (!success && retryCount < maxRetries) {
          retryCount++;
          setTimeout(tryEnhance, 300);
        }
      };
      setTimeout(tryEnhance, 200);

      const summaryElement = sourceSummary;
      if (summaryElement && !summaryElement.dataset.enhanceSummaryObserved) {
        const summaryObserver = new MutationObserver(() => {
          const ids = getOrgAndSiteIds();
          summaryEl.innerHTML = summaryElement.innerHTML;
          // Use setTimeout to ensure DOM is fully parsed after innerHTML assignment
          // Try multiple times in case content loads asynchronously
          let retryCount2 = 0;
          const maxRetries2 = 5;
          const tryEnhance2 = async () => {
            const success = await enhanceMapSummaryTable(summaryEl, summaryElement);
            if (!success && retryCount2 < maxRetries2) {
              retryCount2++;
              setTimeout(tryEnhance2, 300);
            }
          };
          setTimeout(tryEnhance2, 200);
          updateMarvisSummary(panel, ids.orgId, ids.siteId);
        });

        summaryObserver.observe(summaryElement, {
          childList: true,
          subtree: true
        });

        summaryElement.dataset.enhanceSummaryObserved = 'true';
      }

      return true;
    }

    async function enhanceMapSummaryTable(summaryEl, sourceSummary = null) {
      if (!summaryEl) {
        console.log('[Enhance] enhanceMapSummaryTable: summaryEl is null');
        return false;
      }

      // Get siteId from the page
      const { siteId } = getOrgAndSiteIds();
      if (!siteId) {
        console.log('[Enhance] enhanceMapSummaryTable: No siteId found');
        return false;
      }

      // Find the table in the map-summary
      const table = summaryEl.querySelector('table') || summaryEl.querySelector('.css-table');
      if (!table) {
        console.log('[Enhance] enhanceMapSummaryTable: No table found in summaryEl');
        return false;
      }

      // Find the row that contains AP information by looking for the "insights-AccessPoints-total" span
      let totalSpan = summaryEl.querySelector('.insights-AccessPoints-total');
      if (!totalSpan && sourceSummary) {
        totalSpan = sourceSummary.querySelector('.insights-AccessPoints-total');
      }
      if (!totalSpan) {
        // Try case-insensitive search
        const allSpans = summaryEl.querySelectorAll('span');
        for (const span of allSpans) {
          if (span.className && /insights-AccessPoints-total/i.test(span.className)) {
            totalSpan = span;
            break;
          }
        }
      }

      // Find the row containing the AP information
      let row = null;
      if (totalSpan) {
        row = totalSpan.closest('tr') || totalSpan.closest('.css-table-row');
        if (!row) {
          let parent = totalSpan.parentElement;
          while (parent && parent !== summaryEl) {
            if (parent.tagName === 'TR' || parent.classList.contains('css-table-row')) {
              row = parent;
              break;
            }
            parent = parent.parentElement;
          }
        }
      }

      // If we can't find the row by span, try to find any row in the table
      if (!row) {
        const tbody = table.querySelector('tbody');
        if (tbody) {
          const rows = tbody.querySelectorAll('tr, .css-table-row');
          // Try to find a row that might contain AP info (look for numbers)
          for (const r of rows) {
            const text = r.textContent || '';
            if (/AccessPoint|AP|accesspoint/i.test(text) || /\d+\s*(Total|Online|Connected)/i.test(text)) {
              row = r;
              break;
            }
          }
          // If still no row, use the first data row
          if (!row && rows.length > 0) {
            row = rows[0];
          }
        }
      }

      if (!row) {
        console.log('[Enhance] enhanceMapSummaryTable: Could not find row in table');
        return false;
      }

      // Check if we've already added the health column
      if (row.querySelector('[data-enhance-site-health]')) {
        console.log('[Enhance] enhanceMapSummaryTable: Health column already exists');
        return true; // Success - already enhanced
      }

      // Get site stats from cache or fetch if not available
      let data = null;
      const cached = siteStatsCache.get(siteId);
      if (cached && (Date.now() - cached.timestamp < 30000)) {
        console.log('[Enhance] enhanceMapSummaryTable: Using cached site stats');
        data = cached.data;
      } else {
        // Fetch if not cached or cache is stale
        try {
          data = await fetchSiteStats(siteId);
          if (!data) {
            console.warn('[Enhance] enhanceMapSummaryTable: Failed to get site stats');
            return false;
          }
        } catch (error) {
          console.warn('[Enhance] enhanceMapSummaryTable: Failed to fetch site stats:', error);
          return false;
        }
      }

      const totalAPs = data.num_ap || 0;
      const onlineAPs = data.num_ap_connected || 0;

      console.log('[Enhance] enhanceMapSummaryTable: API data - total APs:', totalAPs, 'online APs:', onlineAPs);

      // Calculate percentage
      const percentage = totalAPs > 0 ? Math.round((onlineAPs / totalAPs) * 100) : 0;

      // Determine color class based on percentage
      let healthClass = 'enhance-site-health-red';
      if (percentage >= 95) {
        healthClass = 'enhance-site-health-green';
      } else if (percentage >= 85) {
        healthClass = 'enhance-site-health-yellow';
      }

      // Find the first cell in the row
      const cells = row.querySelectorAll('td, .css-table-cell');
      if (cells.length === 0) {
        console.log('[Enhance] enhanceMapSummaryTable: No cells found in row');
        return false;
      }

      const firstCell = cells[0];
      const cellTagName = firstCell.tagName.toLowerCase();

      // Create the new health percentage cell
      const healthCell = document.createElement(cellTagName === 'td' ? 'td' : (cellTagName === 'th' ? 'th' : 'div'));
      
      // Preserve existing classes from firstCell
      if (firstCell.className) {
        healthCell.className = firstCell.className;
      }
      healthCell.classList.add('enhance-site-health-cell');
      healthCell.setAttribute('data-enhance-site-health', 'true');
      healthCell.classList.add(healthClass);
      healthCell.textContent = `${percentage}%`;
      healthCell.style.textAlign = 'center';
      healthCell.style.fontWeight = '500';

      // Insert as the first cell
      row.insertBefore(healthCell, firstCell);
      
      console.log('[Enhance] enhanceMapSummaryTable: Successfully added health cell with', percentage + '%', healthClass);

      // Also add a header cell if there's a header row
      const thead = table.querySelector('thead');
      const headerRow = thead ? thead.querySelector('tr') : null;
      if (headerRow) {
        const headerCells = headerRow.querySelectorAll('th, .css-table-cell');
        if (headerCells.length > 0 && !headerRow.querySelector('[data-enhance-site-health-header]')) {
          const firstHeaderCell = headerCells[0];
          const healthHeader = document.createElement(firstHeaderCell.tagName === 'TH' ? 'th' : 'div');
          healthHeader.className = firstHeaderCell.className + ' enhance-site-health-header';
          healthHeader.setAttribute('data-enhance-site-health-header', 'true');
          healthHeader.textContent = 'Site Health';
          healthHeader.style.textAlign = 'center';
          headerRow.insertBefore(healthHeader, firstHeaderCell);
        }
      }

      // Adjust table layout to ensure all columns fit on the same row
      if (table.style.tableLayout !== 'fixed') {
        table.style.tableLayout = 'auto';
      }
      
      return true; // Success
    }

    // Initialize Mist.com enhancements
    function initMistEnhancements() {
      const currentUrl = window.location.href;
      
      // Fetch site stats early if we have a siteId
      const { siteId } = getOrgAndSiteIds();
      if (siteId) {
        fetchSiteStats(siteId).catch(err => {
          console.warn('[Enhance] Failed to pre-fetch site stats:', err);
        });
      }
      
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
        
        // Pre-fetch site stats on page load
        fetchSiteStats(siteId).catch(err => {
          console.warn('[Enhance] Failed to pre-fetch site stats:', err);
        });
      }
      
      observeForSection();

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
        observeForSection();
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
        margin-left: 1px;
        padding: 2px 8px;
        background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
        color: white;
        font-size: 11px;
        font-weight: 600;
        border-radius: 4px;
        border: 1px solid #e0e9f2;
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
    let networkServersSectionObserver = null;
    let networkServersTableObserver = null;
    let networkServersTableNode = null;
    let successPercentageRetryTimer = null;
    let suppressNetworkServersObserver = false;

    function addSuccessPercentageColumn() {
      const networkServersSection = document.querySelector('section.section-wrapper.status-section.network-servers-section');
      if (!networkServersSection) {
        return false;
      }

      const table = networkServersSection.querySelector('table');
      if (!table) {
        scheduleSuccessPercentageRetry();
        return false;
      }

      const headerRow = table.querySelector('thead tr');
      const tbody = table.querySelector('tbody');

      if (!headerRow || !tbody) {
        scheduleSuccessPercentageRetry();
        return false;
      }

      suppressNetworkServersObserver = true;

      try {
        if (!headerRow.querySelector('.hdr-successPercentage')) {
          const newHeader = document.createElement('th');
          newHeader.className = 'hdr-successPercentage';
          newHeader.innerHTML = '<span class="sort-heading">Success Percentage</span>';
          headerRow.appendChild(newHeader);
        }

        const rows = tbody.querySelectorAll('tr');
        if (!rows.length) {
          scheduleSuccessPercentageRetry();
          return false;
        }

        rows.forEach((row) => {
          const goodAttemptsCell = row.querySelector('.row-goodAttempts');
          const badAttemptsCell = row.querySelector('.row-badAttempts');

          if (!goodAttemptsCell || !badAttemptsCell) {
            return;
          }

          const goodAttempts = parseInt(goodAttemptsCell.textContent.trim(), 10) || 0;
          const badAttempts = parseInt(badAttemptsCell.textContent.trim(), 10) || 0;
          const totalAttempts = goodAttempts + badAttempts;
          const successPercentage = totalAttempts === 0 ? 0 : ((goodAttempts / totalAttempts) * 100).toFixed(2);

          let percentageCell = row.querySelector('.row-successPercentage');
          if (!percentageCell) {
            percentageCell = document.createElement('td');
            percentageCell.className = 'row-successPercentage';
            row.appendChild(percentageCell);
          }
          percentageCell.textContent = `${successPercentage}%`;
        });

        return true;
      } finally {
        setTimeout(() => {
          suppressNetworkServersObserver = false;
        }, 0);
      }
    }

    function scheduleSuccessPercentageRetry() {
      if (successPercentageRetryTimer) {
        return;
      }

      // # Reason: Mist dashboard hydrates asynchronously; retry until the table is populated.
      successPercentageRetryTimer = setTimeout(() => {
        successPercentageRetryTimer = null;
        addSuccessPercentageColumn();
      }, 250);
    }

    function observeForSection() {
      const didEnhance = addSuccessPercentageColumn();
      const networkServersSection = document.querySelector('section.section-wrapper.status-section.network-servers-section');

      if (networkServersSection) {
        observeTabChanges(networkServersSection);
        observeTableChanges(networkServersSection);
      }

      if (didEnhance || networkServersSection) {
        disconnectSectionObserver();
        return true;
      }

      if (!networkServersSectionObserver) {
        networkServersSectionObserver = new MutationObserver(() => {
          if (observeForSection()) {
            disconnectSectionObserver();
          }
        });

        networkServersSectionObserver.observe(document.body, {
          childList: true,
          subtree: true
        });
      }

      return false;
    }

    function disconnectSectionObserver() {
      if (networkServersSectionObserver) {
        networkServersSectionObserver.disconnect();
        networkServersSectionObserver = null;
      }
    }

    function observeTableChanges(networkServersSection) {
      const table = networkServersSection.querySelector('table');
      const tbody = table ? table.querySelector('tbody') : null;

      if (!tbody) {
        return;
      }

      if (networkServersTableObserver && networkServersTableNode !== tbody) {
        // # Reason: Mist may swap out the tbody element when refreshing data.
        networkServersTableObserver.disconnect();
        networkServersTableObserver = null;
        networkServersTableNode = null;
      }

      if (!networkServersTableObserver) {
        networkServersTableObserver = new MutationObserver(() => {
          if (suppressNetworkServersObserver) {
            return;
          }
          addSuccessPercentageColumn();
        });

        networkServersTableObserver.observe(tbody, {
          childList: true,
          subtree: true,
          characterData: true
        });

        networkServersTableNode = tbody;
      }
    }

    function observeTabChanges(networkServersSection) {
      const tabs = networkServersSection.querySelectorAll('.tab-menu-item');
      tabs.forEach((tab) => {
        if (tab.dataset.enhanceSuccessListener === 'true') {
          return;
        }

        tab.dataset.enhanceSuccessListener = 'true';
        tab.addEventListener('click', () => {
          setTimeout(addSuccessPercentageColumn, 100);
        });
      });
    }
  
    
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
    
    let lastEnhancementRun = 0;
    const ENHANCEMENT_DEBOUNCE_MS = 750;

    // Also watch for dynamic content loading
    const contentObserver = new MutationObserver(() => {
      const now = Date.now();
      if (now - lastEnhancementRun < ENHANCEMENT_DEBOUNCE_MS) {
        return;
      }
      lastEnhancementRun = now;

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

