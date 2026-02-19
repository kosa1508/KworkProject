// withdraw.js - функционал страницы вывода средств

document.addEventListener('DOMContentLoaded', function() {
    // Элементы управления
    const amountInput = document.getElementById('amountInput');
    const amountSlider = document.getElementById('amountSlider');
    const quickAmounts = document.querySelectorAll('.quick-amount');
    const maxAmountBtn = document.getElementById('maxAmount');
    const methodTabs = document.querySelectorAll('.method-tab');
    const methodForms = document.querySelectorAll('.method-form');
    const withdrawBtn = document.getElementById('withdrawBtn');
    const agreeTerms = document.getElementById('agreeTerms');

    // Элементы для отображения
    const withdrawAmountElement = document.getElementById('withdrawAmount');
    const commissionAmountElement = document.getElementById('commissionAmount');
    const netAmountElement = document.getElementById('netAmount');
    const methodNameElement = document.getElementById('methodName');
    const processingTimeElement = document.getElementById('processingTime');

    // Поддержка
    const supportBtn = document.getElementById('supportBtn');
    const supportIconBtn = document.getElementById('supportIconBtn');
    const supportWindow = document.getElementById('supportWindow');
    const supportClose = document.getElementById('supportClose');

    // Текущие значения
    let currentAmount = 2000;
    let currentMethod = 'card';
    let commissionRate = 1; // 1% комиссия
    const availableBalance = 4120;
    const minAmount = 50;

    // Инициализация
    updateAmounts();
    updateProcessingTime();

    // Связь input и slider
    amountInput.addEventListener('input', function() {
        const value = parseInt(this.value) || 0;
        if (value > availableBalance) {
            this.value = availableBalance;
            amountSlider.value = availableBalance;
            currentAmount = availableBalance;
        } else if (value < minAmount) {
            this.value = minAmount;
            amountSlider.value = minAmount;
            currentAmount = minAmount;
        } else {
            amountSlider.value = value;
            currentAmount = value;
        }
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
            if (this.id === 'maxAmount') {
                currentAmount = availableBalance;
            } else {
                currentAmount = parseInt(this.getAttribute('data-amount'));
            }

            amountInput.value = currentAmount;
            amountSlider.value = currentAmount;
            updateAmounts();

            // Активируем выбранную быструю сумму
            quickAmounts.forEach(a => a.classList.remove('active'));
            this.classList.add('active');
        });
    });

    // Методы вывода
    methodTabs.forEach(tab => {
        tab.addEventListener('click', function() {
            methodTabs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            currentMethod = this.getAttribute('data-method');

            // Показываем соответствующую форму
            methodForms.forEach(form => {
                form.classList.remove('active');
                if (form.id === currentMethod + 'Form') {
                    form.classList.add('active');
                }
            });

            // Обновляем комиссию
            switch(currentMethod) {
                case 'card':
                    commissionRate = 1;
                    break;
                case 'yoomoney':
                    commissionRate = 2;
                    break;
                case 'qiwi':
                    commissionRate = 3;
                    break;
                case 'crypto':
                    commissionRate = 0.5;
                    break;
            }

            updateAmounts();
            updateMethodName();
            updateProcessingTime();
        });
    });

    // Соглашение с условиями
    agreeTerms.addEventListener('change', function() {
        withdrawBtn.disabled = !this.checked;
    });

    // Кнопка вывода
    withdrawBtn.addEventListener('click', function() {
        if (currentAmount < minAmount) {
            alert(`Минимальная сумма вывода - ${minAmount} ₽`);
            return;
        }

        if (currentAmount > availableBalance) {
            alert('Недостаточно средств на балансе');
            return;
        }

        if (!agreeTerms.checked) {
            alert('Необходимо согласиться с условиями вывода');
            return;
        }

        // Валидация формы в зависимости от метода
        if (!validateForm()) {
            return;
        }

        // Имитация запроса на вывод
        this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Обработка...';
        this.disabled = true;

        setTimeout(() => {
            alert(`Запрос на вывод ${currentAmount} ₽ успешно отправлен! Средства поступят в течение указанного времени.`);
            this.innerHTML = '<i class="fas fa-paper-plane"></i> Запросить вывод';
            this.disabled = false;

            // Обновляем баланс на странице
            const balanceValue = document.querySelector('.balance-value');
            const currentBalance = parseInt(balanceValue.textContent.replace(/\s/g, ''));
            balanceValue.textContent = (currentBalance - currentAmount).toLocaleString('ru-RU');

            // Сбрасываем форму
            currentAmount = 2000;
            amountInput.value = 2000;
            amountSlider.value = 2000;
            updateAmounts();
            updateQuickAmounts();

            // Снимаем галочку
            agreeTerms.checked = false;
            withdrawBtn.disabled = true;

        }, 2000);
    });

    // Поддержка
    supportBtn.addEventListener('click', toggleSupport);
    supportIconBtn.addEventListener('click', toggleSupport);
    supportClose.addEventListener('click', function() {
        supportWindow.classList.add('hidden');
    });

    // Профиль меню
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

    // Функции
    function updateAmounts() {
        const commission = Math.round(currentAmount * commissionRate / 100);
        const net = currentAmount - commission;

        withdrawAmountElement.textContent = currentAmount.toLocaleString('ru-RU') + ' ₽';
        commissionAmountElement.textContent = commission.toLocaleString('ru-RU') + ' ₽ (' + commissionRate + '%)';
        netAmountElement.textContent = net.toLocaleString('ru-RU') + ' ₽';
    }

    function updateQuickAmounts() {
        quickAmounts.forEach(amount => {
            if (amount.id === 'maxAmount') return;

            const amountValue = parseInt(amount.getAttribute('data-amount'));
            if (amountValue === currentAmount) {
                amount.classList.add('active');
            } else {
                amount.classList.remove('active');
            }
        });
    }

    function updateMethodName() {
        const methodNames = {
            'card': 'Банковская карта',
            'yoomoney': 'ЮMoney',
            'qiwi': 'QIWI',
            'crypto': 'Криптовалюта'
        };
        methodNameElement.textContent = methodNames[currentMethod];
    }

    function updateProcessingTime() {
        const times = {
            'card': '1-24 часа',
            'yoomoney': '5 минут - 2 часа',
            'qiwi': '5-30 минут',
            'crypto': '10-60 минут'
        };
        processingTimeElement.textContent = times[currentMethod];
    }

    function validateForm() {
        switch(currentMethod) {
            case 'card':
                const cardNumber = document.getElementById('cardNumber').value;
                const cardExpiry = document.getElementById('cardExpiry').value;
                const cardCVC = document.getElementById('cardCVC').value;
                const cardHolder = document.getElementById('cardHolder').value;

                if (!cardNumber || cardNumber.replace(/\s/g, '').length !== 16) {
                    alert('Введите корректный номер карты (16 цифр)');
                    return false;
                }

                if (!cardExpiry || !/^\d{2}\/\d{2}$/.test(cardExpiry)) {
                    alert('Введите срок действия в формате ММ/ГГ');
                    return false;
                }

                if (!cardCVC || cardCVC.length !== 3) {
                    alert('Введите корректный CVC код (3 цифры)');
                    return false;
                }

                if (!cardHolder || cardHolder.length < 3) {
                    alert('Введите имя владельца карты');
                    return false;
                }
                break;

            case 'yoomoney':
                const yoomoneyWallet = document.getElementById('yoomoneyWallet').value;
                if (!yoomoneyWallet || yoomoneyWallet.length < 10) {
                    alert('Введите корректный номер кошелька ЮMoney');
                    return false;
                }
                break;

            case 'qiwi':
                const qiwiPhone = document.getElementById('qiwiPhone').value;
                if (!qiwiPhone || qiwiPhone.replace(/\D/g, '').length < 10) {
                    alert('Введите корректный номер телефона QIWI');
                    return false;
                }
                break;

            case 'crypto':
                const cryptoAddress = document.getElementById('cryptoAddress').value;
                if (!cryptoAddress || cryptoAddress.length < 10) {
                    alert('Введите корректный адрес криптокошелька');
                    return false;
                }
                break;
        }

        return true;
    }

    function toggleSupport() {
        supportWindow.classList.toggle('hidden');
    }

    // Маска для номера карты
    const cardNumberInput = document.getElementById('cardNumber');
    if (cardNumberInput) {
        cardNumberInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            value = value.substring(0, 16);
            let formatted = '';
            for (let i = 0; i < value.length; i++) {
                if (i > 0 && i % 4 === 0) formatted += ' ';
                formatted += value[i];
            }
            e.target.value = formatted;
        });
    }

    // Маска для срока действия карты
    const cardExpiryInput = document.getElementById('cardExpiry');
    if (cardExpiryInput) {
        cardExpiryInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length >= 2) {
                value = value.substring(0, 2) + '/' + value.substring(2, 4);
            }
            e.target.value = value;
        });
    }

    // Маска для CVC
    const cardCVCInput = document.getElementById('cardCVC');
    if (cardCVCInput) {
        cardCVCInput.addEventListener('input', function(e) {
            e.target.value = e.target.value.replace(/\D/g, '').substring(0, 3);
        });
    }

    // Маска для телефона QIWI
    const qiwiPhoneInput = document.getElementById('qiwiPhone');
    if (qiwiPhoneInput) {
        qiwiPhoneInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 0) {
                value = '+7 (' + value.substring(1, 4) + ') ' + value.substring(4, 7) + '-' + value.substring(7, 9) + '-' + value.substring(9, 11);
                value = value.replace(/\-$/, '').replace(/\)\s\-$/, ') ');
            }
            e.target.value = value;
        });
    }
});