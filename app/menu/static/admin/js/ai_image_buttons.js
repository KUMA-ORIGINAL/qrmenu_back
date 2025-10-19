function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(";").shift();
}

function getId() {
    const m = window.location.pathname.match(/\/(\d+)\/change\/$/);
    return m ? m[1] : null;
}

function getBasePath() {
    return window.location.pathname.replace(/\/\d+\/change\/$/, "/");
}

function sendAIAction(button, endpoint, actionText, successText, errorText) {
    const id = getId();
    if (!id) {
        alert("Сначала сохраните объект, чтобы получить ID");
        return;
    }

    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || getCookie("csrftoken");
    const base = getBasePath();

    button.textContent = `${actionText}...`;
    button.disabled = true;

    fetch(`${base}${endpoint}/${id}/`, {
        method: "POST",
        headers: {
            "X-CSRFToken": csrftoken,
            "Content-Type": "application/json",
        },
    })
        .then((r) => {
            if (r.redirected) throw new Error("Redirected to login или другой URL");
            if (!r.ok) throw new Error(`HTTP ${r.status}`);
            return r.json();
        })
        .then((data) => {
            if (data.ok) {
                alert(successText);
                window.location.reload();
            } else {
                alert("Ошибка: " + (data.error || "неизвестная ошибка"));
            }
        })
        .catch((e) => alert(`${errorText}: ${e.message}`))
        .finally(() => {
            button.textContent = actionText;
            button.disabled = false;
        });
}

function aiImprove(button) {
    sendAIAction(button, "ai_improve", "Улучшаем", "Изображение улучшено ✅", "Ошибка при улучшении");
}

function aiGenerate(button) {
    sendAIAction(button, "ai_generate", "Генерируем", "Изображение сгенерировано ✅", "Ошибка при генерации");
}