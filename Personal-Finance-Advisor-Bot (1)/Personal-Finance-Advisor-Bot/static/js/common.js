/* Shared helper functions used across dashboard, budget, and reports pages. */

const MONTH_NAMES = ["January","February","March","April","May","June",
                      "July","August","September","October","November","December"];

function formatINR(amount) {
  const n = Number(amount) || 0;
  return "₹" + n.toLocaleString("en-IN", { maximumFractionDigits: 0 });
}

function todayISO() {
  return new Date().toISOString().split("T")[0];
}

/**
 * Populate #monthSelect and #yearSelect dropdowns (if present on the page)
 * and wire up onChange callback. Returns {year, month} for current selection.
 */
function setupMonthYearSelectors(onChange) {
  const monthSelect = document.getElementById("monthSelect");
  const yearSelect = document.getElementById("yearSelect");
  if (!monthSelect || !yearSelect) return null;

  const now = new Date();
  const currentYear = now.getFullYear();
  const currentMonth = now.getMonth() + 1;

  monthSelect.innerHTML = MONTH_NAMES.map((m, i) =>
    `<option value="${i + 1}" ${i + 1 === currentMonth ? "selected" : ""}>${m}</option>`
  ).join("");

  let yearOptions = "";
  for (let y = currentYear - 3; y <= currentYear + 1; y++) {
    yearOptions += `<option value="${y}" ${y === currentYear ? "selected" : ""}>${y}</option>`;
  }
  yearSelect.innerHTML = yearOptions;

  monthSelect.addEventListener("change", () => onChange(parseInt(yearSelect.value), parseInt(monthSelect.value)));
  yearSelect.addEventListener("change", () => onChange(parseInt(yearSelect.value), parseInt(monthSelect.value)));

  return { year: currentYear, month: currentMonth };
}

async function apiRequest(url, options = {}) {
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  let data = null;
  try { data = await response.json(); } catch (e) { data = null; }
  if (!response.ok) {
    const message = (data && data.error) ? data.error : "Something went wrong. Please try again.";
    throw new Error(message);
  }
  return data;
}
