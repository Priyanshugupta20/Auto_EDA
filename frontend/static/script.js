document.getElementById('uploadBtn').addEventListener('click', async () => {
    const fileInput = document.getElementById('fileInput');
    const loading = document.getElementById('loading');
    const errorDiv = document.getElementById('error');
    const resultsSection = document.getElementById('results');
    const edaFrame = document.getElementById("edaReportFrame");
    const downloadLink = document.getElementById('downloadLink');
    const downloadReport = document.getElementById('downloadReport');
    const overviewList = document.getElementById('overviewList');
    // const logContent = document.getElementById('logContent');

    // Reset state
    errorDiv.classList.add('hidden');
    resultsSection.classList.add('hidden');
    overviewList.innerHTML = '';
    logContent.textContent = '';
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
            overviewList.innerHTML = "<p><strong>Error:</strong> Overview data is missing.</p>";
        } else {
            let html = '<table class="overview-table">';

            // Shape
            if (ov.shape) {
                html += `
                    <tr><th>Rows</th><td>${ov.shape.rows}</td></tr>
                    <tr><th>Columns</th><td>${ov.shape.columns}</td></tr>
                `;
            }

            // Duplicates
            if (typeof ov.duplicates === 'number') {
                html += `<tr><th>Duplicate Rows</th><td>${ov.duplicates}</td></tr>`;
            }

            // Total memory usage
            if (ov.memory_usage?.total) {
                html += `<tr><th>Total Memory Usage</th><td>${ov.memory_usage.total}</td></tr>`;
            }

            // Missing values
            if (ov.missing_values) {
                html += `<tr><th>Missing Values</th><td>
                    <table>
                        ${Object.entries(ov.missing_values).map(([col, val]) => `<tr><td>${col}</td><td>${val}</td></tr>`).join('')}
                    </table>
                </td></tr>`;
            }

            // Data types
            if (ov.dtypes) {
                html += `<tr><th>Data Types</th><td>
                    <table>
                        ${Object.entries(ov.dtypes).map(([col, val]) => `<tr><td>${col}</td><td>${val}</td></tr>`).join('')}
                    </table>
                </td></tr>`;
            }

            // Outliers
            if (ov.outliers) {
                html += `<tr><th>Outliers</th><td>
                    <table>
                        ${Object.entries(ov.outliers).map(([col, val]) => `<tr><td>${col}</td><td>${val}</td></tr>`).join('')}
                    </table>
                </td></tr>`;
            }

            html += '</table>';
            overviewList.innerHTML = html;
        }



        // =========================
        // ⬇️ Populate Log (if any)
        // // =========================
        // if (result.log_report) {
        //     logContent.textContent = JSON.stringify(result.log_report, null, 2);
        // } else {
        //     logContent.innerHTML = "<em>No cleaning log provided.</em>";
        // }

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

