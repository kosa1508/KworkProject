/* ================= CASE DATA (ЗАГЛУШКА) ================= */

const CASES = {
    default: {
        title: "Название кейса",
        price: 199,
        drops: [
            { name: "Обычный предмет", price: 12 },
            { name: "Редкий предмет", price: 120 },
            { name: "Легендарный предмет", price: 999 }
        ]
    }
};

/* ================= GET CASE ================= */

const params = new URLSearchParams(window.location.search);
const caseId = params.get("case") || "default";

const currentCase = CASES[caseId] || CASES.default;

/* ================= SET UI ================= */

document.getElementById("caseTitle").innerText = currentCase.title;
document.getElementById("casePrice").innerText = `OR ${currentCase.price}`;

/* ================= OPEN CASE ================= */

const openBtn = document.getElementById("openBtn");
const resultBlock = document.getElementById("caseResult");

openBtn.addEventListener("click", () => {
    const fast = document.getElementById("fastOpen").checked;

    openBtn.disabled = true;
    openBtn.innerText = "Открываем...";

    const drop =
        currentCase.drops[
            Math.floor(Math.random() * currentCase.drops.length)
        ];

    if (fast) {
        showResult(drop);
    } else {
        setTimeout(() => showResult(drop), 1200);
    }
});

function showResult(drop) {
    openBtn.disabled = false;
    openBtn.innerText = "Открыть кейс";

    document.getElementById("dropName").innerText = drop.name;
    document.getElementById("dropPrice").innerText = `OR ${drop.price}`;

    resultBlock.classList.remove("hidden");
}
