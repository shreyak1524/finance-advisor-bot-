/* Expenses page logic: list with filters, add, edit, delete. */

let editingExpenseId = null;

function buildFilterQuery() {
  const params = new URLSearchParams();
  const category = document.getElementById("filterCategory").value;
  const dateFrom = document.getElementById("filterDateFrom").value;
  const dateTo = document.getElementById("filterDateTo").value;
  const search = document.getElementById("filterSearch").value;

  if (category && category !== "all") params.set("category", category);
  if (dateFrom) params.set("date_from", dateFrom);
  if (dateTo) params.set("date_to", dateTo);
  if (search) params.set("search", search);
  return params.toString();
}

async function loadExpenses() {
  try {
    const query = buildFilterQuery();
    const data = await apiRequest(`/api/expenses${query ? "?" + query : ""}`);
    document.getElementById("totalExpenses").textContent = formatINR(data.total);
    renderExpenseTable(data.expenses);
  } catch (err) {
    console.error(err);
  }
}

function renderExpenseTable(expenses) {
  const body = document.getElementById("expenseTableBody");
  if (!expenses.length) {
    body.innerHTML = `<tr><td colspan="6" class="text-center text-muted py-4">No expenses found. Try adjusting filters or add a new expense.</td></tr>`;
    return;
  }
  body.innerHTML = expenses.map((e) => `
    <tr>
      <td>${e.date}</td>
      <td><span class="badge text-bg-light">${e.category}</span></td>
      <td>${e.description || "—"}</td>
      <td>${e.payment_method}</td>
      <td class="text-end fw-semibold text-danger">${formatINR(e.amount)}</td>
      <td class="text-end">
        <button class="btn btn-sm btn-outline-primary me-1" onclick="editExpense(${e.id})"><i class="fa-solid fa-pen"></i></button>
        <button class="btn btn-sm btn-outline-danger" onclick="deleteExpense(${e.id})"><i class="fa-solid fa-trash"></i></button>
      </td>
    </tr>
  `).join("");
}

function showExpenseFormError(message) {
  const el = document.getElementById("expenseFormError");
  el.textContent = message;
  el.classList.remove("d-none");
}
function hideExpenseFormError() {
  document.getElementById("expenseFormError").classList.add("d-none");
}

function resetExpenseForm() {
  editingExpenseId = null;
  document.getElementById("expenseId").value = "";
  document.getElementById("expenseAmount").value = "";
  document.getElementById("expenseCategory").selectedIndex = 0;
  document.getElementById("expenseDate").value = todayISO();
  document.getElementById("expensePaymentMethod").selectedIndex = 0;
  document.getElementById("expenseDescription").value = "";
  document.getElementById("expenseModalTitle").textContent = "Add Expense";
  hideExpenseFormError();
}

async function editExpense(id) {
  try {
    const data = await apiRequest(`/api/expenses${buildFilterQuery() ? "?" + buildFilterQuery() : ""}`);
    const entry = data.expenses.find((e) => e.id === id);
    if (!entry) return;
    editingExpenseId = id;
    document.getElementById("expenseId").value = id;
    document.getElementById("expenseAmount").value = entry.amount;
    document.getElementById("expenseCategory").value = entry.category;
    document.getElementById("expenseDate").value = entry.date;
    document.getElementById("expensePaymentMethod").value = entry.payment_method;
    document.getElementById("expenseDescription").value = entry.description;
    document.getElementById("expenseModalTitle").textContent = "Edit Expense";
    hideExpenseFormError();
    new bootstrap.Modal(document.getElementById("expenseModal")).show();
  } catch (err) {
    alert(err.message);
  }
}

async function deleteExpense(id) {
  if (!confirm("Delete this expense?")) return;
  try {
    await apiRequest(`/api/expenses/${id}`, { method: "DELETE" });
    loadExpenses();
  } catch (err) {
    alert(err.message);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("expenseDate").value = todayISO();
  loadExpenses();

  document.getElementById("addExpenseBtn").addEventListener("click", resetExpenseForm);

  ["filterCategory", "filterDateFrom", "filterDateTo"].forEach((id) => {
    document.getElementById(id).addEventListener("change", loadExpenses);
  });
  let searchTimeout;
  document.getElementById("filterSearch").addEventListener("input", () => {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(loadExpenses, 350);
  });

  document.getElementById("expenseForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    hideExpenseFormError();
    const payload = {
      amount: document.getElementById("expenseAmount").value,
      category: document.getElementById("expenseCategory").value,
      date: document.getElementById("expenseDate").value,
      payment_method: document.getElementById("expensePaymentMethod").value,
      description: document.getElementById("expenseDescription").value,
    };
    try {
      if (editingExpenseId) {
        await apiRequest(`/api/expenses/${editingExpenseId}`, { method: "PUT", body: JSON.stringify(payload) });
      } else {
        await apiRequest("/api/expenses", { method: "POST", body: JSON.stringify(payload) });
      }
      bootstrap.Modal.getInstance(document.getElementById("expenseModal")).hide();
      resetExpenseForm();
      loadExpenses();
    } catch (err) {
      showExpenseFormError(err.message);
    }
  });
});
