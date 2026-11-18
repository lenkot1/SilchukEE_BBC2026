import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

#===== Палитра =====

BG_AERO = "#DFF5EC"
BG_GLASS = "#FFFFFF"
AERO_BORDER = "#8AD8B5"
SBER_LIME = "#52D669"
SBER_MID = "#1FA84D"
SBER_DEEP = "#0C6B32"
SKY_ACCENT = "#29B6F6"
TEXT_DARK = "#0A3622"
TEXT_MUTED = "#4B7A63"

#===== Данные пользователя ====

USER_DATA = {
    "phone": "+7 800 555-35-35",
    "password": "123",
    "name": "Елена Сильчук",
    "cards": {
        "Социальная •••• 4521": {"balance": 84500.50, "type": "Дебетовая", "blocked": False},
        "Сберкнижка / Вклад •• 8830": {"balance": 150000.00, "type": "Сберегательный", "blocked": False}
    },
    "history": [
        "Зачисление стипендии: +12 500.00 ₽",
        "Оплата МТС (терминал): -300.00 ₽"
    ]
}

#===== Главное окно ====

root = tk.Tk()
root.title("Сбербанк Онлайн")
root.geometry("410x700")
root.resizable(False, False)
root.configure(bg=BG_AERO)

main_container = tk.Frame(root, bg=BG_AERO)
main_container.pack(fill="both", expand=True)

def clear_screen():
    for widget in main_container.winfo_children():
        widget.destroy()



def draw_old_sber_logo(parent, size=84):
    canvas = tk.Canvas(parent, width=size, height=size, bg=BG_AERO, highlightthickness=0)

    canvas.create_oval(2, 10, 16, 24, fill="#B2EBF2", outline="#4DD0E1")
    canvas.create_oval(size-18, size-20, size-4, size-6, fill="#C8E6C9", outline="#66BB6A")

    pad = 8
    canvas.create_oval(pad, pad, size-pad, size-pad, fill=SBER_MID, outline=SBER_DEEP, width=2)

    canvas.create_oval(pad + 10, pad + 4, size - pad - 10, size // 2, fill=SBER_LIME, outline="")

    cx = size//2
    for offest in (-8, 0, 8):
        y = cx + offest
        canvas.create_line(cx - 16, y - 4, cx, y + 6, fill="white", width=3, capstyle="round")
        canvas.create_line(cx, y + 6, cx + 18, y - 9, fill="white", width=3, capstyle="round")
    return canvas

# ===== Живые операции (Пополнение, Перевод, Связь, Платежи) =====
def open_operation_modal(mode, preset_title=None):
    modal = tk.Toplevel(root)
    titles = {
        "topup": "Пополнение счёта",
        "transfer": "Перевод клиенту Сбербанка",
        "mobile": "Оплата мобильной связи",
        "payment": preset_title or "Оплата услуг"
    }
    modal.title(titles.get(mode, "Операция"))
    modal.geometry("350x350")
    modal.resizable(False, False)
    modal.configure(bg=BG_AERO)
    modal.grab_set()

    box = tk.Frame(modal, bg=BG_GLASS, padx=18, pady=18,
                   highlightbackground=AERO_BORDER, highlightthickness=2, relief="ridge", bd=2)

    box.pack(fill="both", expand=True, padx=14, pady=14)

    tk.Label(box, text=f"💧 {titles.get(mode)}", font=("Tahoma", 11, "bold"),
             bg=BG_GLASS, fg=SBER_DEEP).pack(anchor="w", pady=(0, 12))


    # Выбор карты
    tk.Label(box, text="Выберите карту / счёт:", font=("Tahoma", 9, "bold"),
             bg=BG_GLASS, fg=TEXT_DARK).pack(anchor="w")

    card_combo = ttk.Combobox(box, values=list(USER_DATA["cards"].keys()), state="readonly", font=("Tahoma", 10))
    card_combo.current(0)
    card_combo.pack(fill="x", pady=(3, 10))

    # Поле получателя или номера телефона (для всех операций, кроме пополнения)
    target_entry = None
    if mode != "topup":
        label_txt = "Номер телефона:" if mode in ("transfer", "mobile") else "Лицевой счёт / Реквизиты:"
        default_val = "+7 900 555-11-22" if mode in ("transfer", "mobile") else "40817810099910004321"
        tk.Label(box, text=label_txt, font=("Tahoma", 9, "bold"),
                 bg=BG_GLASS, fg=TEXT_DARK).pack(anchor="w")

        target_entry = tk.Entry(box, font=("Tahoma", 10), bg="#F2FBF7", relief="sunken", bd=2)
        target_entry.insert(0, default_val)
        target_entry.pack(fill="x", ipady=4, pady=(3, 10))

    # Поле ввода суммы
    tk.Label(box, text="Сумма (₽):", font=("Tahoma", 9, "bold"),
             bg=BG_GLASS, fg=TEXT_DARK).pack(anchor="w")

    amount_entry = tk.Entry(box, font=("Tahoma", 11, "bold"), bg="#F2FBF7", relief="sunken", bd=2)
    amount_entry.pack(fill="x", ipady=5, pady=(3, 15))

    def execute():
        selected_card = card_combo.get()
        try:
            amount = float(amount_entry.get().strip().replace(",", "."))
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка ввода", "Введите корректную сумму больше 0!", parent=modal)
            return

        now_str = datetime.now().strftime("%d.%m %H:%M")

        if mode == "topup":
            USER_DATA["cards"][selected_card]["balance"] += amount
            USER_DATA["history"].insert(0, f"{now_str} | Пополнение: +{amount:,.2f} ₽")
            messagebox.showinfo("Чек", f"Счёт пополнен на {amount:,.2f} ₽!", parent=modal)
        else:
            target = target_entry.get().strip()
            if not target:
                messagebox.showwarning("Внимание", "Заполните поле получателя!", parent=modal)
                return

            if amount > USER_DATA["cards"][selected_card]["balance"]:
                messagebox.showerror("Отказ", "Недостаточно средств на выбранной карте!", parent=modal)
                return

            if not messagebox.askyesno("Подтверждение", f"Списать {amount:,.2f} ₽?", parent=modal):
                return

            USER_DATA["cards"][selected_card]["balance"] -= amount
            op_name = "Перевод" if mode == "transfer" else ("Связь" if mode == "mobile" else titles["payment"])
            USER_DATA["history"].insert(0, f"{now_str} | {op_name} ({target}): -{amount:,.2f} ₽")
            messagebox.showinfo("Исполнено", f"Операция на {amount:,.2f} ₽ выполнена!", parent=modal)

        modal.destroy()
        show_main_screen()

    btn_row = tk.Frame(box, bg=BG_GLASS)
    btn_row.pack(fill="x", side="bottom")
    tk.Button(btn_row, text="Отмена", font=("Tahoma", 10), bg="#E0E0E0", relief="raised", bd=2,
              width=10, command=modal.destroy).pack(side="left", ipady=4)

    tk.Button(btn_row, text="Выполнить ✔", font=("Tahoma", 10, "bold"), bg=SBER_MID, fg="white",
              activebackground=SBER_LIME, relief="raised", bd=2, width=14, command=execute).pack(side="right", ipady=4)


# ===== Экран профиля =====
def show_profile_screen():
    clear_screen()

    # Шапка с кнопкой возврата назад
    header = tk.Frame(main_container, bg=SBER_DEEP, padx=15, pady=10, relief="raised", bd=2)
    header.pack(fill="x")

    tk.Button(header, text="← Назад", font=("Tahoma", 9, "bold"), bg="#E1F5FE", fg="#0277BD",
              relief="raised", bd=2, cursor="hand2", command=show_main_screen).pack(side="left", ipadx=6, ipady=2)

    tk.Label(header, text=" Профиль клиента", font=("Tahoma", 11, "bold"),
             bg=SBER_DEEP, fg="white").pack(side="left")


    # Карточка с данными пользователя
    info_card = tk.Frame(main_container, bg=BG_GLASS, padx=18, pady=18,
                         highlightbackground=AERO_BORDER, highlightthickness=2, relief="ridge", bd=2)

    info_card.pack(fill="x", padx=16, pady=(16, 12))

    tk.Label(info_card, text=f"👤 {USER_DATA['name']}", font=("Tahoma", 13, "bold"),
             bg=BG_GLASS, fg=SBER_DEEP).pack(anchor="w")

    tk.Label(info_card, text=f"Телефон: {USER_DATA['phone']}", font=("Tahoma", 10),
             bg=BG_GLASS, fg=TEXT_MUTED).pack(anchor="w", pady=(4, 0))


    # Кнопки разделов
    sections = [
        ("📋 Личные данные", f"ФИО: {USER_DATA['name']}\nТелефон: {USER_DATA['phone']}\nСтатус: Клиент Сбербанка"),
        ("🔒 Безопасность", "Вход по паролю: Включён\nСМС-подтверждение операций: Активно"),
        ("🔔 Уведомления", "Push-уведомления об операциях: Включены"),
        ("ℹ️ О приложении", "Сбербанк Онлайн (Учебный прототип)\nРазработано на Python (Tkinter)")
    ]

    for title, text in sections:
        tk.Button(main_container, text=title, font=("Tahoma", 10, "bold"), anchor="w",
                  bg=BG_GLASS, fg=TEXT_DARK, activebackground="#E8F5E9",
                  relief="raised", bd=2, padx=14, cursor="hand2",
                  command=lambda t=title, m=text: messagebox.showinfo(t, m)).pack(fill="x", padx=16, pady=4, ipady=6)

    # Кнопка выхода из аккаунта
    tk.Button(main_container, text="Выйти из профиля ⏻", font=("Tahoma", 10, "bold"),
              bg="#FFEBEE", fg="#C62828", relief="raised", bd=2, cursor="hand2",
              command=show_login_screen).pack(fill="x", padx=16, pady=(18, 0), ipady=6)


# ===== Главный экран =====
def show_main_screen():
    clear_screen()

    # 1. Верхняя зелёная шапка
    header = tk.Frame(main_container, bg=SBER_DEEP, padx=15, pady=10, relief="raised", bd=2)
    header.pack(fill="x")

    tk.Button(header, text=f"👤 {USER_DATA['name']}", font=("Tahoma", 10, "bold"),
              bg=SBER_MID, fg="white", activebackground=SBER_LIME,
              relief="raised", bd=2, cursor="hand2", command=show_profile_screen).pack(side="left", ipadx=6, ipady=2)

    tk.Button(header, text="Выход ⏻", font=("Tahoma", 8, "bold"), bg="#E1F5FE", fg="#0277BD",
        relief="raised", bd=2, cursor="hand2", command=show_login_screen).pack(side="right", ipadx=6, ipady=2)

    # 2. Стеклянная карточка общего баланса
    total_balance = sum(c["balance"] for c in USER_DATA["cards"].values())
    bal_card = tk.Frame(main_container, bg=BG_GLASS, padx=18, pady=15,
        highlightbackground=SKY_ACCENT, highlightthickness=2, relief="ridge", bd=2)
    bal_card.pack(fill="x", padx=16, pady=(14, 10))

    tk.Label(bal_card, text="💧 Доступные средства:", font=("Tahoma", 9, "bold"),
        bg=BG_GLASS, fg=TEXT_MUTED).pack(anchor="w")
    tk.Label(bal_card, text=f"{total_balance:,.2f} ₽".replace(",", " "), font=("Trebuchet MS", 22, "bold"),
        bg=BG_GLASS, fg=SBER_DEEP).pack(anchor="w", pady=(2, 12))

    # Кнопки Пополнить и Перевести
    actions_frame = tk.Frame(bal_card, bg=BG_GLASS)
    actions_frame.pack(fill="x")

    tk.Button(actions_frame, text="➕ Пополнить", font=("Tahoma", 10, "bold"),
              bg=SBER_LIME, fg=TEXT_DARK, activebackground=SBER_MID, relief="raised", bd=3,
              cursor="hand2", command=lambda: open_operation_modal("topup")).pack(side="left", expand=True, fill="x", padx=(0, 6), ipady=5)

    tk.Button(actions_frame, text="💸 Перевести", font=("Tahoma", 10, "bold"),
              bg=SBER_MID, fg="white", activebackground=SBER_LIME, relief="raised", bd=3,
              cursor="hand2", command=lambda: open_operation_modal("transfer")).pack(side="right", expand=True, fill="x", padx=(6, 0), ipady=5)


    # Панель быстрых разделов
    quick_grid = tk.Frame(main_container, bg=BG_AERO)
    quick_grid.pack(fill="x", padx=16, pady=(2, 8))

    quick_items = [
        ("🧾", "Платежи", lambda: open_operation_modal("payment", "Оплата ЖКХ и услуг")),
        ("📱", "Мобильная\nсвязь", lambda: open_operation_modal("mobile")),
        ("🔄", "СБП\nперевод", lambda: open_operation_modal("transfer")),
        ("📈", "Инвестиции", lambda: messagebox.showinfo("СберИнвестиции", "Ваш портфель: 42 300 ₽ (+8.4% годовых)"))
    ]

    for idx, (icon, label_text, action) in enumerate(quick_items):
        quick_grid.columnconfigure(idx, weight=1)
        item_box = tk.Frame(quick_grid, bg=BG_AERO)
        item_box.grid(row=0, column=idx, padx=3)

        tk.Button(item_box, text=icon, font=("Segoe UI Emoji", 14),
                  bg=BG_GLASS, fg=SBER_DEEP, activebackground="#E8F5E9",
                  relief="raised", bd=2, width=4, cursor="hand2", command=action).pack(ipady=3)

        tk.Label(item_box, text=label_text, font=("Tahoma", 8, "bold"),
                 bg=BG_AERO, fg=TEXT_DARK, justify="center").pack(pady=(3, 0))


    # 3. Блок «Мои карты и вклады»
    tk.Label(main_container, text="Мои карты и сберкнижки:", font=("Tahoma", 10, "bold"),
             bg=BG_AERO, fg=SBER_DEEP).pack(anchor="w", padx=18, pady=(6, 4))

    for card_name, info in USER_DATA["cards"].items():
        c_frame = tk.Frame(main_container, bg=BG_GLASS, padx=14, pady=10,
                           highlightbackground=AERO_BORDER, highlightthickness=1, relief="raised", bd=2)
        c_frame.pack(fill="x", padx=16, pady=4)

        top_row = tk.Frame(c_frame, bg=BG_GLASS)
        top_row.pack(fill="x")
        tk.Label(top_row, text=f"💳 {card_name}", font=("Tahoma", 10, "bold"),
             bg=BG_GLASS, fg=TEXT_DARK).pack(side="left")
        tk.Label(top_row, text=info["type"], font=("Tahoma", 8),
             bg="#E8F5E9", fg=SBER_DEEP, padx=6).pack(side="right")

        bal_str = f"{info['balance']:,.2f} ₽".replace(",", " ")
        tk.Label(c_frame, text=bal_str, font=("Tahoma", 13, "bold"),
             bg=BG_GLASS, fg=SBER_MID).pack(anchor="w", pady=(4, 0))

    # 4. Живая история операций
    tk.Label(main_container, text="Последние операции:", font=("Tahoma", 10, "bold"),
             bg=BG_AERO, fg=SBER_DEEP).pack(anchor="w", padx=18, pady=(12, 4))

    hist_frame = tk.Frame(main_container, bg="#F2FBF7", padx=12, pady=10,
                          highlightbackground=AERO_BORDER, highlightthickness=1, relief="sunken", bd=2)
    hist_frame.pack(fill="both", expand=True, padx=16, pady=(0, 16))

    for item in USER_DATA["history"][:6]:
        color = SBER_MID if ": +" in item else "#C62828"
        tk.Label(hist_frame, text=item, font=("Tahoma", 9), bg="#F2FBF7", fg=color, anchor="w").pack(fill="x", pady=2)


def show_login_screen():
    clear_screen()

    logo = draw_old_sber_logo(main_container, size=90)
    logo.pack(pady=(35, 8))

    title_frame = tk.Frame(main_container, bg=BG_AERO)
    title_frame.pack()
    tk.Label(title_frame, text="СБЕРБАНК", font=("Trebuchet MS", 20, "bold"),
             bg=BG_AERO, fg=SBER_DEEP).pack(side="left")
    tk.Label(title_frame, text=" Онлайн", font=("Trebuchet MS", 20, "italic"),
             bg=BG_AERO, fg=SBER_MID).pack(side="left")

    tk.Label(main_container, text="Всегда рядом", font=("Tahoma", 9),
             bg=BG_AERO, fg=TEXT_MUTED).pack(pady=(2, 20))

    login_card = tk.Frame(main_container, bg=BG_GLASS, padx=22,
                          highlightbackground=AERO_BORDER, highlightthickness=2, relief="ridge", bd=2)
    login_card.pack(fill="x", padx=25)



    tk.Label(login_card, text="Идентификатор или телефон:", font=("Tahoma", 9, "bold"),
             bg=BG_GLASS, fg=TEXT_DARK).pack(anchor="w")
    phone_entry = tk.Entry(login_card, font=("Tahoma", 11), bg="#F2FBF7", fg=TEXT_DARK,
                           relief="sunken", bd=2)
    phone_entry.insert(0, "+7 800 555-35-35")
    phone_entry.pack(fill="x", ipady=6, pady=(4, 14))



    tk.Label(login_card, text="Постоянный пароль:", font=("Tahoma", 9, "bold"),
             bg=BG_GLASS, fg=TEXT_DARK).pack(anchor="w")
    pass_entry = tk.Entry(login_card, font=("Tahoma", 11), bg="#F2FBF7", fg=TEXT_DARK,
                          relief="sunken", bd=2, show="●")
    pass_entry.pack(fill="x", ipady=6, pady=(4, 10))

    remember_var = tk.BooleanVar(value=True)
    tk.Checkbutton(login_card, text="Запомнить идентификатор", variable=remember_var,
                   bg=BG_GLASS, fg=TEXT_DARK, activebackground=BG_GLASS, font=("Tahoma", 9)).pack(anchor="w", pady=(0, 14))

    def try_login():
        phone = phone_entry.get().strip()
        password = pass_entry.get().strip()

        if not phone or not password:
            messagebox.showwarning("Сбербанк Онлайн", "Введите идентификатор и пароль!")
            return

        if phone == USER_DATA["phone"] and password == USER_DATA["password"]:
            show_main_screen()
        else:
            messagebox.showerror("Ошибка доступа", "Неверный пароль! Подсказка: 123")

    btn_login = tk.Button(login_card, text="Войти в систему ➔", font=("Tahoma", 11, "bold"),
                          bg=SBER_MID, fg="white", activebackground=SBER_LIME, activeforeground="white",
                          relief="raised", bd=3, cursor="hand2", command=try_login)
    btn_login.pack(fill="x", ipady=7)


    hint_frame = tk.Frame(main_container, bg="#E1F5FE", padx=14, pady=10,
                          highlightbackground=SKY_ACCENT, highlightthickness=1)
    hint_frame.pack(fill="x", padx=25, pady=22)
    tk.Label(hint_frame, text="💧 Демо-доступ для проверки:", font=("Tahoma", 9, "bold"),
             bg="#E1F5FE", fg="#0277BD").pack(anchor="w")
    tk.Label(hint_frame, text=f"Логин: {USER_DATA['phone']} | Пароль: {USER_DATA['password']}",
             font=("Tahoma", 9), bg="#E1F5FE", fg=TEXT_DARK).pack(anchor="w", pady=(2, 0))

show_login_screen()

if __name__ == "__main__":
    root.mainloop()