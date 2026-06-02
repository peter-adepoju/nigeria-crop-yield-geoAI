const metrics = [
  { model: "Random Forest", rmse: 1433.59, mae: 808.71, r2: 0.535 },
  { model: "Extra Trees", rmse: 1442.53, mae: 831.85, r2: 0.529 },
  { model: "Gradient Boosting", rmse: 1538.65, mae: 901.20, r2: 0.465 },
];

const predictions = [
  { state: "Benue", zone: "North Central", crop: "MAIZE", actual: 1124.41, pred: 1586.84 },
  { state: "Nasarawa", zone: "North Central", crop: "MAIZE", actual: 1169.89, pred: 1277.50 },
  { state: "Bauchi", zone: "North East", crop: "MAIZE", actual: 1348.54, pred: 1310.56 },
  { state: "Enugu", zone: "South East", crop: "MAIZE", actual: 1440.61, pred: 2379.07 },
  { state: "Imo", zone: "South East", crop: "MAIZE", actual: 1621.14, pred: 2400.82 },
  { state: "Lagos", zone: "South West", crop: "MAIZE", actual: 1536.21, pred: 2297.74 },
  { state: "Osun", zone: "South West", crop: "MAIZE", actual: 1478.14, pred: 2487.35 },
  { state: "Benue", zone: "North Central", crop: "RICE", actual: 1306.67, pred: 1871.31 },
];

const metricList = document.getElementById("metricsList");
metrics.forEach((m) => {
  const el = document.createElement("div");
  el.className = "result";
  el.innerHTML = `<strong>${m.model}</strong><span>RMSE ${m.rmse.toFixed(2)} | MAE ${m.mae.toFixed(2)} | R² ${m.r2.toFixed(3)}</span>`;
  metricList.appendChild(el);
});

new Chart(document.getElementById("metricsChart"), {
  type: "bar",
  data: {
    labels: metrics.map((m) => m.model),
    datasets: [
      { label: "RMSE", data: metrics.map((m) => m.rmse), backgroundColor: "#38bdf8" },
      { label: "MAE", data: metrics.map((m) => m.mae), backgroundColor: "#22c55e" },
    ],
  },
  options: { responsive: true, plugins: { legend: { labels: { color: "#e5eefc" } } }, scales: { x: { ticks: { color: "#9db0cf" } }, y: { ticks: { color: "#9db0cf" } } } },
});

const cropSelect = document.getElementById("cropSelect");
const zoneSelect = document.getElementById("zoneSelect");
const crops = ["All", ...new Set(predictions.map((d) => d.crop))];
const zones = ["All", ...new Set(predictions.map((d) => d.zone))];
[cropSelect, zoneSelect].forEach((sel, idx) => {
  const values = idx === 0 ? crops : zones;
  values.forEach((v) => sel.add(new Option(v, v)));
});

const predChart = new Chart(document.getElementById("predChart"), {
  type: "scatter",
  data: {
    datasets: [{
      label: "Actual vs predicted",
      data: predictions.map((d) => ({ x: d.actual, y: d.pred })),
      backgroundColor: "#38bdf8",
    }],
  },
  options: {
    plugins: { legend: { labels: { color: "#e5eefc" } } },
    scales: {
      x: { title: { display: true, text: "Actual yield", color: "#e5eefc" }, ticks: { color: "#9db0cf" } },
      y: { title: { display: true, text: "Predicted yield", color: "#e5eefc" }, ticks: { color: "#9db0cf" } },
    },
  },
});

function refreshPredChart() {
  const crop = cropSelect.value;
  const zone = zoneSelect.value;
  const filtered = predictions.filter((d) => (crop === "All" || d.crop === crop) && (zone === "All" || d.zone === zone));
  predChart.data.datasets[0].data = filtered.map((d) => ({ x: d.actual, y: d.pred }));
  predChart.update();
}

cropSelect.addEventListener("change", refreshPredChart);
zoneSelect.addEventListener("change", refreshPredChart);
