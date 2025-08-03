// oil.js
import { OilApi } from './api.js';
import { showMessage, showConfirm, formatDate, getTodaysDate, destroyChart, storeChart } from './ui.js';

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
        await loadFillLevelChart();
        await loadFillLevelTrend();
        await loadFillLevels();
    } catch (error) {
        console.error('Error deleting oil entry:', error);
        showMessage(`Fehler beim Löschen des Heizöl-Eintrags: ${error.message}`, 'error');
    }
}

async function showFillLevelsModal() {
    await loadFillLevelChart();
    await loadFillLevelTrend();
    await loadFillLevels();

    const fillLevelDate = document.getElementById("fillLevelDate");
    fillLevelDate.value = getTodaysDate();

    const form = document.getElementById('oilFillLevelForm');
    if (form) {
        form.addEventListener('submit', handleOilFillLevelFormSubmit);
    }

    const fillLevelsModal = document.getElementById("fillLevelsModal");
    const fillLevelsButton = document.getElementById("openFillLevelsModal");
    if (fillLevelsButton && fillLevelsModal) {
        // Open modal
        document.getElementById('openFillLevelsModal').addEventListener('click', function () {
        document.getElementById('fillLevelsModal').style.display = 'flex';
        document.body.style.overflow = 'hidden';
        });
        // Close modal by clicking on "X"
        document.querySelector('#fillLevelsModal .close').addEventListener('click', function () {
        document.getElementById('fillLevelsModal').style.display = 'none';
        document.body.style.overflow = '';
        });
        // Close modal by clicking outside of modal
        document.getElementById('fillLevelsModal').addEventListener('click', function (event) {
        if (event.target === this) {
            this.style.display = 'none';
            document.body.style.overflow = '';
        }
        });
    }

}

async function loadFillLevels() {
    try {
        const fillLevels = await OilApi.getFillLevelEntries();
        const tableBody = document.getElementById("oil-fill-levels-table-body");
        if (!tableBody) return;

        tableBody.innerHTML = "";

        fillLevels.forEach(level => {
            const row = tableBody.insertRow();
            row.dataset.id = level.id;

            row.innerHTML = `
                <td>${formatDate(level.date)}</td>
                <td>${(level.level)}</td>
                <td>
                    <button class="btn-delete" data-id="${level.id}">Löschen</button>
                </td>
            `;
            // Attach event listener directly after creation for efficiency
            row.querySelector('.btn-delete').addEventListener('click', () => confirmDeleteOilFillLevel(level.id));
        });
    } catch (error) {
        console.error('Error loading oil entries:', error);
        showMessage(`Fehler beim Laden der Heizöl-Einträge: ${error.message}`, 'error');
    }
}

async function handleOilFillLevelFormSubmit(event) {
    if (event && typeof event.preventDefault === 'function') {
        event.preventDefault();
    } else {
        console.warn("handleOilFillLevelFormSubmit called without event");
        return;
    }

    const form = event.target;
    const formData = new FormData(form);

    const data = {
        date: formData.get('fillLevelDate'),
        level: parseFloat(formData.get('fillLevel')),
    };

    try {
        await OilApi.addFillLevelEntry(data);
        showMessage('Heizöl-Füllstand erfolgreich hinzugefügt!', 'success');
        form.reset();
        loadFillLevelChart();
        loadFillLevelTrend();
        loadFillLevels();
    } catch (error) {
        console.error('Error adding oil fill level:', error);
        showMessage(`Fehler beim Hinzufügen des Heizöl-Füllstands: ${error.message}`, 'error');
    }
}

async function loadFillLevelChart() {
    try {
        const fillLevels = await OilApi.getFillLevelEntries();
        if (!Array.isArray(fillLevels) || fillLevels.length === 0) return;

        const currentFillLevel = fillLevels[0].level ?? 0;
        const percentage = Math.min(100, Math.round((currentFillLevel / 150) * 100));
        const fillLevelPercentage = [percentage]; // wrap in array for chart

        const ctx = document.getElementById("fillLevelChart")?.getContext('2d');
        if (!ctx) return;

        destroyChart('fillLevelChart'); // Destroy previous chart instance

        const backgroundColors = fillLevelPercentage.map(p => {
            if (p >= 60) return 'rgba(46, 204, 113, 0.8)';
            if (p >= 30) return 'rgba(243, 156, 18, 0.8)';
            return 'rgba(231, 76, 60, 0.8)';
        });

        const newChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Füllstand'],
                datasets: [{
                    label: 'Füllstand',
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
                    },
                    tooltip: {
                        callbacks: {
                            label: function(tooltipItem) {
                                return tooltipItem.dataset.label + ': ' + tooltipItem.formattedValue + '%';
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            callback: value => value + '%'
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

async function loadFillLevelTrend() {
    try {
        const fillLevels = await OilApi.getFillLevelEntries();
        const ctx = document.getElementById('fillLevelTrend')?.getContext('2d');

        if (!ctx) {
            console.warn('fillLevelTrend canvas not found, skipping chart rendering.');
            return;
        }

        destroyChart('fillLevelTrend');

        const labels = [];
        const levels = [];

        fillLevels.forEach(d => {
            if (typeof d.level === 'number' && !isNaN(d.level)) {
                const formattedDate = new Date(d.date).toLocaleDateString('de-DE');
                labels.push(formattedDate);
                levels.push(d.level);
            }
        });

        if (labels.length === 0) {
            console.warn('Keine gültigen Daten für Füllstandstrend vorhanden.');
            return;
        }

        const newChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Füllstand (cm)',
                    data: levels,
                    backgroundColor: 'rgba(255, 206, 86, 0.7)',
                    borderColor: 'rgba(255, 206, 86, 1)',
                    borderWidth: 2,
                    tension: 0.3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        min: 0,
                        max: 160,
                        display: true,
                        ticks: {
                            callback: value => value + ' cm'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Datum',
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
                                return context.dataset.label + ': ' + context.parsed.y + ' cm';
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

        storeChart('fillLevelTrend', newChart);
    } catch (error) {
        console.error('Error loading oil fill level trend:', error);
        showMessage(`Fehler beim Laden der jährlichen Heizöl-Füllstand-Trends: ${error.message}`, 'error');
    }
}

function confirmDeleteOilFillLevel(id) {
    showConfirm('Möchten Sie diesen Heizöl-Füllstand wirklich löschen?', () => deleteOilFillLevelEntry(id));
}

async function deleteOilFillLevelEntry(id) {
    try {
        await OilApi.deleteFillLevelEntry(id);
        showMessage('Heizöl-Füllstand erfolgreich gelöscht!', 'success');
        await loadFillLevelChart();
        await loadFillLevelTrend();
        await loadFillLevels();
    } catch (error) {
        console.error('Error deleting oil fill level entry:', error);
        showMessage(`Fehler beim Löschen des Heizöl-Füllstands: ${error.message}`, 'error');
    }
}