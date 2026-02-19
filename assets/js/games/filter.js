// ===== ПЕРЕМЕННЫЕ =====
const bdList = document.getElementById("bdList");
const bdWindow = document.getElementById("bdWindow");

const bdLeft = document.getElementById("bdLeft");
const bdRight = document.getElementById("bdRight");

// ===== ОБНОВЛЕНИЕ СТРЕЛОК =====
function updateBDArrows() {
    const maxScroll = bdList.scrollWidth - bdWindow.clientWidth;

    bdLeft.classList.toggle("disabled", bdWindow.scrollLeft <= 0);
    bdRight.classList.toggle("disabled", bdWindow.scrollLeft >= maxScroll - 5);
}

// ===== ПЛАВНОЕ ПЕРЕЛИСТЫВАНИЕ =====
const SCROLL_AMOUNT = 220; // можно менять (180–230 идеально)

// ВЛЕВО
bdLeft.onclick = () => {
    bdWindow.scrollBy({
        left: -SCROLL_AMOUNT,
        behavior: "smooth"
    });
};

// ВПРАВО
bdRight.onclick = () => {
    bdWindow.scrollBy({
        left: SCROLL_AMOUNT,
        behavior: "smooth"
    });
};

// При ручном скролле — обновлять стрелки
bdWindow.addEventListener("scroll", updateBDArrows);

// Стартовое обновление
updateBDArrows();


// ===== АКТИВНАЯ КАТЕГОРИЯ =====
document.querySelectorAll(".bd-cat").forEach(cat => {
    cat.addEventListener("click", () => {
        document.querySelectorAll(".bd-cat").forEach(c => c.classList.remove("active"));
        cat.classList.add("active");
    });
});