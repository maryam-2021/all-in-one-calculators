(function () {
  'use strict';

  const routeAliases = {
    '/mortgage-calculator': { loan: 'amount', rate: 'rate', years: 'term', down: 'down' }
  };

  function controls() {
    return Array.from(document.querySelectorAll('.calc-form input[id], .calc-form select[id], .calc-form textarea[id]'));
  }

  function parameterName(control) {
    const aliases = routeAliases[window.location.pathname] || {};
    return control.dataset.shareParam || aliases[control.id] || control.id;
  }

  function buildShareUrl() {
    const url = new URL(window.location.origin + window.location.pathname);
    controls().forEach((control) => {
      const value = control.type === 'checkbox' ? (control.checked ? '1' : '0') : String(control.value || '').trim();
      if (value !== '') url.searchParams.set(parameterName(control), value);
    });
    return url.toString();
  }

  function applyUrlParameters() {
    const params = new URLSearchParams(window.location.search);
    let applied = 0;
    controls().forEach((control) => {
      const value = params.get(parameterName(control));
      if (value === null) return;
      if (control.type === 'checkbox') control.checked = value === '1' || value === 'true';
      else control.value = value;
      control.dispatchEvent(new Event('input', { bubbles: true }));
      control.dispatchEvent(new Event('change', { bubbles: true }));
      applied += 1;
    });
    return applied;
  }

  function resultSummary() {
    const heading = document.querySelector('h1');
    const label = document.getElementById('resultLabel');
    const value = document.getElementById('resultValue');
    const parts = [heading && heading.textContent.trim(), label && label.textContent.trim(), value && value.textContent.trim()].filter(Boolean);
    return parts.join(' — ') || 'TrueCalco calculator result';
  }

  async function shareResult(type) {
    const url = buildShareUrl();
    const text = resultSummary();
    if (type === 'whatsapp') {
      window.open('https://api.whatsapp.com/send?text=' + encodeURIComponent(text + ' ' + url), '_blank', 'noopener,noreferrer');
    } else if (type === 'facebook') {
      window.open('https://www.facebook.com/sharer/sharer.php?u=' + encodeURIComponent(url), '_blank', 'noopener,noreferrer');
    } else if (type === 'copy') {
      await navigator.clipboard.writeText(url);
      window.alert('Shareable link copied!');
    }
    return url;
  }

  function addShareBox() {
    const result = document.getElementById('calcResult');
    if (!result || document.getElementById('shareBox')) return;
    const box = document.createElement('div');
    box.className = 'viral-share truecalco-share';
    box.id = 'shareBox';
    box.setAttribute('aria-label', 'Share this calculator result');
    box.innerHTML = '<p>Share your result and inputs:</p><div class="truecalco-share-actions"><button type="button" class="share-whatsapp" onclick="shareResult(\'whatsapp\')">WhatsApp</button><button type="button" class="share-facebook" onclick="shareResult(\'facebook\')">Facebook</button><button type="button" class="share-copy" onclick="shareResult(\'copy\')">Copy link</button></div>';
    result.appendChild(box);
  }

  window.shareResult = shareResult;
  window.trueCalcoShare = { buildShareUrl, applyUrlParameters };

  document.addEventListener('DOMContentLoaded', () => {
    addShareBox();
    const applied = applyUrlParameters();
    if (applied && typeof window.calculate === 'function') {
      window.setTimeout(() => {
        try { window.calculate(); } catch (error) { console.warn('Could not automatically calculate shared inputs.', error); }
      }, 0);
    }
  });
}());
