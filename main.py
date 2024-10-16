import os
import shutil
import json
import sys
import zipfile
import logging
from tqdm import tqdm  # Прогресс-бар
import tkinter as tk
from tkinter import messagebox, filedialog, ttk, scrolledtext
import threading

# Настройка логирования
logging.basicConfig(filename='module_errors.log', level=logging.ERROR,
                    format='%(asctime)s:%(levelname)s:%(message)s')

# Глобальные переменные для конфигурации
config = {}
extensions_to_process = []
scan_folder = ''
clone_folder = ''

# Функция для загрузки настроек
def load_config():
    global config, extensions_to_process, scan_folder, clone_folder
    try:
        with open('config.json', 'r', encoding='utf-8') as config_file:
            config = json.load(config_file)
        extensions_to_process = config.get("extensions", [".php", ".js", ".py", ".json"])
        scan_folder = config.get("scan_folder", "scan")
        clone_folder = config.get("clone_folder", "clone")
    except FileNotFoundError:
        logging.error("Файл config.json не найден.")
        messagebox.showerror("Ошибка", "Файл config.json не найден.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        logging.error(f"Ошибка декодирования JSON: {e}")
        messagebox.showerror("Ошибка", f"Ошибка в файле config.json: {e}")
        sys.exit(1)

# Функция для сохранения настроек
def save_config():
    try:
        config['extensions'] = extensions_to_process
        config['scan_folder'] = scan_folder
        config['clone_folder'] = clone_folder
        with open('config.json', 'w', encoding='utf-8') as config_file:
            json.dump(config, config_file, ensure_ascii=False, indent=4)
    except Exception as e:
        logging.error(f"Ошибка при сохранении конфигурации: {e}")
        messagebox.showerror("Ошибка", f"Ошибка при сохранении конфигурации: {e}")

# Функция для удаления содержимого папки
def clear_folder(folder_path):
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
    os.makedirs(folder_path)

# Функции обработки файлов и папок (без изменений логики, но с улучшенной обработкой ошибок)
# ...

# Функция для обновления журнала в GUI
def update_log(text_widget, message):
    text_widget.config(state='normal')
    text_widget.insert(tk.END, message + '\n')
    text_widget.see(tk.END)
    text_widget.config(state='disabled')

# Главная функция обработки (модифицированная для работы с GUI)
def main_process(log_widget, progress_bar):
    try:
        # Проверяем обновления (опционально)
        # check_for_updates()
    
        # Загрузка настроек
        load_config()
    
        # Очищаем папку для клонирования перед началом работы
        clear_folder(clone_folder)
        update_log(log_widget, f"Папка '{clone_folder}' очищена.")
    
        # Проверяем наличие папки для сканирования
        if not os.path.exists(scan_folder):
            logging.error(f"Папка для сканирования '{scan_folder}' не найдена.")
            messagebox.showerror("Ошибка", f"Папка для сканирования '{scan_folder}' не найдена.")
            return
    
        # Получаем список папок внутри папки scan
        folders = [f for f in os.listdir(scan_folder) if os.path.isdir(os.path.join(scan_folder, f))]
    
        if not folders:
            messagebox.showinfo("Информация", f"В папке '{scan_folder}' нет папок для обработки.")
            return
    
        for folder in folders:
            folder_path = os.path.join(scan_folder, folder)
            output_file_name = f"{folder}.txt"
            output_file_path = os.path.join(clone_folder, output_file_name)
    
            update_log(log_widget, f"\nНачало обработки папки: {folder}")
    
            # Подсчет общего количества элементов для прогресс-бара
            total_items = count_items(folder_path) * 3  # Умножаем на 3, т.к. три функции обхода
            progress_bar['maximum'] = total_items
            progress_bar['value'] = 0
    
            with open(output_file_path, 'w', encoding='utf-8') as output_file:
                # Создаем экземпляр tqdm для обновления прогресс-бара
                with tqdm(total=total_items, desc="Общий прогресс") as pbar:
                    # Оборачиваем tqdm в функцию, которая обновляет и GUI-прогресс-бар
                    def tqdm_callback():
                        progress_bar['value'] = pbar.n
                        progress_bar.update()
                        log_widget.update_idletasks()
    
                    # Передаем callback в tqdm
                    pbar.monitor_interval = 0.1
                    pbar.set_postfix(refresh=tqdm_callback)
    
                    # Сначала записываем структуру папки
                    process_folder(folder_path, output_file, extensions_to_process, progress_bar=pbar)
                    # Затем записываем содержимое файлов
                    write_file_contents(folder_path, output_file, extensions_to_process, progress_bar=pbar)
    
                update_log(log_widget, f"Иерархия и содержимое файлов сохранены в файл {output_file_path}")
    
                # Клонирование папки с изменением расширений файлов
                clone_destination = os.path.join(clone_folder, folder)
                clone_and_rename(folder_path, clone_destination, extensions_to_process, progress_bar=pbar)
                update_log(log_widget, f"Клонированная папка сохранена в '{clone_destination}'")
    
                # Создание ZIP архива
                zip_name = f"{folder}.zip"
                create_zip(clone_destination, zip_name)
                update_log(log_widget, f"ZIP архив создан: {os.path.join(clone_folder, zip_name)}")
    
        update_log(log_widget, "\nОбработка завершена.")
        messagebox.showinfo("Готово", "Обработка завершена.")
    except Exception as e:
        logging.error(f"Критическая ошибка: {e}")
        messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

# Функция запуска GUI
def run_gui():
    load_config()
    root = tk.Tk()
    root.title("Модуль обработки файлов")
    root.geometry("600x500")
    
    # Применение темы
    style = ttk.Style()
    style.theme_use('clam')
    
    # Основной фрейм
    main_frame = ttk.Frame(root, padding="10")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Кнопки и элементы управления
    btn_frame = ttk.Frame(main_frame)
    btn_frame.pack(fill=tk.X)
    
    btn_start = ttk.Button(btn_frame, text="Начать обработку")
    btn_start.pack(side=tk.LEFT, padx=5, pady=5)
    
    btn_scan = ttk.Button(btn_frame, text="Выбрать папку для сканирования")
    btn_scan.pack(side=tk.LEFT, padx=5, pady=5)
    
    btn_clone = ttk.Button(btn_frame, text="Выбрать папку для клонирования")
    btn_clone.pack(side=tk.LEFT, padx=5, pady=5)
    
    # Поле для ввода расширений
    ext_label = ttk.Label(main_frame, text="Расширения для обработки (через запятую):")
    ext_label.pack(anchor=tk.W, padx=5)
    ext_entry = ttk.Entry(main_frame)
    ext_entry.pack(fill=tk.X, padx=5, pady=5)
    ext_entry.insert(0, ', '.join(extensions_to_process))
    
    # Прогресс-бар
    progress_bar = ttk.Progressbar(main_frame, orient='horizontal', mode='determinate')
    progress_bar.pack(fill=tk.X, padx=5, pady=5)
    
    # Журнал обработки
    log_label = ttk.Label(main_frame, text="Журнал обработки:")
    log_label.pack(anchor=tk.W, padx=5)
    log_text = scrolledtext.ScrolledText(main_frame, height=15, state='disabled')
    log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    # Функции кнопок
    def start_processing():
        # Обновляем список расширений
        global extensions_to_process
        extensions = ext_entry.get()
        extensions_to_process = [ext.strip() for ext in extensions.split(',')]
        save_config()
        # Запускаем обработку в отдельном потоке
        processing_thread = threading.Thread(target=main_process, args=(log_text, progress_bar))
        processing_thread.start()
    
    def open_scan_folder():
        global scan_folder
        folder = filedialog.askdirectory()
        if folder:
            scan_folder = folder
            save_config()
            messagebox.showinfo("Успешно", f"Папка для сканирования установлена: {folder}")
    
    def open_clone_folder():
        global clone_folder
        folder = filedialog.askdirectory()
        if folder:
            clone_folder = folder
            save_config()
            messagebox.showinfo("Успешно", f"Папка для клонирования установлена: {folder}")
    
    # Обработка исключений при закрытии окна
    def on_closing():
        if messagebox.askokcancel("Выход", "Вы действительно хотите выйти?"):
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Привязка функций к кнопкам
    btn_start.config(command=start_processing)
    btn_scan.config(command=open_scan_folder)
    btn_clone.config(command=open_clone_folder)
    
    root.mainloop()

if __name__ == "__main__":
    run_gui()