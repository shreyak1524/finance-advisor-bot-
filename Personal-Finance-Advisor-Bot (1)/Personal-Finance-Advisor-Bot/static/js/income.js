/* Income page logic: list, add, edit, delete income entries. */

let editingIncomeId = null;

async function loadIncomes() {
  try {
    const data = await apiRequest("/api/income");
    document.getElementById("totalIncome").textContent = formatINR(data.total);
    renderIncomeTable(data.incomes);
  } catch (err) {
    console.error(err);
  }
}

function renderIncomeTable(incomes) {
  const body = document.getElementById("incomeTableBody");
  if (!incomes.length) {
    body.innerHTML = `<tr><td colspan="5" class="text-center text-muted py-4">No income recorded yet. Click "Add Income" to get started.</td></tr>`;
    return;
  }
  body.innerHTML = incomes.map((i) => `
    <tr>
      <td>${i.date}</td>
      <td><span class="badge text-bg-light">${i.source}</span></td>
      <td>${i.description || "—"}</td>
      <td class="text-end fw-semibold text-success">${formatINR(i.amount)}</td>
      <td class="text-end">
        <button class="btn btn-sm btn-outline-primary me-1" onclick="editIncome(${i.id})"><i class="fa-solid fa-pen"></i></button>
        <button class="btn btn-sm btn-outline-danger" onclick="deleteIncome(${i.id})"><i class="fa-solid fa-trash"></i></button>
      </td>
    </tr>
  `).join("");
}

function showIncomeFormError(message) {
  const el = document.getElementById("incomeFormError");
  el.textContent = message;
  el.classList.remove("d-none");
}
function hideIncomeFormError() {
  document.getElementById("incomeFormError").classList.add("d-none");
}

function resetIncomeForm() {
  editingIncomeId = null;
  document.getElementById("incomeId").value = "";
  document.getElementById("incomeAmount").value = "";
  document.getElementById("incomeSource").selectedIndex = 0;
  document.getElementById("incomeDate").value = todayISO();
  document.getElementById("incomeDescription").value = "";
  document.getElementById("incomeModalTitle").textContent = "Add Income";
  hideIncomeFormError();
}

async function editIncome(id) {
  try {
    const data = await apiRequest("/api/income");
    const entry = data.incomes.find((i) => i.id === id);
    if (!entry) return;
    editingIncomeId = id;
    document.getElementById("incomeId").value = id;
    document.getElementById("incomeAmount").value = entry.amount;
    document.getElementById("incomeSource").value = entry.source;
    document.getElementById("incomeDate").value = entry.date;
    document.getElementById("incomeDescription").value = entry.description;
    document.getElementById("incomeModalTitle").textContent = "Edit Income";
    hideIncomeFormError();
    new bootstrap.Modal(document.getElementById("incomeModal")).show();
  } catch (err) {
    alert(err.message);
  }
}

async function deleteIncome(id) {
  if (!confirm("Delete this income entry?")) return;
  try {
    await apiRequest(`/api/income/${id}`, { method: "DELETE" });
    loadIncomes();
  } catch (err) {
    alert(err.message);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("incomeDate").value = todayISO();
  loadIncomes();

  document.getElementById("addIncomeBtn").addEventListener("click", resetIncomeForm);

  document.getElementById("incomeForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    hideIncomeFormError();
    const payload = {
      amount: document.getElementById("incomeAmount").value,
      source: document.getElementById("incomeSource").value,
      date: document.getElementById("incomeDate").value,
      description: document.getElementById("incomeDescription").value,
    };
    try {
      if (editingIncomeId) {
        await apiRequest(`/api/income/${editingIncomeId}`, { method: "PUT", body: JSON.stringify(payload) });
      } else {
        await apiRequest("/api/income", { method: "POST", body: JSON.stringify(payload) });
      }
      bootstrap.Modal.getInstance(document.getElementById("incomeModal")).hide();
      resetIncomeForm();
      loadIncomes();
    } catch (err) {
      showIncomeFormError(err.message);
    }
  });
});
