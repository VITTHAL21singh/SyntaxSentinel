document.addEventListener('DOMContentLoaded', () => {
    // UI Elements
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const uploadText = document.getElementById('upload-text');
    const filePreview = document.getElementById('file-preview');
    const userQuery = document.getElementById('user-query');
    const sendBtn = document.getElementById('send-btn');
    const errorBanner = document.getElementById('error-banner');
    const loadingState = document.getElementById('loading-state');
    const resultCard = document.getElementById('result-card');

    // Result Fields
    const vulnTitle = document.getElementById('vuln-title');
    const vulnSeverity = document.getElementById('vuln-severity');
    const vulnRemediation = document.getElementById('vuln-remediation');

    let selectedFile = null;

    function showError(message) {
        if (!errorBanner) return;
        errorBanner.textContent = message;
        errorBanner.classList.remove('hidden');
    }

    function clearError() {
        if (!errorBanner) return;
        errorBanner.textContent = '';
        errorBanner.classList.add('hidden');
    }

    function handleFile(file) {
        if (!file) return;

        // Verify valid image type
        const validExtensions = ['.png', '.jpg', '.jpeg', '.webp', '.bmp', '.gif'];
        const fileName = file.name.toLowerCase();
        const isValidExtension = validExtensions.some(ext => fileName.endsWith(ext));
        const isValidMime = file.type.startsWith('image/');

        if (!isValidMime && !isValidExtension) {
            showError('Invalid file type. Please upload an image (PNG, JPG, JPEG, WEBP, BMP, or GIF).');
            return;
        }

        // Limit size to 16MB
        if (file.size > 16 * 1024 * 1024) {
            showError('File is too large. Maximum size is 16MB.');
            return;
        }

        clearError();
        selectedFile = file;

        // Provide immediate visual feedback
        const sizeFormatted = (file.size / 1024).toFixed(1);
        dropZone.classList.add('has-file');
        uploadText.innerHTML = `<strong>Selected:</strong> ${file.name}`;
        
        filePreview.textContent = `Size: ${sizeFormatted} KB | Type: ${file.type || 'image'}`;
        filePreview.classList.remove('hidden');
    }

    // Trigger file browser when clicking drop zone
    dropZone.addEventListener('click', (e) => {
        if (e.target !== fileInput) {
            fileInput.click();
        }
    });

    // Keyboard accessibility for drop zone
    dropZone.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            fileInput.click();
        }
    });

    // Capture file selection from input
    fileInput.addEventListener('change', (e) => {
        if (e.target.files && e.target.files.length > 0) {
            handleFile(e.target.files[0]);
        }
    });

    // Drag and drop event listeners
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.add('drag-over');
        });
    });

    ['dragleave', 'dragend'].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.remove('drag-over');
        });
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropZone.classList.remove('drag-over');

        if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            handleFile(e.dataTransfer.files[0]);
        }
    });

    // Trigger audit on button click
    sendBtn.addEventListener('click', async () => {
        clearError();

        if (!selectedFile) {
            showError('Please browse or drag & drop an image before running the audit.');
            return;
        }

        // Set UI to loading state
        sendBtn.disabled = true;
        sendBtn.textContent = 'Auditing...';
        loadingState.classList.remove('hidden');
        resultCard.classList.add('hidden');

        const formData = new FormData();
        formData.append('file', selectedFile);
        formData.append('query', userQuery.value.trim());

        try {
            const response = await fetch('/analyze', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || `Server responded with status ${response.status}`);
            }

            // Populate result fields
            vulnTitle.textContent = data.vulnerability || 'No specific vulnerability noted';
            
            const rawSev = (data.severity || 'Info').trim();
            vulnSeverity.textContent = rawSev;
            vulnSeverity.className = 'badge';

            const sevLower = rawSev.toLowerCase();
            if (sevLower.includes('critical')) {
                vulnSeverity.classList.add('badge-critical');
            } else if (sevLower.includes('high')) {
                vulnSeverity.classList.add('badge-high');
            } else if (sevLower.includes('medium')) {
                vulnSeverity.classList.add('badge-medium');
            } else if (sevLower.includes('low')) {
                vulnSeverity.classList.add('badge-low');
            } else {
                vulnSeverity.classList.add('badge-info');
            }

            vulnRemediation.textContent = data.remediation || 'No remediation required.';

            // Reveal result card
            resultCard.classList.remove('hidden');

        } catch (error) {
            showError(`Audit failed: ${error.message}`);
        } finally {
            sendBtn.disabled = false;
            sendBtn.textContent = 'Run Audit';
            loadingState.classList.add('hidden');
        }
    });
});
