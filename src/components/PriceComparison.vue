<template>
  <div class="price-comparison">
    <h1>Price Comparison</h1>
    <input v-model="searchQuery" placeholder="Search for a product" />
    <button @click="fetchPrices">Search</button>
    <div v-if="errorMessage">
      <p class="error">{{ errorMessage }}</p>
    </div>
    <div v-else-if="flipkartPrice && amazonPrice">
      <div class="product">
        <h2>Flipkart Price: {{ flipkartPrice }}</h2>
      </div>
      <div class="product">
        <h2>Amazon Price: {{ amazonPrice }}</h2>
      </div>
    </div>
    <div v-else>
      <p>No products found.</p>
    </div>
    <div>
      <h2>Logs</h2>
      <div v-for="(log, index) in logs" :key="index" class="log">
        <p>{{ log }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'PriceComparison',
  data() {
    return {
      searchQuery: '',
      flipkartPrice: '',
      amazonPrice: '',
      errorMessage: '',
      logs: [],
      maxLogs: 10, // Maximum number of logs to keep
      logUpdateInterval: 100, // Interval to update logs (in milliseconds)
      eventSource: null // Store the EventSource instance
    };
  },
  methods: {
    async fetchPrices() {
      this.errorMessage = '';
      this.flipkartPrice = '';
      this.amazonPrice = '';
      this.logs = []; // Clear logs before fetching prices

      try {
        const response = await axios.get('http://127.0.0.1:5000/compare', {
          params: { query: this.searchQuery }
        });

        if (response.data.flipkart_price === 'Not found' || response.data.amazon_price === 'Not found') {
          this.errorMessage = `Product "${this.searchQuery}" not found on one or both platforms.`;
        } else if (response.data.flipkart_price === 'Error' || response.data.amazon_price === 'Error') {
          this.errorMessage = 'An error occurred while fetching prices.';
        } else {
          this.flipkartPrice = response.data.flipkart_price;
          this.amazonPrice = response.data.amazon_price;
        }
      } catch (error) {
        this.errorMessage = 'An error occurred while fetching prices. Please try again later.';
        console.error('Error fetching prices:', error);
      }
    },
    async fetchLogs() {
      const eventSource = new EventSource('http://127.0.0.1:5000/log');
      let logBuffer = [];

      eventSource.onmessage = (event) => {
        logBuffer.push(event.data); // Add new log message to the log buffer
      };

      setInterval(() => {
        if (logBuffer.length > 0) {
          this.logs = logBuffer.slice(-this.maxLogs); // Update logs with the latest messages
          logBuffer = []; // Clear the log buffer
        }
      }, this.logUpdateInterval);
    }
  },
  mounted() {
    this.fetchLogs();
  },
  beforeDestroy() {
    if (this.eventSource) {
      this.eventSource.close(); // Close the EventSource connection
    }
  }
};
</script>

<style scoped>
.price-comparison {
  text-align: center;
  margin: 20px;
}

.product {
  border: 1px solid #ccc;
  padding: 10px;
  margin: 10px 0;
}

.error {
  color: red;
}

.log {
  border: 1px solid #ccc;
  padding: 10px;
  margin: 10px 0;
  background-color: #f9f9f9;
}
</style>