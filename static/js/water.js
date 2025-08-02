import { WaterApi } from './api.js';
import { showMessage, showConfirm, formatNumber, formatCurrency, destroyChart, storeChart } from './ui.js';

/**
 * Initializes the Water section, attaches event listeners, and loads data.
 */
export function initializeWaterSection() {
    console.log('Initializing Water Section');
    const form = document.getElementById('waterForm');
    if (form) {
        form.addEventListener('submit', handleWaterFormSubmit);
    }

    // Automatically set the same value for wastewater as for water
    const volumeWaterInput = document.querySelector('input[name="volume_water"]');
    const volumeWastewaterInput = document.querySelector('input[name="volume_wastewater"]');
    if (volumeWaterInput && volumeWastewaterInput) {
        volumeWaterInput.addEventListener('input', () => {
            volumeWastewaterInput.value = volumeWaterInput.value;
        });
    }

    // Set default year to last year for submit
    const lastYear = new Date().getFullYear() - 1;
    document.getElementById("year").value = lastYear;

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
                <td>${entry.volume_water} m³</td>
                <td>${entry.volume_wastewater} m³</td>
                <td>${entry.volume_rainwater} m³</td>
                <td>${formatCurrency(entry.costs_water)}</td>
                <td>${formatCurrency(entry.costs_wastewater)}</td>
                <td>${formatCurrency(entry.costs_rainwater)}</td>
                <td>${formatCurrency(entry.price_water, 3)}/m³</td>
                <td>${formatCurrency(entry.price_wastewater, 3)}/m³</td>
                <td>${formatCurrency(entry.price_rainwater, 3)}/m³</td>
                <td>${formatCurrency(entry.fixed_price)}</td>
                <td>${formatCurrency(entry.costs)}</td>
                <td>${formatCurrency(entry.payments)}</td>
                <td>${formatCurrency(entry.monthly_payment)}/Monat</td>
                <td>${formatCurrency(entry.difference)}</td>
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
        document.getElementById("water_total_costs").textContent = formatNumber(stats.total_costs, 0);
        document.getElementById("water_number_of_years").textContent = stats.number_of_years;
        document.getElementById("water_average_volume").textContent = formatNumber(stats.average_volume, 0);
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
                        label: 'Volumen Wasser',
                        data: totalVolumeWater,
                        backgroundColor: 'rgba(0, 123, 255, 0.7)',
                        borderColor: 'rgba(0, 123, 255, 1)',
                        borderWidth: 2,
                        yAxisID: 'y-volume'
                    },
                    {
                        label: 'Kosten Wasser',
                        data: totalCostsWater,
                        backgroundColor: 'rgba(0, 150, 136, 0.7)',
                        borderColor: 'rgba(0, 150, 136, 1)',
                        borderWidth: 2,
                        yAxisID: 'y-costs'
                    },
                    {
                        label: 'Volumen Schmutzwasser',
                        data: totalVolumeWastewater,
                        backgroundColor: 'rgba(76, 175, 80, 0.7)',
                        borderColor: 'rgba(76, 175, 80, 1)',
                        borderWidth: 2,
                        yAxisID: 'y-volume'
                    },
                    {
                        label: 'Kosten Schmutzwasser',
                        data: totalCostsWastewater,
                        borderColor: 'rgba(33, 150, 243, 1)',
                        backgroundColor: 'rgba(33, 150, 243, 0.7)',
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
                        },
                        ticks: {
                            callback: function(value) {
                                return formatNumber(value) + ' m³';
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
                        ticks: {
                            callback: function(value) {
                                return formatNumber(value, 0) + " €";
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

                                // Check on usage or costs
                                if (context.dataset.yAxisID === 'y-volume') {
                                    label += formatNumber(context.parsed.y, 2) + ' m³';
                                } else if (context.dataset.yAxisID === 'y-costs') {
                                    label += formatCurrency(context.parsed.y);
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
 * Loads water price trend data and renders the chart dynamically.
 */
async function loadWaterPriceTrend() {
    try {
        const trendData = await WaterApi.getPriceTrend();

        if (trendData.length === 0) {
            console.warn("No trend data received from the API.");
            showMessage('Keine Daten für den Wasser-Preisverlauf verfügbar.', 'info');
            return;
        }

        // 1. Dynamically determine the start and end years from the data
        const years = trendData.map(d => d.year);
        const minYear = Math.min(...years);
        const maxYear = Math.max(...years);

        // 2. Create a complete list of all years for the x-axis labels
        const allYears = [];
        for (let year = minYear; year <= maxYear; year++) {
            allYears.push(year);
        }

        // 3. Create a map for efficient data lookup
        const dataMap = new Map(trendData.map(d => [d.year, d]));

        // 4. Prepare datasets, handling missing and zero values for gaps
        const pricesWater = allYears.map(year => dataMap.get(year)?.price_water ?? null);
        const pricesWastewater = allYears.map(year => dataMap.get(year)?.price_wastewater ?? null);
        
        // Handle rainwater price: `null` is returned from backend for missing data
        const pricesRainwater = allYears.map(year => dataMap.get(year)?.price_rainwater ?? null);
        
        // Handle fixed price: a `0` value from the backend means no price, so convert to `null`
        const pricesFixed = allYears.map(year => {
            const price = dataMap.get(year)?.price_fixed;
            // The price is considered "not available" if it's null or 0
            return (price === null || price === 0) ? null : price;
        });

        const ctx = document.getElementById('waterPriceChart');
        if (!ctx) return;

        destroyChart('waterPriceChart'); // Destroy previous chart instance

        const newChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: allYears, // Use the dynamically generated complete list of years
                datasets: [
                    {
                        label: 'Wasser (€/m³)',
                        data: pricesWater,
                        borderColor: 'rgb(0, 123, 255)',
                        backgroundColor: 'rgba(0, 123, 255, 0.2)',
                        tension: 0.2,
                        fill: false
                    },
                    {
                        label: 'Schmutzwasser (€/m³)',
                        data: pricesWastewater,
                        borderColor: 'rgb(76, 175, 80)',
                        backgroundColor: 'rgba(76, 175, 80, 0.2)',
                        tension: 0.2,
                        fill: false
                    },
                    {
                        label: 'Niederschlagswasser (€/m³)',
                        data: pricesRainwater,
                        borderColor: 'rgb(33, 150, 243)',
                        backgroundColor: 'rgba(33, 150, 243, 0.2)',
                        tension: 0.2,
                        fill: false
                    },
                    {
                        label: 'Festpreis (€)',
                        data: pricesFixed,
                        borderColor: 'rgb(0, 150, 136)',
                        backgroundColor: 'rgba(0, 150, 136, 0.2)',
                        tension: 0.2,
                        fill: false,
                        hidden: true
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
                            text: 'Preis',
                            font: {
                                size: 14,
                                weight: 'bold'
                            }
                        },
                        ticks: {
                            callback: function(value) {
                                return formatCurrency(value);
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
                                if (context.parsed.y === null) {
                                    return label + ': Daten nicht verfügbar';
                                }
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