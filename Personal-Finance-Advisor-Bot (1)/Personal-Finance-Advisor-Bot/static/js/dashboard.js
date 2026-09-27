/* Dashboard page logic: loads summary data, charts, recent expenses, goals, recs. */

let expenseChart = null;
let trendChart = null;

async function loadDashboard(year, month) {
  try {
    const data = await apiRequest(`/api/dashboard?year=${year}&month=${month}`);
    renderSummary(data.summary);
    renderWarnings(data.budget_warnings);
    renderExpenseChart(data.category_breakdown);
    renderTrendChart(data.trend);
    renderRecentExpenses(data.recent_expenses);
    renderBudgetStatus(data.budget_status);
    renderGoals(data.goals);
    renderRecommendations(data.recommendations);
  } catch (err) {
    console.error(err);
  }
}

function renderSummary(summary) {
  document.getElementById("statIncome").textContent = formatINR(summary.income);
  document.getElementById("statExpenses").textContent = formatINR(summary.expenses);
  document.getElementById("statSavings").textContent = formatINR(summary.savings);
  document.getElementById("statRate").textContent = summary.savings_rate + "%";
}

function renderWarnings(warnings) {
  const area = document.getElementById("warningsArea");
  area.innerHTML = "";
  warnings.forEach((w) => {
    const div = document.createElement("div");
    div.className = "alert alert-danger";
    div.innerHTML = `<i class="fa-solid fa-triangle-exclamation"></i> ${w}`;
    area.appendChild(div);
  });
}

function renderExpenseChart(breakdown) {
  const ctx = document.getElementById("expenseChart");
  const labels = Object.keys(breakdown);
  const values = Object.values(breakdown);

  if (labels.length === 0) {
    labels.push("No expenses yet");
    values.push(1);
  }

  const colors = ["#4f6df5","#e5534b","#22b07d","#f0ad4e","#8f6df5","#f56d9c","#37b6d1","#ff9f6d","#6d8cf5","#a3a8c2"];

  if (expenseChart) expenseChart.destroy();
  expenseChart = new Chart(ctx, {
    type: "doughnut",
    data: { labels, datasets: [{ data: values, backgroundColor: colors }] },
    options: { plugins: { legend: { position: "bottom" } }, cutout: "60%" },
  });
}

function renderTrendChart(trend) {
  const ctx = document.getElementById("trendChart");
  const labels = trend.map((t) => t.label);
  const income = trend.map((t) => t.income);
  const expenses = trend.map((t) => t.expenses);

  if (trendChart) trendChart.destroy();
  trendChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels,
      datasets: [
        { label: "Income", data: income, backgroundColor: "#4f6df5", borderRadius: 6 },
        { label: "Expenses", data: expenses, backgroundColor: "#e5534b", borderRadius: 6 },
      ],
    },
    options: { plugins: { legend: { position: "bottom" } }, scales: { y: { beginAtZero: true } } },
  });
}

function renderRecentExpenses(expenses) {
  const container = document.getElementById("recentExpenses");
  if (!expenses.length) {
    container.innerHTML = `<p class="text-muted mb-0">No expenses recorded yet.</p>`;
    return;
  }
  container.innerHTML = expenses.map((e) => `
    <div class="list-group-item d-flex justify-content-between align-items-center px-0">
      <div>
        <div class="fw-semibold">${e.category}</div>
        <div class="text-muted small">${e.date} ${e.description ? "• " + e.description : ""}</div>
      </div>
      <div class="fw-bold text-danger">-${formatINR(e.amount)}</div>
    </div>
  `).join("");
}

function renderBudgetStatus(statuses) {
  const container = document.getElementById("budgetStatusList");
  const withBudget = statuses.filter((s) => s.status !== "no_budget");
  if (!withBudget.length) {
    container.innerHTML = `<p class="text-muted mb-0">No budget set for this month yet. Visit the Budget page to create one.</p>`;
    return;
  }
  container.innerHTML = withBudget.slice(0, 6).map((s) => {
    let barClass = "bg-success-soft";
    if (s.status === "exceeded") barClass = "bg-danger-soft";
    else if (s.status === "warning") barClass = "bg-warning-soft";
    return `
      <div class="mb-2">
        <div class="d-flex justify-content-between small mb-1">
          <span class="fw-semibold">${s.category}</span>
          <span>${formatINR(s.spent)} / ${formatINR(s.budget)}</span>
        </div>
        <div class="progress" style="height:10px;">
          <div class="progress-bar ${barClass}" style="width:${Math.min(s.percent_used, 100)}%"></div>
        </div>
      </div>
    `;
  }).join("");
}

function renderGoals(goals) {
  const container = document.getElementById("goalsList");
  if (!goals.length) {
    container.innerHTML = `<p class="text-muted mb-0">No goals set yet. Visit the Goals page to create one.</p>`;
    return;
  }
  container.innerHTML = goals.map((g) => `
    <div class="mb-3">
      <div class="d-flex justify-content-between small mb-1">
        <span class="fw-semibold">${g.name}</span>
        <span>${g.progress_percent}%</span>
      </div>
      <div class="progress" style="height:10px;">
        <div class="progress-bar" style="width:${g.progress_percent}%; background:#4f6df5;"></div>
      </div>
      <div class="text-muted small mt-1">${formatINR(g.current_amount)} of ${formatINR(g.target_amount)}</div>
    </div>
  `).join("");
}

function renderRecommendations(recs) {
  const list = document.getElementById("recommendationsList");
  list.innerHTML = recs.map((r) => `<li>${r}</li>`).join("");
}

document.addEventListener("DOMContentLoaded", () => {
  const initial = setupMonthYearSelectors((year, month) => loadDashboard(year, month));
  if (initial) loadDashboard(initial.year, initial.month);
});
