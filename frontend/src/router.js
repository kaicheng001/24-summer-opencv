import Vue from 'vue';
import Router from 'vue-router';
import ImageUploader from './components/ImageUploader.vue';
import ImageEditor from './components/ImageEditor.vue';
import AreaMask from './components/AreaMask.vue';
import ImageSegmentation from './components/ImageSegmentation.vue';
import BackgroundChanger from './components/BackgroundChanger.vue';

Vue.use(Router);

export default new Router({
  routes: [
    { path: '/', name: 'upload', component: ImageUploader },
    { path: '/edit', name: 'edit', component: ImageEditor },
    { path: '/area-mask', name: 'area-mask', component: AreaMask },
    { path: '/segmentation', name: 'segmentation', component: ImageSegmentation },
    { path: '/background-change', name: 'background-change', component: BackgroundChanger }
  ]
});
