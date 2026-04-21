/**
 * PBMS Dashboard - Minimal Mode Detection & Enforcement
 * 
 * This IIFE runs on BOTH the login page (assets_frontend) and backend (assets_backend).
 * It captures the ?minimal=1 URL parameter, persists it in sessionStorage,
 * and enforces UI lockdown (hiding navbars) for dashboard-only users.
 */
(function () {
    'use strict';

    const DASHBOARD_ACTION_TAG = 'pbms_dashboard_main';

    function isLoginPage() {
        const path = window.location.pathname;
        return path.includes('/web/login') || path.includes('/web/signup') || path.includes('/web/reset_password');
    }

    function getSessionInfo() {
        return window.odoo?.__session_info__ || window.odoo?.session_info || null;
    }

    function runEnforcement() {
        const urlParams = new URLSearchParams(window.location.search);

        // 1. Capture URL flag on any page (including login)
        if (urlParams.get('minimal') === '1') {
            sessionStorage.setItem('o_minimal_view', '1');
        } else if (urlParams.get('minimal') === '0') {
            sessionStorage.removeItem('o_minimal_view');
        }

        // Don't enforce UI changes on login/signup pages
        if (isLoginPage()) {
            return;
        }

        const session = getSessionInfo();
        const isMinimal = sessionStorage.getItem('o_minimal_view') === '1';

        // 2. Detect standalone dashboard user on wrong URL
        if (session && session.is_dashboard_standalone && !isMinimal) {
            sessionStorage.setItem('o_portal_mismatch', '1');
        }

        // 3. Apply UI lockdown if in minimal mode
        if (isMinimal || sessionStorage.getItem('o_portal_mismatch') === '1') {
            document.body.classList.add('o_minimal_view');

            // Hide all navbar elements
            var selectors = ['.o_main_navbar', '.o_navbar', 'header', '.o_header'];
            for (var i = 0; i < selectors.length; i++) {
                var el = document.querySelector(selectors[i]);
                if (el) {
                    el.style.display = 'none';
                    el.style.visibility = 'hidden';
                    el.style.height = '0';
                    el.style.overflow = 'hidden';
                }
            }

            // Lock navigation to dashboard action
            // Use the client action tag (not XML ID) — Odoo resolves tags in the hash
            var currentHash = window.location.hash || '';
            if (!currentHash || !currentHash.includes(DASHBOARD_ACTION_TAG)) {
                window.location.hash = '#action=' + DASHBOARD_ACTION_TAG;
            }
        }
    }

    // Run immediately
    runEnforcement();

    // Re-run periodically to counter Odoo's dynamic navbar rendering
    setInterval(runEnforcement, 250);
})();
