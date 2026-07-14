(function () {
  'use strict';

  const storageKey = 'truecalco.savedTools';

  function readSaved() {
    try {
      const value = JSON.parse(window.localStorage.getItem(storageKey) || '[]');
      return Array.isArray(value) ? value.filter((item) => item && item.path && item.title).slice(0, 12) : [];
    } catch (_) {
      return [];
    }
  }

  function writeSaved(items) {
    try {
      window.localStorage.setItem(storageKey, JSON.stringify(items.slice(0, 12)));
      return true;
    } catch (_) {
      return false;
    }
  }

  function toggleSaved(tool) {
    const saved = readSaved();
    const index = saved.findIndex((item) => item.path === tool.path);
    if (index >= 0) saved.splice(index, 1);
    else saved.unshift(tool);
    writeSaved(saved);
    return index < 0;
  }

  function bookmarkShortcut() {
    return /Mac|iPhone|iPad/.test(navigator.platform || '') ? 'Press ⌘D to bookmark this page.' : 'Press Ctrl+D to bookmark this page.';
  }

  function addSavePrompt() {
    const form = document.querySelector('.calc-form');
    const header = document.querySelector('.calc-header');
    if (!form || !header || document.getElementById('returnPrompt')) return;
    const heading = document.querySelector('h1');
    const tool = { path: window.location.pathname, title: heading ? heading.textContent.trim() : document.title };
    const prompt = document.createElement('aside');
    prompt.id = 'returnPrompt';
    prompt.className = 'return-prompt';
    prompt.setAttribute('aria-label', 'Save this calculator');
    prompt.innerHTML = '<div><strong>Use this tool often?</strong><span>Save it locally or bookmark it. No account required.</span></div><div class="return-actions"><button type="button" class="save-tool-button"></button><button type="button" class="bookmark-help-button">Bookmark</button></div><p class="return-status" role="status" aria-live="polite"></p>';
    header.insertAdjacentElement('afterend', prompt);

    const saveButton = prompt.querySelector('.save-tool-button');
    const bookmarkButton = prompt.querySelector('.bookmark-help-button');
    const status = prompt.querySelector('.return-status');
    const refresh = () => {
      const selected = readSaved().some((item) => item.path === tool.path);
      saveButton.textContent = selected ? 'Saved ✓' : 'Save this tool';
      saveButton.setAttribute('aria-pressed', String(selected));
    };
    saveButton.addEventListener('click', () => {
      const selected = toggleSaved(tool);
      refresh();
      status.textContent = selected ? 'Saved in this browser. It will appear under Saved tools on the homepage.' : 'Removed from Saved tools.';
    });
    bookmarkButton.addEventListener('click', () => { status.textContent = bookmarkShortcut(); });
    refresh();
  }

  function renderSavedTools() {
    if (window.location.pathname !== '/' && window.location.pathname !== '/index.html') return;
    const saved = readSaved();
    const main = document.querySelector('main');
    if (!saved.length || !main || document.getElementById('savedTools')) return;
    const section = document.createElement('section');
    section.id = 'savedTools';
    section.className = 'saved-tools site-wrapper';
    const links = saved.map((item) => '<li><a href="' + encodeURI(item.path) + '">' + escapeHtml(item.title) + '</a></li>').join('');
    section.innerHTML = '<div><span class="eyebrow">Stored on this device</span><h2>Saved tools</h2><p>No account or tracking profile is used.</p><ul>' + links + '</ul></div>';
    main.appendChild(section);
  }

  function escapeHtml(value) {
    return String(value).replace(/[&<>'"]/g, (char) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' })[char]);
  }

  window.trueCalcoRetention = { readSaved, toggleSaved, bookmarkShortcut };
  document.addEventListener('DOMContentLoaded', () => { addSavePrompt(); renderSavedTools(); });
}());
