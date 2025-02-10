document.getElementById('startBtn').addEventListener('click', async () => {
    const response = await fetch('/estimate', {
        method: 'POST',
    });
    const result = await response.json();

    if (result.error) {
        alert(result.error);
        return;
    }

    document.getElementById('systolic').textContent = result.systolic;
    document.getElementById('diastolic').textContent = result.diastolic;
    document.getElementById('heartRate').textContent = result.heart_rate;
    document.getElementById('result').classList.remove('hidden');
});