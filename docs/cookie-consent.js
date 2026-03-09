(function() {
    'use strict';

    var CONSENT_KEY = 'cookie_consent';
    var GA_ID = 'G-FC4RG249V0';
    var ADSENSE_ID = 'ca-pub-1635655844040461';

    function getConsent() {
        try {
            return localStorage.getItem(CONSENT_KEY);
        } catch (e) {
            return null;
        }
    }

    function setConsent(value) {
        try {
            localStorage.setItem(CONSENT_KEY, value);
        } catch (e) {
            // localStorage unavailable
        }
    }

    function loadScript(src, attrs) {
        var script = document.createElement('script');
        script.async = true;
        script.src = src;
        if (attrs) {
            for (var key in attrs) {
                if (attrs.hasOwnProperty(key)) {
                    script.setAttribute(key, attrs[key]);
                }
            }
        }
        document.head.appendChild(script);
    }

    function loadGA() {
        loadScript('https://www.googletagmanager.com/gtag/js?id=' + GA_ID);
        window.dataLayer = window.dataLayer || [];
        function gtag() { window.dataLayer.push(arguments); }
        window.gtag = gtag;
        gtag('js', new Date());
        gtag('config', GA_ID);
    }

    function loadAdSense() {
        if (document.querySelector('meta[name="no-adsense"]')) return;
        loadScript(
            'https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=' + ADSENSE_ID,
            { crossorigin: 'anonymous' }
        );
    }

    function loadAll() {
        loadGA();
        loadAdSense();
    }

    function showBanner() {
        var banner = document.getElementById('cookie-consent-banner');
        if (banner) {
            banner.classList.add('visible');
        }
    }

    function hideBanner() {
        var banner = document.getElementById('cookie-consent-banner');
        if (banner) {
            banner.classList.remove('visible');
            banner.style.display = 'none';
        }
    }

    function onAccept() {
        setConsent('accepted');
        hideBanner();
        loadAll();
    }

    function onReject() {
        setConsent('rejected');
        hideBanner();
    }

    // Initialize on DOM ready
    function init() {
        var consent = getConsent();

        if (consent === 'accepted') {
            loadAll();
            return;
        }

        if (consent === 'rejected') {
            return;
        }

        // No consent recorded yet — show banner
        showBanner();
    }

    // Expose handlers globally for onclick
    window.cookieConsentAccept = onAccept;
    window.cookieConsentReject = onReject;

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
