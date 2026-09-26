// Shared Chart.js theming. Colors come from the CSS design tokens so charts
// follow the active light/dark theme; call ChartTheme.onChange(fn) to
// re-render when the theme is toggled.
window.ChartTheme = (function () {
  var SERIES_COUNT = 8;

  function token(name) {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  }

  function series(slot) {
    return token('--series-' + (slot + 1));
  }

  function apply() {
    if (!window.Chart) return;
    var d = Chart.defaults;
    d.font.family = token('--font-sans') || 'system-ui, sans-serif';
    d.font.size = 12;
    d.color = token('--chart-text');
    d.borderColor = token('--chart-grid');
    d.animation.duration = 300;

    var tooltip = d.plugins.tooltip;
    tooltip.backgroundColor = token('--surface');
    tooltip.borderColor = token('--border-strong');
    tooltip.borderWidth = 1;
    tooltip.titleColor = token('--text-3');
    tooltip.bodyColor = token('--text');
    tooltip.titleFont = { size: 12, weight: '500' };
    tooltip.bodyFont = { size: 13, weight: '600' };
    tooltip.padding = 10;
    tooltip.cornerRadius = 8;
    tooltip.boxPadding = 6;
    tooltip.caretSize = 0;
  }

  // Standard scale styling: hairline grid, recessive axis, muted ticks.
  function scale(extra) {
    var base = {
      border: { color: token('--chart-axis') },
      grid: { color: token('--chart-grid'), tickColor: 'transparent' },
      ticks: { color: token('--chart-text'), padding: 6 },
      title: { color: token('--chart-text'), font: { size: 12, weight: '500' } }
    };
    return deepMerge(base, extra || {});
  }

  function deepMerge(target, source) {
    Object.keys(source).forEach(function (key) {
      var value = source[key];
      if (value && typeof value === 'object' && !Array.isArray(value) && target[key] && typeof target[key] === 'object') {
        deepMerge(target[key], value);
      } else {
        target[key] = value;
      }
    });
    return target;
  }

  function onChange(callback) {
    document.addEventListener('themechange', function () {
      apply();
      callback();
    });
  }

  apply();

  return {
    SERIES_COUNT: SERIES_COUNT,
    token: token,
    series: series,
    scale: scale,
    apply: apply,
    onChange: onChange
  };
})();
