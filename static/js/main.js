let currentPage = 1;
const itemsPerPage = 10;
let totalSamples = 0;

async function loadSamples(page = 1, search = '') {
    const skip = (page - 1) * itemsPerPage;
    const url = `/samples?skip=${skip}&limit=${itemsPerPage}&search=${encodeURIComponent(search)}`;
    
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const samples = await response.json();
        displaySamples(samples);
        
        // Update pagination buttons
        updatePaginationButtons(samples.length);
        
        // If no samples found, show message
        if (samples.length === 0) {
            const container = document.getElementById('samplesList');
            container.innerHTML = '<div class="sample-card"><p>No samples found</p></div>';
        }
    } catch (error) {
        console.error('Error loading samples:', error);
        showError('Failed to load samples. Please try again later.');
    }
}

function displaySamples(samples) {
    const container = document.getElementById('samplesList');
    container.innerHTML = '';
    
    samples.forEach(sample => {
        const card = document.createElement('div');
        card.className = 'sample-card';
        
        const description = sample.description || 'No description available';
        const wordCount = sample.word_count || 'N/A';
        const readTime = sample.read_time || 'N/A';
        
        card.innerHTML = `
            <h2>${escapeHtml(sample.title)}</h2>
            <p>${escapeHtml(description)}</p>
            <p>Word Count: ${escapeHtml(String(wordCount))}</p>
            <p>Read Time: ${escapeHtml(String(readTime))}</p>
        `;
        
        // Add click handler to view full sample
        card.addEventListener('click', () => viewSample(sample._id));
        container.appendChild(card);
    });
}

function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

async function viewSample(sampleId) {
    try {
        const response = await fetch(`/samples/${sampleId}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const sample = await response.json();
        showSampleModal(sample);
    } catch (error) {
        console.error('Error loading sample:', error);
        showError('Failed to load sample details.');
    }
}

function showSampleModal(sample) {
    // Create modal container
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-content">
            <span class="close">&times;</span>
            <h2>${escapeHtml(sample.title)}</h2>
            <div class="sample-sections">
                ${Object.entries(sample.sections).map(([key, value]) => `
                    <div class="section">
                        <h3>${escapeHtml(key.replace('_', ' ').toUpperCase())}</h3>
                        <p>${escapeHtml(value.content)}</p>
                        ${value.checklist_items.length ? `
                            <h4>Checklist:</h4>
                            <ul>
                                ${value.checklist_items.map(item => `
                                    <li>${escapeHtml(item)}</li>
                                `).join('')}
                            </ul>
                        ` : ''}
                    </div>
                `).join('')}
            </div>
        </div>
    `;
    
    // Add close functionality
    modal.querySelector('.close').onclick = () => {
        document.body.removeChild(modal);
    };
    
    document.body.appendChild(modal);
}

function loadPrevious() {
    if (currentPage > 1) {
        currentPage--;
        loadSamples(currentPage, document.getElementById('searchInput').value);
        updatePageInfo();
    }
}

function loadNext() {
    currentPage++;
    loadSamples(currentPage, document.getElementById('searchInput').value);
    updatePageInfo();
}

function updatePageInfo() {
    document.getElementById('pageInfo').textContent = `Page ${currentPage}`;
}

function updatePaginationButtons(samplesCount) {
    const prevButton = document.querySelector('.pagination button:first-child');
    const nextButton = document.querySelector('.pagination button:last-child');
    
    prevButton.disabled = currentPage === 1;
    nextButton.disabled = samplesCount < itemsPerPage;
}

function searchSamples() {
    const query = document.getElementById('searchInput').value;
    currentPage = 1;
    loadSamples(currentPage, query);
    updatePageInfo();
}

function showError(message) {
    const container = document.getElementById('samplesList');
    container.innerHTML = `
        <div class="error-message">
            <p>${escapeHtml(message)}</p>
        </div>
    `;
}

// Add search on enter key
document.getElementById('searchInput').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        searchSamples();
    }
});

// Load initial samples
loadSamples();