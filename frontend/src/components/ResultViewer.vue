<template>
  <div>
    <h3>Processed Image Result</h3>
    <img :src="imagePath" alt="Processed Image" />
  </div>
</template>

<script>
export default {
  props: ['imagePath']
};
</script>
