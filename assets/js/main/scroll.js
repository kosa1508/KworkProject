// ===== НАСТРОЙКИ =====
const OFFSET = 180; // высота фиксированного хедера
const cats = document.querySelectorAll('.bd-cat');
const sections = Array.from(document.querySelectorAll('.cases-category'));
const filterContainer = document.getElementById('bdWindow');

// ===== АКТИВНАЯ КАТЕГОРИЯ =====
function setActiveCat(id) {
    cats.forEach(cat => {
        cat.classList.toggle('active', cat.dataset.target === id);
    });

    scrollFilterToActive();
}

// ===== АВТОСКРОЛЛ ФИЛЬТРА =====
function scrollFilterToActive() {
    const active = document.querySelector('.bd-cat.active');
    if (!active || !filterContainer) return;

    const containerRect = filterContainer.getBoundingClientRect();
    const activeRect = active.getBoundingClientRect();

    // если активная категория вне видимой области
    if (
        activeRect.left < containerRect.left ||
        activeRect.right > containerRect.right
    ) {
        const scrollLeft =
            active.offsetLeft -
            filterContainer.clientWidth / 2 +
            active.clientWidth / 2;

        filterContainer.scrollTo({
            left: scrollLeft,
            behavior: 'smooth'
        });
    }
}

// ===== КЛИК ПО ФИЛЬТРУ =====
cats.forEach(cat => {
    cat.addEventListener('click', () => {
        const targetId = cat.dataset.target;
        const target = document.getElementById(targetId);
        if (!target) return;

        setActiveCat(targetId);

        const y =
            target.getBoundingClientRect().top +
            window.pageYOffset -
            OFFSET;

        window.scrollTo({
            top: y,
            behavior: 'smooth'
        });
    });
});

// ===== SCROLL-SPY =====
window.addEventListener('scroll', () => {
    let current = null;

    sections.forEach(section => {
        const rect = section.getBoundingClientRect();
        const trigger = OFFSET + 20;

        if (rect.top <= trigger && rect.bottom > trigger) {
            current = section.id;
        }
    });

    if (current) setActiveCat(current);
});