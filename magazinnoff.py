import time
from magazinoff_pkg.collector import run_collection


def main():
    start = time.time()
    print("🚀 Начинаем парсинг Magazinnoff.ru (модульная версия)...")

    try:
        all_data = run_collection()
        finish = time.time()
        print(f"✅ Парсинг завершен. Время работы: {(finish - start) / 60:.2f} минут.")
        return all_data
    except Exception as e:
        print(f"❌ Критическая ошибка при запуске: {e}")
        return []


if __name__ == "__main__":
    main()