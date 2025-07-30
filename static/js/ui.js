// static/js/ui.js

// Global Chart.js instances for management
let activeCharts = {}; // Stores references to active Chart.js objects

const DATE_FORMAT_OPTIONS = {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
};

// Universal confirmation modal elements
let confirmActionCallback = null; // Stores the callback for the confirmation modal

/**
 * Displays a message to the user.
 * @param {string} message - The message text.
 * @param {string} type - 'success' or 'error'.
 */
export function showMessage(message, type) {
    const messageElement = document.getElementById('messageDisplay');
    if (!messageElement) {
        console.error('Error: #messageDisplay element not found.');
        return;
    }
    messageElement.textContent = message;
    messageElement.className = `message ${type}`;
    messageElement.style.display = 'block';

    // Hide message after 5 seconds
    setTimeout(() => {
        messageElement.style.display = 'none';
    }, 5000);
}

/**
 * Opens a modal by its ID.
 * @param {string} modalId - The ID of the modal element.
 */
export function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'flex'; // Use flex for centering
    }
}

/**
 * Closes a modal by its ID.
 * @param {string} modalId - The ID of the modal element.
 */
export function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
        if (modalId === 'confirmModal') {
            confirmActionCallback = null; // Clear callback when confirmation modal is closed
        }
    }
}

/**
 * Shows a confirmation dialog.
 * @param {string} message - The confirmation message.
 * @param {Function} callback - Function to execute if confirmed.
 */
export function showConfirm(message, callback) {
    const confirmMessageElement = document.getElementById('confirmMessage');
    if (confirmMessageElement) {
        confirmMessageElement.textContent = message;
    }
    confirmActionCallback = callback;
    openModal('confirmModal');
}

/**
 * Formats a date string to 'DD.MM.YYYY'.
 * @param {string} dateString - The date string from the backend (e.g., 'YYYY-MM-DD').
 * @returns {string} Formatted date.
 */
export function formatDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('de-DE', DATE_FORMAT_OPTIONS);
}

/**
 * Destroys a specific Chart.js instance.
 * @param {string} chartKey - The key used to store the chart instance in `activeCharts`.
 */
export function destroyChart(chartKey) {
    if (activeCharts[chartKey]) {
        activeCharts[chartKey].destroy();
        activeCharts[chartKey] = null;
    }
}

/**
 * Stores a Chart.js instance.
 * @param {string} chartKey - The key to store the chart instance.
 * @param {Chart} chartInstance - The Chart.js instance.
 */
export function storeChart(chartKey, chartInstance) {
    activeCharts[chartKey] = chartInstance;
}

/**
 * Initializes listeners for universal modals (confirm modal).
 * This should be called once when the main app structure is loaded.
 */
export function initializeUniversalModals() {
    // Attach listeners for universal confirmation modal
    const confirmYesButton = document.getElementById('confirmYesButton');
    const confirmNoButton = document.getElementById('confirmNoButton');

    if (confirmYesButton) {
        confirmYesButton.addEventListener('click', () => {
            if (confirmActionCallback) {
                confirmActionCallback();
            }
            closeModal('confirmModal');
        });
    }

    if (confirmNoButton) {
        confirmNoButton.addEventListener('click', () => {
            closeModal('confirmModal');
        });
    }
}