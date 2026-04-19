// Background service worker - handles fetches to localhost (not subject to loopback restrictions)
chrome.runtime.onInstalled.addListener(() => {
  console.log('[Breadcrumbs] Extension installed');
});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type !== 'BREADCRUMBS_EVENT') return;

  fetch('http://127.0.0.1:8000/event', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(message.data)
  }).then(r => {
    console.log('[Breadcrumbs] sent', message.data.type, r.status);
    sendResponse({ ok: true });
  }).catch(err => {
    console.error('[Breadcrumbs] send failed:', err.message);
    sendResponse({ ok: false });
  });

  return true; // keep message channel open for async response
});
