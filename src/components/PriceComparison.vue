<template>
    <div class="price-comparison">
      <h1>Price Comparison</h1>
      <input v-model="searchQuery" placeholder="Search for a product" />
      <button @click="fetchPrices">Search</button>
      <div v-if="products.length">
        <div v-for="product in products" :key="product.id" class="product">
          <h2>{{ product.name }}</h2>
          <p>Price: {{ product.price }}</p>
          <p>Store: {{ product.store }}</p>
        </div>
      </div>
      <div v-else>
        <p>No products found.</p>
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
        products: []
        };
    },
    methods: {
        async fetchPrices() {
        try {
            const response = await axios.get(`YOUR_API_ENDPOINT?query=${this.searchQuery}`);
            this.products = response.data;
        } catch (error) {
            console.error('Error fetching prices:', error);
        }
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
</style>