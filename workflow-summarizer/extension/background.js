// Minimal background worker - just keeps extension alive
chrome.runtime.onInstalled.addListener(() => {
  console.log('[Breadcrumbs] Extension installed');
});
