<template>
  <div>
    <h3>ID Photo Maker</h3>
    <button @click="makeIDPhoto">Make ID Photo</button>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  props: ['imagePath'],
  methods: {
    makeIDPhoto() {
      axios.post('/process', {
        filepath: this.imagePath,
        action: 'id_photo'
      })
      .then(response => {
        this.$emit('imageProcessed', response.data.filepath);
      })
      .catch(error => {
        console.error("Error making ID photo:", error);
      });
    }
  }
};
</script>
