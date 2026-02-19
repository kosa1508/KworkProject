// ========== PROFILE MENU + TABS + SUPPORT + PROMO ==========

document.addEventListener("DOMContentLoaded", () => {

    /* ===============================
       PROFILE DROPDOWN MENU
    =============================== */
    const profileBtn = document.getElementById("profileBtn");
    const profileMenu = document.getElementById("profileMenu");

    if (profileBtn && profileMenu) {

        // Открытие / закрытие меню
        profileBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            profileMenu.classList.toggle("open");
            profileBtn.classList.toggle("arrow-open");
        });

        // Закрытие кликом вне
        document.addEventListener("click", (e) => {
            if (!profileMenu.contains(e.target) && !profileBtn.contains(e.target)) {
                profileMenu.classList.remove("open");
                profileBtn.classList.remove("arrow-open");
            }
        });

    } else {
        console.warn("Profile menu elements not found");
    }


    /* ===============================
       PROFILE TABS (INVENTORY / WITHDRAWS)
    =============================== */
    const tabs = document.querySelectorAll(".or-profile-tab-wide");
    const sections = document.querySelectorAll(".or-profile-section");

    if (tabs.length && sections.length) {
        tabs.forEach(tab => {
            tab.addEventListener("click", () => {

                const targetId = tab.dataset.tab;

                tabs.forEach(t => t.classList.remove("active"));
                sections.forEach(sec => sec.classList.remove("active"));

                tab.classList.add("active");

                const targetSection = document.getElementById(targetId);
                if (targetSection) {
                    targetSection.classList.add("active");
                }
            });
        });
    }


    /* ===============================
       SUPPORT CHAT (HELP BUTTON)
    =============================== */
    const helpBtn = document.getElementById("helpBtn");
    const supportWindow = document.getElementById("supportWindow");
    const supportClose = document.getElementById("supportClose");
    const supportIcon = document.getElementById("supportIcon");

    if (helpBtn && supportWindow) {
        helpBtn.addEventListener("click", (e) => {
            e.preventDefault();

            profileMenu?.classList.remove("open");
            profileBtn?.classList.remove("arrow-open");

            supportWindow.classList.remove("hidden");
        });
    }

    if (supportIcon && supportWindow) {
        supportIcon.addEventListener("click", () => {
            supportWindow.classList.remove("hidden");
        });
    }

    if (supportClose && supportWindow) {
        supportClose.addEventListener("click", () => {
            supportWindow.classList.add("hidden");
        });
    }


    /* ===============================
       PROMO CODE MODAL
    =============================== */

    const promoBtn = document.querySelector('[onclick*="openPromo"]');
    const promoOverlay = document.getElementById("promoOverlay");

    // Открытие промо
    window.openPromo = function () {
        if (!promoOverlay) return;

        // закрываем профильное меню
        profileMenu?.classList.remove("open");
        profileBtn?.classList.remove("arrow-open");

        promoOverlay.style.display = "flex";
    };

    // Закрытие промо
    window.closePromo = function () {
        if (!promoOverlay) return;
        promoOverlay.style.display = "none";
    };

    // Закрытие по клику на фон
    if (promoOverlay) {
        promoOverlay.addEventListener("click", (e) => {
            if (e.target === promoOverlay) {
                closePromo();
            }
        });
    }

});