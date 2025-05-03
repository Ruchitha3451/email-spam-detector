document.getElementById("checkBtn").addEventListener("click", function() {
    // Get email input from popup
    const emailContent = document.getElementById("emailInput").value.trim();
    
    if (emailContent === "") {
        document.getElementById("result").textContent = "Please enter an email.";
        document.getElementById("result").style.color = "orange";
        return;
    }

    fetch("http://localhost:5000/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: emailContent })
    })
    .then(response => response.json())
    .then(data => {
        const resultElement = document.getElementById("result");
        if (data.result) {
            resultElement.textContent = `Prediction: ${data.result}`;
            resultElement.style.color = data.result === "Spam" ? "red" : "green";
        } else {
            resultElement.textContent = `Error: ${data.error}`;
            resultElement.style.color = "red";
        }
    })
    .catch(error => {
        document.getElementById("result").textContent = "Error: Could not connect to Flask server.";
        document.getElementById("result").style.color = "red";
    });
});
