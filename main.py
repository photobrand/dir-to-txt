import os
import shutil
import json
import sys
import zipfile
import logging
import threading
import time
import tkinter as tk
from tkinter import messagebox, filedialog, ttk, scrolledtext
from datetime import datetime

# Настройка логирования
logging.basicConfig(filename='module.log', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Глобальные переменные для конфигурации
config = {}
extensions_to_process = []
scan_folder = ''
clone_folder = ''
exclude_paths = []
version = '1.1.0'  # Обновленная версия
author = 'Your Name'  # Укажите ваше имя или никнейм

# Функция для загрузки настроек
def load_config():
    global config, extensions_to_process, scan_folder, clone_folder, exclude_paths
    try:
        # Проверяем наличие config.json, если нет, создаем с настройками по умолчанию
        if not os.path.exists('config.json'):
            default_config = {
                "extensions": [".php", ".js", ".py", ".json"],
                "scan_folder": "scan",
                "clone_folder": "clone",
                "exclude": []
            }
            with open('config.json', 'w', encoding='utf-8') as config_file:
                json.dump(default_config, config_file, ensure_ascii=False, indent=4)
            config = default_config
        else:
            with open('config.json', 'r', encoding='utf-8') as config_file:
                config = json.load(config_file)

        extensions_to_process = config.get("extensions", [".php", ".js", ".py", ".json"])
        scan_folder = config.get("scan_folder", "scan")
        clone_folder = config.get("clone_folder", "clone")
        exclude_paths = config.get("exclude", [])

        # Создаем папки scan и clone, если они не существуют
        if not os.path.exists(scan_folder):
            os.makedirs(scan_folder)
        if not os.path.exists(clone_folder):
            os.makedirs(clone_folder)

    except Exception as e:
        logging.error(f"Ошибка при загрузке конфигурации: {e}")
        messagebox.showerror("Ошибка", f"Ошибка при загрузке конфигурации: {e}")
        sys.exit(1)

# Функция для сохранения настроек
def save_config():
    try:
        config['extensions'] = extensions_to_process
        config['scan_folder'] = scan_folder
        config['clone_folder'] = clone_folder
        config['exclude'] = exclude_paths
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

# Проверка на исключенные пути
def is_excluded(path):
    for exclude in exclude_paths:
        if os.path.commonpath([os.path.abspath(path), os.path.abspath(exclude)]) == os.path.abspath(exclude):
            return True
    return False

# Функции обработки файлов и папок
def process_folder(folder_path, output_lines, relative_path=""):
    try:
        for item in sorted(os.listdir(folder_path)):
            item_path = os.path.join(folder_path, item)
            display_path = os.path.join(relative_path, item)

            if is_excluded(item_path):
                logging.info(f"Исключен из обработки: {item_path}")
                continue

            if os.path.isdir(item_path):
                output_lines.append(f"📁 {display_path}/")
                process_folder(item_path, output_lines, display_path)
            else:
                if any(item.endswith(ext) for ext in extensions_to_process):
                    output_lines.append(f"📄 {display_path}")
    except Exception as e:
        logging.error(f"Ошибка при обработке папки '{folder_path}': {e}")

def write_file_contents(folder_path, output_lines, relative_path=""):
    try:
        for item in sorted(os.listdir(folder_path)):
            item_path = os.path.join(folder_path, item)
            display_path = os.path.join(relative_path, item)

            if is_excluded(item_path):
                logging.info(f"Исключен из обработки: {item_path}")
                continue

            if os.path.isdir(item_path):
                write_file_contents(item_path, output_lines, display_path)
            else:
                if any(item.endswith(ext) for ext in extensions_to_process):
                    output_lines.append(f"\n---\n**Файл:** `{display_path}`\n```")
                    try:
                        with open(item_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            output_lines.append(content)
                    except Exception as e:
                        output_lines.append(f"Ошибка чтения файла: {e}")
                        logging.error(f"Ошибка чтения файла '{item_path}': {e}")
                    output_lines.append("```\n")
    except Exception as e:
        logging.error(f"Ошибка при записи содержимого файлов из '{folder_path}': {e}")

# Функция для клонирования папки
def clone_and_rename(folder_path, destination_path, relative_path=""):
    try:
        for item in sorted(os.listdir(folder_path)):
            s = os.path.join(folder_path, item)
            d = os.path.join(destination_path, item)

            if is_excluded(s):
                logging.info(f"Исключен из клонирования: {s}")
                continue

            if os.path.isdir(s):
                os.makedirs(d, exist_ok=True)
                clone_and_rename(s, d, os.path.join(relative_path, item))
            else:
                if any(item.endswith(ext) for ext in extensions_to_process):
                    new_file_name = item + '.txt'
                    d = os.path.join(destination_path, new_file_name)
                    shutil.copy2(s, d)
                else:
                    continue
    except Exception as e:
        logging.error(f"Ошибка при клонировании папки '{folder_path}': {e}")

# Функция для создания ZIP архива
def create_zip(source_folder, zip_name):
    try:
        zip_path = os.path.join(clone_folder, zip_name)
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(source_folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, start=clone_folder)
                    zipf.write(file_path, arcname)
    except Exception as e:
        logging.error(f"Ошибка при создании ZIP архива '{zip_name}': {e}")

# Функция для обновления журнала в GUI
def update_log(text_widget, message):
    text_widget.after(0, lambda: append_text(text_widget, message))

def append_text(text_widget, message):
    text_widget.config(state='normal')
    text_widget.insert(tk.END, message + '\n')
    text_widget.see(tk.END)
    text_widget.config(state='disabled')

# Главная функция обработки
def main_process(log_widget):
    start_time = time.time()
    total_files_processed = 0
    total_size = 0

    try:
        # Загрузка настроек
        load_config()

        # Очищаем папку для клонирования перед началом работы
        clear_folder(clone_folder)
        update_log(log_widget, f"Папка '{clone_folder}' очищена.")
        logging.info(f"Папка '{clone_folder}' очищена.")

        # Проверяем наличие папки для сканирования
        if not os.path.exists(scan_folder):
            logging.error(f"Папка для сканирования '{scan_folder}' не найдена.")
            update_log(log_widget, f"Ошибка: Папка для сканирования '{scan_folder}' не найдена.")
            return

        # Получаем список папок внутри папки scan
        folders = [f for f in os.listdir(scan_folder) if os.path.isdir(os.path.join(scan_folder, f))]

        if not folders:
            update_log(log_widget, f"Информация: В папке '{scan_folder}' нет папок для обработки.")
            return

        for folder in folders:
            folder_path = os.path.join(scan_folder, folder)
            output_file_name = f"{folder}.txt"
            output_file_path = os.path.join(clone_folder, output_file_name)

            update_log(log_widget, f"\nНачало обработки папки: {folder}")
            logging.info(f"Начало обработки папки: {folder}")

            output_lines = []

            # Сначала записываем структуру папки
            output_lines.append(f"# Иерархия файлов и папок для '{folder}':\n")
            process_folder(folder_path, output_lines)

            # Затем записываем содержимое файлов
            output_lines.append("\n# Содержимое файлов:\n")
            write_file_contents(folder_path, output_lines)

            # Записываем все в выходной файл
            with open(output_file_path, 'w', encoding='utf-8') as output_file:
                output_file.write('\n'.join(output_lines))

            update_log(log_widget, f"Иерархия и содержимое файлов сохранены в файл {output_file_path}")
            logging.info(f"Иерархия и содержимое файлов сохранены в файл {output_file_path}")

            # Клонирование папки с изменением расширений файлов
            clone_destination = os.path.join(clone_folder, folder)
            clone_and_rename(folder_path, clone_destination)
            update_log(log_widget, f"Клонированная папка сохранена в '{clone_destination}'")
            logging.info(f"Клонированная папка сохранена в '{clone_destination}'")

            # Создание ZIP архива
            zip_name = f"{folder}.zip"
            create_zip(clone_destination, zip_name)
            update_log(log_widget, f"ZIP архив создан: {os.path.join(clone_folder, zip_name)}")
            logging.info(f"ZIP архив создан: {os.path.join(clone_folder, zip_name)}")

            # Обновляем статистику
            files_processed = sum(len(files) for _, _, files in os.walk(folder_path))
            total_files_processed += files_processed

            folder_size = sum(os.path.getsize(os.path.join(dp, f)) for dp, dn, filenames in os.walk(folder_path) for f in filenames)
            total_size += folder_size

        elapsed_time = time.time() - start_time
        update_log(log_widget, "\nОбработка завершена.")
        logging.info("Обработка завершена.")

        # Отображаем сводку
        summary = f"Обработка завершена за {elapsed_time:.2f} секунд.\n" \
                  f"Всего файлов обработано: {total_files_processed}\n" \
                  f"Общий размер файлов: {total_size / (1024 * 1024):.2f} МБ"

        update_log(log_widget, "\n" + summary)
        logging.info(summary)
        messagebox.showinfo("Готово", summary)
    except Exception as e:
        logging.error(f"Критическая ошибка: {e}")
        update_log(log_widget, f"Критическая ошибка: {e}")
        messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

# Функция запуска GUI
def run_gui():
    load_config()
    root = tk.Tk()
    root.title("Модуль обработки файлов")
    root.geometry("700x750")

    # Применение темы
    style = ttk.Style()
    style.theme_use('clam')

    # Основной фрейм
    main_frame = ttk.Frame(root, padding="10")
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Заголовок и информация о модуле
    title_label = ttk.Label(main_frame, text="Модуль обработки файлов", font=("Helvetica", 16, "bold"))
    title_label.pack(pady=5)

    info_text = f"""Версия: {version}
Автор: {author}

Данный модуль позволяет:
- Сканировать папку '{scan_folder}' на наличие проектов.
- Создавать файл с иерархией и содержимым файлов.
- Клонировать структуру папок с изменением расширений файлов на '.txt'.
- Создавать ZIP-архив для удобной передачи данных.

Для начала работы поместите проект в папку '{scan_folder}' и нажмите 'Начать обработку'."""
    info_label = ttk.Label(main_frame, text=info_text, justify=tk.LEFT)
    info_label.pack(pady=5)

    # Кнопки и элементы управления
    btn_frame = ttk.Frame(main_frame)
    btn_frame.pack(fill=tk.X, pady=5)

    btn_start = ttk.Button(btn_frame, text="Начать обработку")
    btn_start.pack(side=tk.LEFT, padx=5)

    btn_scan = ttk.Button(btn_frame, text="Выбрать папку для сканирования")
    btn_scan.pack(side=tk.LEFT, padx=5)

    btn_clone = ttk.Button(btn_frame, text="Выбрать папку для клонирования")
    btn_clone.pack(side=tk.LEFT, padx=5)

    # Поле для ввода расширений
    ext_label = ttk.Label(main_frame, text="Расширения для обработки (через запятую):")
    ext_label.pack(anchor=tk.W, padx=5)
    ext_entry = ttk.Entry(main_frame)
    ext_entry.pack(fill=tk.X, padx=5, pady=5)
    ext_entry.insert(0, ', '.join(extensions_to_process))

    # Поле для ввода исключений
    exclude_label = ttk.Label(main_frame, text="Исключить файлы или папки (через запятую):")
    exclude_label.pack(anchor=tk.W, padx=5)
    exclude_entry = ttk.Entry(main_frame)
    exclude_entry.pack(fill=tk.X, padx=5, pady=5)
    exclude_entry.insert(0, ', '.join(exclude_paths))

    # Журнал обработки
    log_label = ttk.Label(main_frame, text="Журнал обработки:")
    log_label.pack(anchor=tk.W, padx=5)
    log_text = scrolledtext.ScrolledText(main_frame, height=20, state='disabled')
    log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    # Функции кнопок
    def start_processing():
        # Обновляем список расширений и исключений
        global extensions_to_process, exclude_paths
        extensions = ext_entry.get()
        extensions_to_process = [ext.strip() for ext in extensions.split(',') if ext.strip()]
        excludes = exclude_entry.get()
        exclude_paths = [path.strip() for path in excludes.split(',') if path.strip()]
        save_config()
        # Запускаем обработку в отдельном потоке
        processing_thread = threading.Thread(target=main_process, args=(log_text,))
        processing_thread.start()

    def open_scan_folder():
        global scan_folder
        folder = filedialog.askdirectory()
        if folder:
            scan_folder = folder
            save_config()
            messagebox.showinfo("Успешно", f"Папка для сканирования установлена: {folder}")
            info_label.config(text=info_text.replace(f"'{scan_folder}'", f"'{folder}'"))

    def open_clone_folder():
        global clone_folder
        folder = filedialog.askdirectory()
        if folder:
            clone_folder = folder
            save_config()
            messagebox.showinfo("Успешно", f"Папка для клонирования установлена: {folder}")
            info_label.config(text=info_text.replace(f"'{clone_folder}'", f"'{folder}'"))

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
