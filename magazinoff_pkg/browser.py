import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth

# Путь к папке с профилем (куки и сессии)
PROFILE_DIR = os.path.join(os.getcwd(), "magazinnoff_profile")


def init_driver(headless=False):
    """Инициализация Chrome с сохранением профиля и маскировкой"""
    options = webdriver.ChromeOptions()

    # ПУТЬ К КУКАМ
    options.add_argument(f"--user-data-dir={PROFILE_DIR}")

    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")


    if headless:
        options.add_argument("--headless=new")

    driver = webdriver.Chrome(options=options)

    stealth(driver,
            languages=["ru-RU", "ru"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
            )
    return driver


def wait_for_humanity(driver, timeout=30):
    """Ожидание прохождения защиты Cloudflare/AntiBot"""
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: "Just a moment" not in d.title and
                      "Checking your browser" not in d.page_source
        )
        time.sleep(1)
        return True
    except Exception:
        return False


def save_debug_html(driver, name_prefix):
    """Сохранение HTML для анализа"""
    if not os.path.exists("debug"):
        os.makedirs("debug")
    filename = os.path.join("debug", f"debug_{name_prefix}.html")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(driver.page_source)