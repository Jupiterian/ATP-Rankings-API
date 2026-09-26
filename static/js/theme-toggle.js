// Theme toggle. The initial theme is applied by an inline script in
// base.html before first paint; this wires up the header button, follows OS
// changes until the user picks a theme, and emits a `themechange` event so
// charts can re-read the color tokens.
(function () {
  var root = document.documentElement;
  var button = document.getElementById('themeToggle');
  var media = window.matchMedia ? window.matchMedia('(prefers-color-scheme: light)') : null;

  function savedTheme() {
    try { return localStorage.getItem('theme'); } catch (e) { return null; }
  }

  function currentTheme() {
    return root.getAttribute('data-theme') === 'light' ? 'light' : 'dark';
  }

  function updateButton() {
    if (!button) return;
    var next = currentTheme() === 'dark' ? 'light' : 'dark';
    button.setAttribute('aria-label', 'Switch to ' + next + ' mode');
    button.title = 'Switch to ' + next + ' mode';
  }

  function applyTheme(theme, persist) {
    root.setAttribute('data-theme', theme);
    if (persist) {
      try { localStorage.setItem('theme', theme); } catch (e) {}
    }
    updateButton();
    document.dispatchEvent(new CustomEvent('themechange', { detail: { theme: theme } }));
  }

  if (button) {
    updateButton();
    button.addEventListener('click', function () {
      applyTheme(currentTheme() === 'dark' ? 'light' : 'dark', true);
    });
  }

  if (media && media.addEventListener) {
    media.addEventListener('change', function (event) {
      var saved = savedTheme();
      if (saved !== 'light' && saved !== 'dark') {
        applyTheme(event.matches ? 'light' : 'dark', false);
      }
    });
  }
})();
