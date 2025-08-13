document.getElementById('uploadBtn').addEventListener('click', async () => {
    const fileInput = document.getElementById('fileInput');
    const loading = document.getElementById('loading');
    const errorDiv = document.getElementById('error');
    const resultsSection = document.getElementById('results');
    const edaDiv = document.getElementById('eda');
    const downloadLink = document.getElementById('downloadLink');

    // Reset state
    errorDiv.classList.add('hidden');
    resultsSection.classList.add('hidden');

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
        const response = await fetch("/api/clean-data", {
            method: "POST",
            body: formData
        });

        if (!response.ok) throw new Error("Server error during file processing.");

        const result = await response.json();
        loading.classList.add('hidden');

        // Show EDA
        edaDiv.innerHTML = `
            <h3>Dataset Summary</h3>
            <pre>${JSON.stringify(result.eda_summary, null, 2)}</pre>
        `;

        // Set download link
        downloadLink.href = result.cleaned_file_url;

        // Show results section
        resultsSection.classList.remove('hidden');

    } catch (err) {
        loading.classList.add('hidden');
        errorDiv.textContent = `❌ ${err.message}`;
        errorDiv.classList.remove('hidden');
    }
});
