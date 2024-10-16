# Инструкция по использованию модуля

## Описание

Данный модуль предназначен для:

- Чтения содержимого файлов с определенными расширениями внутри заданной папки.
- Создания текстового файла с иерархией папок и файлов, включая содержимое каждого файла.
- Клонирования структуры папок и файлов с изменением расширений файлов на `.txt`.

## Требования

- Python 3.11 или выше.
- Установленные зависимости из `requirements.txt`.

## Установка

1. Склонируйте репозиторий или скачайте файлы `main.py`, `config.json`, `README.md` и `requirements.txt`.

2. Установите зависимости:

   ```bash
   pip install -r requirements.txt
   
   
   
   
Создайте папку scan в той же директории, что и main.py (если ее еще нет).

Поместите в папку scan папки с проектами или файлами, которые вы хотите обработать.

При необходимости измените настройки в файле config.json (например, список расширений файлов).

Запустите модуль:

python main.py

После выполнения программы:

В текущей директории появятся текстовые файлы с названиями обработанных папок и расширением .txt, содержащие иерархию и содержимое файлов.
В папке clone появятся клонированные папки с файлами, у которых к названию добавлено расширение .txt.
Пример
Если в папке scan находится папка project, после запуска модуля вы получите:

Файл project.txt с иерархией и содержимым файлов из папки project.
В папке clone/project будет скопирована структура папки project, а файлы будут иметь расширение .txt (например, module.php станет module.php.txt).
Контактная информация
Если у вас возникли вопросы или предложения, пожалуйста, свяжитесь с автором модуля.


Дополнительные пояснения и рекомендации
Кодировка файлов: В коде мы используем encoding='utf-8' при открытии файлов. Если ваши файлы имеют другую кодировку, возможно, вам потребуется изменить этот параметр.

Обработка ошибок: В функции process_folder добавлена обработка исключений при чтении файлов. Если файл не удастся прочитать, программа запишет сообщение об ошибке в выходной файл и продолжит работу.

Интерфейс консоли: Программа выводит информативные сообщения в консоль о ходе выполнения, включая информацию о текущей обрабатываемой папке и файлах.

Минимизация файлов: Мы используем минимальное количество файлов для удобства обслуживания: основной скрипт, файл настроек, инструкцию и файл зависимостей.


Пример использования
Подготовка:

Поместите вашу папку с проектом (например, my_project) внутрь папки scan.
Запуск модуля:

python main.py

Результат:

В корневой директории появится файл my_project.txt с иерархией и содержимым файлов из папки my_project.
В папке clone/my_project будет скопирована структура папки my_project, а все файлы будут иметь расширение .txt.


## Изменения

- **Фильтрация файлов при клонировании**: Теперь в клонированную папку копируются только файлы с расширениями, указанными в настройках (`extensions`).

- **Вывод структуры и содержимого**: В папке `scan` создается файл с названием обрабатываемой папки и расширением `.txt`, который содержит:
  - Структуру папки (только файлы с поддерживаемыми расширениями).
  - Содержимое каждого файла с указанием его пути.

## Примечания

- **Формат вывода**: Структура папки и содержимое файлов разделены для удобства чтения.
- **Пути к файлам**: Относительные пути указываются с использованием обратного слеша `\` для соответствия вашему примеру.



# Инструкция по использованию модуля

## Описание

Данный модуль предназначен для:

- Чтения содержимого файлов с определенными расширениями внутри заданной папки.
- Создания текстового файла с иерархией папок и файлов, включая содержимое каждого файла.
- Клонирования структуры папок и файлов с изменением расширений файлов на `.txt`.
- Создания ZIP-архива с содержимым клонированной папки.

## Требования

- Python 3.11 или выше.

## Установка

1. Склонируйте репозиторий или скачайте файлы `main.py`, `config.json`, `README.md`.

2. Установите зависимости (если они появятся в будущем):

   ```bash
   pip install -r requirements.txt
