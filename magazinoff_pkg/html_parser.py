import re
from bs4 import BeautifulSoup

BASE_URL = "https://www.magazinnoff.ru"


def transliterate_city(city_name):
    """Транслитерация для URL (Нижний Новгород -> nizhniy-novgorod)"""
    symbols = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
        'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
        'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch',
        'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
        ' ': '-', '-': '-'
    }
    result = ''.join(symbols.get(c, c) for c in city_name.lower())
    return re.sub(r'-+', '-', result).strip('-')


def parse_stores(html, target_names=None):
    """Извлекает список магазинов со страницы города"""
    soup = BeautifulSoup(html, "lxml")
    found_stores = {}

    links = soup.find_all("a", href=True)
    for a in links:
        href = a.get("href", "")
        # Ищем ссылки вида /magazin/{slug}
        if href.startswith("/magazin/"):
            parts = href.split("/")
            if len(parts) >= 3:
                store_slug = parts[2]
                if store_slug in ["search", "map"]: continue  # Игнор служебных

                name_tag = a.find("h3")
                store_real_name = name_tag.text.split(" в ")[0].strip() if name_tag else store_slug.capitalize()

                if not target_names:
                    found_stores[store_slug] = store_real_name
                else:
                    for target in target_names:
                        if target.lower() in store_real_name.lower():
                            found_stores[store_slug] = store_real_name
                            break
    return found_stores


def parse_search_results(html, store_name):
    """Парсит список товаров из поиска"""
    soup = BeautifulSoup(html, "lxml")
    items = []

    if "Ничего не найдено" in soup.text:
        return []

    for s in soup.find_all("div", class_="strip"):
        try:
            t_tag = s.find("div", class_="item_title")
            name = t_tag.find("h3").text.strip() if t_tag and t_tag.find("h3") else "Unknown"

            price = None
            p_span = s.find("span", style=lambda x: x and "16px" in x)
            if not p_span:
                p_text = s.find(string=re.compile(r"\d+[\.,]\d{2}"))
                if p_text: p_span = p_text.parent

            if p_span:
                clean_price = re.sub(r"[^\d.,]", "", p_span.text).replace(",", ".")
                if clean_price: price = float(clean_price)

            l_tag = s.find("a", class_="strip_info")
            link = BASE_URL + l_tag.get("href") if l_tag else None

            img_tag = s.find("img")
            img = None
            if img_tag:
                img = img_tag.get("data-src") or img_tag.get("src")
                if img and not img.startswith("http"): img = BASE_URL + img

            items.append({
                "name": name, "price": price, "store": store_name,
                "link": link, "img": img
            })
        except:
            continue
    return items


def parse_product_details(html, name_fallback):
    """Парсит детальную страницу товара"""
    soup = BeautifulSoup(html, "lxml")
    specs = {}

    container = soup.find("div", attrs={"itemprop": "description"})
    if container:
        cols = container.find_all("div", class_="col-6")
        for i in range(0, len(cols) - 1, 2):
            k = cols[i].get_text(strip=True).lower().rstrip(":")
            v = cols[i + 1].get_text(strip=True)
            specs[k] = v

    brand = specs.get("бренд") or specs.get("производитель") or specs.get("торговая марка")
    weight = specs.get("вес") or specs.get("масса") or specs.get("масса нетто")
    volume = specs.get("объем") or specs.get("объём") or specs.get("емкость")

    exact_price = None
    price_tag = soup.find(attrs={"itemprop": "price"})
    if price_tag and price_tag.has_attr('content'):
        try:
            exact_price = float(price_tag['content'])
        except:
            pass

    # Regex подстраховка
    if not weight and not volume:
        finds = re.findall(r"(\d+(?:[.,]\d+)?\s*(?:г|кг|мл|л|шт))", name_fallback.lower())
        if finds:
            ext = finds[-1]
            if any(x in ext for x in ["мл", "л"]):
                volume = ext
            else:
                weight = ext

    return brand, weight, volume, exact_price