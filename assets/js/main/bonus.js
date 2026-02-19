const DAYS = 6;

let bonusData = JSON.parse(localStorage.getItem("dailyBonus")) || {
    day: 1,
    lastClaim: 0
};

const grid = document.getElementById("bonusGrid");
const timer = document.getElementById("bonusTimer");

function renderGrid() {
    grid.innerHTML = "";

    for (let i = 1; i <= DAYS; i++) {
        const tile = document.createElement("div");
        tile.className = "bonus-tile";

        if (i < bonusData.day) tile.classList.add("completed");
        if (i === bonusData.day) tile.classList.add("active");

        tile.innerHTML = `
            ${i}
            <span>День ${i}</span>
        `;

        grid.appendChild(tile);
    }
}

function updateTimer() {
    if (!bonusData.lastClaim) {
        timer.textContent = "—";
        return;
    }

    let diff = bonusData.lastClaim + 86400000 - Date.now();
    if (diff <= 0) {
        timer.textContent = "Доступно!";
        return;
    }

    let h = Math.floor(diff / 3600000);
    let m = Math.floor((diff % 3600000) / 60000);
    let s = Math.floor((diff % 60000) / 1000);

    timer.textContent =
        ${String(h).padStart(2, '0')}: +
        ${String(m).padStart(2, '0')}: +
        ${String(s).padStart(2, '0')};
}

function checkProgress() {
    if (!bonusData.lastClaim) return;

    if (Date.now() - bonusData.lastClaim > 86400000) {
        bonusData.day = 1;
        localStorage.setItem("dailyBonus", JSON.stringify(bonusData));
    }
}

function claimBonus() {
    const today = new Date().toDateString();

    if (localStorage.getItem("claimedToday") === today) return;

    bonusData.lastClaim = Date.now();
    bonusData.day++;

    if (bonusData.day > DAYS) bonusData.day = 1;

    localStorage.setItem("dailyBonus", JSON.stringify(bonusData));
    localStorage.setItem("claimedToday", today);

    renderGrid();
}

// INITIAL
checkProgress();
claimBonus();
renderGrid();

setInterval(updateTimer, 1000);