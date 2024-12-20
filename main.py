import argparse
import asyncio
from pathlib import Path
from tqdm import tqdm  

# Функція читання
async def read_folder(path):
    loop = asyncio.get_event_loop()
    directory = Path(path)

    files = []
    tasks = []

    async def collect_files(dir_path, progress_bar):
        entries = await loop.run_in_executor(None, list, dir_path.iterdir())
        for entry in entries:
            if entry.is_dir():
                # Якщо це папка, рекурсивно викликаємо collect_files
                await collect_files(entry, progress_bar)
            elif entry.is_file():
                # Якщо це файл, додаємо його до списку та оновлюємо прогрес-бар
                files.append(entry)
                progress_bar.update(1)

    # Підраховуємо загальну кількість файлів для прогрес-бару
    total_files = sum(1 for _ in directory.rglob('*') if _.is_file())

    with tqdm(total=total_files, desc="Обробка файлів") as progress_bar:
        await collect_files(directory, progress_bar)

    return files


async def main():
    parser = argparse.ArgumentParser(description="Асинхронне сортування файлів за розширенням.")
    parser.add_argument("source", type=str, help="Шлях до вихідної папки.")
    parser.add_argument("output", type=str, help="Шлях до цільової папки.")

    args = parser.parse_args()

    source_path = Path(args.source)
    output_path = Path(args.output)

    if not source_path.is_dir():
        print(f"Помилка: {source_path} не є папкою.")
        return

    if not output_path.exists():
        output_path.mkdir(parents=True, exist_ok=True)

    try:
        files = await read_folder(source_path)
        print("\nЗнайдені файли:")
        for file in files:
            print(file)
    except Exception as e:
        print(f"Помилка при читанні папки: {e}")

    print(f"\nЦільова папка: {output_path}")


if __name__ == "__main__":
    asyncio.run(main())
