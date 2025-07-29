// oil.js
import { OilApi } from './api.js';
import { showMessage, showConfirm, formatDate, destroyChart, storeChart, openModal } from './ui.js';

/**
 * Initializes the Oil section, attaches event listeners, and loads data.
 */
export function initializeOilSection() {
    console.log('Initializing Oil Section');
    const form = document.getElementById('oilForm');
    if (form) {
        form.addEventListener('submit', handleOilFormSubmit);
    }

    loadOilEntries();
    loadOilOverallStats();
    loadOilPriceTrend();
    loadOilYearlySummary();

    showFillLevelsModal();
}

/**
 * Handles the submission of the new oil entry form.
 * @param {Event} event - The form submission event.
 */
async function handleOilFormSubmit(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);

    const data = {
        date: formData.get('date'),
        volume: parseFloat(formData.get('volume')),
        costs: parseFloat(formData.get('costs')),
        retailer: formData.get('retailer'),
        note: formData.get('note') || null
    };

    try {
        await OilApi.addEntry(data);
        showMessage('Heizöl-Eintrag erfolgreich hinzugefügt!', 'success');
        form.reset();
        loadOilEntries();
        loadOilOverallStats();
        loadOilPriceTrend();
        loadOilYearlySummary();
    } catch (error) {
        console.error('Error adding oil entry:', error);
        showMessage(`Fehler beim Hinzufügen des Heizöl-Eintrags: ${error.message}`, 'error');
    }
}

/**
 * Loads and displays all oil entries in the table.
 */
async function loadOilEntries() {
    try {
        const entries = await OilApi.getEntries();
        const tableBody = document.getElementById('oil-entries-table-body');
        if (!tableBody) return;

        tableBody.innerHTML = ''; // Clear existing entries

        entries.forEach(entry => {
            const row = tableBody.insertRow();
            row.dataset.id = entry.id; // Store ID on the row

            row.innerHTML = `
                <td>${formatDate(entry.date)}</td>
                <td>${(entry.volume)}</td>
                <td>${(entry.costs)}</td>
                <td>${(entry.price)}</td>
                <td>${entry.retailer}</td>
                <td>${entry.note || ''}</td>
                <td>
                    <button class="btn-delete" data-id="${entry.id}">Löschen</button>
                </td>
            `;
            // Attach event listener directly after creation for efficiency
            row.querySelector('.btn-delete').addEventListener('click', () => confirmDeleteOil(entry.id));
        });
    } catch (error) {
        console.error('Error loading oil entries:', error);
        showMessage(`Fehler beim Laden der Heizöl-Einträge: ${error.message}`, 'error');
    }
}

/**
 * Loads and displays overall oil statistics.
 */
async function loadOilOverallStats() {
    try {
        const stats = await OilApi.getOverallStats();
        document.getElementById('oil_total_volume').textContent = stats.total_volume;
        document.getElementById('oil_total_costs').textContent = stats.total_costs;
        document.getElementById('oil_number_of_years').textContent = stats.number_of_years;
        document.getElementById('oil_average_volume').textContent = stats.average_volume;
    } catch (error) {
        console.error('Error loading oil overall stats:', error);
        showMessage(`Fehler beim Laden der Heizöl-Statistiken: ${error.message}`, 'error');
    }
}

/**
 * Loads and renders the oil yearly summary chart.
 */
async function loadOilYearlySummary() {
    try {
        const yearlySummaryData = await OilApi.getYearlySummary();
        const ctx = document.getElementById('oilYearlySummaryChart')?.getContext('2d');

        if (!ctx) {
            console.warn('oilYearlySummaryChart canvas not found, skipping chart rendering.');
            return;
        }

        destroyChart('oilYearlySummaryChart'); // Destroy existing chart if any

        const labels = yearlySummaryData.map(d => d.year);
        const totalVolumes = yearlySummaryData.map(d => d.total_volume);
        const totalCosts = yearlySummaryData.map(d => d.total_costs);

        const newChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Heizölvolumen (L)',
                        data: totalVolumes,
                        backgroundColor: 'rgba(255, 206, 86, 0.7)',
                        borderColor: 'rgba(255, 206, 86, 1)',
                        borderWidth: 2,
                    },
                    {
                        label: 'Heizölkosten (€)',
                        data: totalCosts,
                        backgroundColor: 'rgba(75, 192, 192, 0.7)',
                        borderColor: 'rgba(75, 192, 192, 1)',
                        borderWidth: 2
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Jahr',
                            font: {
                                size: 14,
                                weight: 'bold'
                            }
                        }
                    },
                    'y-volume': {
                        type: 'linear',
                        position: 'left',
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Volumen (m³)',
                            font: {
                                size: 14,
                                weight: 'bold'
                            }
                        }
                    },
                    'y-costs': {
                        type: 'linear',
                        position: 'right',
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Kosten (€)',
                            font: {
                                size: 14,
                                weight: 'bold'
                            }
                        },
                        grid: {
                            drawOnChartArea: false // Only draw grid lines for the left axis
                        }
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                let label = context.dataset.label || '';
                                if (label) {
                                    label += ': ';
                                }
                                if (context.dataset.label.includes('Volumen')) {
                                    label += context.parsed.y + ' L';
                                } else if (context.dataset.label.includes('Kosten')) {
                                    label += context.parsed.y + ' €';
                                }
                                return label;
                            }
                        }
                    },
                    legend: {
                        position: 'top',
                        labels: {
                            font: {
                                size: 12
                            }
                        }
                    }
                }
            }
        });
        storeChart('oilYearlySummaryChart', newChart);
    } catch (error) {
        console.error('Error loading oil yearly summary:', error);
        showMessage(`Fehler beim Laden der jährlichen Heizöl-Zusammenfassung: ${error.message}`, 'error');
    }
}

/**
 * Loads oil price trend data and renders the chart.
 */
async function loadOilPriceTrend() {
    try {
        const trendData = await OilApi.getPriceTrend();

        const labels = trendData.map(d => d.year);
        const prices = trendData.map(d => d.average_price);

        const ctx = document.getElementById('oilPriceChart');
        if (!ctx) return;

        destroyChart('oilPriceChart'); // Destroy previous chart instance

        const newChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Heizölpreis (€/L)',
                    data: prices,
                    borderColor: 'rgba(16, 185, 129, 1)',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: 'rgba(16, 185, 129, 1)',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 5,
                    pointHoverRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Preis (€/L)',
                            font: {
                                size: 14,
                                weight: 'bold'
                            }
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Jahr',
                            font: {
                                size: 14,
                                weight: 'bold'
                            }
                        }
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.dataset.label + ': ' + context.parsed.y + ' €/L';
                            }
                        }
                    },
                    legend: {
                        position: 'top',
                        labels: {
                            font: {
                                size: 12
                            }
                        }
                    }
                }
            }
        });
        storeChart('oilPriceChart', newChart);
    } catch (error) {
        console.error('Error loading oil price trend:', error);
        showMessage(`Fehler beim Laden des Heizöl-Preisverlaufs: ${error.message}`, 'error');
    }
}

/**
 * Shows a confirmation dialog before deleting an oil entry.
 * @param {number} id - The ID of the oil entry to delete.
 */
function confirmDeleteOil(id) {
    showConfirm('Möchten Sie diesen Heizöl-Eintrag wirklich löschen?', () => deleteOilEntry(id));
}

/**
 * Deletes an oil entry.
 * @param {number} id - The ID of the oil entry to delete.
 */
async function deleteOilEntry(id) {
    try {
        await OilApi.deleteEntry(id);
        showMessage('Heizöl-Eintrag erfolgreich gelöscht!', 'success');
        loadOilOverallStats();
        loadOilYearlySummary();
        loadOilPriceTrend();
        loadOilEntries();
    } catch (error) {
        console.error('Error deleting oil entry:', error);
        showMessage(`Fehler beim Löschen des Heizöl-Eintrags: ${error.message}`, 'error');
    }
}

async function showFillLevelsModal() {
    await loadFillLevelChart();
    await loadFillLevels();
    await handleOilFillLevelFormSubmit();
    const form = document.getElementById('oilFillLevelForm');
    if (form) {
        form.addEventListener('submit', handleOilFillLevelFormSubmit);
    }

    const fillLevelsModal = document.getElementById("fillLevelsModal");
    const fillLevelsButton = document.getElementById("openFillLevelsModal");
    fillLevelsButton.addEventListener("click", () => fillLevelsModal.style.display = "block");
}

async function loadFillLevels() {
    try {
        const fillLevels = OilApi.getFillLevels();
        const tableBody = document.getElementById("oil-fill-levels-table-body");
        if(!tableBody) return;

        tableBody.innerHTML = "";

        fillLevels.forEach(level => {
            const row = tableBody.insertRow();
            row.dataset.id = level.id;

            row.innerHTML = `
                <td>${formatDate(level.date)}</td>
                <td>${(level.height)}</td>
            `
        });
    } catch (error) {
        console.error('Error loading oil entries:', error);
        showMessage(`Fehler beim Laden der Heizöl-Einträge: ${error.message}`, 'error');
    }
}

async function handleOilFillLevelFormSubmit(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);

    const data = {
        date: formData.get('date'),
        fill_level: parseFloat(formData.get('fillLevel')),
    };

    try {
        await OilApi.addFillLevel(data);
        showMessage('Heizöl-Füllstand erfolgreich hinzugefügt!', 'success');
        form.reset();
        loadFillLevels();
    } catch (error) {
        console.error('Error adding oil fill level:', error);
        showMessage(`Fehler beim Hinzufügen des Heizöl-Füllstands: ${error.message}`, 'error');
    }
}

async function loadFillLevelChart() {
    try {
        const fillLevels = await OilApi.getFillLevels();
        const currentFileLevel = fillLevels.level && fillLevels.lengt > 0
                                    ? fillLevels.level[0]
                                    : null;
        const fillLevelPercentage = 150 / currentFileLevel;

        const ctx = document.getElementById("fillLevelChart").getContext('2d');
        if (!ctx) return;
        destroyChart('oilPriceChart'); // Destroy previous chart instance

        const backgroundColors = fillLevelPercentage.map(percentage => {
            if (percentage >= 60) return 'rgba(46, 204, 113, 0.8)';
            if (percentage >= 30) return 'rgba(243, 156, 18, 0.8)';
            return 'rgba(231, 76, 60, 0.8)';
        });

        const newChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: "Füllstand",
                datasets: [{
                    label: 'Heizölpreis (€/L)',
                    data: fillLevelPercentage,
                    backgroundColor: backgroundColors,
                    borderColor: backgroundColors.map(color => color.replace('0.8', '1')),
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    }
                }
            }
        });
        storeChart("fillLevelChart", newChart);
    } catch (error) {
        console.error('Error loading fill level chart:', error);
        showMessage(`Fehler beim Laden des Heizöl-Füllstands: ${error.message}`, 'error');
    }
}