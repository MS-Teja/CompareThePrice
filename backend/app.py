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
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}}) # Enable CORS for your app
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
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(options=chrome_options)
        driver.get('https://www.flipkart.com')
        log_messages.append("Navigated to Flipkart")
        logging.info("Navigated to Flipkart")

        # Close the login popup if it appears
        try:
            close_button = driver.find_element(By.XPATH, '//button[@class="_2KpZ6l _2doB4z"]')
            close_button.click()
            log_messages.append("Closed login popup on Flipkart")
            logging.info("Closed login popup on Flipkart")
        except NoSuchElementException:
            log_messages.append("Login popup not found on Flipkart")
            logging.info("Login popup not found on Flipkart")

        search_box = driver.find_element(By.NAME, 'q')
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)
        log_messages.append(f"Searched for '{query}' on Flipkart")
        logging.info(f"Searched for '{query}' on Flipkart")

        # Locate the product name elements
        products = WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "KzDlHZ")]'))
        )
        log_messages.append(f"Located {len(products)} products on Flipkart")
        logging.info(f"Located {len(products)} products on Flipkart")

        for product in products:
            log_messages.append(f"Product found: {product.text}")
            logging.info(f"Product found: {product.text}")
            if query.lower() in product.text.lower():
                product_url = product.find_element(By.XPATH, './ancestor::a').get_attribute('href')
                if product_url:
                    log_messages.append(f"Found product URL: {product_url}")
                    logging.info(f"Found product URL: {product_url}")
                    product.click()
                    log_messages.append(f"Clicked on product matching '{query}' on Flipkart")
                    logging.info(f"Clicked on product matching '{query}' on Flipkart")
                    break
            else:
                log_messages.append(f"No product matching '{query}' found on Flipkart")
                logging.info(f"No product matching '{query}' found on Flipkart")
                driver.quit()
                return {"price": "Not found", "url": ""}

        # Wait for the product page to load and then locate the price element
        # WebDriverWait(driver, 10).until(
        #     EC.presence_of_element_located((By.XPATH, '//span[@class="B_NuCI"]'))
        # )

        try:
            # Updated XPath based on provided HTML structure
            price_element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div.Nx9bqj.CxhGGd'))
            )
            price = price_element.text.replace('₹', '').strip()
            log_messages.append(f"Found price '{price}' on Flipkart")
            logging.info(f"Found price '{price}' on Flipkart")
            driver.quit()
            return {"price": price, "url": product_url}
        except TimeoutException:
            log_messages.append("Timeout while waiting for price element on Flipkart")
            logging.info("Timeout while waiting for price element on Flipkart")
            driver.quit()
            return {"price": "Error", "url": ""}
        except Exception as e:
            log_messages.append(f"Exception while fetching price on Flipkart: {e}")
            logging.error(f"Exception while fetching price on Flipkart: {e}")
            driver.quit()
            return {"price": "Error", "url": ""}

    except Exception as e:
        log_messages.append(f"Error fetching Flipkart price: {e}")
        logging.error(f"Error fetching Flipkart price: {e}")
        return {"price": "Error", "url": ""}



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

        # Use a more specific XPath to locate product elements
        products = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, '//div[@data-component-type="s-search-result"]//h2/a'))
        )

        for product in products:
            if query.lower() in product.text.lower():
                product_url = product.get_attribute('href')
                if product_url:
                    log_messages.append(f"Found product URL: {product_url}")
                    product.click()
                    log_messages.append(f"Clicked on product matching '{query}' on Amazon")
                    break
        else:
            log_messages.append(f"No product matching '{query}' found on Amazon")
            driver.quit()
            return {"price": "Not found", "url": ""}

        time.sleep(5)

        price = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//span[@class="a-price-whole"]'))
        ).text

        log_messages.append(f"Found price '{price}' on Amazon")
        driver.quit()
        return {"price": price, "url": product_url}
    except Exception as e:
        log_messages.append(f"Error fetching Amazon price: {e}")
        return {"price": "Error", "url": ""}

@app.route('/compare', methods=['GET'])
def compare():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'Query parameter is required'}), 400

    flipkart_result = get_flipkart_price(query)
    amazon_result = get_amazon_price(query)

    return jsonify({
        'flipkart_price': flipkart_result["price"] if flipkart_result["price"] != "Not found" else "Product not available",
        'flipkart_url': flipkart_result["url"],
        'amazon_price': amazon_result["price"] if amazon_result["price"] != "Not found" else "Product not available",
        'amazon_url': amazon_result["url"]
    })

if __name__ == '__main__':
    app.run(debug=True)

