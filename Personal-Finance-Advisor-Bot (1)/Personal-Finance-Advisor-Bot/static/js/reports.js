/* Reports page logic: load and render the full monthly report. */

async function loadReport(year, month) {
  try {
    const data = await apiRequest(`/api/reports/${year}/${month}`);
    document.getElementById("summaryText").textContent = data.summary_text;

    document.getElementById("rIncome").textContent = formatINR(data.summary.income);
    document.getElementById("rExpenses").textContent = formatINR(data.summary.expenses);
    document.getElementById("rSavings").textContent = formatINR(data.summary.savings);
    document.getElementById("rRate").textContent = data.summary.savings_rate + "%";

    renderCategoryAnalysis(data.category_analysis);
    renderBudgetPerformance(data.budget_performance);
    renderIncomeVariability(data.income_variability);
    renderReportRecommendations(data.recommendations);
  } catch (err) {
    console.error(err);
  }
}

function renderCategoryAnalysis(rows) {
  const body = document.getElementById("categoryAnalysisBody");
  if (!rows.length) {
    body.innerHTML = `<tr><td colspan="3" class="text-center text-muted py-3">No expenses recorded for this month.</td></tr>`;
    return;
  }
  body.innerHTML = rows.map((r) => `
    <tr>
      <td>${r.category}</td>
      <td class="text-end">${formatINR(r.amount)}</td>
      <td class="text-end">${r.percent_of_total}%</td>
    </tr>
  `).join("");
}

function renderBudgetPerformance(perf) {
  const area = document.getElementById("budgetPerformanceArea");
  function section(title, items, badgeClass) {
    if (!items.length) return "";
    return `
      <div class="mb-3">
        <div class="fw-semibold small text-muted mb-1">${title}</div>
        ${items.map((i) => `<span class="badge ${badgeClass} me-1 mb-1">${i.category} (${i.percent_used}%)</span>`).join("")}
      </div>
    `;
  }
  const html =
    section("Exceeded Budget", perf.exceeded, "badge-status-exceeded") +
    section("Approaching Limit", perf.approaching, "badge-status-warning") +
    section("Within Budget", perf.within_budget, "badge-status-on_track");

  area.innerHTML = html || `<p class="text-muted mb-0">No budget set for this month.</p>`;
}

function renderIncomeVariability(v) {
  const area = document.getElementById("incomeVariabilityArea");
  if (!v.average) {
    area.innerHTML = `<p class="text-muted mb-0">Not enough income history yet.</p>`;
    return;
  }
  area.innerHTML = `
    <div class="row text-center g-2 mb-3">
      <div class="col-4"><div class="small text-muted">Average</div><div class="fw-bold">${formatINR(v.average)}</div></div>
      <div class="col-4"><div class="small text-muted">Highest</div><div class="fw-bold text-success">${formatINR(v.highest)}</div></div>
      <div class="col-4"><div class="small text-muted">Lowest</div><div class="fw-bold text-danger">${formatINR(v.lowest)}</div></div>
    </div>
    ${v.variable ? `<div class="alert alert-warning small mb-0"><i class="fa-solid fa-triangle-exclamation"></i> Your income varies significantly month to month. Consider building an emergency fund.</div>` : `<div class="alert alert-success small mb-0"><i class="fa-solid fa-check"></i> Your income has been relatively stable.</div>`}
  `;
}

function renderReportRecommendations(recs) {
  document.getElementById("reportRecommendations").innerHTML = recs.map((r) => `<li>${r}</li>`).join("");
}

document.addEventListener("DOMContentLoaded", () => {
  const initial = setupMonthYearSelectors((year, month) => loadReport(year, month));
  if (initial) loadReport(initial.year, initial.month);
});
