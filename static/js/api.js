const API_BASE_ELECTRICITY = '/electricity';
const API_BASE_OIL = '/oil';
const API_BASE_WATER = '/water';

/**
 * Generic API request handler.
 * @param {string} url - The API endpoint URL.
 * @param {string} method - HTTP method (GET, POST, DELETE).
 * @param {Object} [data=null] - Data to send with POST requests.
 * @returns {Promise<Object|void>} - The JSON response or void for 204.
 * @throws {Error} - If the API request fails.
 */
async function apiRequest(url, method, data = null) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        },
    };

    if (data) {
        options.body = JSON.stringify(data);
    }

    const response = await fetch(url, options);

if (!response.ok) {
    let errorDetail = 'Unbekannter Fehler';
    try {
        const errorData = await response.json();
        // If errorData.detail is an array (common for Pydantic validation errors), join them.
        // Otherwise, use it directly.
        if (Array.isArray(errorData.detail)) {
            errorDetail = errorData.detail.map(err => `${err.loc.join('.')} -> ${err.msg}`).join('; ');
        } else {
            errorDetail = errorData.detail || errorDetail;
        }
    } catch (e) {
        errorDetail = response.statusText;
    }
    throw new Error(`HTTP error! Status: ${response.status}, Detail: ${errorDetail}`);
}

    // For DELETE requests with 204 No Content, response.json() would throw an error
    if (response.status === 204) {
        return;
    }

    return response.json();
}

// --- Electricity API Functions ---

export const ElectricityApi = {
    async getEntries() {
        return apiRequest(`${API_BASE_ELECTRICITY}/entries`, 'GET');
    },
    async addEntry(data) {
        return apiRequest(`${API_BASE_ELECTRICITY}/entries`, 'POST', data);
    },
    async getEntry(id) {
        return apiRequest(`${API_BASE_ELECTRICITY}/entries/${id}`, 'GET');
    },
    async updateEntry(id, data) {
        return apiRequest(`${API_BASE_ELECTRICITY}/entries/${id}`, 'PUT', data);
    },
    async deleteEntry(id) {
        return apiRequest(`${API_BASE_ELECTRICITY}/entries/${id}`, 'DELETE');
    },
    async getOverallStats() {
        return apiRequest(`${API_BASE_ELECTRICITY}/stats/overall`, 'GET');
    },
    async getPriceTrend() {
        return apiRequest(`${API_BASE_ELECTRICITY}/stats/price_trend`, 'GET');
    },
    async getYearlySummary() {
        return apiRequest(`${API_BASE_ELECTRICITY}/stats/yearly_summary`, 'GET');
    }
};

// --- Oil API Functions ---

export const OilApi = {
    async getEntries() {
        return apiRequest(`${API_BASE_OIL}/entries`, 'GET');
    },
    async addEntry(data) {
        return apiRequest(`${API_BASE_OIL}/entries`, 'POST', data);
    },
    async getEntry(id) {
        return apiRequest(`${API_BASE_OIL}/entries/${id}`, 'GET');
    },
    async deleteEntry(id) {
        return apiRequest(`${API_BASE_OIL}/entries/${id}`, 'DELETE');
    },
    async getOverallStats() {
        return apiRequest(`${API_BASE_OIL}/stats/overall`, 'GET');
    },
    async getPriceTrend() {
        return apiRequest(`${API_BASE_OIL}/stats/price_trend`, 'GET');
    },
    async getYearlySummary() {
        return apiRequest(`${API_BASE_OIL}/stats/yearly_summary`, 'GET');
    }
};

// --- Water API Functions ---

export const WaterApi = {
    async getEntries() {
        return apiRequest(`${API_BASE_WATER}/entries`, 'GET');
    },
    async addEntry(data) {
        return apiRequest(`${API_BASE_WATER}/entries`, 'POST', data);
    },
    async getEntry(id) {
        return apiRequest(`${API_BASE_WATER}/entries/${id}`, 'GET');
    },
    async updateEntry(id, data) {
        return apiRequest(`${API_BASE_WATER}/entries/${id}`, 'PUT', data);
    },
    async deleteEntry(id) {
        return apiRequest(`${API_BASE_WATER}/entries/${id}`, 'DELETE');
    },
    async getOverallStats() {
        return apiRequest(`${API_BASE_WATER}/stats/overall`, 'GET');
    },
    async getPriceTrend() {
        return apiRequest(`${API_BASE_WATER}/stats/price_trend`, 'GET');
    },
    async getYearlySummary() {
        return apiRequest(`${API_BASE_WATER}/stats/yearly_summary`, 'GET');
    }
};