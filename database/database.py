import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

class DatabaseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("База данных сотрудников")
        self.root.geometry("800x600")

        # 1. Подключение к базе данных
        self.conn = sqlite3.connect('employees.db')
        self.cursor = self.conn.cursor()
        
        # Создание таблицы, если её нет
        self.create_table()

        # 2. Создание интерфейса (GUI)
        self.create_widgets()
        
        # Загрузка данных при старте
        self.fetch_data()

    def create_table(self):
        """Создает таблицу в БД"""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                surname TEXT NOT NULL,
                age INTEGER,
                position TEXT
            )
        """)
        self.conn.commit()

    def create_widgets(self):
        """Создает поля ввода и кнопки"""
        
        # --- Верхняя панель (Ввод данных) ---
        input_frame = tk.LabelFrame(self.root, text="Данные сотрудника", padx=10, pady=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        # Поля ввода
        tk.Label(input_frame, text="Имя:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.entry_name = tk.Entry(input_frame)
        self.entry_name.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(input_frame, text="Фамилия:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.entry_surname = tk.Entry(input_frame)
        self.entry_surname.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(input_frame, text="Возраст:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.entry_age = tk.Entry(input_frame)
        self.entry_age.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(input_frame, text="Должность:").grid(row=1, column=2, padx=5, pady=5, sticky="e")
        self.entry_position = tk.Entry(input_frame)
        self.entry_position.grid(row=1, column=3, padx=5, pady=5)

        # Кнопки управления
        btn_frame = tk.Frame(input_frame)
        btn_frame.grid(row=2, column=0, columnspan=4, pady=10)

        tk.Button(btn_frame, text="Добавить", command=self.add_record, bg="#4CAF50", fg="white").pack(side="left", padx=5)
        tk.Button(btn_frame, text="Обновить", command=self.update_record, bg="#2196F3", fg="white").pack(side="left", padx=5)
        tk.Button(btn_frame, text="Удалить", command=self.delete_record, bg="#f44336", fg="white").pack(side="left", padx=5)
        tk.Button(btn_frame, text="Очистить поля", command=self.clear_entries).pack(side="left", padx=5)

        # --- Средняя панель (Поиск) ---
        search_frame = tk.Frame(self.root)
        search_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(search_frame, text="Поиск по фамилии:").pack(side="left")
        self.entry_search = tk.Entry(search_frame)
        self.entry_search.pack(side="left", padx=5)
        tk.Button(search_frame, text="Найти", command=self.search_record).pack(side="left")
        tk.Button(search_frame, text="Показать все", command=self.fetch_data).pack(side="left", padx=5)

        # --- Нижняя панель (Таблица) ---
        table_frame = tk.Frame(self.root)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Настройка таблицы (Treeview)
        columns = ("ID", "Имя", "Фамилия", "Возраст", "Должность")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        # Заголовки
        self.tree.heading("ID", text="ID")
        self.tree.heading("Имя", text="Имя")
        self.tree.heading("Фамилия", text="Фамилия")
        self.tree.heading("Возраст", text="Возраст")
        self.tree.heading("Должность", text="Должность")

        # Настройка ширины колонок
        self.tree.column("ID", width=50)
        self.tree.column("Имя", width=100)
        self.tree.column("Фамилия", width=100)
        self.tree.column("Возраст", width=50)
        self.tree.column("Должность", width=150)

        # Скроллбар
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Обработка клика по строке (для редактирования)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    # --- Логика работы с БД ---

    def add_record(self):
        """Добавляет новую запись"""
        if self.validate_input():
            try:
                self.cursor.execute("""
                    INSERT INTO employees (name, surname, age, position) 
                    VALUES (?, ?, ?, ?)
                """, (
                    self.entry_name.get(),
                    self.entry_surname.get(),
                    self.entry_age.get(),
                    self.entry_position.get()
                ))
                self.conn.commit()
                self.fetch_data()
                self.clear_entries()
                messagebox.showinfo("Успех", "Сотрудник добавлен!")
            except sqlite3.Error as e:
                messagebox.showerror("Ошибка", f"Ошибка БД: {e}")

    def update_record(self):
        """Обновляет выбранную запись"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите запись в таблице для обновления!")
            return

        item_id = self.tree.item(selected[0])['values'][0] # Получаем ID
        
        try:
            self.cursor.execute("""
                UPDATE employees 
                SET name=?, surname=?, age=?, position=? 
                WHERE id=?
            """, (
                self.entry_name.get(),
                self.entry_surname.get(),
                self.entry_age.get(),
                self.entry_position.get(),
                item_id
            ))
            self.conn.commit()
            self.fetch_data()
            messagebox.showinfo("Успех", "Данные обновлены!")
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Ошибка БД: {e}")

    def delete_record(self):
        """Удаляет запись"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите запись для удаления!")
            return

        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить эту запись?"):
            item_id = self.tree.item(selected[0])['values'][0]
            try:
                self.cursor.execute("DELETE FROM employees WHERE id=?", (item_id,))
                self.conn.commit()
                self.fetch_data()
                self.clear_entries()
            except sqlite3.Error as e:
                messagebox.showerror("Ошибка", f"Ошибка БД: {e}")

    def search_record(self):
        """Ищет по фамилии"""
        search_term = self.entry_search.get()
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        self.cursor.execute("SELECT * FROM employees WHERE surname LIKE ?", ('%' + search_term + '%',))
        rows = self.cursor.fetchall()
        
        for row in rows:
            self.tree.insert("", "end", values=row)

    def fetch_data(self):
        """Загружает все данные в таблицу"""
        for row in self.tree.get_children():
            self.tree.delete(row) # Очистка таблицы
        
        self.cursor.execute("SELECT * FROM employees")
        rows = self.cursor.fetchall()
        
        for row in rows:
            self.tree.insert("", "end", values=row)

    def on_select(self, event):
        """Заполняет поля ввода при клике на строку таблицы"""
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])['values']
            self.clear_entries()
            self.entry_name.insert(0, item[1])
            self.entry_surname.insert(0, item[2])
            self.entry_age.insert(0, item[3])
            self.entry_position.insert(0, item[4])

    def clear_entries(self):
        """Очищает поля ввода"""
        self.entry_name.delete(0, tk.END)
        self.entry_surname.delete(0, tk.END)
        self.entry_age.delete(0, tk.END)
        self.entry_position.delete(0, tk.END)

    def validate_input(self):
        """Простая проверка, что поля не пустые"""
        if not self.entry_name.get() or not self.entry_surname.get():
            messagebox.showerror("Ошибка", "Имя и Фамилия обязательны!")
            return False
        return True

    def __del__(self):
        """Закрытие соединения при выходе"""
        if self.conn:
            self.conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = DatabaseApp(root)
    root.mainloop()