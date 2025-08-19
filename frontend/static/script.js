document.getElementById('uploadBtn').addEventListener('click', async () => {
    const fileInput = document.getElementById('fileInput');
    const loading = document.getElementById('loading');
    const errorDiv = document.getElementById('error');
    const resultsSection = document.getElementById('results');
    const edaFrame = document.getElementById("edaReportFrame");
    const downloadLink = document.getElementById('downloadLink');
    const downloadReport = document.getElementById('downloadReport');
    const basicStats = document.getElementById("basicStats").innerHTML = '';
    const missingStats = document.getElementById("missingStats").innerHTML = '';
    const dtypeStats = document.getElementById("dtypeStats").innerHTML = '';
    const logContent = document.getElementById('logContent');

    // Reset state
    errorDiv.classList.add('hidden');
    resultsSection.classList.add('hidden');
    basicStats.innerHTML = '';
    missingStats.innerHTML = '';
    dtypeStats.innerHTML = '';
    logContent.innerHTML = '';
    edaFrame.src = '';
    downloadLink.href = '#';
    downloadReport.href = '#';

    if (!fileInput.files.length) {
        errorDiv.textContent = "⚠ Please select a file before uploading.";
        errorDiv.classList.remove('hidden');
        return;
    }

    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append("file", file);

    // Show loading
    loading.classList.remove('hidden');

    try {
        // Backend API call
        const response = await fetch("/upload", {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            // Get the server error message if available
            const errorData = await response.json();
            throw new Error(errorData.error || "Server error during file processing.");
        }

        const result = await response.json();
        loading.classList.add('hidden');

        // ========================
        // ⬇️ Populate Overview Info
        // ========================
        const ov = result.overview;

        if (!ov || typeof ov !== 'object') {
            document.getElementById("overviewContainer").innerHTML = "<p><strong>Error:</strong> Overview data is missing.</p>";
        } else {
            // ➤ Basic Stats Block
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
            document.getElementById("basicStats").innerHTML = basicHtml;

            // ➤ Missing Values Block
            let missingHtml = '<h3>Missing Values</h3><table>';
            if (ov.missing_values && Object.keys(ov.missing_values).length > 0) {
                for (const [col, count] of Object.entries(ov.missing_values)) {
                    missingHtml += `<tr><td>${col}</td><td>${count}</td></tr>`;
                }
            } else {
                missingHtml += `<tr><td colspan="2"><em>No missing values</em></td></tr>`;
            }
            missingHtml += '</table>';
            document.getElementById("missingStats").innerHTML = missingHtml;

            // ➤ Data Types Block
            let dtypeHtml = '<h3>Data Types</h3><table>';
            if (ov.dtypes && Object.keys(ov.dtypes).length > 0) {
                for (const [col, dtype] of Object.entries(ov.dtypes)) {
                    dtypeHtml += `<tr><td>${col}</td><td>${dtype}</td></tr>`;
                }
            } else {
                dtypeHtml += `<tr><td colspan="2"><em>No dtype info</em></td></tr>`;
            }
            dtypeHtml += '</table>';
            document.getElementById("dtypeStats").innerHTML = dtypeHtml;
        }

        // =========================
        // ⬇️ Populate Log (if any)
        // =========================
        if (result.log_report && result.log_report.length > 0) {
        logContent.innerHTML = '';  // Clear previous content
        console.log(result.log_report)

        result.log_report.forEach((step, stepIndex) => {

            if (step.length !== 0) {

                const table = document.createElement('table');
                table.classList.add('log-table');

                // Table headers (based on keys of first entry)
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

                // Table rows
                const tbody = document.createElement('tbody');
                step.forEach(entry => {
                    const row = document.createElement('tr');
                    headers.forEach(key => {
                        const td = document.createElement('td');
                        const value = entry[key];

                        if (typeof value === 'object' && value !== null) {
                            td.textContent = JSON.stringify(value);
                        } else {
                            td.textContent = value;
                        }

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


        // Show EDA
        edaFrame.src = `/eda/${result.eda_report}`;

        downloadReport.href = `/eda/${result.eda_report}`;
        downloadReport.download = result.eda_report;

        // Set download link
        downloadLink.href = `/download/${result.cleaned_file}`;
        downloadLink.download = result.cleaned_file;
        downloadLink.classList.remove("hidden");

        // Show results section
        resultsSection.classList.remove('hidden');

    } catch (err) {
        loading.classList.add('hidden');
        errorDiv.textContent = `❌ ${err.message}`;
        errorDiv.classList.remove('hidden');
    }
});