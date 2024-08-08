<template>
  <div id="app">
    <PriceComparison />
  </div>
</template>

<script>
  import PriceComparison from './components/PriceComparison.vue';

  export default {
    name: 'App',
    components: {
      PriceComparison
    }
  };
</script>

<style>
  #app {
    font-family: Avenir, Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    text-align: center;
    color: #2c3e50;
    margin-top: 60px;
  }
</style>