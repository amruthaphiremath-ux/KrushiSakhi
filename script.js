/*
ALGORITHM 7 — FRONTEND TABLE RENDERING
------------------------------------------
START
1. Receive prediction list from backend
2. Clear any previous table rows
3. FOR each prediction:
     - Insert month into column 1
     - Insert predicted price into column 2
     - Append row to table
   END FOR
END

ALGORITHM 8 — GRAPH / CHART VISUALIZATION
------------------------------------------
START
1. Select canvas element for the chart
2. Assign predicted months to the X-axis
3. Assign predicted prices to the Y-axis
4. Render as a line chart using Chart.js
END
*/

let priceChart = null;

const monthNames = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                     "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

document.getElementById("predictBtn").addEventListener("click", async () => {
  const crop = document.getElementById("crop").value;
  const months = document.getElementById("months").value;
  const errorMsg = document.getElementById("errorMsg");
  errorMsg.textContent = "";

  if (!crop) {
    errorMsg.textContent = "Please select a crop.";
    return;
  }

  try {
    const response = await fetch("/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ crop, months_ahead: Number(months) }),
    });
    const data = await response.json();

    if (!data.success) {
      errorMsg.textContent = data.message || "Prediction failed.";
      return;
    }

    renderTable(data.predictions);
    renderChart(data.predictions, crop);
  } catch (err) {
    errorMsg.textContent = "Could not reach the prediction server.";
    console.error(err);
  }
});

// ---------------- Algorithm 7 ----------------
function renderTable(predictions) {
  const tbody = document.querySelector("#resultsTable tbody");
  tbody.innerHTML = ""; // Step 2: clear existing rows

  predictions.forEach((p) => {          // Step 3: loop through predictions
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${monthNames[p.month]}</td>
      <td>${p.year}</td>
      <td>₹ ${p.predicted_price.toLocaleString()}</td>
    `;
    tbody.appendChild(row);              // Step 3d: append row
  });
}

// ---------------- Algorithm 8 ----------------
function renderChart(predictions, crop) {
  const ctx = document.getElementById("priceChart").getContext("2d"); // Step 1
  const labels = predictions.map(p => `${monthNames[p.month]} ${p.year}`); // Step 2
  const values = predictions.map(p => p.predicted_price);                 // Step 3

  if (priceChart) priceChart.destroy();

  priceChart = new Chart(ctx, {                // Step 4: render line chart
    type: "line",
    data: {
      labels,
      datasets: [{
        label: `${crop.charAt(0).toUpperCase() + crop.slice(1)} — Predicted Price (₹)`,
        data: values,
        borderColor: "#1e7d34",
        backgroundColor: "rgba(30,125,52,0.15)",
        fill: true,
        tension: 0.3,
      }],
    },
    options: {
      responsive: true,
      plugins: { legend: { display: true } },
      scales: { y: { beginAtZero: false } },
    },
  });
}
