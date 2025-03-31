from fastapi import FastAPI
from pydantic import BaseModel
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

app = FastAPI()

class TaskRequest(BaseModel):
    app_slug: str

@app.post("/scrapZapier")
def scrape_zapier_integrations(request: TaskRequest):
    url = f"https://zapier.com/apps/{request.app_slug}/integrations"

    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 10)

    try:
        driver.get(url)
        time.sleep(3)

        container = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "css-2tvymq"))
        )

        while True:
            try:
                load_more_btn = container.find_element(By.XPATH, './/button[contains(., "Load more")]')
                ActionChains(driver).move_to_element(load_more_btn).click().perform()
                time.sleep(2)
            except:
                break

        soup = BeautifulSoup(driver.page_source, "html.parser")
        target_div = soup.find("div", class_="css-ywpy44")
        if not target_div:
            return []

        result = []

        all_items = target_div.select("div.css-1ybx9px, div.css-cgake2")

        for div in all_items:
            name = ""
            description = ""
            action_type = ""
            triggertype = ""
            input_fields = []

            name_span = div.select_one("span.app-action__title.css-pgz5n6")
            if name_span:
                name = name_span.get_text(strip=True)

            desc_p = div.find("p", class_="css-1nnqqud")
            if desc_p:
                description = desc_p.get_text(strip=True)

            tooltip_wrapper = div.find("div", class_="_tooltip-wrapper_8x43p_1")
            if tooltip_wrapper:
                type_span = tooltip_wrapper.find("span")
                if type_span:
                    action_type = type_span.get_text(strip=True).lower()

            trigger_span = div.find("span", class_="css-1kefmdn")
            if trigger_span:
                triggertype = trigger_span.get_text(strip=True)

            input_spans = div.select("span.field-label")
            for span in input_spans:
                # Get only direct text (exclude child elements like <div>)
                text_nodes = [t for t in span.contents if isinstance(t, str)]
                text = ''.join(text_nodes).strip()
                if text:
                    input_fields.append(text)

            result.append({
                "name": name,
                "description": description,
                "type": action_type,
                "triggertype": triggertype,
                "inputFields": input_fields
            })

        return result

    finally:
        driver.quit()
