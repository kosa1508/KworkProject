import { initBalanceUI } from "./core/balance-ui.js";
import { initCasesUI } from "./core/cases-ui.js";


document.addEventListener("DOMContentLoaded", () => {

// =======================================
// ========== CATEGORY ARROW =============
// =======================================
const scrollBox = document.getElementById("catScroll");
const arrow = document.getElementById("catArrow");

let direction = 1;

if (arrow && scrollBox) {
    arrow.onclick = () => {
        scrollBox.scrollBy({
            left: direction * 200,
            behavior: "smooth"
        });

        if (scrollBox.scrollLeft + scrollBox.clientWidth >= scrollBox.scrollWidth - 50) {
            direction = -1;
            arrow.textContent = "←";
        } else if (scrollBox.scrollLeft <= 50) {
            direction = 1;
            arrow.textContent = "→";
        }
    };
}


// =======================================
// ========== ELEMENTS ====================
// =======================================
const supportWindow = document.getElementById("supportWindow");
const supportIcon   = document.getElementById("supportIcon");
const supportClose  = document.getElementById("supportClose");
const supportHeader = document.getElementById("supportHeader");

const chatBody  = document.getElementById("chatBody");
const chatInput = document.getElementById("chatInput");
const chatSend  = document.getElementById("chatSend");

let chatInitialized = false;


// =======================================
// ========== OPEN / CLOSE ================
// =======================================
if (supportIcon) {
    supportIcon.onclick = () => {
        supportWindow.classList.remove("hidden");
        initChat();
    };
}

if (supportClose) {
    supportClose.onclick = () => {
        supportWindow.classList.add("hidden");
    };
}


// =======================================
// ========== DATE / TIME =================
// =======================================
function getTime() {
    const d = new Date();
    return d.toLocaleTimeString("ru-RU", {
        hour: "2-digit",
        minute: "2-digit"
    });
}

function getDate() {
    return new Date().toLocaleDateString("ru-RU", {
        day: "2-digit",
        month: "2-digit",
        year: "numeric"
    });
}


// =======================================
// ========== CHAT UI =====================
// =======================================
function addDate() {
    const date = document.createElement("div");
    date.className = "chat-date";
    date.innerText = getDate();
    chatBody.appendChild(date);
}

function addMsg(text, type) {
    const msg = document.createElement("div");
    msg.className = `msg ${type}`;
    msg.innerText = text;

    const time = document.createElement("div");
    time.className = "msg-time";
    time.innerText = getTime();

    chatBody.appendChild(msg);
    chatBody.appendChild(time);
    chatBody.scrollTop = chatBody.scrollHeight;
}


// =======================================
// ========== INIT CHAT ===================
// =======================================
function initChat() {
    if (chatInitialized) return;
    chatInitialized = true;

    addDate();
    addMsg(
        "Здравствуйте! Вы общаетесь с оператором ZIVRIK. Опишите вашу проблему, и я постараюсь помочь.",
        "operator"
    );
}


// =======================================
// ========== SEND MESSAGE ================
// =======================================
function sendMessage() {
    const text = chatInput.value.trim();
    if (!text) return;

    addMsg(text, "user");
    chatInput.value = "";

    // Заглушка ответа оператора (потом заменится на админку / backend)
    setTimeout(() => {
        addMsg(
            "Ваше сообщение получено. Оператор ответит вам в ближайшее время.",
            "operator"
        );
    }, 800);
}

if (chatSend) {
    chatSend.onclick = sendMessage;
}

if (chatInput) {
    chatInput.addEventListener("keydown", e => {
        if (e.key === "Enter") sendMessage();
    });
}


// =======================================
// ========== DRAG WINDOW =================
// =======================================
let isDragging = false;
let offsetX = 0;
let offsetY = 0;

supportHeader.addEventListener("mousedown", e => {
    isDragging = true;
    offsetX = e.clientX - supportWindow.offsetLeft;
    offsetY = e.clientY - supportWindow.offsetTop;
    supportHeader.style.cursor = "grabbing";
});

document.addEventListener("mousemove", e => {
    if (!isDragging) return;

    supportWindow.style.left = `${e.clientX - offsetX}px`;
    supportWindow.style.top  = `${e.clientY - offsetY}px`;
    supportWindow.style.right = "auto";
    supportWindow.style.bottom = "auto";
});

document.addEventListener("mouseup", () => {
    isDragging = false;
    supportHeader.style.cursor = "grab";
});


// =======================================
// ========== ORpass COUNTDOWN ===========
// =======================================
const launchDate = new Date("2025-01-10T00:00:00").getTime();

function updateTimer() {
    const t = document.getElementById("timer");
    if (!t) return;

    const now = Date.now();
    const diff = launchDate - now;

    if (diff <= 0) {
        t.innerHTML = "Уже скоро!";
        return;
    }

    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    const hours = Math.floor((diff / (1000 * 60 * 60)) % 24);
    const minutes = Math.floor((diff / (1000 * 60)) % 60);
    const seconds = Math.floor((diff / 1000) % 60);

    document.getElementById("days").innerText = days.toString().padStart(2, "0");
    document.getElementById("hours").innerText = hours.toString().padStart(2, "0");
    document.getElementById("minutes").innerText = minutes.toString().padStart(2, "0");
    document.getElementById("seconds").innerText = seconds.toString().padStart(2, "0");
}

setInterval(updateTimer, 1000);
updateTimer();


// =======================================
// ========== AUTH OPEN/CLOSE ============
// =======================================

const authBg = document.getElementById("authBg");
const authWindow = document.getElementById("authWindow");
const authClose = document.getElementById("authClose");
const loginBtn = document.querySelector(".btn-login");

// ==== открыть окно авторизации ====
if (loginBtn && authBg && authWindow) {
    loginBtn.addEventListener("click", () => {
        authBg.style.display = "block";
        authWindow.classList.add("open");
    });
}

// ==== закрыть крестиком ====
if (authClose && authBg && authWindow) {
    authClose.addEventListener("click", () => {
        authBg.style.display = "none";
        authWindow.classList.remove("open");
    });
}

// ==== закрыть кликом на фон ====
if (authBg && authWindow) {
    authBg.addEventListener("click", () => {
        authBg.style.display = "none";
        authWindow.classList.remove("open");
    });
}


// ===========================================
// =============== BANNERS ====================
// ===========================================

let bannerIndex = 0;
const track = document.querySelector(".slider-track");
const slides = document.querySelectorAll(".banner-slide");

if (track && slides.length > 0) {
    function rotateBanner() {
        bannerIndex = (bannerIndex + 1) % slides.length;
        track.style.transform = `translateX(-${bannerIndex * 100}%)`;
    }

    setInterval(rotateBanner, 5000);
}


// =======================================
// =============== TOWER GAME ============
// =======================================

    const grid = document.getElementById("towerGrid");
    if (!grid) return; // Если не на странице башни — выходим

    console.log("Tower.js loaded");

    let mode = "easy"; // easy = 2 колонки, hard = 3
    const rows = 10;

    function renderGrid() {
        grid.innerHTML = "";

        const cols = mode === "easy" ? 2 : 3;

        for (let r = 0; r < rows; r++) {
            const row = document.createElement("div");
            row.className = "tower-row";
            row.style.gridTemplateColumns = `repeat(${cols}, 1fr)`;

            for (let c = 0; c < cols; c++) {
                const cell = document.createElement("div");
                cell.className = "tower-cell";
                cell.textContent = "+0.3";
                row.appendChild(cell);
            }

            grid.appendChild(row);
        }
    }

    // Первая отрисовка
    renderGrid();

    // Переключение сложности
    document.querySelectorAll(".diff-btn").forEach(btn => {
        btn.addEventListener("click", () => {

            document.querySelectorAll(".diff-btn")
                .forEach(x => x.classList.remove("active"));

            btn.classList.add("active");

            mode = btn.dataset.mode;
            renderGrid();
        });
    });


    // --- Запускаем только на странице Tower ---
    if (!window.location.pathname.includes("tower")) {
        return; 
    }

    const betInput = document.querySelector(".bet-input");
    const betMinus = document.querySelector(".bet-minus");
    const betPlus = document.querySelector(".bet-plus");

    // Если элементов нет — значит tower ещё не загружен
    if (!betInput || !betMinus || !betPlus) {
        return; 
    }

    // --- ЛОГИКА МИНУС ---
    betMinus.addEventListener("click", () => {
        let v = parseInt(betInput.value) || 0;
        v = Math.max(1, v - 100);
        betInput.value = v;
    });

    // --- ЛОГИКА ПЛЮС ---
    betPlus.addEventListener("click", () => {
        let v = parseInt(betInput.value) || 0;
        betInput.value = v + 100;
    });

    // --- РУЧНОЙ ВВОД ---
    betInput.addEventListener("input", () => {
        let v = parseInt(betInput.value);
        if (isNaN(v) || v < 1) betInput.value = 1;
    });


if (document.querySelector(".ladder-grid")) {

    document.querySelectorAll(".ladder-row").forEach(row => {
        let count = row.dataset.count;
        for (let i = 0; i < count; i++) {
            let cell = document.createElement("div");
            cell.className = "ladder-cell";
            row.appendChild(cell);
        }
    });

}



initBalanceUI();
initCasesUI();

});