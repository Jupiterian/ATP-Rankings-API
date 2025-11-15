// Theme Toggle Functionality
(function() {
  // Get saved theme from localStorage or default to 'dark'
  const savedTheme = localStorage.getItem('theme') || 'dark';
  
  // Apply theme on page load
  document.documentElement.setAttribute('data-theme', savedTheme);
  
  // Function to toggle theme
  function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    
    // Update button icon
    updateToggleIcon(newTheme);
  }
  
  // Function to update toggle button icon
  function updateToggleIcon(theme) {
    const toggleBtn = document.getElementById('themeToggle');
    if (toggleBtn) {
      toggleBtn.textContent = theme === 'dark' ? '☀️' : '🌙';
      toggleBtn.setAttribute('aria-label', `Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`);
    }
  }
  
  // Initialize when DOM is ready
  document.addEventListener('DOMContentLoaded', function() {
    // Create toggle button if it doesn't exist
    if (!document.getElementById('themeToggle')) {
      const toggleBtn = document.createElement('button');
      toggleBtn.id = 'themeToggle';
      toggleBtn.className = 'theme-toggle';
      toggleBtn.setAttribute('aria-label', `Switch to ${savedTheme === 'dark' ? 'light' : 'dark'} mode`);
      toggleBtn.textContent = savedTheme === 'dark' ? '☀️' : '🌙';
      toggleBtn.onclick = toggleTheme;
      document.body.appendChild(toggleBtn);
    }
    
    // Update icon on load
    updateToggleIcon(savedTheme);
  });
})();
