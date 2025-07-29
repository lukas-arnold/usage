// static/js/app.js

import { initializeUniversalModals, showMessage, destroyChart } from './ui.js';
import { initializeElectricitySection } from './electricity.js';
import { initializeOilSection } from './oil.js';
import { initializeWaterSection } from './water.js';

let currentLoadedSection = null; // Track the currently loaded section

// Dynamically create the main application structure
document.addEventListener('DOMContentLoaded', () => {
    // Retrieve appContainer here to ensure the element exists after DOM is loaded
    const appContainer = document.getElementById('app-container');
    if (!appContainer) {
        console.error('Error: #app-container element not found in the DOM. Cannot initialize app.');
        // Optionally, display a message to the user if this error occurs
        // alert('Anwendungscontainer nicht gefunden. Bitte wenden Sie sich an den Support.');
        return;
    }

    // Inject the main content area and universal modals
    appContainer.innerHTML = `
        <div class="main-container">
            <nav class="tab-navigation">
                <button class="tab-button active" data-target="electricity-section">⚡ Strom</button>
                <button class="tab-button" data-target="oil-section">🛢️ Heizöl</button>
                <button class="tab-button" data-target="water-section">💧 Wasser</button>
            </nav>
            <div id="content-area">
                </div>
        </div>

        <div id="confirmModal" class="modal confirm-modal">
            <div class="modal-content confirm-modal-content">
                <p id="confirmMessage"></p>
                <div class="confirm-modal-buttons">
                    <button id="confirmYesButton" class="btn-primary">Ja</button>
                    <button id="confirmNoButton" class="btn-secondary">Nein</button>
                </div>
            </div>
        </div>

        <div id="messageDisplay" class="message"></div>
    `;

    // Attach event listeners to dynamically created tab buttons
    // These must be selected AFTER innerHTML has injected them
    document.querySelectorAll('.tab-button').forEach(button => {
        button.addEventListener('click', () => {
            loadSection(button.dataset.target);
        });
    });

    // Initialize universal modal listeners from ui.js
    initializeUniversalModals();

    // Load the default section on initial page load
    loadSection('electricity-section');
});

/**
 * Loads the content for a specific section (tab).
 * @param {string} sectionId - The ID of the section to load (e.g., 'electricity-section').
 */
async function loadSection(sectionId) {
    // Destroy charts from the previously loaded section before loading new one
    // This ensures no old chart instances interfere and memory is cleared.
    destroyChart('electricityPriceChart');
    destroyChart('electricityYearlySummaryChart'); // Destroy the new chart
    destroyChart('oilPriceChart');
    destroyChart('waterPriceChart');


    let htmlFile = '';
    // Determine the correct HTML file based on the sectionId
    if (sectionId === 'electricity-section') {
        htmlFile = '/static/electricity.html';
    } else if (sectionId === 'oil-section') {
        htmlFile = '/static/oil.html';
    } else if (sectionId === 'water-section') {
        htmlFile = '/static/water.html';
    } else {
        console.error('Unknown section:', sectionId);
        showMessage(`Unbekannter Abschnitt: ${sectionId}`, 'error');
        return;
    }

    try {
        const response = await fetch(htmlFile);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const html = await response.text();
        // Select content-area AFTER it has been injected by appContainer.innerHTML
        const contentArea = document.getElementById('content-area');
        if (contentArea) {
            contentArea.innerHTML = html;
        } else {
            console.error('Error: #content-area not found after dynamic injection. Cannot load section HTML.');
            showMessage('Inhaltsbereich konnte nicht gefunden werden.', 'error');
            return;
        }


        // Update active tab button
        document.querySelectorAll('.tab-button').forEach(button => {
            if (button.dataset.target === sectionId) {
                button.classList.add('active');
            } else {
                button.classList.remove('active');
            }
        });

        // Initialize section-specific functionality after its HTML is loaded
        // This dynamically calls the correct initialization function for the loaded section.
        if (sectionId === 'electricity-section') {
            initializeElectricitySection();
        } else if (sectionId === 'oil-section') {
            initializeOilSection();
        } else if (sectionId === 'water-section') {
            initializeWaterSection();
        }

        currentLoadedSection = sectionId; // Update tracking of loaded section

    } catch (error) {
        console.error(`Error loading section ${sectionId}:`, error);
        showMessage(`Abschnitt konnte nicht geladen werden: ${sectionId}. Bitte versuchen Sie es erneut. Details: ${error.message}`, 'error');
    }
}

// Global error handling for unhandled promise rejections
window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
    showMessage(`Ein unerwarteter Fehler ist aufgetreten: ${event.reason.message || event.reason}`, 'error');
});
