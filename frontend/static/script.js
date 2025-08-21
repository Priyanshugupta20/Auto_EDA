document.getElementById('uploadBtn').addEventListener('click', async () => {
    const fileInput = document.getElementById('fileInput');
    const loading = document.getElementById('loading');
    const errorDiv = document.getElementById('error');
    const resultsSection = document.getElementById('results');
    const edaFrame = document.getElementById("edaReportFrame");
    const downloadLink = document.getElementById('downloadLink');
    const downloadReport = document.getElementById('downloadReport');
    const basicStats = document.getElementById("basicStats");
    const missingStats = document.getElementById("missingStats");
    const dtypeStats = document.getElementById("dtypeStats");
    const logContent = document.getElementById('logContent');

    // Reset UI state
    errorDiv.classList.add('hidden');
    resultsSection.classList.add('hidden');
    basicStats.innerHTML = '';
    missingStats.innerHTML = '';
    dtypeStats.innerHTML = '';
    logContent.innerHTML = '';
    edaFrame.src = '';
    downloadLink.href = '#';
    downloadReport.href = '#';

    const file = fileInput.files[0];
    if (!file) {
        errorDiv.textContent = "⚠ Please select a file before uploading.";
        errorDiv.classList.remove('hidden');
        return;
    }

    loading.classList.remove('hidden');

    try {
        const result = await uploadFileInChunks(file);
        loading.classList.add('hidden');

        const ov = result.overview;
        if (!ov || typeof ov !== 'object') {
            document.getElementById("overviewContainer").innerHTML = "<p><strong>Error:</strong> Overview data is missing.</p>";
        } else {
            // Basic Info
            let basicHtml = '<h3>Basic Info</h3><table>';
            if (ov.shape) {
                basicHtml += `<tr><td>Rows</td><td>${ov.shape.rows}</td></tr>`;
                basicHtml += `<tr><td>Columns</td><td>${ov.shape.columns}</td></tr>`;
            }
            if (typeof ov.duplicates === 'number') {
                basicHtml += `<tr><td>Duplicate Rows</td><td>${ov.duplicates}</td></tr>`;
            }
            if (ov.memory_usage?.total) {
                basicHtml += `<tr><td>Memory Usage</td><td>${ov.memory_usage.total}</td></tr>`;
            }
            basicHtml += '</table>';
            basicStats.innerHTML = basicHtml;

            // Missing Values
            let missingHtml = '<h3>Missing Values</h3><table>';
            if (ov.missing_values && Object.keys(ov.missing_values).length > 0) {
                for (const [col, count] of Object.entries(ov.missing_values)) {
                    missingHtml += `<tr><td>${col}</td><td>${count}</td></tr>`;
                }
            } else {
                missingHtml += `<tr><td colspan="2"><em>No missing values</em></td></tr>`;
            }
            missingHtml += '</table>';
            missingStats.innerHTML = missingHtml;

            // Data Types
            let dtypeHtml = '<h3>Data Types</h3><table>';
            if (ov.dtypes && Object.keys(ov.dtypes).length > 0) {
                for (const [col, dtype] of Object.entries(ov.dtypes)) {
                    dtypeHtml += `<tr><td>${col}</td><td>${dtype}</td></tr>`;
                }
            } else {
                dtypeHtml += `<tr><td colspan="2"><em>No dtype info</em></td></tr>`;
            }
            dtypeHtml += '</table>';
            dtypeStats.innerHTML = dtypeHtml;
        }

        // Log Report
        if (result.log_report && result.log_report.length > 0) {
            logContent.innerHTML = '';
            result.log_report.forEach(step => {
                if (step.length !== 0) {
                    const table = document.createElement('table');
                    table.classList.add('log-table');

                    const headers = Object.keys(step[0]);
                    const thead = document.createElement('thead');
                    const headerRow = document.createElement('tr');
                    headers.forEach(key => {
                        const th = document.createElement('th');
                        th.textContent = key;
                        headerRow.appendChild(th);
                    });
                    thead.appendChild(headerRow);
                    table.appendChild(thead);

                    const tbody = document.createElement('tbody');
                    step.forEach(entry => {
                        const row = document.createElement('tr');
                        headers.forEach(key => {
                            const td = document.createElement('td');
                            const value = entry[key];
                            td.textContent = typeof value === 'object' && value !== null ? JSON.stringify(value) : value;
                            row.appendChild(td);
                        });
                        tbody.appendChild(row);
                    });

                    table.appendChild(tbody);
                    logContent.appendChild(table);
                }
            });
        } else {
            logContent.innerHTML = "<em>No cleaning log provided.</em>";
        }

        // Show reports
        edaFrame.src = `/eda/${result.eda_report}`;
        downloadReport.href = `/eda/${result.eda_report}`;
        downloadReport.download = result.eda_report;

        downloadLink.href = `/download/${result.cleaned_file}`;
        downloadLink.download = result.cleaned_file;
        downloadLink.classList.remove("hidden");

        resultsSection.classList.remove('hidden');

    } catch (err) {
        loading.classList.add('hidden');
        errorDiv.textContent = `❌ ${err.message}`;
        errorDiv.classList.remove('hidden');
    }
});

// ========== ⬇️ Chunked Upload Logic ==========

async function uploadFileInChunks(file) {
    const chunkSize = 2 * 1024 * 1024; // 2MB
    const totalChunks = Math.ceil(file.size / chunkSize);
    const fileId = Date.now().toString();

    for (let i = 0; i < totalChunks; i++) {
        const start = i * chunkSize;
        const end = Math.min(start + chunkSize, file.size);
        const chunk = file.slice(start, end);

        const formData = new FormData();
        formData.append('file_id', fileId);
        formData.append('chunk_index', i);
        formData.append('total_chunks', totalChunks);
        formData.append('file', chunk);

        const response = await fetch('/upload_chunk', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`Upload failed at chunk ${i}`);
        }
    }

    // Merge and process file
    const mergeResponse = await fetch('/merge_chunks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            file_id: fileId,
            filename: file.name
        })
    });

    if (!mergeResponse.ok) {
        const errorData = await mergeResponse.json();
        throw new Error(errorData.error || "Merge or processing failed.");
    }

    return await mergeResponse.json();
}
