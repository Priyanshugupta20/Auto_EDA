// script.js

document.getElementById('uploadBtn').addEventListener('click', async () => {
    const fileInput = document.getElementById('fileInput');
    const loading = document.getElementById('loading');
    const errorDiv = document.getElementById('error');
    const resultsSection = document.getElementById('results');
    const edaLink = document.getElementById('edaLink');
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

    // Show loading indicator
    loading.classList.remove('hidden');

    try {
        // Backend API call. The URL is corrected to match app.py's endpoint.
        const response = await fetch("http://127.0.0.1:5000/upload", {
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

        // Set the link to view the EDA report
        edaLink.href = `http://127.0.0.1:5000/eda/${result.eda_report}`;
        edaLink.classList.remove('hidden');

        // Set the download link for the cleaned file
        downloadLink.href = `http://127.0.0.1:5000/download/${result.cleaned_file}`;
        downloadLink.classList.remove('hidden');

        // Show the results section
        resultsSection.classList.remove('hidden');
        
        // Hide the EDA section text that was there before.
        document.getElementById('eda').classList.add('hidden');

    } catch (err) {
        loading.classList.add('hidden');
        errorDiv.textContent = `❌ ${err.message}`;
        errorDiv.classList.remove('hidden');
    }
});
