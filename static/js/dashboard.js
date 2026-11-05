const API_URL = "";

const token = sessionStorage.getItem("access_token");

let allTickets = [];

const ticketsBody = document.getElementById("tickets-body");
const searchInput = document.getElementById("search-input");
const statusFilter = document.getElementById("status-filter");

// Проверяем авторизацию
if (!token) {
    window.location.href = "/login";
}

// Общие настройки запросов
function getHeaders() {
    return {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json"
    };
}

// Получаем данные пользователя
async function loadUser() {
    try {
        const response = await fetch(`${API_URL}/auth/me`, {
            headers: getHeaders()
        });

        if (response.status === 401) {
            logout();
            return;
        }

        if (!response.ok) {
            throw new Error("Не удалось получить пользователя");
        }

        const user = await response.json();

        if (!["employee", "admin"].includes(user.role)) {
            window.location.href = "/";
            return;
        }

        document.getElementById("user-name").textContent =
            user.full_name;

        document.getElementById("user-avatar").textContent =
            user.full_name.charAt(0).toUpperCase();

    } catch (error) {
        console.error(error);
        alert("Не удалось проверить пользователя");
    }
}

// Получаем заявки
async function loadTickets() {
    ticketsBody.innerHTML = `
        <tr>
            <td colspan="6" class="loading">
                Загружаем заявки...
            </td>
        </tr>
    `;

    try {
        const response = await fetch(
            `${API_URL}/tickets/?limit=100&offset=0`,
            {
                headers: getHeaders()
            }
        );

        if (response.status === 401) {
            logout();
            return;
        }

        if (!response.ok) {
            throw new Error("Ошибка загрузки заявок");
        }

        allTickets = await response.json();

        updateStatistics();
        renderTickets();

    } catch (error) {
        console.error(error);

        ticketsBody.innerHTML = `
            <tr>
                <td colspan="6" class="empty">
                    Не удалось загрузить заявки.
                    Попробуйте обновить страницу.
                </td>
            </tr>
        `;
    }
}

// Считаем статистику
function updateStatistics() {
    document.getElementById("total-count").textContent =
        allTickets.length;

    document.getElementById("new-count").textContent =
        allTickets.filter(t => t.status === "Новая").length;

    document.getElementById("progress-count").textContent =
        allTickets.filter(t => t.status === "В процессе").length;

    document.getElementById("resolved-count").textContent =
        allTickets.filter(t => t.status === "Решена").length;
}

// Безопасное отображение текста
function escapeHTML(value) {
    return String(value ?? "").replace(/[&<>"']/g, char => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#039;"
    })[char]);
}

// Определяем CSS-класс статуса
function getStatusClass(status) {
    const classes = {
        "Новая": "status-new",
        "В процессе": "status-progress",
        "Решена": "status-resolved",
        "Отклонена": "status-rejected"
    };

    return classes[status] || "";
}

// Выводим заявки в таблицу
function renderTickets() {
    const search = searchInput.value.toLowerCase().trim();
    const selectedStatus = statusFilter.value;

    const filteredTickets = allTickets.filter(ticket => {
        const matchesSearch = ticket.title
            .toLowerCase()
            .includes(search);

        const matchesStatus = !selectedStatus ||
            ticket.status === selectedStatus;

        return matchesSearch && matchesStatus;
    });

    ticketsBody.innerHTML = "";

    if (filteredTickets.length === 0) {
        ticketsBody.innerHTML = `
            <tr>
                <td colspan="6" class="empty">
                    Заявки не найдены
                </td>
            </tr>
        `;

        document.getElementById("tickets-info").textContent =
            "Нет подходящих заявок";

        return;
    }

    filteredTickets.forEach(ticket => {
        const row = document.createElement("tr");

        const statusOptions = [
            "Новая",
            "В процессе",
            "Решена",
            "Отклонена"
        ];

        const statusSelect = statusOptions.map(status => `
            <option value="${status}"
                ${ticket.status === status ? "selected" : ""}>
                ${status}
            </option>
        `).join("");

        row.innerHTML = `
            <td>#${ticket.id}</td>

            <td class="ticket-title">
                ${escapeHTML(ticket.title)}
            </td>

            <td>${escapeHTML(ticket.category_name ?? "—")}</td>

<td>${escapeHTML(ticket.location_name ? "Кабинет " + ticket.location_name : "—")}</td>

            <td>
                ${new Date(ticket.created_at).toLocaleDateString("ru-RU")}
            </td>

            <td>
                <select
                    class="status-select ${getStatusClass(ticket.status)}"
                    data-ticket-id="${ticket.id}">
                    ${statusSelect}
                </select>
            </td>
        `;

        ticketsBody.appendChild(row);
    });

    document.getElementById("tickets-info").textContent =
        `Показано заявок: ${filteredTickets.length}`;
}

// Изменяем статус заявки
async function updateTicketStatus(ticketId, newStatus) {
    try {
        const response = await fetch(
            `${API_URL}/tickets/${ticketId}/status`,
            {
                method: "PATCH",
                headers: getHeaders(),
                body: JSON.stringify({
                    status: newStatus
                })
            }
        );

        if (response.status === 401) {
            logout();
            return;
        }

        if (!response.ok) {
            throw new Error("Не удалось изменить статус");
        }

        await loadTickets();

    } catch (error) {
        console.error(error);
        alert("Ошибка изменения статуса");
        await loadTickets();
    }
}

// Обработчик изменения статуса
ticketsBody.addEventListener("change", event => {
    if (event.target.classList.contains("status-select")) {
        const ticketId = event.target.dataset.ticketId;
        const newStatus = event.target.value;

        updateTicketStatus(ticketId, newStatus);
    }
});

// Поиск
searchInput.addEventListener("input", renderTickets);

// Фильтрация
statusFilter.addEventListener("change", renderTickets);

// Обновление
document.getElementById("refresh-btn").addEventListener(
    "click",
    loadTickets
);

// Выход
function logout() {
    sessionStorage.removeItem("access_token");
    window.location.href = "/login";
}

document.getElementById("logout-btn").addEventListener(
    "click",
    logout
);

// Запуск
async function initDashboard() {
    await loadUser();
    await loadTickets();
}

initDashboard();