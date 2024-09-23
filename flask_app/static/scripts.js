function uploadFiles() {
    const input = document.getElementById('fileInput');
    const files = input.files;
    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
        formData.append('files[]', files[i]);
    }

    fetch('/upload', {
        method: 'POST',
        body: formData
    }).then(response => {
        if (response.ok) {
            alert('Files uploaded successfully');
            listFiles();
        } else {
            alert('File upload failed');
        }
    });
}

function listFiles() {
    fetch('/files')
        .then(response => response.json())
        .then(files => {
            const fileList = document.getElementById('fileList');
            fileList.innerHTML = '';
            files.forEach(file => {
                const li = document.createElement('li');
                li.className = 'list-group-item d-flex justify-content-between align-items-center';
                li.textContent = file;
                const deleteButton = document.createElement('button');
                deleteButton.className = 'btn btn-danger btn-sm';
                deleteButton.textContent = 'Delete';
                deleteButton.onclick = () => deleteFile(file);
                li.appendChild(deleteButton);
                fileList.appendChild(li);
            });
        });
}

function processFiles() {
    const progressBar = document.getElementById('progressBar');
    const processResult = document.getElementById('processResult');
    progressBar.style.width = '0%';
    progressBar.setAttribute('aria-valuenow', 0);
    progressBar.textContent = '0%';
    processResult.textContent = '';

    fetch('/process', {
        method: 'POST'
    }).then(response => {
        if (response.ok) {
            const interval = setInterval(() => {
                fetch('/status')
                    .then(response => response.json())
                    .then(status => {
                        const progress = Math.round((status.processed_files / status.total_files) * 100);
                        progressBar.style.width = `${progress}%`;
                        progressBar.setAttribute('aria-valuenow', progress);
                        progressBar.textContent = `${progress}%`;
                        processResult.textContent = `Processing file: ${status.current_file}`;

                        if (progress === 100) {
                            clearInterval(interval);
                            processResult.textContent = 'Processing complete!';
                        }
                    });
            }, 1000);
        } else {
            alert('File processing failed');
        }
    });
}

function downloadXLSX() {
    window.location.href = '/download_xlsx';
}

function deleteFile(filename) {
    const formData = new FormData();
    formData.append('filename', filename);

    fetch('/delete', {
        method: 'POST',
        body: formData
    }).then(response => {
        if (response.ok) {
            alert('File deleted successfully');
            listFiles();
        } else {
            alert('File deletion failed');
        }
    });
}

function deleteAllFiles() {
    fetch('/delete_all', {
        method: 'POST'
    }).then(response => {
        if (response.ok) {
            alert('All files deleted successfully');
            listFiles();
        } else {
            alert('Failed to delete all files');
        }
    });
}

document.addEventListener('DOMContentLoaded', listFiles);

document.querySelector('.custom-file-input').addEventListener('change', function(e) {
    const files = Array.from(document.getElementById("fileInput").files);
    const fileNames = files.map(file => file.name).join(', ');
    const nextSibling = e.target.nextElementSibling;
    nextSibling.innerText = fileNames;
});
