// deposit.js - функционал страницы пополнения баланса

document.addEventListener('DOMContentLoaded', function() {
    // Элементы управления
    const amountInput = document.getElementById('amountInput');
    const amountSlider = document.getElementById('amountSlider');
    const quickAmounts = document.querySelectorAll('.quick-amount');
    const methodCards = document.querySelectorAll('.method-card');
    const depositBtn = document.getElementById('depositBtn');

    // Элементы для отображения сумм
    const payAmountElement = document.getElementById('payAmount');
    const commissionAmountElement = document.getElementById('commissionAmount');
    const totalAmountElement = document.getElementById('totalAmount');

    // Поддержка
    const supportBtn = document.getElementById('supportBtn');
    const supportIconBtn = document.getElementById('supportIconBtn');
    const supportWindow = document.getElementById('supportWindow');
    const supportClose = document.getElementById('supportClose');

    // FAQ
    const faqItems = document.querySelectorAll('.faq-item');

    // Текущие значения
    let currentAmount = 1000;
    let currentMethod = 'card';
    let commissionRate = 0; // 0% для карт РФ

    // Инициализация
    updateAmounts();

    // Связь input и slider
    amountInput.addEventListener('input', function() {
        const value = parseInt(this.value) || 0;
        amountSlider.value = value;
        currentAmount = value;
        updateAmounts();
        updateQuickAmounts();
    });

    amountSlider.addEventListener('input', function() {
        const value = parseInt(this.value);
        amountInput.value = value;
        currentAmount = value;
        updateAmounts();
        updateQuickAmounts();
    });

    // Быстрые суммы
    quickAmounts.forEach(amount => {
        amount.addEventListener('click', function() {
            const value = parseInt(this.getAttribute('data-amount'));
            amountInput.value = value;
            amountSlider.value = value;
            currentAmount = value;
            updateAmounts();

            // Активируем выбранную быструю сумму
            quickAmounts.forEach(a => a.classList.remove('active'));
            this.classList.add('active');
        });
    });

    // Методы оплаты
    methodCards.forEach(card => {
        card.addEventListener('click', function() {
            methodCards.forEach(c => c.classList.remove('active'));
            this.classList.add('active');
            currentMethod = this.getAttribute('data-method');

            // Устанавливаем комиссию в зависимости от метода
            switch(currentMethod) {
                case 'card':
                    commissionRate = 0;
                    break;
                case 'yoomoney':
                case 'qiwi':
                    commissionRate = 2.5;
                    break;
                case 'crypto':
                    commissionRate = 1;
                    break;
                case 'mobile':
                    commissionRate = 5;
                    break;
                case 'other':
                    commissionRate = 3;
                    break;
            }

            updateAmounts();
        });
    });

    // Кнопка пополнения
    depositBtn.addEventListener('click', function() {
        if (currentAmount < 50) {
            alert('Минимальная сумма пополнения - 50 ₽');
            return;
        }

        // Имитация пополнения
        this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Обработка...';
        this.disabled = true;

        setTimeout(() => {
            alert(`Успешно! Баланс пополнен на ${currentAmount} ₽`);
            this.innerHTML = '<i class="fas fa-lock"></i> Пополнить баланс';
            this.disabled = false;

            // Обновляем баланс на странице (в реальном приложении - запрос к серверу)
            const balanceValue = document.querySelector('.balance-value');
            const currentBalance = parseInt(balanceValue.textContent.replace(/\s/g, ''));
            balanceValue.textContent = (currentBalance + currentAmount).toLocaleString('ru-RU');

            // Обновляем общую сумму пополнений
            const totalDeposited = document.querySelectorAll('.balance-card-amount')[1];
            const currentTotal = parseInt(totalDeposited.textContent.replace(/\s/g, ''));
            totalDeposited.textContent = (currentTotal + currentAmount).toLocaleString('ru-RU');

            // Сбрасываем форму
            currentAmount = 1000;
            amountInput.value = 1000;
            amountSlider.value = 1000;
            updateAmounts();
            updateQuickAmounts();

        }, 1500);
    });

    // Поддержка
    supportBtn.addEventListener('click', toggleSupport);
    supportIconBtn.addEventListener('click', toggleSupport);
    supportClose.addEventListener('click', function() {
        supportWindow.classList.add('hidden');
    });

    // FAQ
    faqItems.forEach(item => {
        const question = item.querySelector('.faq-question');
        question.addEventListener('click', function() {
            item.classList.toggle('active');
        });
    });

    // Функции
    function updateAmounts() {
        const commission = Math.round(currentAmount * commissionRate / 100);
        const total = currentAmount + commission;

        payAmountElement.textContent = currentAmount.toLocaleString('ru-RU') + ' ₽';
        commissionAmountElement.textContent = commission.toLocaleString('ru-RU') + ' ₽';
        totalAmountElement.textContent = total.toLocaleString('ru-RU') + ' ₽';
    }

    function updateQuickAmounts() {
        quickAmounts.forEach(amount => {
            const amountValue = parseInt(amount.getAttribute('data-amount'));
            if (amountValue === currentAmount) {
                amount.classList.add('active');
            } else {
                amount.classList.remove('active');
            }
        });
    }

    function toggleSupport() {
        supportWindow.classList.toggle('hidden');
    }

    // Обработка нажатия Enter в поле суммы
    amountInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            depositBtn.click();
        }
    });

    // Профиль меню (если нужно)
    const profileBtn = document.querySelector('.profile-btn');
    const profileMenu = document.querySelector('.profile-menu');
    const profileArrow = document.querySelector('.profile-arrow svg');

    if (profileBtn) {
        profileBtn.addEventListener('click', function() {
            profileMenu.classList.toggle('open');
            this.parentElement.classList.toggle('arrow-open');
        });

        // Закрытие меню при клике вне его
        document.addEventListener('click', function(e) {
            if (!e.target.closest('.profile')) {
                profileMenu.classList.remove('open');
                profileBtn.parentElement.classList.remove('arrow-open');
            }
        });
    }

    // Анимация прогресс-бара бонуса
    setTimeout(() => {
        const progressFill = document.querySelector('.progress-fill');
        progressFill.style.width = '0%';

        setTimeout(() => {
            progressFill.style.width = '100%';
        }, 500);
    }, 1000);
});