<template>
  <div id="app">
    <h1>Image Processing Application</h1>
    <div class="button-container">
      <button class="animated-button" @click="navigateTo('upload')">Upload Image</button>
      <button class="animated-button" @click="navigateTo('edit')">Edit Image</button>
      <button class="animated-button" @click="navigateTo('area-mask')">Apply Area Mask</button>
      <button class="animated-button" @click="navigateTo('segmentation')">Segment Image</button>
      <button class="animated-button" @click="navigateTo('background-change')">Change Background</button>
    </div>
    <router-view />
  </div>
</template>

<script>
export default {
  methods: {
    navigateTo(routeName) {
      this.$router.push({ name: routeName });
    }
  }
};
</script>

<style>
.button-container {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-bottom: 20px;
}

.animated-button {
  padding: 10px 20px;
  font-size: 16px;
  color: white;
  background-color: #4CAF50;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s, transform 0.3s;
}

.animated-button:hover {
  background-color: #45a049;
  transform: scale(1.1);
}
</style>
