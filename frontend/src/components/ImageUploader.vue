<template>
  <div>
    <h2>Upload Your Image</h2>
    <input type="file" @change="uploadImage" />
    <div v-if="uploadedImagePath">
      <p>Image uploaded successfully!</p>
      <img :src="uploadedImagePath" alt="Uploaded Image" />
      <button @click="$emit('startEditing', uploadedImagePath)">Start Editing</button>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      uploadedImagePath: null,
    };
  },
  methods: {
    uploadImage(event) {
      const file = event.target.files[0];
      const formData = new FormData();
      formData.append("file", file);
      axios.post("/upload", formData)
        .then(response => {
          this.uploadedImagePath = response.data.filepath;
        })
        .catch(error => {
          console.error("Error uploading image:", error);
        });
    }
  }
};
</script>
