from bs4 import BeautifulSoup

def parse_resultado(html: str) -> dict:
    soup = BeautifulSoup(html, "lxml")
    panel = soup.select_one(".panel.panel-primary")

    if not panel:
        return {"error": "No se encontró información"}

    data = {}
    for item in panel.select(".list-group-item"):
        label = item.select_one(".col-sm-5, .col-sm-3")
        value = item.select_one(".col-sm-7, .col-sm-3:nth-of-type(2)")
        if label and value:
            key = label.get_text(strip=True).replace(":", "")
            val = value.get_text(" ", strip=True)
            data[key] = val

    return data
