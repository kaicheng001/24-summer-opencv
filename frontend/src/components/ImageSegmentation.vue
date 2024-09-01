<template>
  <div>
    <h3>Image Segmentation</h3>
    <button @click="segmentImage">Segment Image</button>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  props: ['imagePath'],
  methods: {
    segmentImage() {
      axios.post('/process', {
        filepath: this.imagePath,
        action: 'segmentation'
      })
      .then(response => {
        this.$emit('imageProcessed', response.data.filepath);
      })
      .catch(error => {
        console.error("Error segmenting image:", error);
      });
    }
  }
};
</script>
