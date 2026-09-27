/* Goals page logic: list, add, edit, delete goals with progress bars. */

let editingGoalId = null;

async function loadGoals() {
  try {
    const data = await apiRequest("/api/goals");
    renderGoalCards(data.goals);
  } catch (err) {
    console.error(err);
  }
}

function renderGoalCards(goals) {
  const container = document.getElementById("goalsContainer");
  if (!goals.length) {
    container.innerHTML = `<div class="col-12"><div class="card-panel text-center text-muted py-4">No goals yet. Click "Add Goal" to set your first financial target.</div></div>`;
    return;
  }
  container.innerHTML = goals.map((g) => {
    const barColor = g.progress_percent >= 100 ? "#22b07d" : "#4f6df5";
    return `
    <div class="col-md-6 col-lg-4">
      <div class="goal-card">
        <div class="d-flex justify-content-between align-items-start">
          <h6>${g.name}</h6>
          <div>
            <button class="btn btn-sm btn-outline-primary me-1" onclick="editGoal(${g.id})"><i class="fa-solid fa-pen"></i></button>
            <button class="btn btn-sm btn-outline-danger" onclick="deleteGoal(${g.id})"><i class="fa-solid fa-trash"></i></button>
          </div>
        </div>
        ${g.description ? `<p class="text-muted small mb-2">${g.description}</p>` : ""}
        <div class="d-flex justify-content-between small mb-1">
          <span>Target: <strong>${formatINR(g.target_amount)}</strong></span>
          <span>${g.progress_percent}%</span>
        </div>
        <div class="progress goal-progress-wrap mb-2">
          <div class="progress" style="height:12px;">
            <div class="progress-bar" style="width:${g.progress_percent}%; background:${barColor};"></div>
          </div>
        </div>
        <div class="d-flex justify-content-between small text-muted">
          <span>Saved: ${formatINR(g.current_amount)}</span>
          <span>Remaining: ${formatINR(g.remaining)}</span>
        </div>
        ${g.target_date ? `<div class="small text-muted mt-1"><i class="fa-regular fa-calendar"></i> Target date: ${g.target_date}</div>` : ""}
        <button class="btn btn-sm btn-outline-success w-100 mt-3" onclick="updateSavedAmount(${g.id}, ${g.current_amount}, ${g.target_amount})">
          <i class="fa-solid fa-plus"></i> Update Saved Amount
        </button>
      </div>
    </div>
    `;
  }).join("");
}

async function updateSavedAmount(id, currentAmount, targetAmount) {
  const input = prompt("Enter new saved amount (₹):", currentAmount);
  if (input === null) return;
  const newAmount = parseFloat(input);
  if (isNaN(newAmount) || newAmount < 0) {
    alert("Please enter a valid non-negative number.");
    return;
  }
  try {
    const data = await apiRequest("/api/goals");
    const goal = data.goals.find((g) => g.id === id);
    if (!goal) return;
    await apiRequest(`/api/goals/${id}`, {
      method: "PUT",
      body: JSON.stringify({
        name: goal.name, target_amount: goal.target_amount,
        current_amount: newAmount, target_date: goal.target_date, description: goal.description,
      }),
    });
    loadGoals();
  } catch (err) {
    alert(err.message);
  }
}

function showGoalFormError(message) {
  const el = document.getElementById("goalFormError");
  el.textContent = message;
  el.classList.remove("d-none");
}
function hideGoalFormError() {
  document.getElementById("goalFormError").classList.add("d-none");
}

function resetGoalForm() {
  editingGoalId = null;
  document.getElementById("goalId").value = "";
  document.getElementById("goalName").selectedIndex = 0;
  document.getElementById("goalNameCustom").value = "";
  document.getElementById("goalNameCustom").classList.add("d-none");
  document.getElementById("goalTarget").value = "";
  document.getElementById("goalCurrent").value = 0;
  document.getElementById("goalDate").value = "";
  document.getElementById("goalDescription").value = "";
  document.getElementById("goalModalTitle").textContent = "Add Goal";
  hideGoalFormError();
}

async function editGoal(id) {
  try {
    const data = await apiRequest("/api/goals");
    const goal = data.goals.find((g) => g.id === id);
    if (!goal) return;
    editingGoalId = id;
    document.getElementById("goalId").value = id;

    const select = document.getElementById("goalName");
    const customInput = document.getElementById("goalNameCustom");
    const matchesOption = Array.from(select.options).some((o) => o.value === goal.name);
    if (matchesOption) {
      select.value = goal.name;
      customInput.classList.add("d-none");
    } else {
      select.value = "Custom Goal";
      customInput.value = goal.name;
      customInput.classList.remove("d-none");
    }

    document.getElementById("goalTarget").value = goal.target_amount;
    document.getElementById("goalCurrent").value = goal.current_amount;
    document.getElementById("goalDate").value = goal.target_date || "";
    document.getElementById("goalDescription").value = goal.description;
    document.getElementById("goalModalTitle").textContent = "Edit Goal";
    hideGoalFormError();
    new bootstrap.Modal(document.getElementById("goalModal")).show();
  } catch (err) {
    alert(err.message);
  }
}

async function deleteGoal(id) {
  if (!confirm("Delete this goal?")) return;
  try {
    await apiRequest(`/api/goals/${id}`, { method: "DELETE" });
    loadGoals();
  } catch (err) {
    alert(err.message);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  loadGoals();

  document.getElementById("addGoalBtn").addEventListener("click", resetGoalForm);

  document.getElementById("goalName").addEventListener("change", (e) => {
    const customInput = document.getElementById("goalNameCustom");
    if (e.target.value === "Custom Goal") {
      customInput.classList.remove("d-none");
    } else {
      customInput.classList.add("d-none");
    }
  });

  document.getElementById("goalForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    hideGoalFormError();

    const selectValue = document.getElementById("goalName").value;
    const customValue = document.getElementById("goalNameCustom").value.trim();
    const name = (selectValue === "Custom Goal" && customValue) ? customValue : selectValue;

    const payload = {
      name,
      target_amount: document.getElementById("goalTarget").value,
      current_amount: document.getElementById("goalCurrent").value,
      target_date: document.getElementById("goalDate").value,
      description: document.getElementById("goalDescription").value,
    };
    try {
      if (editingGoalId) {
        await apiRequest(`/api/goals/${editingGoalId}`, { method: "PUT", body: JSON.stringify(payload) });
      } else {
        await apiRequest("/api/goals", { method: "POST", body: JSON.stringify(payload) });
      }
      bootstrap.Modal.getInstance(document.getElementById("goalModal")).hide();
      resetGoalForm();
      loadGoals();
    } catch (err) {
      showGoalFormError(err.message);
    }
  });
});
