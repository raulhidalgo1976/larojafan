/* Optional Google Analytics: loaded only after affirmative consent. */
(function () {
  'use strict';
  const measurementId = '__GA4_MEASUREMENT_ID__';
  const key = 'larojafan_analytics_consent_v1';
  function getChoice() { try { return localStorage.getItem(key); } catch (_) { return null; } }
  function setChoice(value) { try { localStorage.setItem(key, value); } catch (_) {} }
  let started = false;
  function startAnalytics() {
    if (started) return;
    started = true;
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    window.gtag('js', new Date());
    window.gtag('config', measurementId);
    const script = document.createElement('script');
    script.async = true;
    script.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(measurementId);
    document.head.appendChild(script);
    document.addEventListener('click', function (event) {
      const link = event.target.closest('a[href]');
      if (!link) return;
      try {
        const url = new URL(link.href, location.href);
        if (/^(www\.)?amazon\./i.test(url.hostname) && url.searchParams.get('tag') === '__AMAZON_TAG__') {
          window.gtag('event', 'affiliate_click', {affiliate_partner: 'amazon', link_url: url.href});
        }
      } catch (_) {}
    });
  }
  function showBanner() {
    if (document.getElementById('analytics-consent')) return;
    const banner = document.createElement('aside');
    banner.id = 'analytics-consent';
    banner.setAttribute('aria-label', 'Analytics cookie choice');
    banner.innerHTML = '<p>May we use optional Google Analytics cookies to understand website visits? <a href="/privacy/">Privacy details</a>.</p><div><button type="button" id="analytics-reject">Reject optional analytics</button><button type="button" id="analytics-accept">Accept analytics</button></div>';
    document.body.appendChild(banner);
    function choose(choice) { setChoice(choice); banner.remove(); if (choice === 'accepted') startAnalytics(); else if (window.gtag) location.reload(); }
    document.getElementById('analytics-reject').addEventListener('click', () => choose('rejected'));
    document.getElementById('analytics-accept').addEventListener('click', () => choose('accepted'));
  }
  function ready() {
    if (getChoice() === 'accepted') startAnalytics();
    else if (getChoice() !== 'rejected') showBanner();
    const settings = document.getElementById('cookie-settings');
    if (settings) settings.addEventListener('click', showBanner);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', ready); else ready();
}());
