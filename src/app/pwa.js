/* PWA install and update checks. Safe in the standalone HTML download too. */
(() => {
  if (!('serviceWorker' in navigator) || !/^https?:$/.test(location.protocol)) return;
  let hasController = Boolean(navigator.serviceWorker.controller);
  let pendingUpdate = false;
  let reloading = false;
  let lastCheck = 0;
  const isPracticing = () => ['learnScreen', 'studioScreen'].some(id => {
    const screen = document.getElementById(id);
    return screen && !screen.hidden;
  });
  const applyUpdateWhenIdle = () => {
    if (!pendingUpdate || reloading || document.hidden || isPracticing()) return;
    reloading = true;
    location.reload();
  };
  const checkForUpdates = async () => {
    if (document.hidden || Date.now() - lastCheck < 60000) return;
    lastCheck = Date.now();
    try {
      const registration = await navigator.serviceWorker.getRegistration('./');
      if (!registration) return;
      await registration.update();
      if (navigator.serviceWorker.controller) {
        navigator.serviceWorker.controller.postMessage({ type: 'ARIA_CHECK_UPDATE' });
      }
    } catch (_) {
      // No connectivity or browser restrictions must not interrupt practice.
    }
  };
  navigator.serviceWorker.addEventListener('message', event => {
    if (event.data && event.data.type === 'ARIA_UPDATE_AVAILABLE') {
      pendingUpdate = true;
      applyUpdateWhenIdle();
    }
  });
  navigator.serviceWorker.addEventListener('controllerchange', () => {
    if (hasController) {
      pendingUpdate = true;
      applyUpdateWhenIdle();
    }
    hasController = true;
  });
  navigator.serviceWorker.register('./sw.js', { scope: './', updateViaCache: 'none' })
    .then(checkForUpdates)
    .catch(() => {});
  window.addEventListener('pageshow', checkForUpdates);
  window.addEventListener('focus', checkForUpdates);
  document.addEventListener('visibilitychange', () => {
    if (!document.hidden) {
      applyUpdateWhenIdle();
      checkForUpdates();
    }
  });
  const home = document.getElementById('courseScreen');
  if (home) new MutationObserver(applyUpdateWhenIdle)
    .observe(home, { attributes: true, attributeFilter: ['hidden'] });
  setInterval(checkForUpdates, 30 * 60 * 1000);
})();
