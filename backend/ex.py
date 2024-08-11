# Using BeautifulSoup to Scrape Data from Flipkart and Amazon
# from flask import Flask, request, jsonify
# from bs4 import BeautifulSoup
# import requests
# import logging
# import time
# import random

# # Configure Flask app
# app = Flask(__name__)

# # Configure logging
# logging.basicConfig(level=logging.DEBUG)

# # User-Agent to mimic a real browser request
# HEADERS = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
# }

# def get_flipkart_price(query):
#     url = f'https://www.flipkart.com/search?q={query}'
#     retries = 3  # Number of retries

#     for attempt in range(retries):
#         try:
#             response = requests.get(url, headers=HEADERS)
#             if response.status_code == 429:
#                 logging.error("Too many requests to Flipkart, adding delay.")
#                 time.sleep(random.uniform(20, 30))  # Increased delay between 20 and 30 seconds
#                 continue
#             response.raise_for_status()

#             soup = BeautifulSoup(response.text, 'html.parser')
#             product_container = soup.find('div', {'class': '_1YokD2 _3Mn1Gg'})
#             if not product_container:
#                 logging.error(f"No products found for '{query}' on Flipkart")
#                 return "Not found"

#             product = product_container.find('div', {'class': '_1AtVbE col-12-12'})
#             if product:
#                 price = product.find('div', {'class': '_30jeq3 _1_WHN1'})
#                 if price:
#                     return price.text.replace('₹', '').strip()

#             logging.error(f"No price found for '{query}' on Flipkart")
#             return "Not found"
#         except requests.exceptions.RequestException as e:
#             logging.error(f"Error fetching Flipkart price: {e}")
#             time.sleep(random.uniform(20, 30))  # Increased delay before retrying
#     return "Error"

# def get_amazon_price(query):
#     url = f'https://www.amazon.in/s?k={query}'
#     retries = 3  # Number of retries

#     for attempt in range(retries):
#         try:
#             response = requests.get(url, headers=HEADERS)
#             if response.status_code == 503:
#                 logging.error("Service unavailable on Amazon, adding delay.")
#                 time.sleep(random.uniform(20, 30))  # Increased delay between 20 and 30 seconds
#                 continue
#             response.raise_for_status()

#             soup = BeautifulSoup(response.text, 'html.parser')
#             product = soup.find('span', {'class': 'a-price-whole'})
#             if product:
#                 return product.text.replace(',', '').strip()

#             logging.error(f"No products found for '{query}' on Amazon")
#             return "Not found"
#         except requests.exceptions.RequestException as e:
#             logging.error(f"Error fetching Amazon price: {e}")
#             time.sleep(random.uniform(20, 30))  # Increased delay before retrying
#     return "Error"

# @app.route('/compare', methods=['GET'])
# def compare():
#     query = request.args.get('query')
#     if not query:
#         return jsonify({'error': 'Query parameter is required'}), 400

#     flipkart_price = get_flipkart_price(query)
#     amazon_price = get_amazon_price(query)

#     return jsonify({
#         'flipkart_price': flipkart_price,
#         'amazon_price': amazon_price
#     })

# if __name__ == '__main__':
#     print("Starting the Flask application...")
#     app.run(debug=True)
