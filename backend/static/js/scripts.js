new Vue({
    el: '#app',
    data: {
        imageSrc: null,
        file: null,  // 保存上传的文件
        brightness: 100,
        contrast: 100,
        saturation: 100,
        hue: 0,
        inputKey: 0,  // 用于强制重新渲染 input 元素
        activeSection: 'basic',  // 控制第二个共享区域的展示部分，默认显示“基本”部分
        processSection: ''  // 用于控制第一个共享区域的显示内容
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
            this.resetInput();  // 强制重新渲染 input
        },
        resetFilters() {
            this.brightness = 100;
            this.contrast = 100;
            this.saturation = 100;
            this.hue = 0;
        },
        resetInput() {
            this.inputKey += 1;
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
        // 切换第一个共享区域的内容（浏览、马赛克、分隔等）
        setProcessSection(section) {
            this.processSection = section;
        },
        // 保留的函数，控制第二个共享区域的内容（基本、滤镜、文字、水印等）
        setActiveSection(section) {
            this.activeSection = section;
        },
        async processImage(action) {               //executeImageProcessing
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
                    this.imageSrc = `${data.filepath}?t=${new Date().getTime()}`;  // 防止缓存
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
        },
        // 基本、滤镜、文字、水印按钮的功能，切换第二个共享区域的内容
        basic() {
            this.setActiveSection('basic');
        },
        filters() {
            this.setActiveSection('filters');
        },
        word() {
            this.setActiveSection('word');
        },
        reset() {
            this.setActiveSection('watermark');
        }
    }
});
