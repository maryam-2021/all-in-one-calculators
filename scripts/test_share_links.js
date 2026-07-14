const fs = require('fs');
const vm = require('vm');

const code = fs.readFileSync('share-links.js', 'utf8');
const listeners = {};
const opened = [];
let copied = '';
let calculated = 0;

function control(id, value, type = 'number') {
  return { id, value: String(value), type, checked: false, dataset: {}, dispatchEvent() {} };
}

const fields = [control('loan', 300000), control('rate', 6.5), control('years', 30), control('down', 60000)];
const document = {
  querySelectorAll(selector) { return selector.startsWith('.calc-form') ? fields : []; },
  querySelector(selector) { return selector === 'h1' ? { textContent: 'Mortgage Calculator' } : null; },
  getElementById(id) { return ({ resultLabel: { textContent: 'Monthly payment' }, resultValue: { textContent: '$1,517.04' } })[id] || null; },
  addEventListener(name, fn) { listeners[name] = fn; },
  createElement() { return {}; }
};
const window = {
  location: { origin: 'https://truecalco.com', pathname: '/mortgage-calculator', search: '?amount=325000&rate=6.25&term=20&down=65000' },
  open(url) { opened.push(url); },
  alert() {},
  calculate() { calculated += 1; },
  setTimeout(fn) { fn(); }
};
const context = { document, window, navigator: { clipboard: { async writeText(value) { copied = value; } } }, URL, URLSearchParams, Event: class {}, console, encodeURIComponent };
vm.createContext(context);
vm.runInContext(code, context);

const url = context.window.trueCalcoShare.buildShareUrl();
if (url !== 'https://truecalco.com/mortgage-calculator?amount=300000&rate=6.5&term=30&down=60000') throw new Error('Unexpected share URL: ' + url);

listeners.DOMContentLoaded();
if (fields[0].value !== '325000' || fields[1].value !== '6.25' || fields[2].value !== '20' || fields[3].value !== '65000') throw new Error('URL parameters were not applied.');
if (calculated !== 1) throw new Error('Shared inputs did not trigger calculation.');

context.window.shareResult('copy').then(() => {
  if (!copied.includes('amount=325000') || !copied.includes('term=20')) throw new Error('Copied URL omitted shared values: ' + copied);
  context.window.shareResult('whatsapp');
  context.window.shareResult('facebook');
  if (opened.length !== 2 || !opened.every((value) => value.includes('amount%3D325000'))) throw new Error('Social share URLs omitted shared values.');
  console.log('PASS: share URLs build, prefill, recalculate, and copy correctly.');
});
