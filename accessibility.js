(function () {
  'use strict';

  function setupFaqs() {
    document.querySelectorAll('.faq-question').forEach((button, index) => {
      const item = button.closest('.faq-item');
      const answer = item && item.querySelector('.faq-answer');
      if (!item || !answer) return;
      if (!answer.id) answer.id = 'faq-answer-' + (index + 1);
      button.setAttribute('aria-controls', answer.id);
      const update = () => {
        const expanded = item.classList.contains('open');
        button.setAttribute('aria-expanded', String(expanded));
        answer.hidden = !expanded;
      };
      update();
      button.addEventListener('click', update);
    });
  }

  function setupMenu() {
    const button = document.getElementById('hamburgerBtn');
    const nav = document.getElementById('navLinks');
    if (!button || !nav) return;
    button.setAttribute('aria-controls', 'navLinks');
    const update = () => button.setAttribute('aria-expanded', String(nav.classList.contains('active')));
    update();
    button.addEventListener('click', update);
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape' && nav.classList.contains('active')) {
        nav.classList.remove('active');
        update();
        button.focus();
      }
    });
  }

  function setupTheme() {
    const button = document.getElementById('themeToggle');
    if (!button) return;
    const update = () => button.setAttribute('aria-pressed', String(document.body.classList.contains('light-mode')));
    update();
    button.addEventListener('click', update);
  }

  function setupResults() {
    const value = document.getElementById('resultValue');
    if (value) {
      value.setAttribute('role', 'status');
      value.setAttribute('aria-live', 'polite');
    }
  }

  function labelRecipeIngredients() {
    const list = document.getElementById('ingsList');
    if (!list) return;
    const apply = () => {
      list.querySelectorAll('.ing-input').forEach((input, index) => {
        if (!input.id) input.id = 'ingredient-' + (index + 1) + '-' + Date.now();
        if (!list.querySelector('label[for="' + input.id + '"]')) {
          const label = document.createElement('label');
          label.className = 'sr-only';
          label.htmlFor = input.id;
          label.textContent = 'Ingredient ' + (index + 1);
          input.insertAdjacentElement('beforebegin', label);
        }
      });
    };
    apply();
    new MutationObserver(apply).observe(list, { childList: true, subtree: true });
  }

  document.addEventListener('DOMContentLoaded', () => {
    setupFaqs();
    setupMenu();
    setupTheme();
    setupResults();
    labelRecipeIngredients();
  });
}());
