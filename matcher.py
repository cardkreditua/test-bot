import json
import difflib

# Загрузка базы категорий и сервисов
with open("services_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

def find_category(product_name):
    product_name = product_name.lower()
    matches = []

    for category, values in data.items():
        for keyword in values.get("keywords", []):
            ratio = difflib.SequenceMatcher(None, product_name, keyword.lower()).ratio()
            if ratio > 0.6:  # Порог для "похожести"
                matches.append((category, ratio))

    if matches:
        best_match = sorted(matches, key=lambda x: -x[1])[0]
        return best_match[0]
    return None

def get_services_for_product(product_name):
    category = find_category(product_name)
    if not category:
        return "На жаль, я не можу визначити категорію товару. Зверніться до менеджера SUPPORT.UA."

    services = data[category]["services"]
    response_lines = [f"Категорія: {category}\nДоступні сервіси:"]
    for service in services:
        response_lines.append(f"- {service['name']}: {service['desc']}")
    return "\n".join(response_lines)

