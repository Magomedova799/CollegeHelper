
const loginForm = document.getElementById("loginForm");
const errorMessage = document.getElementById("errorMessage");
const loginButton = document.getElementById("loginButton");

loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    errorMessage.textContent = "";
    loginButton.disabled = true;
    loginButton.textContent = "Выполняется вход...";

    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;

    try {
        // 1. Отправляем email и пароль на backend
        const loginResponse = await fetch("/auth/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                email: email,
                password: password
            })
        });

        const loginData = await loginResponse.json();

        if (!loginResponse.ok) {
            throw new Error(loginData.detail || "Неверный email или пароль");
        }

        // 2. Сохраняем полученный токен
        sessionStorage.setItem(
            "access_token",
            loginData.access_token
        );

        // 3. Проверяем пользователя через backend
        const userResponse = await fetch("/auth/me", {
            headers: {
                "Authorization": `Bearer ${loginData.access_token}`
            }
        });

        const userData = await userResponse.json();

        if (!userResponse.ok) {
            sessionStorage.removeItem("access_token");
            throw new Error("Не удалось проверить пользователя");
        }

        // 4. Проверяем роль пользователя
        if (!["employee", "admin"].includes(userData.role)) {
            sessionStorage.removeItem("access_token");
            throw new Error("Доступ разрешён только сотрудникам колледжа");
        }

        // 5. Открываем панель сотрудников
        window.location.href = "/dashboard";

    } catch (error) {
        errorMessage.textContent = error.message;
    } finally {
        loginButton.disabled = false;
        loginButton.textContent = "Войти";
    }
});
