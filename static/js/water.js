import { WaterApi } from './api.js';
import { showMessage, showConfirm, destroyChart, storeChart } from './ui.js';

/**
 * Initializes the Water section, attaches event listeners, and loads data.
 */
export function initializeWaterSection() {
    console.log('Initializing Water Section');
    const form = document.getElementById('waterForm');
    if (form) {
        form.addEventListener('submit', handleWaterFormSubmit);
    }

    loadWaterOverallStats();
    loadWaterYearlySummaryChart();
    loadWaterPriceTrend();
    loadWaterEntries();
}

/**
 * Handles the submission of the new water entry form.
 * @param {Event} event - The form submission event.
 */
async function handleWaterFormSubmit(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);

    const data = {
        year: parseInt(formData.get('year')),
        volumeWater: parseInt(formData.get('volume_water')),
        volumeWastewater: parseFloat(formData.get('volume_wastewater')),
        volumeRainwater: parseFloat(formData.get('volume_rainwater')),
        costsWater: parseFloat(formData.get('costs_water')),
        costsWastewater: parseFloat(formData.get('costs_wastewater')),
        costsRainwater: parseFloat(formData.get('costs_rainwater')),
        payments: parseFloat(formData.get('payments')),
        fixedPrice: parseFloat(formData.get('fixed_price')),
        note: formData.get('note') || null
    };

    try {
        await WaterApi.addEntry(data);
        showMessage('Wasser-Eintrag erfolgreich hinzugefügt!', 'success');
        form.reset();
        loadWaterOverallStats();
        loadWaterYearlySummaryChart();
        loadWaterPriceTrend();
        loadWaterEntries();
    } catch (error) {
        console.error('Error adding water entry:', error);
        showMessage(`Fehler beim Hinzufügen des Wasser-Eintrags: ${error.message}`, 'error');
    }
}

/**
 * Loads and displays all water entries in the table.
 */
async function loadWaterEntries() {
    try {
        const entries = await WaterApi.getEntries();
        const tableBody = document.getElementById('water-entries-table-body');
        if (!tableBody) return;

        tableBody.innerHTML = ''; // Clear existing entries

        entries.forEach(entry => {
            const row = tableBody.insertRow();
            row.dataset.id = entry.id; // Store ID on the row

            row.innerHTML = `
                <td>${entry.year}</td>
                <td>${entry.volume_water}</td>
                <td>${entry.volume_wastewater}</td>
                <td>${entry.volume_rainwater}</td>
                <td>${entry.costs_water}</td>
                <td>${entry.costs_wastewater}</td>
                <td>${entry.costs_rainwater}</td>
                <td>${entry.price_water}</td>
                <td>${entry.price_wastewater}</td>
                <td>${entry.price_rainwater}</td>
                <td>${entry.fixed_price}</td>
                <td>${entry.payments}</td>
                <td>${entry.monthly_payment}</td>
                <td>${entry.difference}</td>
                <td>${entry.note || ''}</td>
                <td>
                    <button class="btn-delete" data-id="${entry.id}">Löschen</button>
                </td>
            `;
            // Attach event listeners directly after creation for efficiency
            row.querySelector('.btn-delete').addEventListener('click', () => confirmDeleteWater(entry.id));
        });
    } catch (error) {
        console.error('Error loading water entries:', error);
        showMessage(`Fehler beim Laden der Wasser-Einträge: ${error.message}`, 'error');
    }
}

/**
 * Loads and displays overall water statistics.
 */
async function loadWaterOverallStats() {
    try {
        const stats = await WaterApi.getOverallStats();
        document.getElementById("water_total_volume").textContent = stats.total_volume;
        document.getElementById("water_total_costs").textContent = stats.total_costs;
        document.getElementById("water_number_of_years").textContent = stats.number_of_years;
        document.getElementById("water_average_volume").textContent = stats.average_volume;
    } catch (error) {
        console.error('Error loading water overall stats:', error);
        showMessage(`Fehler beim Laden der Wasser-Statistiken: ${error.message}`, 'error');
    }
}

/**
 * Loads yearly water usage and costs data and renders the chart.
 */
async function loadWaterYearlySummaryChart() {
    try {
        const yearlySummaryData = await WaterApi.getYearlySummary();

        const labels = yearlySummaryData.map(d => d.year);
        const totalVolumeWater = yearlySummaryData.map(d => d.volume_water);
        const totalCostsWater = yearlySummaryData.map(d => d.costs_water);
        const totalVolumeWastewater = yearlySummaryData.map(d => d.volume_wastewater);
        const totalCostsWastewater = yearlySummaryData.map(d => d.costs_wastewater);

        const ctx = document.getElementById('waterYearlySummaryChart');
        if (!ctx) return;

        destroyChart('waterYearlySummaryChart'); // Destroy previous chart instance

        const newChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Volumen Wasser (m³)',
                        data: totalVolumeWater,
                        backgroundColor: 'rgba(255, 206, 86, 0.7)',
                        borderColor: 'rgba(255, 206, 86, 1)',
                        borderWidth: 2,
                        yAxisID: 'y-volume'
                    },
                    {
                        label: 'Kosten Wasser (€)',
                        data: totalCostsWater,
                        backgroundColor: 'rgba(75, 192, 192, 0.7)',
                        borderColor: 'rgba(75, 192, 192, 1)',
                        borderWidth: 2,
                        yAxisID: 'y-costs'
                    },
                    {
                        label: 'Volumen Schmutzwasser (m³)',
                        data: totalVolumeWastewater,
                        backgroundColor: 'rgba(153, 102, 255, 0.7)',
                        borderColor: 'rgba(153, 102, 255, 1)',
                        borderWidth: 2,
                        yAxisID: 'y-volume'
                    },
                    {
                        label: 'Kosten Schmutzwasser (€)',
                        data: totalCostsWastewater,
                        borderColor: 'rgba(55, 43, 223, 1)',
                        backgroundColor: 'rgba(94, 118, 255, 1)',
                        borderWidth: 2,
                        yAxisID: 'y-costs'
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
                                if (label.includes('Volumen')) {
                                    label += context.parsed.y + ' m³';
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
        storeChart('waterYearlySummaryChart', newChart);
    } catch (error) {
        console.error('Error loading water yearly summary chart:', error);
        showMessage(`Fehler beim Laden des jährlichen Wasser-Überblicks: ${error.message}`, 'error');
    }
}

/**
 * Loads water price trend data and renders the chart.
 */
async function loadWaterPriceTrend() {
    try {
        const trendData = await WaterApi.getPriceTrend();

        const labels = trendData.map(d => d.year);
        const pricesWater = trendData.map(d => d.price_water);
        const pricesWastewater = trendData.map(d => d.price_wastewater);
        const pricesRainwater = trendData.map(d => d.price_rainwater);
        const pricesFixed = trendData.map(d => d.fixed_price);

        const ctx = document.getElementById('waterPriceChart');
        if (!ctx) return;

        destroyChart('waterPriceChart'); // Destroy previous chart instance

        const newChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Wasser (€/m³)',
                        data: pricesWater,
                        borderColor: 'rgb(60, 179, 113)',
                        backgroundColor: 'rgba(60, 179, 113, 0.2)',
                        tension: 0.2,
                        fill: false
                    },
                    {
                        label: 'Schmutzwasser (€/m³)',
                        data: pricesWastewater,
                        borderColor: 'rgb(128, 128, 128)',
                        backgroundColor: 'rgba(128, 128, 128, 0.2)',
                        tension: 0.2,
                        fill: false
                    },
                    {
                        label: 'Niederschlagswasser (€/m³)',
                        data: pricesRainwater,
                        borderColor: 'rgb(70, 130, 180)',
                        backgroundColor: 'rgba(70, 130, 180, 0.2)',
                        tension: 0.2,
                        fill: false
                    },
                    {
                        label: 'Festpreis (€)',
                        data: pricesFixed,
                        borderColor: 'rgb(148, 0, 211)',
                        backgroundColor: 'rgba(148, 0, 211, 0.2)',
                        tension: 0.2,
                        fill: false
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Preis (€)',
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
                                let label = context.dataset.label || '';
                                if (label) {
                                    label += ': ';
                                }
                                if (label.includes('Festpreis')) {
                                    return label + context.parsed.y + ' €';
                                } else {
                                    return label + context.parsed.y + ' €/m³';
                                }
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
        storeChart('waterPriceChart', newChart);
    } catch (error) {
        console.error('Error loading water price trend:', error);
        showMessage(`Fehler beim Laden des Wasser-Preisverlaufs: ${error.message}`, 'error');
    }
}

/**
 * Shows a confirmation dialog before deleting a water entry.
 * @param {number} id - The ID of the water entry to delete.
 */
function confirmDeleteWater(id) {
    showConfirm('Möchten Sie diesen Wasser-Eintrag wirklich löschen?', () => deleteWaterEntry(id));
}

/**
 * Deletes a water entry.
 * @param {number} id - The ID of the water entry to delete.
 */
async function deleteWaterEntry(id) {
    try {
        await WaterApi.deleteEntry(id);
        showMessage('Wasser-Eintrag erfolgreich gelöscht!', 'success');
        loadWaterOverallStats();
        loadWaterYearlySummaryChart();
        loadWaterPriceTrend();
        loadWaterEntries();
    } catch (error) {
        console.error('Error deleting water entry:', error);
        showMessage(`Fehler beim Löschen des Wasser-Eintrags: ${error.message}`, 'error');
    }
}