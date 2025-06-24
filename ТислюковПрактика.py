import tkinter as tk
from tkinter import ttk, messagebox
import random

class InsuranceType:

    def __init__(self, name, monthly_payment, duration_months, max_compensation, franchise, base_demand):
        self.name = name
        self.monthly_payment = monthly_payment
        self.duration_months = duration_months
        self.max_compensation = max_compensation
        self.franchise = franchise
        self.base_demand = base_demand
        self.active_policies = 0
        self.cases_this_month = 0
        self.payouts_this_month = 0.0
        self.income_this_month = 0.0
        self.sold_this_month = 0

    def get_total_cost(self):
        return self.monthly_payment * self.duration_months

    def calculate_demand(self):
        ratio = self.get_total_cost() / self.max_compensation
        demand_multiplier = max(0.1, 2.0 - ratio * 3)
        return int(self.base_demand * demand_multiplier)


class InsuranceCompany:

    def __init__(self, initial_capital=30000, tax_rate=0.09):
        self.capital = initial_capital
        self.initial_capital = initial_capital
        self.tax_rate = tax_rate
        self.month = 0
        self.is_bankrupt = False
        self.insurance_types = {
            "housing": InsuranceType("Жилище", 90, 12, 20000, 500, 100),
            "auto": InsuranceType("Автомобиль", 120, 12, 15000, 300, 80),
            "health": InsuranceType("Здоровье", 150, 12, 25000, 200, 60)
        }

        self.history = []

    def pay_tax(self):
        tax_amount = self.capital * self.tax_rate
        self.capital -= tax_amount
        return tax_amount

    def sell_policies(self):
        total_income = 0
        sales_info = {}

        for key, insurance in self.insurance_types.items():
            current_demand = insurance.calculate_demand()
            actual_sales = max(0, current_demand + random.randint(-10, 10))

            income = actual_sales * insurance.monthly_payment
            total_income += income
            insurance.active_policies += actual_sales
            insurance.income_this_month = income
            insurance.sold_this_month = actual_sales
            sales_info[key] = actual_sales

        self.capital += total_income
        return total_income, sales_info

    def process_insurance_cases(self):
        total_payouts = 0
        cases_info = {}

        for key, insurance in self.insurance_types.items():
            if insurance.active_policies > 0:
                max_cases = min(25, insurance.active_policies // 4)
                cases_count = random.randint(1, max(1, max_cases))
                insurance.cases_this_month = cases_count
                monthly_payout = 0
                for _ in range(cases_count):
                    damage_coefficient = random.uniform(0.1, 1.0)
                    payout = insurance.max_compensation * damage_coefficient
                    if payout > insurance.franchise:
                        monthly_payout += payout

                insurance.payouts_this_month = monthly_payout
                total_payouts += monthly_payout
                cases_info[key] = {'cases': cases_count, 'payout': monthly_payout}

        if self.capital < total_payouts:
            self.is_bankrupt = True
            return total_payouts, cases_info

        self.capital -= total_payouts
        return total_payouts, cases_info

    def simulate_month(self):
        if self.is_bankrupt:
            return None

        self.month += 1
        capital_before = self.capital

        tax = self.pay_tax()

        income, sales = self.sell_policies()

        payouts, cases = self.process_insurance_cases()

        insurance_details = {}
        for key, insurance in self.insurance_types.items():
            insurance_details[key] = {
                'name': insurance.name,
                'income': insurance.income_this_month,
                'sold': insurance.sold_this_month,
                'cases': insurance.cases_this_month,
                'payouts': insurance.payouts_this_month,
                'active_policies': insurance.active_policies
            }

        month_data = {
            'month': self.month,
            'capital_before': capital_before,
            'capital_after': self.capital,
            'capital_change': self.capital - capital_before,
            'tax': tax,
            'total_income': income,
            'total_payouts': payouts,
            'insurance_details': insurance_details,
            'bankrupt': self.is_bankrupt
        }

        self.history.append(month_data)
        return month_data

    def set_initial_capital(self, new_capital):
        if self.month == 0:
            self.initial_capital = new_capital
            self.capital = new_capital
            return True
        return False


class InsuranceSimulationApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Модель управления страховой компанией")
        self.root.geometry("1200x800")

        self.company = InsuranceCompany()
        self.max_months = 24
        self.running = False

        self.create_widgets()
        self.update_display()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        info_frame = ttk.LabelFrame(main_frame, text="Состояние компании", padding="10")
        info_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        self.info_label = ttk.Label(info_frame, text="", font=("Arial", 12))
        self.info_label.grid(row=0, column=0, sticky=tk.W)
        settings_frame = ttk.LabelFrame(main_frame, text="Настройки", padding="10")
        settings_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Label(settings_frame, text="Начальный капитал:").grid(row=0, column=0, sticky=tk.W)
        self.capital_var = tk.DoubleVar(value=self.company.initial_capital)
        capital_entry = ttk.Entry(settings_frame, textvariable=self.capital_var, width=15)
        capital_entry.grid(row=0, column=1, padx=5)

        apply_capital_btn = ttk.Button(settings_frame, text="Применить", command=self.apply_capital)
        apply_capital_btn.grid(row=0, column=2, padx=5)
        ttk.Label(settings_frame, text="Налоговая ставка (%):").grid(row=1, column=0, sticky=tk.W)
        self.tax_var = tk.DoubleVar(value=self.company.tax_rate * 100)
        tax_entry = ttk.Entry(settings_frame, textvariable=self.tax_var, width=15)
        tax_entry.grid(row=1, column=1, padx=5)

        apply_tax_btn = ttk.Button(settings_frame, text="Применить", command=self.apply_tax)
        apply_tax_btn.grid(row=1, column=2, padx=5)

        insurance_frame = ttk.LabelFrame(main_frame, text="Управление страховками", padding="10")
        insurance_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))

        self.create_insurance_controls(insurance_frame)
        stats_frame = ttk.LabelFrame(main_frame, text="Подробная статистика", padding="10")
        stats_frame.grid(row=1, column=1, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))

        self.stats_text = tk.Text(stats_frame, width=60, height=30, wrap=tk.WORD, font=("Courier", 9))
        stats_scroll = ttk.Scrollbar(stats_frame, orient=tk.VERTICAL, command=self.stats_text.yview)
        self.stats_text.configure(yscrollcommand=stats_scroll.set)
        self.stats_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        stats_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))

        control_frame = ttk.Frame(main_frame, padding="10")
        control_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E))

        self.start_btn = ttk.Button(control_frame, text="Запустить симуляцию", command=self.start_simulation)
        self.start_btn.grid(row=0, column=0, padx=5)

        self.step_btn = ttk.Button(control_frame, text="Следующий месяц", command=self.next_month)
        self.step_btn.grid(row=0, column=1, padx=5)

        self.stop_btn = ttk.Button(control_frame, text="Остановить", command=self.stop_simulation, state=tk.DISABLED)
        self.stop_btn.grid(row=0, column=2, padx=5)

        self.reset_btn = ttk.Button(control_frame, text="Сброс", command=self.reset_simulation)
        self.reset_btn.grid(row=0, column=3, padx=5)

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=2)
        main_frame.rowconfigure(2, weight=1)
        stats_frame.columnconfigure(0, weight=1)
        stats_frame.rowconfigure(0, weight=1)

    def apply_capital(self):
        new_capital = self.capital_var.get()
        if self.company.set_initial_capital(new_capital):
            self.update_display()
            messagebox.showinfo("Успех", f"Начальный капитал установлен: {new_capital:,.0f} у.е.")
        else:
            messagebox.showwarning("Ошибка", "Начальный капитал можно изменить только до начала симуляции!")

    def apply_tax(self):
        new_tax_rate = self.tax_var.get() / 100
        self.company.tax_rate = new_tax_rate
        messagebox.showinfo("Успех", f"Налоговая ставка установлена: {new_tax_rate * 100:.1f}%")

    def create_insurance_controls(self, parent):
        self.insurance_vars = {}

        row = 0
        for key, insurance in self.company.insurance_types.items():

            title_label = ttk.Label(parent, text=f"=== {insurance.name} ===", font=("Arial", 11, "bold"))
            title_label.grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))
            row += 1


            vars_dict = {
                'payment': tk.DoubleVar(value=insurance.monthly_payment),
                'duration': tk.IntVar(value=insurance.duration_months),
                'compensation': tk.DoubleVar(value=insurance.max_compensation),
                'franchise': tk.DoubleVar(value=insurance.franchise),
                'demand': tk.IntVar(value=insurance.base_demand)
            }
            self.insurance_vars[key] = vars_dict

            fields = [
                ("Месячный взнос:", 'payment'),
                ("Срок (мес.):", 'duration'),
                ("Макс. возмещение:", 'compensation'),
                ("Франшиза:", 'franchise'),
                ("Базовый спрос:", 'demand')
            ]

            for label_text, var_key in fields:
                ttk.Label(parent, text=label_text).grid(row=row, column=0, sticky=tk.W, padx=(20, 5))
                ttk.Entry(parent, textvariable=vars_dict[var_key], width=12).grid(row=row, column=1, sticky=tk.W)
                row += 1

            apply_btn = ttk.Button(parent, text="Применить",
                                   command=lambda k=key: self.apply_changes(k))
            apply_btn.grid(row=row, column=0, columnspan=2, pady=5)
            row += 1

    def apply_changes(self, insurance_key):
        insurance = self.company.insurance_types[insurance_key]
        vars_dict = self.insurance_vars[insurance_key]

        insurance.monthly_payment = vars_dict['payment'].get()
        insurance.duration_months = vars_dict['duration'].get()
        insurance.max_compensation = vars_dict['compensation'].get()
        insurance.franchise = vars_dict['franchise'].get()
        insurance.base_demand = vars_dict['demand'].get()

        self.update_display()
        messagebox.showinfo("Успех", f"Параметры страховки '{insurance.name}' обновлены!")

    def update_display(self):
        status = "БАНКРОТ" if self.company.is_bankrupt else "Активна"
        info_text = f"Месяц: {self.company.month}/{self.max_months} | Капитал: {self.company.capital:,.0f} у.е. | Статус: {status}"
        self.info_label.config(text=info_text)

        self.stats_text.delete(1.0, tk.END)

        stats = f"{'=' * 60}\n"
        stats += f"           ТЕКУЩЕЕ СОСТОЯНИЕ КОМПАНИИ\n"
        stats += f"{'=' * 60}\n"
        stats += f"Начальный капитал: {self.company.initial_capital:>15,.0f} у.е.\n"
        stats += f"Текущий капитал:   {self.company.capital:>15,.0f} у.е.\n"
        stats += f"Изменение:         {self.company.capital - self.company.initial_capital:>15,.0f} у.е.\n"
        stats += f"Месяц:             {self.company.month:>15}\n"
        stats += f"Налоговая ставка:  {self.company.tax_rate * 100:>14.1f}%\n\n"

        stats += f"{'=' * 60}\n"
        stats += f"                   СТРАХОВКИ\n"
        stats += f"{'=' * 60}\n"
        for key, insurance in self.company.insurance_types.items():
            demand = insurance.calculate_demand()
            stats += f"{insurance.name}:\n"
            stats += f"  Месячный взнос:     {insurance.monthly_payment:>10.0f} у.е.\n"
            stats += f"  Срок договора:      {insurance.duration_months:>10} мес.\n"
            stats += f"  Общая стоимость:    {insurance.get_total_cost():>10.0f} у.е.\n"
            stats += f"  Макс. возмещение:   {insurance.max_compensation:>10,.0f} у.е.\n"
            stats += f"  Франшиза:           {insurance.franchise:>10,.0f} у.е.\n"
            stats += f"  Базовый спрос:      {insurance.base_demand:>10} чел.\n"
            stats += f"  Текущий спрос:      {demand:>10} чел.\n"
            stats += f"  Активные полисы:    {insurance.active_policies:>10}\n"
            stats += f"  Случаев в месяце:   {insurance.cases_this_month:>10}\n"
            stats += f"  Выплат в месяце:    {insurance.payouts_this_month:>10,.0f} у.е.\n"
            stats += f"  Доходов в месяце:   {insurance.income_this_month:>10,.0f} у.е.\n\n"

        if self.company.history:
            stats += f"{'=' * 60}\n"
            stats += f"       ДЕТАЛЬНАЯ ИСТОРИЯ (последние 5 месяцев)\n"
            stats += f"{'=' * 60}\n"
            for data in self.company.history[-5:]:
                stats += f"\n--- МЕСЯЦ {data['month']} ---\n"
                stats += f"Капитал до операций:  {data['capital_before']:>12,.0f} у.е.\n"
                stats += f"Капитал после:        {data['capital_after']:>12,.0f} у.е.\n"
                stats += f"Изменение капитала:   {data['capital_change']:>12,.0f} у.е.\n\n"

                stats += f"РАСХОДЫ:\n"
                stats += f"  Налог государству:  {data['tax']:>12,.0f} у.е.\n"
                total_payouts = 0
                for key, details in data['insurance_details'].items():
                    if details['payouts'] > 0:
                        stats += f"  {details['name']} (выплаты): {details['payouts']:>8,.0f} у.е.\n"
                        total_payouts += details['payouts']
                stats += f"  Итого выплат:       {total_payouts:>12,.0f} у.е.\n"
                stats += f"  ВСЕГО РАСХОДОВ:     {data['tax'] + total_payouts:>12,.0f} у.е.\n\n"

                stats += f"ДОХОДЫ:\n"
                total_income = 0
                for key, details in data['insurance_details'].items():
                    if details['income'] > 0:
                        stats += f"  {details['name']} ({details['sold']} полисов): {details['income']:>8,.0f} у.е.\n"
                        total_income += details['income']
                stats += f"  ВСЕГО ДОХОДОВ:      {total_income:>12,.0f} у.е.\n\n"

                stats += f"РЕЗУЛЬТАТ МЕСЯЦА:     {data['capital_change']:>12,.0f} у.е.\n"
                stats += f"{'─' * 40}\n"

        self.stats_text.insert(tk.END, stats)

    def next_month(self):
        if self.company.is_bankrupt:
            messagebox.showwarning("Банкротство", "Компания обанкротилась! Игра окончена.")
            return

        if self.company.month >= self.max_months:
            messagebox.showinfo("Завершение", "Достигнут максимальный срок симуляции!")
            return

        data = self.company.simulate_month()
        if data:
            if data['bankrupt']:
                messagebox.showerror("Банкротство",
                                     f"Компания обанкротилась в месяце {data['month']}!\n"
                                     f"Недостаточно средств для выплат: {data['total_payouts']:,.0f} у.е.")
            self.update_display()

    def start_simulation(self):
        self.running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.run_auto_simulation()

    def stop_simulation(self):
        self.running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)

    def run_auto_simulation(self):
        if not self.running or self.company.is_bankrupt or self.company.month >= self.max_months:
            self.stop_simulation()
            return

        self.next_month()
        self.root.after(1000, self.run_auto_simulation)

    def reset_simulation(self):
        self.running = False
        initial_capital = self.capital_var.get()
        tax_rate = self.tax_var.get() / 100

        self.company = InsuranceCompany(initial_capital, tax_rate)

        for key, insurance in self.company.insurance_types.items():
            if key in self.insurance_vars:
                vars_dict = self.insurance_vars[key]
                vars_dict['payment'].set(insurance.monthly_payment)
                vars_dict['duration'].set(insurance.duration_months)
                vars_dict['compensation'].set(insurance.max_compensation)
                vars_dict['franchise'].set(insurance.franchise)
                vars_dict['demand'].set(insurance.base_demand)

        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.update_display()


if __name__ == "__main__":
    root = tk.Tk()
    app = InsuranceSimulationApp(root)
    root.mainloop()
