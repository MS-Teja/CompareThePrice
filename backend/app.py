from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time
import logging

app = Flask(__name__)
CORS(app)  # Enable CORS for your app
log_messages = []

# Configure logging
logging.basicConfig(level=logging.INFO)

@app.route('/log', methods=['GET'])
def log():
    def generate():
        while True:
            if log_messages:
                message = log_messages.pop(0)
                yield f"data: {message}\n\n"
            time.sleep(1)
    return Response(generate(), mimetype="text/event-stream")

def get_flipkart_price(query):
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(options=chrome_options)
        driver.get('https://www.flipkart.com')
        log_messages.append("Navigated to Flipkart")

        # Close the login popup if it appears
        try:
            close_button = driver.find_element(By.XPATH, '/html/body/div[2]/div/div/button')
            close_button.click()
            log_messages.append("Closed login popup on Flipkart")
        except NoSuchElementException:
            log_messages.append("Login popup not found on Flipkart")

        search_box = driver.find_element(By.CLASS_NAME, 'Pke_EE')
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)
        log_messages.append(f"Searched for '{query}' on Flipkart")

        products = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, 'KzDlHZ'))
        )
        for product in products:
            if query.lower() in product.text.lower():
                product.click()
                log_messages.append(f"Clicked on product matching '{query}' on Flipkart")
                break
        else:
            log_messages.append(f"No product matching '{query}' found on Flipkart")
            driver.quit()
            return "Not found"

        # Wait for product page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'cPHDOP'))
        )

        outer_html = driver.find_element(By.CLASS_NAME, 'cPHDOP').get_attribute('outerHTML')

        # Use a broader XPath to locate the price element
        try:
            price_elements = WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "hl05eU")]//div[contains(@class, "Nx9bqj")]'))
            )
            for element in price_elements:
                if '₹' in element.text:
                    price = element.text.replace('₹', '').strip()
                    log_messages.append(f"Found price '{price}' on Flipkart")
                    driver.quit()
                    return price

            log_messages.append("Price element not found despite broader search")
            driver.quit()
            return "Error"
        except TimeoutException:
            log_messages.append("Timeout while waiting for price element on Flipkart")
            driver.quit()
            return "Error"
        except Exception as e:
            log_messages.append(f"Exception while fetching price on Flipkart: {e}")
            driver.quit()
            return "Error"

    except Exception as e:
        log_messages.append(f"Error fetching Flipkart price: {e}")
        return "Error"

def get_amazon_price(query):
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(options=chrome_options)
        driver.get('https://www.amazon.in')
        log_messages.append("Navigated to Amazon")

        search_box = driver.find_element(By.ID, 'twotabsearchtextbox')
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)
        log_messages.append(f"Searched for '{query}' on Amazon")

        time.sleep(5)

        products = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, 'a-size-medium.a-color-base.a-text-normal'))
        )

        for product in products:
            if query.lower() in product.text.lower():
                product.click()
                log_messages.append(f"Clicked on product matching '{query}' on Amazon")
                break
        else:
            log_messages.append(f"No product matching '{query}' found on Amazon")
            driver.quit()
            return "Not found"

        time.sleep(5)

        price = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'a-price-whole'))
        ).text

        log_messages.append(f"Found price '{price}' on Amazon")
        driver.quit()
        return price
    except Exception as e:
        log_messages.append(f"Error fetching Amazon price: {e}")
        return "Error"

@app.route('/compare', methods=['GET'])
def compare():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'Query parameter is required'}), 400

    flipkart_price = get_flipkart_price(query)
    amazon_price = get_amazon_price(query)

    return jsonify({
        'flipkart_price': flipkart_price,
        'amazon_price': amazon_price
    })

if __name__ == '__main__':
    app.run(debug=True)

