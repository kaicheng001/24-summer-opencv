<template>
  <div>
    <h2>Edit Your Image</h2>
    <img :src="imagePath" alt="Image to Edit" />
    <div>
      <button @click="applyAreaMask">Apply Area Mask</button>
      <button @click="applySegmentation">Apply Segmentation</button>
      <button @click="changeBackground">Change Background</button>
    </div>
    <div v-if="processedImagePath">
      <h3>Processed Image</h3>
      <img :src="processedImagePath" alt="Processed Image" />
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  props: ['imagePath'],
  data() {
    return {
      processedImagePath: null
    };
  },
  methods: {
    applyAreaMask() {
      this.processImage('area_mask');
    },
    applySegmentation() {
      this.processImage('segmentation');
    },
    changeBackground() {
      this.processImage('background_change');
    },
    processImage(action) {
      axios.post('/process', {
        filepath: this.imagePath,
        action: action
      })
      .then(response => {
        this.processedImagePath = response.data.filepath;
      })
      .catch(error => {
        console.error("Error processing image:", error);
      });
    }
  }
};
</script>
