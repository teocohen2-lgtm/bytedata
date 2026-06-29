let customers = [];
let filteredCustomers = [];
let selectedCustomer = null;
const PAGE_SIZE = 20;
let currentPage = 1;
let allCustomers = [];

document.addEventListener("DOMContentLoaded", () => {
  loadCommunicationDashboard();
  loadCustomers();
  loadCurrentUser();

  const search = document.getElementById("searchCustomer");

  if (search) {
    search.addEventListener("keyup", filterCustomers);
  }
});

async function loadCustomers() {
  try {
    const res = await fetch("/communications-v2data");

    allCustomers = await res.json();

    filteredCustomers = [...allCustomers];

    renderCustomerList();
  } catch (err) {
    console.error(err);
  }
}

function filterCustomers() {
  const keyword = document.getElementById("searchCustomer").value.toLowerCase();

  filteredCustomers = customers.filter(
    (customer) =>
      customer.company_name.toLowerCase().includes(keyword) ||
      customer.customer_name.toLowerCase().includes(keyword) ||
      customer.email.toLowerCase().includes(keyword)
  );

  renderCustomerList();
}

function renderCustomerList() {
  const list = document.getElementById("conversationList");
  const start = (currentPage - 1) * PAGE_SIZE;

  const end = start + PAGE_SIZE;

  const pageCustomers = filteredCustomers.slice(start, end);

  list.innerHTML = "";

  pageCustomers.forEach((customer) => {
    const card = createCustomerCard(customer);

    list.appendChild(card);
  });

  renderPagination();
}

function renderPagination() {
  const total = filteredCustomers.length;

  const totalPages = Math.ceil(total / PAGE_SIZE);

  const start = total === 0 ? 0 : (currentPage - 1) * PAGE_SIZE + 1;

  const end = Math.min(currentPage * PAGE_SIZE, total);

  document.getElementById(
    "paginationInfo"
  ).innerText = `Showing ${start} to ${end} of ${total} conversations`;

  const container = document.getElementById("pagination");

  container.innerHTML = "";

  // Previous

  const prev = document.createElement("button");

  prev.className =
    "w-8 h-8 rounded-lg inner-bg border border-color flex items-center justify-center text-muted hover:text-white";

  prev.innerHTML = '<i class="fas fa-chevron-left text-xs"></i>';

  prev.disabled = currentPage === 1;

  prev.onclick = () => {
    if (currentPage > 1) {
      currentPage--;

      renderCustomerList();
    }
  };

  container.appendChild(prev);

  // Pages

  for (let i = 1; i <= totalPages; i++) {
    const btn = document.createElement("button");

    btn.innerText = i;

    if (i === currentPage) {
      btn.className =
        "w-8 h-8 rounded-lg bg-blue-600 text-white flex items-center justify-center";
    } else {
      btn.className =
        "w-8 h-8 rounded-lg inner-bg border border-color flex items-center justify-center text-muted hover:text-white";
    }

    btn.onclick = () => {
      currentPage = i;

      renderCustomerList();
    };

    container.appendChild(btn);
  }

  // Next

  const next = document.createElement("button");

  next.className =
    "w-8 h-8 rounded-lg inner-bg border border-color flex items-center justify-center text-muted hover:text-white";

  next.innerHTML = '<i class="fas fa-chevron-right text-xs"></i>';

  next.disabled = currentPage === totalPages;

  next.onclick = () => {
    if (currentPage < totalPages) {
      currentPage++;

      renderCustomerList();
    }
  };

  container.appendChild(next);
}

function createCustomerCard(customer) {
  const div = document.createElement("div");

  let activeClass = "";

  if (
    selectedCustomer &&
    selectedCustomer.customer_id === customer.customer_id &&
    selectedCustomer.lead_id === customer.lead_id
  ) {
    activeClass = "border-blue-600 bg-blue-900/10";
  } else {
    activeClass = "border-transparent hover:bg-white/5";
  }

  div.className = `p-3 rounded-xl border cursor-pointer flex gap-3 transition-colors ${activeClass}`;

  div.onclick = () => {
    selectCustomer(customer, div);
  };

  div.innerHTML = `

        <div
            class="w-10 h-10 rounded-full bg-blue-700 flex items-center justify-center font-bold shrink-0">

            ${customer.avatar}

        </div>

        <div class="flex-1 min-w-0">

            <div class="flex justify-between items-start mb-1">

                <div
                    class="font-medium text-white truncate pr-2 flex items-center gap-2">

                    ${customer.company_name}

                    ${statusDot(customer.status)}

                </div>

                <span class="text-[10px] text-muted">

                    ${customer.last_message_time || ""}

                </span>

            </div>

            <div class="flex justify-between items-center">

                <p class="text-xs text-gray-300 truncate pr-3">

                    ${customer.last_message || customer.customer_name}

                </p>

                ${badge(customer.unread_count)}

            </div>

        </div>

    `;

  return div;
}

function badge(count) {
  if (count <= 0) return "";

  return `

        <span

            class="bg-blue-600 text-white text-[10px] px-1.5 py-0.5 rounded-full">

            ${count}

        </span>

    `;
}

function statusDot(status) {
  status = (status || "").toLowerCase();

  if (status === "active")
    return `<span class="w-2 h-2 rounded-full bg-green-500"></span>`;

  if (status === "overdue")
    return `<span class="w-2 h-2 rounded-full bg-red-500"></span>`;

  if (status === "due soon")
    return `<span class="w-2 h-2 rounded-full bg-yellow-500"></span>`;

  return `<span class="w-2 h-2 rounded-full bg-gray-500"></span>`;
}

function updateProfile(customer) {
  document.getElementById("profileEmail").innerHTML = customer.email || "-";

  document.getElementById("profileEmail").href =
    "mailto:" + (customer.email || "");

  document.getElementById("profilePhone").innerHTML = customer.phone || "-";

  document.getElementById("profileCountry").innerHTML = customer.country || "-";

  document.getElementById("profileWebsite").innerHTML =
    customer.company_name || "-";

  document.getElementById("profileStatus").innerHTML = customer.status || "-";

  document.getElementById("profilePriority").innerHTML =
    customer.status == "Overdue" ? "High" : "Medium";

  document.getElementById("profileChannel").innerHTML =
    customer.source || "Email";

  document.getElementById("profileAssigned").innerHTML =
    customer.assigned_to || "-";

  document.getElementById("profileUpdated").innerHTML =
    new Date().toLocaleString();
  document.getElementById("chatCompanyName").innerHTML =
    customer.company_name || "-";

  document.getElementById("chatAvatar").innerHTML = customer.avatar || "B";

  document.getElementById(
    "chatCompanyInfo"
  ).innerHTML = `${customer.status} • ${customer.payment_status}`;
}

function renderMessages(messages) {
  const chat = document.getElementById("chatMessages");

  chat.innerHTML = "";

  if (messages.length === 0) {
    chat.innerHTML = `

            <div class="text-center text-gray-500 py-20">

                No conversation yet

            </div>

        `;

    return;
  }

  messages.forEach((message) => {
    const sender = (message.sender || "").trim().toLowerCase();

    const isAgent = ["agent", "admin", "system", "bytedata"].includes(sender);
    if (isAgent) {
      // RIGHT SIDE
      chat.innerHTML += `
    
        <div class="flex gap-4 max-w-[85%] ml-auto justify-end">
    
            <div class="flex flex-col items-end">
    
                <div class="bg-[#2563EB] text-white p-4 rounded-2xl rounded-tr-sm text-sm">
    
                    ${message.message}
    
                </div>
    
                <div class="text-[10px] text-muted mt-1 mr-1">
    
                    ${message.created_at}
    
                </div>
    
            </div>
    
            <div
                class="w-10 h-10 rounded-full bg-[#1A56DB] flex items-center justify-center text-lg font-bold shrink-0 mt-1">
    
                B
    
            </div>
    
        </div>
    
        `;
    } else {
      // LEFT SIDE
      chat.innerHTML += `
    
        <div class="flex gap-4 max-w-[85%]">
    
            <div
                class="w-10 h-10 rounded-full bg-purple-700 flex items-center justify-center text-lg font-bold shrink-0 mt-1">
    
                ${selectedCustomer.avatar}
    
            </div>
    
            <div>
    
                <div
                    class="bg-[#1A2235] border border-[#2B2A4C] p-4 rounded-2xl rounded-tl-sm text-sm text-gray-200">
    
                    ${message.message}
    
                </div>
    
                <div class="text-[10px] text-muted mt-1 ml-1">
    
                    ${message.created_at}
    
                </div>
    
            </div>
    
        </div>
    
        `;
    }
  });

  chat.scrollTop = chat.scrollHeight;
}

async function loadConversation(leadId) {
  console.log("Loading conversation:", leadId);

  const chat = document.getElementById("chatMessages");

  chat.innerHTML = `
  <div class="flex items-center justify-center h-full text-gray-400">
      <div class="text-center">
          <i class="fas fa-spinner fa-spin text-3xl mb-3"></i>
          <div>Loading conversation...</div>
      </div>
  </div>
  `;
  const res = await fetch("/conversation/" + leadId);

  console.log("Loading conversation:", leadId);

  const messages = await res.json();

  if (!Array.isArray(messages)) {
    console.error(messages);

    return;
  }

  renderMessages(messages);

  fetch(`/mark-conversation-read/${leadId}`, {
    method: "POST",
  });

  // await loadConversation();
}

async function sendMessage() {
  if (!selectedCustomer) {
    alert("Select customer first.");

    return;
  }

  const box = document.getElementById("messageInput");

  const text = box.value.trim();

  if (text == "") return;

  const res = await fetch(
    "/send-message",

    {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify({
        conversation_id: selectedCustomer.conversation_id,
        customer_id: selectedCustomer.customer_id,

        lead_id: selectedCustomer.lead_id,

        company_name: selectedCustomer.company_name,

        customer_name: selectedCustomer.customer_name,

        customer_email: selectedCustomer.email,

        customer_phone: selectedCustomer.phone,

        payment_status: selectedCustomer.payment_status,

        dataset_status: selectedCustomer.dataset_status,

        message: text,
      }),
    }
  );

  const result = await res.json();

  if (result.status == "success") {
    appendAgentMessage(
      text,

      result.created_at
    );

    box.value = "";
  }
}

function appendAgentMessage(
  message,

  time
) {
  const chat = document.getElementById("chatMessages");

  chat.innerHTML += `

    <div class="flex gap-4 max-w-[85%]">

        <div
            class="w-10 h-10 rounded-full bg-[#1A56DB] flex items-center justify-center text-xl font-bold shrink-0 mt-1">

            B

        </div>

        <div>

            <div
                class="bg-[#1A2235] p-4 rounded-2xl rounded-tl-sm text-sm text-gray-200">

                ${message}

            </div>

            <div
                class="text-[10px] text-muted mt-1 ml-1">

                ${time}

            </div>

        </div>

    </div>

    `;

  chat.scrollTop = chat.scrollHeight;
}

function selectCustomer(customer, card) {
  selectedCustomer = customer;
  customer.unread_count = 0;

  // renderCustomerList();
  document
    .querySelectorAll("#conversationList > div")
    .forEach((c) => c.classList.remove("border-blue-600", "bg-blue-900/10"));

  card.classList.add("border-blue-600", "bg-blue-900/10");
  updateProfile(customer);

  // Remove unread badge immediately
  card.querySelector(".bg-blue-600")?.remove();

  loadConversation(customer.lead_id);
}

async function loadCommunicationDashboard() {
  const res = await fetch("/communications-dashboard");

  const data = await res.json();

  setKPI(
    "kpiConversations",
    "kpiConversationChange",
    data.total_conversations,
    data.conversation_change
  );

  setKPI(
    "kpiMessages",
    "kpiMessagesChange",
    data.messages_sent,
    data.messages_change
  );

  setKPI(
    "kpiAwaiting",
    "kpiAwaitingChange",
    data.awaiting_response,
    data.awaiting_change
  );

  setKPI(
    "kpiResolved",
    "kpiResolvedChange",
    data.resolved,
    data.resolved_change
  );

  document.getElementById("todayMessages").textContent = data.today_messages;

  setTrend(
    "todayMessagesChange",

    data.today_change
  );
}

function setKPI(valueId, changeId, value, change) {
  document.getElementById(valueId).childNodes[0].nodeValue = value + " ";

  const changeElement = document.getElementById(changeId);

  if (change >= 0) {
    changeElement.innerHTML = `<i class="fas fa-arrow-up"></i> ${change}%`;

    changeElement.className = "text-green-500 text-xs font-medium mb-0.5";
  } else {
    changeElement.innerHTML = `<i class="fas fa-arrow-down"></i> ${Math.abs(
      change
    )}%`;

    changeElement.className = "text-red-500 text-xs font-medium mb-0.5";
  }
}

async function loadCurrentUser() {
  const res = await fetch("/current-user");

  const user = await res.json();

  document.getElementById("loggedUserName").textContent = user.name;

  document.getElementById("loggedUserRole").textContent = user.role;

  document.getElementById("loggedUserAvatar").textContent = user.avatar;
}

function setTrend(id, value) {
  const el = document.getElementById(id);

  if (value >= 0) {
    el.innerHTML = `<i class="fas fa-arrow-up"></i> ${value}%`;

    el.className = "text-green-500 text-xs font-medium";
  } else {
    el.innerHTML = `<i class="fas fa-arrow-down"></i> ${Math.abs(value)}%`;

    el.className = "text-red-500 text-xs font-medium";
  }
}

// setInterval(async () => {
//   // Refresh left conversation list
//   await loadCustomers();

//   // Refresh current open chat
//   if (selectedCustomer) {
//     const res = await fetch("/conversation/" + selectedCustomer.lead_id);

//     const messages = await res.json();

//     renderMessages(messages);
//   }
// }, 30000);

function sendReminder() {
  alert("Reminder Email Sent Successfully");
}
function sendPaymentLink() {
  alert("Payment Link Sent Successfully");
}
function checkPaymentStatus() {
  alert("Payment status check completed");
}

async function markConversationResolved() {
  if (!selectedCustomer) {
    alert("Select customer first.");
    return;
  }

  const btn = event.currentTarget;

  const confirmClose = confirm(
    "Mark this conversation as resolved?\n\nThe AI customer will stop replying."
  );

  if (!confirmClose) return;

  btn.disabled = true;

  btn.innerHTML = `<i class="fas fa-spinner fa-spin"></i> Processing...`;

  try {
    const res = await fetch("/resolve-conversation", {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify({
        customer_id: selectedCustomer.customer_id,

        lead_id: selectedCustomer.lead_id,
      }),
    });

    const result = await res.json();

    if (result.status === "success") {
      btn.innerHTML = `<i class="fas fa-check"></i> Resolved`;

      setTimeout(() => {
        alert("Conversation marked as resolved.");

        closeConversation();

        loadCustomers();
      }, 600);
    } else {
      alert(result.message);

      btn.disabled = false;

      btn.innerHTML = `<i class="fas fa-check"></i> Mark as Resolved`;
    }
  } catch (err) {
    console.error(err);

    alert("Something went wrong.");

    btn.disabled = false;

    btn.innerHTML = `<i class="fas fa-check"></i> Mark as Resolved`;
  }
}

function openTaskModal() {
  if (!selectedCustomer) {
    alert("Select customer first.");
    return;
  }
  document.getElementById("taskResult").innerHTML = "";

  document.getElementById("submitTaskBtn").disabled = false;

  document.getElementById(
    "submitTaskBtn"
  ).innerHTML = `<i class="far fa-calendar-check"></i> Submit Task`;

  document.getElementById("taskCompany").value =
    selectedCustomer.company_name || "";

  document.getElementById("taskCustomer").value =
    selectedCustomer.customer_name || "";

  document.getElementById("taskTitle").value = "";

  document.getElementById("taskDescription").value = "";

  document.getElementById("taskPriority").value = "Medium";

  document.getElementById("taskDueDate").value = "";

  document.getElementById("taskModal").classList.remove("hidden");
  document.getElementById("taskModal").classList.add("flex");
}

function closeTaskModal() {
  document.getElementById("taskModal").classList.add("hidden");
  document.getElementById("taskModal").classList.remove("flex");
}

async function submitSupportTask() {
  if (!selectedCustomer) {
    alert("Select customer first.");
    return;
  }

  const title = document.getElementById("taskTitle").value.trim();
  const description = document.getElementById("taskDescription").value.trim();

  if (!title || !description) {
    alert("Please enter task title and description.");
    return;
  }

  const btn = document.getElementById("submitTaskBtn");

  btn.disabled = true;
  btn.innerHTML = `<i class="fas fa-spinner fa-spin"></i> Creating...`;

  try {
    const res = await fetch("/create-support-task", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        conversation_id: selectedCustomer.conversation_id || "",
        customer_id: selectedCustomer.customer_id || "",
        lead_id: selectedCustomer.lead_id || "",
        company_name: selectedCustomer.company_name || "",
        customer_name: selectedCustomer.customer_name || "",
        customer_email: selectedCustomer.email || "",
        assigned_to: selectedCustomer.assigned_to || "",
        task_title: title,
        task_description: description,
        priority: document.getElementById("taskPriority").value,
        due_date: document.getElementById("taskDueDate").value,
        notes: "",
      }),
    });

    const result = await res.json();

    if (result.status === "success") {
      btn.innerHTML = `<i class="fas fa-check"></i> Task Created`;

      document.getElementById("taskResult").innerHTML = `
        <div class="mt-4 p-3 rounded-lg bg-green-900/30 border border-green-600 text-sm text-green-200">
          <div class="mb-2 font-medium">Task created successfully</div>
    
          <div class="flex items-center justify-between gap-2 bg-[#111726] border border-color rounded-lg px-3 py-2">
            <span id="createdTaskId" class="font-mono text-white">${result.task_id}</span>
    
            <button
              onclick="copyTaskId()"
              class="text-xs bg-blue-600 hover:bg-blue-700 text-white px-2 py-1 rounded"
            >
              Copy
            </button>
          </div>
        </div>
      `;

      btn.disabled = true;
    } else {
      alert(result.message || "Failed to create task.");
      btn.disabled = false;
      btn.innerHTML = `<i class="far fa-calendar-check"></i> Submit Task`;
    }
  } catch (err) {
    console.error(err);
    alert("Something went wrong while creating task.");
    btn.disabled = false;
    btn.innerHTML = `<i class="far fa-calendar-check"></i> Submit Task`;
  }
}

function copyTaskId() {
  const taskId = document.getElementById("createdTaskId").innerText;

  navigator.clipboard.writeText(taskId);

  alert("Task ID copied: " + taskId);
}
