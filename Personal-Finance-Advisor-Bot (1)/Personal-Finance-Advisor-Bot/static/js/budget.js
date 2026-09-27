/* Budget page logic: load status, save budgets, auto-generate suggestion. */

let budgetChart = null;
let currentYear, currentMonth;

async function loadBudget(year, month) {
  currentYear = year;
  currentMonth = month;
  try {
    const data = await apiRequest(`/api/budget?year=${year}&month=${month}`);
    applyBudgetStatus(data.budget_status);
  } catch (err) {
    console.error(err);
  }
}

function applyBudgetStatus(statuses) {
  const statusByCategory = {};
  statuses.forEach((s) => { statusByCategory[s.category] = s; });

  const warningsArea = document.getElementById("budgetWarnings");
  warningsArea.innerHTML = "";

  const rows = document.querySelectorAll("#budgetTableBody tr");
  const chartLabels = [];
  const chartBudget = [];
  const chartSpent = [];

  rows.forEach((row) => {
    const category = row.dataset.category;
    const s = statusByCategory[category];
    const input = row.querySelector(".budget-input");
    const spentCell = row.querySelector(".spent-cell");
    const remainingCell = row.querySelector(".remaining-cell");
    const bar = row.querySelector(".usage-bar");

    const budgetAmt = s ? s.budget : 0;
    const spentAmt = s ? s.spent : 0;
    const remaining = s ? s.remaining : 0;
    const pct = s ? Math.min(s.percent_used, 100) : 0;

    input.value = budgetAmt;
    spentCell.textContent = formatINR(spentAmt);
    remainingCell.textContent = formatINR(remaining);
    remainingCell.className = "remaining-cell " + (remaining < 0 ? "text-danger fw-semibold" : "text-success");
    bar.style.width = pct + "%";
    bar.textContent = pct + "%";
    bar.className = "progress-bar usage-bar " + (
      s && s.status === "exceeded" ? "bg-danger-soft" :
      s && s.status === "warning" ? "bg-warning-soft" : "bg-success-soft"
    );

    chartLabels.push(category);
    chartBudget.push(budgetAmt);
    chartSpent.push(spentAmt);

    if (s && s.status === "exceeded") {
      const div = document.createElement("div");
      div.className = "alert alert-danger";
      div.innerHTML = `<i class="fa-solid fa-triangle-exclamation"></i> You have exceeded your ${category} budget by ${formatINR(Math.abs(remaining))}.`;
      warningsArea.appendChild(div);
    }
  });

  renderBudgetChart(chartLabels, chartBudget, chartSpent);
}

function renderBudgetChart(labels, budgetData, spentData) {
  const ctx = document.getElementById("budgetChart");
  if (budgetChart) budgetChart.destroy();
  budgetChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels,
      datasets: [
        { label: "Budget", data: budgetData, backgroundColor: "#4f6df5", borderRadius: 6 },
        { label: "Spent", data: spentData, backgroundColor: "#e5534b", borderRadius: 6 },
      ],
    },
    options: { plugins: { legend: { position: "bottom" } }, scales: { y: { beginAtZero: true } } },
  });
}

async function saveBudget() {
  const items = [];
  document.querySelectorAll("#budgetTableBody tr").forEach((row) => {
    const category = row.dataset.category;
    const amount = parseFloat(row.querySelector(".budget-input").value) || 0;
    items.push({ category, amount });
  });

  try {
    await apiRequest("/api/budget", {
      method: "POST",
      body: JSON.stringify({ year: currentYear, month: currentMonth, items }),
    });
    loadBudget(currentYear, currentMonth);
    alert("Budget saved successfully!");
  } catch (err) {
    alert(err.message);
  }
}

async function generateBudget() {
  try {
    const data = await apiRequest(`/api/budget/generate?year=${currentYear}&month=${currentMonth}`);
    const suggestion = data.suggested_budget;
    document.querySelectorAll("#budgetTableBody tr").forEach((row) => {
      const category = row.dataset.category;
      const input = row.querySelector(".budget-input");
      if (suggestion[category] !== undefined) {
        input.value = Math.round(suggestion[category]);
      }
    });
    const message = data.based_on_history
      ? "Budget generated based on your last 3 months of spending history!"
      : "Budget generated using a standard 50/30/20 style allocation (no spending history found yet).";
    alert(message + " Review and click 'Save Budget' to confirm.");
  } catch (err) {
    alert(err.message);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const initial = setupMonthYearSelectors((year, month) => loadBudget(year, month));
  if (initial) loadBudget(initial.year, initial.month);

  document.getElementById("saveBudgetBtn").addEventListener("click", saveBudget);
  document.getElementById("generateBudgetBtn").addEventListener("click", generateBudget);
});
