// Get the input element by its ID (assuming an ID of 'fileInput')
const fileInput = document.getElementById('avatarUpload');
const updateStatus = document.getElementById('updateStatus');

// Add an event listener for the 'change' event
fileInput.addEventListener('change', (event) => {
    // Access the list of selected files
    const files = event.target.files;

    if (files.length > 0) {
        console.log("Selected file name:", files[0].name);
        updateStatus.textContent = files[0].name;

    } else {
        console.log("No file was selected (dialog was cancelled or cleared).");
    }
});

document.getElementById('form').addEventListener('submit', (event) => {
    if (fileInput.files.length == 0) {
        // Prevent the default form submission behavior
        event.preventDefault();

        // You can add your own validation logic here
        updateStatus.textContent = "Please, choose a file";
    }
});