
const form = document.getElementById("ticketForm");
const result = document.getElementById("result");
const submitBtn = document.getElementById("submit-btn");

form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const data = new FormData(form);

    const category = data.get("category_id");
    const locationId = form.dataset.locationId;

    const payload = {
        title: data.get("title"),
        description: data.get("description"),
        category_id: category ? Number(category) : null,
        location_id: locationId ? Number(locationId) : null
    };

    submitBtn.disabled = true;
    submitBtn.textContent = "Отправка...";

    result.textContent = "";

    try {
        const response = await fetch("/tickets/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        const answer = await response.json();

        if (!response.ok) {
            result.textContent =
                typeof answer.detail === "string"
                    ? answer.detail
                    : "Не удалось отправить заявку";

            return;
        }

        result.textContent =
            "Заявка №" + answer.id + " успешно создана!";

        form.reset();

    } catch (error) {
        result.textContent =
            "Не удалось связаться с сервером";

    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = "Отправить заявку";
    }
});
