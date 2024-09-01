<template>
  <div>
    <h3>Apply Area Mask</h3>
    <button @click="applyMask">Apply Mask</button>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  props: ['imagePath'],
  methods: {
    applyMask() {
      axios.post('/process', {
        filepath: this.imagePath,
        action: 'area_mask'
      })
      .then(response => {
        this.$emit('imageProcessed', response.data.filepath);
      })
      .catch(error => {
        console.error("Error applying mask:", error);
      });
    }
  }
};
</script>
