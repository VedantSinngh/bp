// Function to start the webcam stream
async function startWebcam() {
    const videoElement = document.getElementById("webcam");

    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        videoElement.srcObject = stream;
    } catch (error) {
        console.error("Error accessing webcam:", error);
        document.getElementById("error").classList.remove("hidden");
        document.getElementById("error").textContent = "Could not access the webcam. Please allow camera permissions.";
    }
}

// Function to send a request to the Flask backend to start measurement
async function startMeasurement() {
    document.getElementById("measure-btn").textContent = "Measuring...";
    document.getElementById("measure-btn").disabled = true;

    try {
        const response = await fetch("/measure", { method: "POST" });
        const data = await response.json();

        if (data.error) {
            throw new Error(data.error);
        }

        document.getElementById("systolic").textContent = data.systolic;
        document.getElementById("diastolic").textContent = data.diastolic;
        document.getElementById("heart-rate").textContent = data.heart_rate;
        document.getElementById("results").classList.remove("hidden");
    } catch (error) {
        document.getElementById("error").classList.remove("hidden");
        document.getElementById("error").textContent = error.message;
    } finally {
        document.getElementById("measure-btn").textContent = "Start Measurement";
        document.getElementById("measure-btn").disabled = false;
    }
}

// Start the webcam feed when the page loads
window.onload = startWebcam;
