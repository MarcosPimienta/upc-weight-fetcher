import re


def convert_to_grams(weight, unit):
    unit = unit.lower()
    if unit in ["kg", "kilograms"]:
        return weight * 1000
    elif unit in ["g", "grams"]:
        return weight
    elif unit in ["lb", "lbs", "pounds"]:
        return weight * 453.592
    elif unit in ["oz", "ounces"]:
        return weight * 28.3495
    else:
        return None


def truncate_title(title):
    clean_title = re.sub(r"^\d+\s*[a-zA-Z]*\s*", "", title).strip()
    delimiters = [":", "-"]
    truncated_titles = [clean_title]
    for delimiter in delimiters:
        if delimiter in clean_title:
            parts = clean_title.split(delimiter)
            for i in range(1, len(parts)):
                truncated_titles.append(delimiter.join(parts[:i]).strip())
    return truncated_titles
