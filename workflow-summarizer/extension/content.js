// Breadcrumbs: DOM click capture

function getSelector(el) {
  if (el.id) {
    return `#${el.id}`;
  }

  if (el.getAttribute('data-testid')) {
    return `[data-testid="${el.getAttribute('data-testid')}"]`;
  }

  if (el.getAttribute('aria-label')) {
    return `[aria-label="${el.getAttribute('aria-label')}"]`;
  }

  let path = [];
  let current = el;

  while (current && current !== document.body && path.length < 4) {
    let selector = current.tagName.toLowerCase();

    if (current.className && typeof current.className === 'string') {
      const classes = current.className.trim().split(/\s+/).slice(0, 2);
      if (classes.length && classes[0]) {
        selector += '.' + classes.join('.');
      }
    }

    path.unshift(selector);
    current = current.parentElement;
  }

  return path.join(' > ');
}

function getElementInfo(el) {
  return {
    tag: el.tagName.toLowerCase(),
    id: el.id || null,
    classes: el.className || null,
    text: (el.innerText || el.value || '').slice(0, 100).trim(),
    href: el.href || el.closest('a')?.href || null,
    role: el.getAttribute('role'),
    ariaLabel: el.getAttribute('aria-label'),
    placeholder: el.placeholder || null,
    selector: getSelector(el),
    inputType: el.type || null
  };
}

function sendEvent(data) {
  chrome.runtime.sendMessage({ type: 'BREADCRUMBS_EVENT', data });
}

document.addEventListener('click', (e) => {
  sendEvent({
    type: 'click',
    timestamp: Date.now(),
    url: window.location.href,
    title: document.title,
    x: e.clientX,
    y: e.clientY,
    element: getElementInfo(e.target)
  });
}, true);

document.addEventListener('submit', (e) => {
  const form = e.target;
  sendEvent({
    type: 'submit',
    timestamp: Date.now(),
    url: window.location.href,
    title: document.title,
    formAction: form.action,
    formMethod: form.method,
    element: getElementInfo(form)
  });
}, true);

document.addEventListener('keydown', (e) => {
  if (!['Enter', 'Tab', 'Escape'].includes(e.key)) return;

  sendEvent({
    type: 'keypress',
    timestamp: Date.now(),
    url: window.location.href,
    title: document.title,
    key: e.key,
    element: getElementInfo(e.target)
  });
}, true);

console.log('[Breadcrumbs] DOM capture active');
