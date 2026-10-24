// UI Controls
const uploadBtn = document.getElementById('upload-btn');
const fileInput = document.getElementById('file-input');
const sendBtn = document.getElementById('send-btn');

// Display Areas
const loading = document.getElementById('loading');
const auditOutput = document.getElementById('audit-output');

// Data Spans
const resVuln = document.getElementById('res-vuln');
const resSev = document.getElementById('res-sev');
const resRem = document.getElementById('res-rem');

let selectedFile = null;

// 1. Map the Orange 'Upload File' button to the hidden file input
uploadBtn.addEventListener('click', () => {
    fileInput.click();
});

// 2. Capture the selected file and provide visual feedback
fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        selectedFile = e.target.files[0];
        // Truncate long file names for the button text
        let fileName = selectedFile.name;
        if (fileName.length > 15) fileName = fileName.substring(0, 15) + '...';
        
        uploadBtn.textContent = `Attached: ${fileName}`;
        uploadBtn.style.background = 'var(--primary-green)'; 
    }
});

// 3. Handle the 'Send' action and backend communication
sendBtn.addEventListener('click', async () => {
    if (!selectedFile) {
        alert("Please upload a file before sending.");
        return;
    }

    // Toggle loading state
    auditOutput.classList.add('hidden');
    loading.classList.remove('hidden');

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
        const response = await fetch('/analyze', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (!response.ok) throw new Error(data.error || 'Server error');

        // Inject the JSON response into the DOM
        resVuln.textContent = data.vulnerability;
        resSev.textContent = data.severity;
        resRem.textContent = data.remediation;

        // Display the final audit report
        loading.classList.add('hidden');
        auditOutput.classList.remove('hidden');

    } catch (error) {
        alert(`Analysis failed: ${error.message}`);
        loading.classList.add('hidden');
    }
});
