new Vue({
    el: '#app',
    data: {
        imageSrc: null,
        file: null,  // 保存上传的文件
        brightness: 50,
        contrast: 50,
        saturation: 50,
        hue: 50,
        inputKey: 0  // 用于强制重新渲染 input 元素
    },
    methods: {
        openImage() {
            this.$refs.fileInput.click();
        },
        loadImage(event) {
            this.file = event.target.files[0];
            const reader = new FileReader();
            reader.onload = e => {
                this.imageSrc = e.target.result;  // 设置新图片路径
                this.resetFilters();  // 重置滤镜到默认状态
            };
            reader.readAsDataURL(this.file);

            // 强制重新渲染 input，以确保可以选择同一个文件
            this.resetInput();
        },
        resetFilters() {
            // 重置所有图像滤镜的值
            this.brightness = 50;
            this.contrast = 50;
            this.saturation = 50;
            this.hue = 50;
        },
        resetInput() {
            // 强制重新渲染 input 元素，清空 file input
            this.inputKey += 1;
        },
        applyFilter() {
            const img = document.querySelector('.editor-image');
            if (img) {
                // 应用图像处理滤镜
                img.style.filter = `
                    brightness(${this.brightness}%)
                    contrast(${this.contrast}%)
                    saturate(${this.saturation}%)
                    hue-rotate(${this.hue}deg)
                `;
            }
        },
        async processImage(action) {
            if (!this.file) {
                alert('Please upload an image first.');
                return;
            }

            const formData = new FormData();
            formData.append('file', this.file);
            formData.append('action', action);

            try {
                const response = await fetch('/process', {
                    method: 'POST',
                    body: formData
                });

                if (response.ok) {
                    const data = await response.json();
                    // Set the image source with a timestamp to avoid caching issues
                    this.imageSrc = `${data.filepath}?t=${new Date().getTime()}`;
                } else {
                    alert('Image processing failed.');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('An error occurred during image processing.');
            }
        },
        saveImage() {
            if (!this.imageSrc) {
                alert('Please upload an image first.');
                return;
            }

            const link = document.createElement('a');
            link.href = this.imageSrc;
            link.download = 'edited-image.png';  // 下载处理后的图片
            link.click();
        },
        moreOptions() {
            alert('More options functionality is not implemented yet.');
        }
    }
});
