new Vue({
    el: '#app',
    data: {
        imageSrc: null,
        file: null,  // 保存上传的文件
        brightness: 50,
        contrast: 50,
        saturation: 50,
        hue: 50
    },
    methods: {
        openImage() {
            this.$refs.fileInput.click();
        },
        loadImage(event) {
            this.file = event.target.files[0];
            const reader = new FileReader();
            reader.onload = e => {
                this.imageSrc = e.target.result;
                this.resetFilters();
            };
            reader.readAsDataURL(this.file);
        },
        resetFilters() {
            this.brightness = 50;
            this.contrast = 50;
            this.saturation = 50;
            this.hue = 50;
        },
        applyFilter() {
            const img = document.querySelector('.editor-image');
            if (img) {
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
                    this.imageSrc = `/processed/${data.filepath.split('/').pop()}`;
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
            link.download = 'edited-image.png';
            link.click();
        },
        moreOptions() {
            alert('More options functionality is not implemented yet.');
        }
    }
});
