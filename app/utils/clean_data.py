import re

def remove_pure_number_rows(text: str, max_number: int = 3000) -> str:
    # Match lines like: |  123  |    |    |   |
    pattern = re.compile(rf"^\s*\|\s*([1-9][0-9]{{0,3}})\s*\|\s*(\|\s*){{0,}}$", re.MULTILINE)
    cleaned_text = pattern.sub("", text)
    return cleaned_text.strip()