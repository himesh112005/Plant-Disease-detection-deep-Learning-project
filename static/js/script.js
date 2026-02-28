document.addEventListener('DOMContentLoaded', () => {
    const dropArea = document.getElementById('drop-area');
    const fileInput = document.getElementById('file-input');
    const uploadContent = document.getElementById('upload-content');
    const previewContainer = document.getElementById('preview-container');
    const imagePreview = document.getElementById('image-preview');
    const removeBtn = document.getElementById('remove-btn');
    const submitBtn = document.getElementById('submit-btn');
    const loader = document.getElementById('loader');
    const errorMessage = document.getElementById('error-message');
    const resultsSection = document.getElementById('results-section');

    // Result elements
    const resultImgDisplay = document.getElementById('result-img-display');
    const diseaseName = document.getElementById('disease-name');
    const confidenceBar = document.getElementById('confidence-bar');
    const confidenceScore = document.getElementById('confidence-score');
    const remedyText = document.getElementById('remedy-text');

    let selectedFile = null;

    // Drag & Drop Events
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, () => dropArea.classList.add('drag-over'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, () => dropArea.classList.remove('drag-over'), false);
    });

    dropArea.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    }

    // File Input Event
    fileInput.addEventListener('change', function () {
        handleFiles(this.files);
    });

    function handleFiles(files) {
        if (files.length === 0) return;

        const file = files[0];

        // Ensure it's an image
        if (!file.type.match('image.*')) {
            showError("Please upload an image file (JPG, PNG, etc).");
            return;
        }

        selectedFile = file;
        hideError();
        showPreview(file);
    }

    function showPreview(file) {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onloadend = function () {
            imagePreview.src = reader.result;
            resultImgDisplay.src = reader.result; // Also set result image

            uploadContent.classList.add('hidden');
            previewContainer.classList.remove('hidden');

            // Enable submit button
            submitBtn.disabled = false;
            submitBtn.classList.remove('disabled');
        }
    }

    // Remove Image
    removeBtn.addEventListener('click', (e) => {
        e.stopPropagation(); // prevent clicking drop-area
        clearSelection();
    });

    function clearSelection() {
        selectedFile = null;
        fileInput.value = '';
        imagePreview.src = '';

        previewContainer.classList.add('hidden');
        uploadContent.classList.remove('hidden');

        // Disable submit button
        submitBtn.disabled = true;
        submitBtn.classList.add('disabled');

        // Hide results
        resultsSection.classList.add('hidden');
        hideError();
    }

    // Show/Hide Errors
    function showError(msg) {
        errorMessage.textContent = msg;
        errorMessage.classList.remove('hidden');
    }

    function hideError() {
        errorMessage.classList.add('hidden');
    }

    // Form Submission
    submitBtn.addEventListener('click', async () => {
        if (!selectedFile) return;

        // Hide old results, show loader, disable button
        resultsSection.classList.add('hidden');
        submitBtn.classList.add('hidden');
        loader.classList.remove('hidden');
        hideError();

        // Reset progress bar
        confidenceBar.style.width = '0%';
        confidenceScore.textContent = '0%';

        const formData = new FormData();
        formData.append('image', selectedFile);

        try {
            const response = await fetch('/predict', {
                method: 'POST',
                body: formData
            });

            let data;
            const contentType = response.headers.get("content-type");
            if (contentType && contentType.includes("application/json")) {
                data = await response.json();
                if (!response.ok) {
                    throw new Error(data.error || 'Failed to process the image.');
                }
            } else {
                const textDetail = await response.text();
                throw new Error(`Server error (${response.status}): The server ran out of memory or timed out. Please try again!`);
            }

            displayResults(data);

        } catch (error) {
            showError("Error: " + error.message);
        } finally {
            // Hide loader, show button again
            loader.classList.add('hidden');
            submitBtn.classList.remove('hidden');
        }
    });

    function displayResults(data) {
        // Update DOM
        diseaseName.textContent = data.disease;
        remedyText.textContent = data.remedy;

        let confidenceVal = parseFloat(data.confidence);

        // Show section
        resultsSection.classList.remove('hidden');

        // Scroll to results
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });

        // Animate confidence bar
        setTimeout(() => {
            confidenceBar.style.width = `${confidenceVal}%`;

            // Number increment animation
            let start = 0;
            const duration = 1500; // ms
            const stepTime = 20;
            const steps = duration / stepTime;
            const increment = confidenceVal / steps;

            let timer = setInterval(() => {
                start += increment;
                if (start >= confidenceVal) {
                    clearInterval(timer);
                    start = confidenceVal;
                }
                confidenceScore.textContent = `${start.toFixed(2)}%`;
            }, stepTime);

            // Adjust bar color based on confidence
            if (confidenceVal < 60) {
                confidenceBar.style.background = 'linear-gradient(90deg, #f39c12, #e74c3c)';
            } else if (confidenceVal < 85) {
                confidenceBar.style.background = 'linear-gradient(90deg, #f1c40f, #2ecc71)';
            } else {
                confidenceBar.style.background = 'linear-gradient(90deg, #27ae60, #2ecc71)';
            }

        }, 300); // small delay to allow DOM render before animating width
    }
});
