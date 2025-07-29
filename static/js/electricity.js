import { ElectricityApi } from './api.js';
import { showMessage, showConfirm, formatDate, destroyChart, storeChart } from './ui.js';

/**
 * Initializes the Electricity section, attaches event listeners, and loads data.
 */
export function initializeElectricitySection() {
    console.log('Initializing Electricity Section');
    const form = document.getElementById('electricityForm');
    if (form) {
        form.addEventListener('submit', handleElectricityFormSubmit);
    }

    loadElectricityOverallStats();
    loadElectricityYearlySummaryChart();
    loadElectricityPriceTrend();
    loadElectricityEntries();
}

/**
 * Handles the submission of the new electricity entry form.
 * @param {Event} event - The form submission event.
 */
async function handleElectricityFormSubmit(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);

    const data = {
        time_from: formData.get('time_from'),
        time_to: formData.get('time_to'),
        usage: parseFloat(formData.get('usage')),
        costs: parseFloat(formData.get('costs')),
        retailer: formData.get('retailer'),
        payments: parseFloat(formData.get('payments')),
        note: formData.get('note') || null
    };

    try {
        await ElectricityApi.addEntry(data);
        showMessage('Strom-Eintrag erfolgreich hinzugefügt!', 'success');
        form.reset();
        loadElectricityOverallStats();
        loadElectricityYearlySummaryChart();
        loadElectricityPriceTrend();
        loadElectricityEntries();
    } catch (error) {
        console.error('Error adding electricity entry:', error);
        showMessage(`Fehler beim Hinzufügen des Strom-Eintrags: ${error.message}`, 'error');
    }
}

/**
 * Loads and displays all electricity entries in the table.
 */
async function loadElectricityEntries() {
    try {
        const entries = await ElectricityApi.getEntries();
        const tableBody = document.getElementById('electricity-entries-table-body');
        if (!tableBody) return;

        tableBody.innerHTML = ''; // Clear existing entries

        entries.forEach(entry => {
            const row = tableBody.insertRow();
            row.dataset.id = entry.id; // Store ID on the row

            row.innerHTML = `
                <td>${formatDate(entry.time_from)}</td>
                <td>${formatDate(entry.time_to)}</td>
                <td>${entry.usage}</td>
                <td>${entry.costs}</td>
                <td>${entry.price}</td>
                <td>${entry.retailer}</td>
                <td>${entry.payments}</td>
                <td>${entry.monthly_payment}</td>
                <td>${entry.difference}</td>
                <td>${entry.note || ''}</td>
                <td>
                    <button class="btn-delete" data-id="${entry.id}">Löschen</button>
                </td>
            `;
            // Attach event listener directly after creation for efficiency
            row.querySelector('.btn-delete').addEventListener('click', () => confirmDeleteElectricity(entry.id));
        });
    } catch (error) {
        console.error('Error loading electricity entries:', error);
        showMessage(`Fehler beim Laden der Strom-Einträge: ${error.message}`, 'error');
    }
}

/**
 * Loads and displays overall electricity statistics.
 */
async function loadElectricityOverallStats() {
    try {
        const stats = await ElectricityApi.getOverallStats();
        document.getElementById('electricity_total_usage').textContent = stats.total_usage;
        document.getElementById('electricity_total_costs').textContent = stats.total_costs;
        document.getElementById('electricity_number_of_years').textContent = stats.number_of_years;
        document.getElementById('electricity_average_usage').textContent = stats.average_usage;
    } catch (error) {
        console.error('Error loading electricity overall stats:', error);
        showMessage(`Fehler beim Laden der Strom-Statistiken: ${error.message}`, 'error');
    }
}

/**
 * Loads yearly electricity usage and costs data and renders the chart.
 */
async function loadElectricityYearlySummaryChart() {
    try {
        const yearlySummaryData = await ElectricityApi.getYearlySummary();

        const labels = yearlySummaryData.map(d => d.year);
        const totalUsages = yearlySummaryData.map(d => d.total_usage);
        const totalCosts = yearlySummaryData.map(d => d.total_costs);

        const ctx = document.getElementById('electricityYearlySummaryChart');
        if (!ctx) return; // Ensure canvas exists

        destroyChart('electricityYearlySummaryChart');

        const newChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Stromverbrauch (kWh)',
                        data: totalUsages,
                        backgroundColor: 'rgba(255, 206, 86, 0.7)',
                        borderColor: 'rgba(255, 206, 86, 1)',
                        borderWidth: 2,
                    },
                    {
                        label: 'Stromkosten (€)',
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
                            text: 'Verbrauch (kWh)',
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
                                if (context.dataset.label.includes('Verbrauch')) {
                                    label += context.parsed.y + ' kWh';
                                } else {
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
        storeChart('electricityYearlySummaryChart', newChart);
    } catch (error) {
        console.error('Error loading electricity yearly summary chart:', error);
        showMessage(`Fehler beim Laden des jährlichen Strom-Überblicks: ${error.message}`, 'error');
    }
}


/**
 * Loads electricity price trend data and renders the chart.
 */
async function loadElectricityPriceTrend() {
    try {
        const trendData = await ElectricityApi.getPriceTrend();

        const labels = trendData.map(d => d.year);
        const prices = trendData.map(d => d.average_price);

        const ctx = document.getElementById('electricityPriceChart');
        if (!ctx) return; // Ensure canvas exists

        destroyChart('electricityPriceChart');

        const newChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Strompreis (€/kWh)',
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
                            text: 'Preis (€/kWh)',
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
                                return context.dataset.label + ': ' + context.parsed.y + ' €/kWh';
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
        storeChart('electricityPriceChart', newChart);
    } catch (error) {
        console.error('Error loading electricity price trend:', error);
        showMessage(`Fehler beim Laden des Strom-Preisverlaufs: ${error.message}`, 'error');
    }
}

/**
 * Shows a confirmation dialog before deleting an electricity entry.
 * @param {number} id - The ID of the electricity entry to delete.
 */
function confirmDeleteElectricity(id) {
    showConfirm('Möchten Sie diesen Strom-Eintrag wirklich löschen?', () => deleteElectricityEntry(id));
}

/**
 * Deletes an electricity entry.
 * @param {number} id - The ID of the electricity entry to delete.
 */
async function deleteElectricityEntry(id) {
    try {
        await ElectricityApi.deleteEntry(id);
        showMessage('Strom-Eintrag erfolgreich gelöscht!', 'success');
        loadElectricityOverallStats();
        loadElectricityYearlySummaryChart();
        loadElectricityPriceTrend();
        loadElectricityEntries();
    } catch (error) {
        console.error('Error deleting electricity entry:', error);
        showMessage(`Fehler beim Löschen des Strom-Eintrags: ${error.message}`, 'error');
    }
}