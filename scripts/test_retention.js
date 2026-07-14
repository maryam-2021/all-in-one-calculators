const fs = require('fs');
const vm = require('vm');
const code = fs.readFileSync('retention.js', 'utf8');
const values = new Map();
const listeners = {};
const context = {
  window: { location: { pathname: '/mortgage-calculator' }, localStorage: { getItem: (key) => values.get(key) || null, setItem: (key, value) => values.set(key, value) } },
  document: { addEventListener: (name, fn) => { listeners[name] = fn; }, querySelector: () => null, getElementById: () => null },
  navigator: { platform: 'Win32' },
  JSON, Array, String, encodeURI, console
};
vm.createContext(context);
vm.runInContext(code, context);
const retention = context.window.trueCalcoRetention;
if (!retention.toggleSaved({ path: '/mortgage-calculator', title: 'Mortgage Calculator' })) throw new Error('Tool was not saved.');
if (retention.readSaved().length !== 1) throw new Error('Saved tool was not retained.');
if (retention.toggleSaved({ path: '/mortgage-calculator', title: 'Mortgage Calculator' })) throw new Error('Tool was not removed.');
if (retention.readSaved().length !== 0) throw new Error('Removed tool remains in storage.');
if (!retention.bookmarkShortcut().includes('Ctrl+D')) throw new Error('Incorrect bookmark guidance.');
console.log('PASS: private saved-tool retention and bookmark guidance work.');
