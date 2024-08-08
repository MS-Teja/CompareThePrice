# backend/app.py
from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time
import logging

app = Flask(__name__)
CORS(app)  # Enable CORS for your app
logging.basicConfig(level=logging.INFO)

def get_flipkart_price(query):
    try:
        driver = webdriver.Chrome()
        driver.get('https://www.flipkart.com')
        logging.info("Navigated to Flipkart")

        # Close the login popup if it appears
        try:
            close_button = driver.find_element(By.XPATH, '/html/body/div[2]/div/div/button')
            close_button.click()
            logging.info("Closed login popup on Flipkart")
        except NoSuchElementException:
            logging.info("Login popup not found on Flipkart")

        search_box = driver.find_element(By.CLASS_NAME, 'Pke_EE')
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)
        logging.info(f"Searched for '{query}' on Flipkart")

        time.sleep(5)

        products = driver.find_elements(By.CLASS_NAME, 'KzDlHZ')
        for product in products:
            if query.lower() in product.text.lower():
                product.click()
                logging.info(f"Clicked on product matching '{query}' on Flipkart")
                break
        else:
            logging.error(f"No product matching '{query}' found on Flipkart")
            driver.quit()
            return "Not found"

        # Wait for product page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'cPHDOP'))
        )

        # Log the outer HTML to debug the structure
        # logging.info("Product page loaded, fetching outer HTML for debugging")
        outer_html = driver.find_element(By.CLASS_NAME, 'cPHDOP').get_attribute('outerHTML')
        # logging.info(f"Outer HTML of the product section: {outer_html}")

        # Use a broader XPath to locate the price element
        try:
            price_elements = WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "hl05eU")]//div[contains(@class, "Nx9bqj")]'))
            )
            for element in price_elements:
                if '₹' in element.text:
                    price = element.text.replace('₹', '').strip()
                    logging.info(f"Found price '{price}' on Flipkart")
                    driver.quit()
                    return price

            logging.error("Price element not found despite broader search")
            driver.quit()
            return "Error"
        except TimeoutException:
            logging.error("Timeout while waiting for price element on Flipkart")
            driver.quit()
            return "Error"
        except Exception as e:
            logging.error(f"Exception while fetching price on Flipkart: {e}")
            driver.quit()
            return "Error"

    except Exception as e:
        logging.error(f"Error fetching Flipkart price: {e}")
        return "Error"



def get_amazon_price(query):
    try:
        driver = webdriver.Chrome()
        driver.get('https://www.amazon.in')
        logging.info("Navigated to Amazon")

        search_box = driver.find_element(By.ID, 'twotabsearchtextbox')
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)
        logging.info(f"Searched for '{query}' on Amazon")

        time.sleep(5)

        products = driver.find_elements(By.CLASS_NAME, 'a-size-medium.a-color-base.a-text-normal')
        for product in products:
            if query.lower() in product.text.lower():
                product.click()
                logging.info(f"Clicked on product matching '{query}' on Amazon")
                break
        else:
            logging.error(f"No product matching '{query}' found on Amazon")
            driver.quit()
            return "Not found"

        time.sleep(5)

        price = driver.find_element(By.CLASS_NAME, 'a-price-whole').text
        logging.info(f"Found price '{price}' on Amazon")
        driver.quit()
        return price
    except Exception as e:
        logging.error(f"Error fetching Amazon price: {e}")
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