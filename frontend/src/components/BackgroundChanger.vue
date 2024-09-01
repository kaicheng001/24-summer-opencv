<template>
  <div>
    <h3>Background Changer</h3>
    <button @click="changeBackground">Change Background</button>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  props: ['imagePath'],
  methods: {
    changeBackground() {
      axios.post('/process', {
        filepath: this.imagePath,
        action: 'background_change'
      })
      .then(response => {
        this.$emit('imageProcessed', response.data.filepath);
      })
      .catch(error => {
        console.error("Error changing background:", error);
      });
    }
  }
};
</script>
