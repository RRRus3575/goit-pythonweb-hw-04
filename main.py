import argparse
import asyncio
from pathlib import Path
from tqdm import tqdm
import shutil
import logging

# Налаштування логування
logging.basicConfig(
    filename="log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

# Функція читання
async def read_folder(src_path, dest_path):
    loop = asyncio.get_event_loop()
    directory = Path(src_path)

    async def collect_files(dir_path, progress_bar):
        entries = await loop.run_in_executor(None, list, dir_path.iterdir())
        tasks = []
        for entry in entries:
            if entry.is_dir():
                # Якщо це папка, рекурсивний виклик collect_files
                tasks.append(collect_files(entry, progress_bar))
            elif entry.is_file():
                tasks.append(copy_file(entry, dest_path, progress_bar))

        await asyncio.gather(*tasks)

    # Підрахунок загальної кількості файлів для прогрес-бару
    total_files = sum(1 for _ in directory.rglob('*') if _.is_file())

    with tqdm(total=total_files, desc="Обробка файлів") as progress_bar:
        await collect_files(directory, progress_bar)


# Функція копіювання
async def copy_file(src_file, dest_folder, progress_bar):
    loop = asyncio.get_event_loop()
    src_path = Path(src_file)
    dest_path = Path(dest_folder)

    dest_path.mkdir(parents=True, exist_ok=True)

    # Визначення розширення файлу або "no_extension", якщо його немає
    extension = src_path.suffix.lstrip('.')
    if not extension:
        extension = "no_extension"

    extension_folder = dest_path / extension
    extension_folder.mkdir(parents=True, exist_ok=True)

    # Формування шляху для цільового файлу
    dest_file_path = extension_folder / src_path.name

    # Копіюємо файл з обробкою помилок
    try:
        await loop.run_in_executor(None, shutil.copy, src_file, dest_file_path)
        logging.info(f"Файл успішно скопійовано: {src_file} -> {dest_file_path}")
    except Exception as e:
        logging.error(f"Помилка копіювання файлу {src_file}: {e}")

    # Оновлення прогрес-бара після копіювання файлу
    progress_bar.update(1)


# Основна функція
async def main():
    parser = argparse.ArgumentParser(description="Асинхронне сортування файлів за розширенням.")
    parser.add_argument("source", type=str, help="Шлях до вихідної папки.")
    parser.add_argument("output", type=str, help="Шлях до цільової папки.")

    args = parser.parse_args()

    source_path = Path(args.source)
    output_path = Path(args.output)

    if not source_path.is_dir():
        logging.error(f"Помилка: {source_path} не є папкою.")
        return

    if not output_path.exists():
        output_path.mkdir(parents=True, exist_ok=True)

    try:
        await read_folder(source_path, output_path)
        logging.info("\nКопіювання завершено")
    except Exception as e:
        logging.error(f"Помилка при читанні папки: {e}")


if __name__ == "__main__":
    asyncio.run(main())
