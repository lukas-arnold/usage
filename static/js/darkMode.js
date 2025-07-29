document.addEventListener('DOMContentLoaded', () => {
    const themeIconToggle = document.getElementById('theme-icon-toggle'); // New ID for the icon container
    const body = document.body;

    // Load theme preference from local storage
    const currentTheme = localStorage.getItem('theme');
    if (currentTheme) {
        body.setAttribute('data-theme', currentTheme);
    } else {
        // Optional: Set default theme to light if no preference found
        body.setAttribute('data-theme', 'light');
        localStorage.setItem('theme', 'light');
    }

    // Toggle dark mode function
    function toggleDarkMode() {
        if (body.getAttribute('data-theme') === 'dark') {
            body.setAttribute('data-theme', 'light'); // Switch to light
            localStorage.setItem('theme', 'light');
        } else {
            body.setAttribute('data-theme', 'dark'); // Switch to dark
            localStorage.setItem('theme', 'dark');
        }
    }

    // Event listener for the icon container
    if (themeIconToggle) {
        themeIconToggle.addEventListener('click', toggleDarkMode);
    }
});