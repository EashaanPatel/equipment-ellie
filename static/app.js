const state = {
  equipment: [],
  people: [],
  filter: "all",
  search: "",
  selectedId: null,
  editingEquipmentId: null,
  editingPersonId: null,
};

const elements = {
  equipmentList: document.getElementById("equipmentList"),
  equipmentCount: document.getElementById("equipmentCount"),
  detailsPanel: document.getElementById("detailsPanel"),
  searchInput: document.getElementById("searchInput"),
  filterButtons: document.querySelectorAll(".filter-button"),
  addEquipmentBtn: document.getElementById("addEquipmentBtn"),
  managePeopleBtn: document.getElementById("managePeopleBtn"),
  equipmentDialog: document.getElementById("equipmentDialog"),
  equipmentForm: document.getElementById("equipmentForm"),
  equipmentDialogTitle: document.getElementById("equipmentDialogTitle"),
  peopleDialog: document.getElementById("peopleDialog"),
  peopleForm: document.getElementById("peopleForm"),
  peopleDialogTitle: document.getElementById("peopleDialogTitle"),
  peopleList: document.getElementById("peopleList"),
  toast: document.getElementById("toast"),
};

const formatDate = (iso) => {
  if (!iso) return "";
  const date = new Date(iso);
  return date.toLocaleString();
};

const now = () => new Date();

const statusLabel = (equipment) => {
  if (equipment.status !== "checked_out") {
    return { label: "Available", className: "status-available" };
  }
  const due = equipment.due_at ? new Date(equipment.due_at) : null;
  if (due && due < now()) {
    return { label: "Overdue", className: "status-overdue" };
  }
  const soon = due && due.toDateString() === now().toDateString();
  if (soon) {
    return { label: "Due today", className: "status-due" };
  }
  return { label: "Checked out", className: "status-checked_out" };
};

const showToast = (message, isError = false) => {
  elements.toast.textContent = message;
  elements.toast.style.background = isError ? "#ef4444" : "#1f2933";
  elements.toast.classList.add("show");
  setTimeout(() => elements.toast.classList.remove("show"), 2400);
};

const api = async (path, options = {}) => {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const text = await response.text();
  let data = null;
  try {
    data = text ? JSON.parse(text) : null;
  } catch (error) {
    data = null;
  }
  if (!response.ok) {
    throw new Error((data && data.error) || text || "Something went wrong");
  }
  return data;
};

const loadData = async () => {
  try {
    state.equipment = await api("/api/equipment");
    state.people = await api("/api/people");
  } catch (error) {
    state.equipment = [];
    state.people = [];
    showToast("API unavailable. Showing empty state.", true);
  }
  render();
};

const filteredEquipment = () => {
  const search = state.search.toLowerCase();
  return state.equipment.filter((item) => {
    const matchesSearch =
      item.name.toLowerCase().includes(search) ||
      (item.tag || "").toLowerCase().includes(search) ||
      personName(item.checked_out_to).toLowerCase().includes(search);

    if (!matchesSearch) return false;

    if (state.filter === "all") return true;
    if (state.filter === "available") return item.status === "available";
    if (state.filter === "checked_out") return item.status === "checked_out";
    if (state.filter === "overdue") {
      return (
        item.status === "checked_out" &&
        item.due_at &&
        new Date(item.due_at) < now()
      );
    }
    return true;
  });
};

const personName = (personId) => {
  const person = state.people.find((p) => p.id === personId);
  return person ? person.name : "";
};

const renderEquipmentList = () => {
  const items = filteredEquipment();
  elements.equipmentCount.textContent = items.length;
  elements.equipmentList.innerHTML = "";

  items.forEach((equipment) => {
    const card = document.createElement("div");
    const status = statusLabel(equipment);
    card.className = `equipment-card ${
      state.selectedId === equipment.id ? "selected" : ""
    }`;
    card.innerHTML = `
      <div class="equipment-meta">
        <div class="equipment-name">${equipment.name}</div>
        <div class="equipment-sub">
          ${equipment.tag ? `Tag: ${equipment.tag}` : "No tag"} ·
          ${
            equipment.status === "checked_out"
              ? `With ${personName(equipment.checked_out_to) || "Unknown"}`
              : "Available"
          }
        </div>
      </div>
      <div class="equipment-meta" style="align-items: flex-end;">
        <span class="status-pill ${status.className}">${status.label}</span>
        <span class="equipment-sub">${
          equipment.due_at ? `Due ${formatDate(equipment.due_at)}` : ""
        }</span>
      </div>
    `;
    card.addEventListener("click", () => {
      state.selectedId = equipment.id;
      render();
    });
    elements.equipmentList.appendChild(card);
  });
};

const renderDetailsPanel = () => {
  const equipment = state.equipment.find((item) => item.id === state.selectedId);
  if (!equipment) {
    elements.detailsPanel.innerHTML = `
      <div class="details-empty">
        <h2>Pick equipment to see details</h2>
        <p>Select an item from the list to check out, check in, or transfer.</p>
      </div>
    `;
    return;
  }

  const status = statusLabel(equipment);
  const assignedName = personName(equipment.checked_out_to) || "Unassigned";

  elements.detailsPanel.innerHTML = `
    <div class="details-section">
      <h2>${equipment.name}</h2>
      <div class="details-row"><span>Status</span><span>${status.label}</span></div>
      <div class="details-row"><span>Tag</span><span>${equipment.tag || "—"}</span></div>
      <div class="details-row"><span>Assigned to</span><span>${assignedName}</span></div>
      <div class="details-row"><span>Due</span><span>${
        equipment.due_at ? formatDate(equipment.due_at) : "—"
      }</span></div>
      <p class="equipment-sub">${equipment.description || "No description"}</p>
    </div>
    <div class="details-actions" id="actionArea"></div>
    <div class="inline-actions">
      <button class="secondary" id="editEquipment">Edit</button>
      <button class="ghost" id="deleteEquipment">Delete</button>
    </div>
  `;

  renderActionArea(equipment);
  attachDetailEvents(equipment);
};

const renderActionArea = (equipment) => {
  const actionArea = document.getElementById("actionArea");
  if (!actionArea) return;

  const peopleOptions = state.people
    .map((person) => `<option value="${person.id}">${person.name}</option>`)
    .join("");

  if (equipment.status === "available") {
    actionArea.innerHTML = `
      <label>
        Assign to
        <select id="assignPerson">
          <option value="">Select person</option>
          ${peopleOptions}
        </select>
      </label>
      <button class="primary" id="assignBtn">Assign</button>
    `;
    return;
  }

  actionArea.innerHTML = `
    <button class="primary" id="checkInBtn">Check in</button>
    <label>
      Transfer to
      <select id="transferPerson">
        <option value="">Select person</option>
        ${peopleOptions}
      </select>
    </label>
    <button class="secondary" id="transferBtn">Transfer</button>
  `;
};

const attachDetailEvents = (equipment) => {
  const assignBtn = document.getElementById("assignBtn");
  const transferBtn = document.getElementById("transferBtn");
  const checkInBtn = document.getElementById("checkInBtn");
  const editEquipment = document.getElementById("editEquipment");
  const deleteEquipment = document.getElementById("deleteEquipment");

  if (assignBtn) {
    assignBtn.addEventListener("click", async () => {
      const personId = document.getElementById("assignPerson").value;
      if (!personId) {
        showToast("Select a person to assign.", true);
        return;
      }
      try {
        await api("/api/checkout", {
          method: "POST",
          body: JSON.stringify({ equipment_id: equipment.id, person_id: personId }),
        });
        showToast("Equipment assigned.");
        await loadData();
      } catch (error) {
        showToast(error.message, true);
      }
    });
  }

  if (checkInBtn) {
    checkInBtn.addEventListener("click", async () => {
      try {
        await api("/api/checkin", {
          method: "POST",
          body: JSON.stringify({ equipment_id: equipment.id }),
        });
        showToast("Checked in.");
        await loadData();
      } catch (error) {
        showToast(error.message, true);
      }
    });
  }

  if (transferBtn) {
    transferBtn.addEventListener("click", async () => {
      const personId = document.getElementById("transferPerson").value;
      if (!personId) {
        showToast("Select a person to transfer to.", true);
        return;
      }
      try {
        await api("/api/transfer", {
          method: "POST",
          body: JSON.stringify({ equipment_id: equipment.id, person_id: personId }),
        });
        showToast("Equipment transferred.");
        await loadData();
      } catch (error) {
        showToast(error.message, true);
      }
    });
  }

  editEquipment?.addEventListener("click", () => openEquipmentDialog(equipment));
  deleteEquipment?.addEventListener("click", async () => {
    if (!confirm("Delete this equipment?")) return;
    try {
      await api(`/api/equipment/${equipment.id}`, { method: "DELETE" });
      showToast("Equipment deleted.");
      state.selectedId = null;
      await loadData();
    } catch (error) {
      showToast(error.message, true);
    }
  });
};

const renderPeopleList = () => {
  elements.peopleList.innerHTML = "";
  state.people.forEach((person) => {
    const row = document.createElement("div");
    row.className = "person-row";
    row.innerHTML = `
      <div>
        <strong>${person.name}</strong>
        <div class="equipment-sub">${person.email || "No email"} · ${
      person.role || "No role"
    }</div>
      </div>
      <div class="inline-actions">
        <button class="secondary" data-edit="${person.id}">Edit</button>
        <button class="ghost" data-delete="${person.id}">Delete</button>
      </div>
    `;
    elements.peopleList.appendChild(row);
  });

  elements.peopleList.querySelectorAll("button[data-edit]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const personId = btn.dataset.edit;
      const person = state.people.find((p) => p.id === personId);
      if (person) {
        openPeopleDialog(person);
      }
    });
  });

  elements.peopleList.querySelectorAll("button[data-delete]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const personId = btn.dataset.delete;
      if (!confirm("Delete this person?")) return;
      try {
        await api(`/api/people/${personId}`, { method: "DELETE" });
        showToast("Person deleted.");
        await loadData();
        renderPeopleList();
      } catch (error) {
        showToast(error.message, true);
      }
    });
  });
};

const render = () => {
  renderEquipmentList();
  renderDetailsPanel();
};

const openEquipmentDialog = (equipment = null) => {
  elements.equipmentForm.reset();
  state.editingEquipmentId = equipment?.id || null;
  elements.equipmentDialogTitle.textContent = equipment
    ? "Edit equipment"
    : "Add equipment";

  if (equipment) {
    elements.equipmentForm.name.value = equipment.name || "";
    elements.equipmentForm.tag.value = equipment.tag || "";
    elements.equipmentForm.description.value = equipment.description || "";
  }

  elements.equipmentDialog.showModal();
};

const openPeopleDialog = (person = null) => {
  elements.peopleForm.reset();
  state.editingPersonId = person?.id || null;
  elements.peopleDialogTitle.textContent = person ? "Edit person" : "Add person";

  if (person) {
    elements.peopleForm.name.value = person.name || "";
    elements.peopleForm.email.value = person.email || "";
    elements.peopleForm.role.value = person.role || "";
  }

  elements.peopleDialog.showModal();
  renderPeopleList();
};

const closeDialog = (dialogId) => {
  const dialog = document.getElementById(dialogId);
  dialog?.close();
};

const handleEquipmentSubmit = async (event) => {
  event.preventDefault();
  const payload = {
    name: elements.equipmentForm.name.value.trim(),
    tag: elements.equipmentForm.tag.value.trim(),
    description: elements.equipmentForm.description.value.trim(),
  };
  try {
    if (state.editingEquipmentId) {
      await api(`/api/equipment/${state.editingEquipmentId}`, {
        method: "PUT",
        body: JSON.stringify(payload),
      });
      showToast("Equipment updated.");
    } else {
      await api("/api/equipment", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      showToast("Equipment added.");
    }
    closeDialog("equipmentDialog");
    await loadData();
  } catch (error) {
    showToast(error.message, true);
  }
};

const handlePeopleSubmit = async (event) => {
  event.preventDefault();
  const payload = {
    name: elements.peopleForm.name.value.trim(),
    email: elements.peopleForm.email.value.trim(),
    role: elements.peopleForm.role.value.trim(),
  };
  try {
    if (state.editingPersonId) {
      await api(`/api/people/${state.editingPersonId}`, {
        method: "PUT",
        body: JSON.stringify(payload),
      });
      showToast("Person updated.");
    } else {
      await api("/api/people", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      showToast("Person added.");
    }
    closeDialog("peopleDialog");
    await loadData();
  } catch (error) {
    showToast(error.message, true);
  }
};

const bindEvents = () => {
  elements.searchInput.addEventListener("input", (event) => {
    state.search = event.target.value;
    renderEquipmentList();
  });

  elements.filterButtons.forEach((button) => {
    button.addEventListener("click", () => {
      elements.filterButtons.forEach((btn) => btn.classList.remove("active"));
      button.classList.add("active");
      state.filter = button.dataset.filter;
      renderEquipmentList();
    });
  });

  elements.addEquipmentBtn.addEventListener("click", () => openEquipmentDialog());
  elements.managePeopleBtn.addEventListener("click", () => openPeopleDialog());

  elements.equipmentForm.addEventListener("submit", handleEquipmentSubmit);
  elements.peopleForm.addEventListener("submit", handlePeopleSubmit);

  document.querySelectorAll("button[data-close]").forEach((button) => {
    button.addEventListener("click", () => closeDialog(button.dataset.close));
  });
};

bindEvents();
loadData();
