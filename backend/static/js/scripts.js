new Vue({
  el: "#app",
  data: {
    imageSrc: null,
    imageSrc1: null,
    imageSrctemp: null,
    file: null, // 保存上传的文件
    fil11: null,
    brightness: 100,
    contrast: 100,
    saturation: 100,
    hue: 100,
    temperature: 100,
    inputKey: 0, // 用于强制重新渲染 input 元素
    activeSection: "basic", // 控制第二个共享区域的展示部分，默认显示“基本”部分
    processSection: "", // 用于控制第一个共享区域的显示内容
    /////////////////
    imageHistory: [], // 图片路径的栈
    filesHistory: [], // 文件历史的栈
    currentVersion: 0, // 当前图片操作版本号
    /////////////////////////canvas
    canvas: null,
    ctx: null,
    isDrawing: false,
    isInsert: false,
    isTuo: false,
    startX: 0,
    startY: 0,
    rectWidth: 0,
    rectHeight: 0,
    rotation: 0, // 用于旋转矩形的角度
    cropInfo: null, // 保存裁剪区域信息
    R: 255, ////////////RGB用于证件照制作和背景更换
    G: 255,
    B: 255,
    pointInfo: null,

    rotationPic: 0,
    imageWidth: 300, // 初始图片宽度
    imageHeight: 200, // 初始图片高度
    resizing: false, // 是否正在调整大小
    initialWidth: 0, // 初始宽度
    initialHeight: 0, // 初始高度
    zeroWidth: 0,
    zeroHeight: 0,
    startX: 0, // 鼠标开始拖动的 X 坐标
    startY: 0, // 鼠标开始拖动的 Y 坐标

    translateX: 0,
    translateY: 0,
    initialX: 0,
    initialY: 0,
    zeroX: 0,
    zeroY: 0,
    inputText: "", // New: Holds the user-entered text
    isDraggingText: false, // New: For text dragging state
    textPosition: { x: 50, y: 50 }, // New: Initial position for the text

    texiao: "tutou",
    actionhuabi: "mosaic",

    segsize:10,
    mosaicsize:10,
    huabisize:10,
    //下面这部分是我添加的每个滤镜图片示例的数据
    data: {
      activeSection: "filters", // 控制展示的功能部分，默认显示“滤镜”部分
    },
  },
  methods: {
    // New method: Add text to canvas
    // New method: Add text to canvas
    addTextToCanvas() {
      if (!this.inputText) {
        alert("Please enter some text");
        return;
      }

      this.ctx.font = "20px Arial";
      this.ctx.fillStyle = "blue"; // You can customize the font style
      this.ctx.fillText(
        this.inputText,
        this.textPosition.x,
        this.textPosition.y
      );

      // Enable dragging after adding text
      this.enableTextDragging();
    },

    // New method: Enable text dragging
    enableTextDragging() {
      const canvas = this.canvas;
      this.canvas.addEventListener("mousedown", this.startDraggingText);
      this.canvas.addEventListener("mousemove", this.dragText);
      this.canvas.addEventListener("mouseup", this.stopDraggingText);
    },

    startDraggingText(e) {
      const rect = this.canvas.getBoundingClientRect();
      const mouseX = e.clientX - rect.left;
      const mouseY = e.clientY - rect.top;

      // Check if the mouse is on the text
      if (
        mouseX >= this.textPosition.x &&
        mouseX <=
          this.textPosition.x + this.ctx.measureText(this.inputText).width &&
        mouseY >= this.textPosition.y - 20 &&
        mouseY <= this.textPosition.y
      ) {
        this.isDraggingText = true;
        this.startX = mouseX - this.textPosition.x;
        this.startY = mouseY - this.textPosition.y;
      }
    },

    dragText(e) {
      if (!this.isDraggingText) return;

      const rect = this.canvas.getBoundingClientRect();
      const mouseX = e.clientX - rect.left;
      const mouseY = e.clientY - rect.top;

      // Update text position
      this.textPosition.x = mouseX - this.startX;
      this.textPosition.y = mouseY - this.startY;

      // Clear the canvas and redraw everything including the text at the new position
      this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
      const img = new Image();
      img.src = this.imageSrc;
      img.onload = () => {
        this.ctx.drawImage(img, 0, 0, this.canvas.width, this.canvas.height);
        this.ctx.fillText(
          this.inputText,
          this.textPosition.x,
          this.textPosition.y
        );
      };
    },

    stopDraggingText() {
      this.isDraggingText = false;
    },

    async textimage() {
      const formData = new FormData();
      formData.append("inputtext", this.inputText);
     
      try {
        const response = await fetch("/processtext", {
          method: "POST",
          body: formData,
        });
        if (response.ok) {
          const data = await response.json();

          // 更新图像显示
          // Base64 编码的图像数据直接赋值给 imageSrc
          this.imageSrc1 = `data:image/jpeg;base64,${data.image_base64}`;
          console.error("insert processing succes.");
        } else {
          console.error("insert processing failed.");
        }
      } catch (error) {
        console.error("Error:", error);
      }
      this.enableInsertListeners();
    },

    openImage() {
      this.$refs.fileInput.click();
    },
    loadImage(event) {
      this.file = event.target.files[0];
      const reader = new FileReader();
      reader.onload = (e) => {
        this.imageSrc = e.target.result; // 设置新图片路径
        this.resetFilters(); // 重置滤镜到默认状态

        // 重置图片历史
        this.imageHistory = [this.imageSrc]; // 将最初的图片放入栈底
        this.currentVersion = 0;
        const img = new Image();
        img.src = this.imageSrc;
        console.log("imgck");

        img.onload = () => {
          console.log(img.width);
          this.imageWidth = img.width;
          this.imageHeight = img.height;
          this.zeroHeight = img.height;
          this.zeroWidth = img.width;
          console.log("wi", this.imageWidth);
          console.log("hi:", this.imageHeight);
        };
        ///////////canvas
        this.$nextTick(() => {
          console.log("Image should now be in the DOM");
          this.setupCanvas();
          alert("canvas start");
        }); ///////
      };
      reader.readAsDataURL(this.file);
      this.resetInput(); // 强制重新渲染 input
    },
    openImage1() {
      this.$refs.fileInput1.click(); // 触发隐藏的文件选择器
    },

    loadImage1(event) {
      this.file1 = event.target.files[0]; // 将文件读取到 this.file1
      const reader = new FileReader();
      reader.onload = (e) => {
        this.imageSrc1 = e.target.result; // 设置新图片路径
        this.$nextTick(() => {
          //this.imageWidth=img.width;
          //this.imageHeight=img.height;
          this.enableInsertListeners();
        });
      };
      reader.readAsDataURL(this.file1);
      this.resetInput();
    },
    returnSize() {
      this.imageHeight = this.zeroHeight;
      this.imageWidth = this.zeroWidth;
      this.translateX = this.zeroX;
      this.translateY = this.zeroY;
      this.rotationPic = 0;
    },
    startResize(corner, event) {
      this.resizing = true;
      this.initialWidth = this.imageWidth;
      this.initialHeight = this.imageHeight;
      this.startX = event.clientX; // 记录鼠标初始X位置
      this.startY = event.clientY; // 记录鼠标初始Y位置
      document.addEventListener("mousemove", this.resize);
      document.addEventListener("mouseup", this.stopResize);
    },
    resize(event) {
      if (!this.resizing) return;
      let dx = event.clientX - this.startX; // 计算鼠标在X方向的移动距离
      let dy = event.clientY - this.startY; // 计算鼠标在Y方向的移动距离

      // 根据拖动方向计算新的宽高
      this.imageWidth = this.initialWidth + dx;
      this.imageHeight = this.initialHeight + dy;
    },
    stopResize() {
      this.resizing = false;
      document.removeEventListener("mousemove", this.resize);
      document.removeEventListener("mouseup", this.stopResize);
    },

    resetFilters() {
      this.brightness = 100;
      this.contrast = 100;
      this.saturation = 100;
      this.hue = 0;
      this.temperature = 0;
      this.R = 0;
      this.G = 0;
      this.B = 0;
    },
    resetInput() {
      this.inputKey += 1;
    },
    applyFilter() {
      const img = document.querySelector(".editor-image");
      if (img) {
        img.style.filter = `
                    brightness(${this.brightness}%)
                    contrast(${this.contrast}%)
                    saturate(${this.saturation}%)
                    hue-rotate(${this.hue}deg)
                    sepia(${this.temperature}%)
                `;
      }
    },
    /////////执行12中滤镜操作
    async applyFilterRGB() {
      if (this.file) {
        const formData = new FormData();
        formData.append("file", this.file);
        formData.append("R", this.R);
        formData.append("G", this.G);
        formData.append("B", this.B);

        try {
          const response = await fetch("/apply-rgb-filter", {
            method: "POST",
            body: formData,
          });

          if (response.ok) {
            const blob = await response.blob();
            const url = URL.createObjectURL(blob);
            this.imageSrc = url; // 实时更新图片
          } else {
            console.error("RGB filter application failed.");
          }
        } catch (error) {
          console.error("Error during RGB filter application:", error);
        }
      }
    },

    //////////canvas
    setupCanvas() {
      const img = document.getElementById("image");
      const canvas = document.getElementById("canvas");

      if (!img) {
        console.error("Image element not found in the DOM");
        return;
      }

      if (!canvas) {
        console.error("Canvas element not found in the DOM");
        return;
      }

      img.onload = () => {
        // 确保图片加载完毕后再设置画布大小
        this.canvas = canvas;
        this.ctx = this.canvas.getContext("2d");

        this.canvas.width = img.naturalWidth; // 使用图片的实际宽度
        this.canvas.height = img.naturalHeight; // 使用图片的实际高度
        // 确保 canvas 的 CSS 尺寸和图片显示尺寸一致
        canvas.style.width = `${img.clientWidth}px`;
        canvas.style.height = `${img.clientHeight}px`;
        console.log(
          `Canvas dimensions set to: ${this.canvas.width}x${this.canvas.height}`
        );

        // 监听鼠标事件
      };

      if (img.complete) {
        img.onload(); // 如果图片已经加载完成，手动触发 onload
      }
    },

    removeAllListeners() {
      this.canvas.removeEventListener("mousedown", this.startDrawing);
      this.canvas.removeEventListener("mousemove", this.drawRect);
      this.canvas.removeEventListener("mouseup", this.finishDrawing);
      this.canvas.removeEventListener("click", this.markPoint);
      this.canvas.removeEventListener("mousemove", this.trackMouseMove);
      this.canvas.removeEventListener("mousedown", this.startInsert);
      this.canvas.removeEventListener("mousemove", this.insertPic);
      this.canvas.removeEventListener("mouseup", this.finishInsert);
      this.canvas.removeEventListener("mousedown", this.startTuo);
      this.canvas.removeEventListener("mousemove", this.Tuo);
      this.canvas.removeEventListener("mouseup", this.finishTuo);
    },
    // 启用矩形绘制的监听器
    enableDrawRectListeners() {
      this.removeAllListeners(); // 先移除其他的监听器
      this.canvas.addEventListener("mousedown", this.startDrawing);
      this.canvas.addEventListener("mousemove", this.drawRect);
      this.canvas.addEventListener("mouseup", this.finishDrawing);
    },
    // 启用单点绘制的监听器
    enablePointListeners(action) {
      this.action = action;
      this.removeAllListeners(); // 先移除其他的监听器
      this.canvas.addEventListener("click", this.markPoint); // 添加新的点击监听器
    },
    // 启用连续点绘制的监听器
    enableMosaicListeners(action) {
      this.imageSrctemp = this.imageSrc;
      this.actionhuabi = action;
      this.removeAllListeners(); // 先移除其他的监听器
      this.canvas.addEventListener("mousemove", this.trackMouseMove); // 添加新的点击监听器
      this.sendmask();
    },
    enableInsertListeners() {
      this.imageSrctemp = this.imageSrc;
      console.log("jiantingcharu");
      this.removeAllListeners();
      this.canvas.addEventListener("mousedown", this.startInsert);
      this.canvas.addEventListener("mousemove", this.insertPic);
      this.canvas.addEventListener("mouseup", this.finishInsert);
    },
    enableTuoListeners() {
      this.removeAllListeners();
      this.canvas.addEventListener("mousedown", this.startTuo);
      this.canvas.addEventListener("mousemove", this.Tuo);
      this.canvas.addEventListener("mouseup", this.finishTuo);
    },
    startTuo(e) {
      this.isTuo = true;
      this.initialX = this.translateX;
      this.initialY = this.translateY;
      this.startX = e.clientX; // 记录鼠标初始X位置
      this.startY = e.clientY; // 记录鼠标初始Y位置
    },
    Tuo(e) {
      if (!this.isTuo) return;
      let dx = e.clientX - this.startX; // 计算鼠标在X方向的移动距离
      let dy = e.clientY - this.startY; // 计算鼠标在Y方向的移动距离

      // 根据拖动方向计算新的宽高
      this.translateX = this.initialX + dx;
      this.translateY = this.initialY + dy;
    },
    finishTuo() {
      this.isTuo = false;
    },
    startInsert() {
      this.isDrawing = true;
    },
    async insertPic(e) {
      if (!this.isDrawing) return;
      const rect = this.canvas.getBoundingClientRect();

      // 计算缩放比例
      const scaleX = this.canvas.width / rect.width;
      const scaleY = this.canvas.height / rect.height;

      // 获取鼠标移动时的位置
      const x = (e.clientX - rect.left) * scaleX;
      const y = (e.clientY - rect.top) * scaleY;

      // 保存当前点的位置
      this.pointInfo = { x, y };
      if (
        !this.imageSrctemp.startsWith("data:image/") &&
        this.imageSrctemp.includes("/processed/")
      ) {
        // 如果是文件地址形式，将其转换为 Base64
        this.imageSrctemp = await this.convertImageToBase64(this.imageSrctemp);
      }
      let base64Data = this.imageSrctemp;
      if (this.imageSrctemp.includes(",")) {
        base64Data = this.imageSrctemp.split(",")[1]; // 去掉前缀
      } else {
        console.error("Invalid image source format");
        return; // 如果格式不对，停止执行
      }
      ///
      if (
        !this.imageSrc1.startsWith("data:image/") &&
        this.imageSrc1.includes("/processed/")
      ) {
        // 如果是文件地址形式，将其转换为 Base64
        this.imageSrc1 = await this.convertImageToBase64(this.imageSrc1);
      }
      let base64Data1 = this.imageSrc1;
      if (this.imageSrc1.includes(",")) {
        base64Data1 = this.imageSrc1.split(",")[1]; // 去掉前缀
      } else {
        console.error("Invalid image source format");
        return; // 如果格式不对，停止执行
      }
      const formData = new FormData();
      formData.append("x", x);
      formData.append("y", y);
      formData.append("action", "mosaic"); // 传递给后端的操作类型
      formData.append("image_base64", base64Data);
      formData.append("image_base64_1", base64Data1);
      formData.append("version", this.imageHistory.length);
      try {
        const response = await fetch("/processInsert", {
          method: "POST",
          body: formData,
        });
        if (response.ok) {
          const data = await response.json();

          // 更新图像显示
          // Base64 编码的图像数据直接赋值给 imageSrc
          this.imageSrc = `data:image/jpeg;base64,${data.image_base64}`;
          console.error("insert processing succes.");
        } else {
          console.error("insert processing failed.");
        }
      } catch (error) {
        console.error("Error:", error);
      }
    },
    finishInsert() {
      this.isDrawing = false;
    },
    startDrawing(e) {
      this.isDrawing = true;
      const rect = this.canvas.getBoundingClientRect();

      // 计算缩放比例
      const scaleX = this.canvas.width / rect.width; // 如果 canvas 宽度和显示宽度不同
      const scaleY = this.canvas.height / rect.height; // 如果 canvas 高度和显示高度不同

      // 获取正确的鼠标坐标，考虑到缩放
      this.startX = (e.clientX - rect.left) * scaleX;
      this.startY = (e.clientY - rect.top) * scaleY;

      this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    },
    drawRect(e) {
      if (!this.isDrawing) return;
      const rect = this.canvas.getBoundingClientRect();

      // 获取当前鼠标位置，考虑缩放
      const currentX = e.clientX - rect.left;
      const currentY = e.clientY - rect.top;

      this.rectWidth = currentX - this.startX;
      this.rectHeight = currentY - this.startY;

      // 清除之前的矩形并重新绘制
      this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
      this.ctx.save();
      this.ctx.translate(
        this.startX + this.rectWidth / 2,
        this.startY + this.rectHeight / 2
      );
      this.ctx.rotate((this.rotation * Math.PI) / 180);
      this.ctx.strokeStyle = "red";
      this.ctx.strokeRect(
        -this.rectWidth / 2,
        -this.rectHeight / 2,
        this.rectWidth,
        this.rectHeight
      );
      this.ctx.restore();
    },
    finishDrawing() {
      this.isDrawing = false;
      // 保存裁剪的位置信息
      this.cropInfo = {
        x: this.startX,
        y: this.startY,
        width: this.rectWidth,
        height: this.rectHeight,
        rotation: this.rotation,
      };
    },
    rotateRect() {
      if (this.isDrawing) return;
      // 重新绘制旋转后的矩形
      this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
      this.ctx.save();
      this.ctx.translate(
        this.startX + this.rectWidth / 2,
        this.startY + this.rectHeight / 2
      );
      this.ctx.rotate((this.rotation * Math.PI) / 180);
      this.ctx.strokeStyle = "red";
      this.ctx.strokeRect(
        -this.rectWidth / 2,
        -this.rectHeight / 2,
        this.rectWidth,
        this.rectHeight
      );
      this.ctx.restore();
    },
    async cropImage() {
      // 将 canvas 中的裁剪区域按实际图片的尺寸进行缩放
      const rect = this.canvas.getBoundingClientRect();

      // 计算缩放比例，反向缩放回原始图片尺寸
      const scaleX = this.canvas.width / rect.width;
      const scaleY = this.canvas.height / rect.height;
      // 将裁剪信息发送到后端
      const formData = new FormData();
      formData.append("x", this.cropInfo.x);
      formData.append("y", this.cropInfo.y);
      formData.append("width", this.cropInfo.width);
      formData.append("height", this.cropInfo.height);
      formData.append("rotation", this.cropInfo.rotation);
      formData.append("action", "crop");
      formData.append("file", this.file);
      formData.append("version", this.imageHistory.length); // 发送新的版本号
      try {
        const response = await fetch("/processcanvas", {
          method: "POST",
          body: formData,
        });
        if (response.ok) {
          const data = await response.json();

          // 添加新处理的图片路径到栈
          this.imageHistory.push(`${data.filepath}?t=${new Date().getTime()}`);
          // Set the image source with a timestamp to avoid caching issues
          // 更新当前版本号并展示最新处理结果
          this.currentVersion = this.imageHistory.length - 1;
          this.imageSrc = this.imageHistory[this.currentVersion];
          const img = new Image();
          img.src = this.imageSrc;//////////////////////////////////////////////////////
          console.log("imgck");

          img.onload = () => {
          console.log(img.width);
          this.imageWidth = img.width;
          this.imageHeight = img.height;
          this.zeroHeight = img.height;
          this.zeroWidth = img.width;
          this.rotationPic=0;
          console.log("wi", this.imageWidth);
          console.log("hi:", this.imageHeight);
           };
          // 将处理后的图片路径转换为 Blob 并更新 this.file
          await this.updateFileFromImageSrc(this.imageSrc);
        } else {
          alert("Image processing failed.");
        }
      } catch (error) {
        console.error("Error:", error);
        alert("An error occurred during image processing.");
      }
    },
    
    async rotateImage() {
        const formData = new FormData();
        formData.append("action", "rotate");
        formData.append("file", this.file);
        formData.append("version", this.imageHistory.length); // 发送新的版本号
        formData.append('angle',this.rotationPic);
        formData.append('width',this.imageWidth);
        formData.append('height',this.imageHeight);
         try {
        const response = await fetch("/processcanvas", {
          method: "POST",
          body: formData,
        });
        if (response.ok) {
          const data = await response.json();

          // 添加新处理的图片路径到栈
          this.imageHistory.push(`${data.filepath}?t=${new Date().getTime()}`);
          // Set the image source with a timestamp to avoid caching issues
          // 更新当前版本号并展示最新处理结果
          this.currentVersion = this.imageHistory.length - 1;
          this.imageSrc = this.imageHistory[this.currentVersion];
          const img = new Image();
          img.src = this.imageSrc;//////////////////////////////////////////////////////
          console.log("imgck");

          img.onload = () => {
          console.log(img.width);
          this.imageWidth = img.width;
          this.imageHeight = img.height;
          this.zeroHeight = img.height;
          this.zeroWidth = img.width;
          this.rotationPic=0;
          console.log("wi", this.imageWidth);
          console.log("hi:", this.imageHeight);
           };
          // 将处理后的图片路径转换为 Blob 并更新 this.file
          await this.updateFileFromImageSrc(this.imageSrc);
        } else {
          alert("Image processing failed.");
        }
      } catch (error) {
        console.error("Error:", error);
        alert("An error occurred during image processing.");
      }
    },
    
    // 标记点的事件处理函数
    markPoint(e) {
      const rect = this.canvas.getBoundingClientRect();

      // 计算缩放比例
      const scaleX = this.canvas.width / rect.width;
      const scaleY = this.canvas.height / rect.height;

      // 获取点击位置的鼠标坐标，考虑到缩放
      const x = (e.clientX - rect.left) * scaleX;
      const y = (e.clientY - rect.top) * scaleY;

      // 保存点的位置
      this.pointInfo = { x, y };

      // 清除画布并绘制标点
      this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
      this.drawPoint(x, y);
    },

    // 绘制单个标点的函数
    drawPoint(x, y) {
      this.ctx.fillStyle = "blue"; // 设置标点颜色
      const pointSize = 5; // 标点的大小
      this.ctx.beginPath();
      this.ctx.arc(x, y, pointSize, 0, Math.PI * 2); // 绘制圆形标点
      this.ctx.fill();
    },

    async transImage() {
      // 将 canvas 中的裁剪区域按实际图片的尺寸进行缩放
      // 将裁剪信息发送到后端
      const formData = new FormData();
      formData.append("x", this.pointInfo.x);
      formData.append("y", this.pointInfo.y);
      formData.append("action", this.action);
      formData.append("file", this.file);
      formData.append("version", this.imageHistory.length); // 发送新的版本号
      try {
        const response = await fetch("/processtrans", {
          method: "POST",
          body: formData,
        });
        if (response.ok) {
          const data = await response.json();

          // 添加新处理的图片路径到栈
          this.imageHistory.push(`${data.filepath}?t=${new Date().getTime()}`);
          // Set the image source with a timestamp to avoid caching issues
          // 更新当前版本号并展示最新处理结果
          this.currentVersion = this.imageHistory.length - 1;
          this.imageSrc = this.imageHistory[this.currentVersion];

          // 将处理后的图片路径转换为 Blob 并更新 this.file
          await this.updateFileFromImageSrc(this.imageSrc);
        } else {
          alert("Image processing failed.");
        }
      } catch (error) {
        console.error("Error:", error);
        alert("An error occurred during image processing.");
      }
    },

    // 实时追踪鼠标位置并发送坐标到后端的函数
    async trackMouseMove(e) {
      // 使用节流函数减少请求频率
      const rect = this.canvas.getBoundingClientRect();

      // 计算缩放比例
      const scaleX = this.canvas.width / rect.width;
      const scaleY = this.canvas.height / rect.height;

      // 获取鼠标移动时的位置
      const x = (e.clientX - rect.left) * scaleX;
      const y = (e.clientY - rect.top) * scaleY;

      // 保存当前点的位置
      this.pointInfo = { x, y };

      // 清除画布并绘制标点
      this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
      this.drawPoint(x, y);

      if (
        !this.imageSrc.startsWith("data:image/") &&
        this.imageSrc.includes("/processed/")
      ) {
        // 如果是文件地址形式，将其转换为 Base64
        this.imageSrc = await this.convertImageToBase64(this.imageSrc);
      }
      let base64Data = this.imageSrc;
      if (this.imageSrc.includes(",")) {
        base64Data = this.imageSrc.split(",")[1]; // 去掉前缀
      } else {
        console.error("Invalid image source format");
        return; // 如果格式不对，停止执行
      }

      ///
      

      const formData = new FormData();
      formData.append("x", x);
      formData.append("y", y);
      formData.append("action", this.actionhuabi); // 传递给后端的操作类型
      formData.append("image_base64", base64Data);
      formData.append("version", this.imageHistory.length);
      if (this.actionhuabi=='mosaic'){
        formData.append("size", this.mosaicsize);
      }
      else if(this.actionhuabi=='mask'){
        formData.append("size", this.segsize);
      }
      else if(this.actionhuabi=='huahua'){
        formData.append("size", this.huabisize);
      }
      try {
        const response = await fetch("/processmosaic", {
          method: "POST",
          body: formData,
        });
        if (response.ok) {
          const data = await response.json();

          // 更新图像显示
          // Base64 编码的图像数据直接赋值给 imageSrc
          this.imageSrc = `data:image/jpeg;base64,${data.image_base64}`;
          console.error("Mosaic processing succes.");
        } else {
          console.error("Mosaic processing failed.");
        }
      } catch (error) {
        console.error("Error:", error);
      }
    },
    async convertImageToBase64(url) {
      try {
        const response = await fetch(url);
        const blob = await response.blob(); // 获取图片的 blob 数据
        return new Promise((resolve, reject) => {
          const reader = new FileReader();
          reader.onloadend = () => resolve(reader.result); // 读取完成后返回 Base64 字符串
          reader.onerror = reject;
          reader.readAsDataURL(blob); // 将 blob 转换为 Base64
        });
      } catch (error) {
        console.error("Error converting image to Base64:", error);
        throw error;
      }
    },

    async mosaicImage() {
      const formData = new FormData();

      if (
        !this.imageSrc.startsWith("data:image/") &&
        this.imageSrc.includes("/processed/")
      ) {
        // 如果是文件地址形式，将其转换为 Base64
        this.imageSrc = await this.convertImageToBase64(this.imageSrc);
      }
      let base64Data = this.imageSrc;
      if (this.imageSrc.includes(",")) {
        base64Data = this.imageSrc.split(",")[1]; // 去掉前缀
      } else {
        console.error("Invalid image source format");
        return; // 如果格式不对，停止执行
      }
      formData.append("image_base64", base64Data);
      formData.append("version", this.imageHistory.length); // 发送新的版本号
      formData.append("file", this.file);
      try {
        const response = await fetch("/okmosaic", {
          method: "POST",
          body: formData,
        });
        if (response.ok) {
          const data = await response.json();

          // 添加新处理的图片路径到栈
          this.imageHistory.push(`${data.filepath}?t=${new Date().getTime()}`);
          // Set the image source with a timestamp to avoid caching issues
          // 更新当前版本号并展示最新处理结果
          this.currentVersion = this.imageHistory.length - 1;
          this.imageSrc = this.imageHistory[this.currentVersion];

          // 将处理后的图片路径转换为 Blob 并更新 this.file
          await this.updateFileFromImageSrc(this.imageSrc);
        } else {
          alert("Image processing failed.");
        }
      } catch (error) {
        console.error("Error:", error);
        alert("An error occurred during image processing.");
      }
    },

    async maskImage() {
      const formData = new FormData();

      if (
        !this.imageSrc.startsWith("data:image/") &&
        this.imageSrc.includes("/processed/")
      ) {
        // 如果是文件地址形式，将其转换为 Base64
        this.imageSrc = await this.convertImageToBase64(this.imageSrc);
      }
      let base64Data = this.imageSrc;
      if (this.imageSrc.includes(",")) {
        base64Data = this.imageSrc.split(",")[1]; // 去掉前缀
      } else {
        console.error("Invalid image source format");
        return; // 如果格式不对，停止执行
      }
      ///
      if (
        !this.imageSrctemp.startsWith("data:image/") &&
        this.imageSrctemp.includes("/processed/")
      ) {
        // 如果是文件地址形式，将其转换为 Base64
        this.imageSrctemp = await this.convertImageToBase64(this.imageSrctemp);
      }
      let base64Data1 = this.imageSrctemp;
      if (this.imageSrctemp.includes(",")) {
        base64Data1 = this.imageSrctemp.split(",")[1]; // 去掉前缀
      } else {
        console.error("Invalid image source format");
        return; // 如果格式不对，停止执行
      }
      formData.append("image_base64", base64Data);
      formData.append("version", this.imageHistory.length); // 发送新的版本号
      formData.append("file", this.file);
      formData.append('image_base64_1',base64Data1);
      try {
        const response = await fetch("/okmask", {
          method: "POST",
          body: formData,
        });
        if (response.ok) {
          const data = await response.json();

          // 添加新处理的图片路径到栈
          this.imageHistory.push(`${data.filepath}?t=${new Date().getTime()}`);
          // Set the image source with a timestamp to avoid caching issues
          // 更新当前版本号并展示最新处理结果
          this.currentVersion = this.imageHistory.length - 1;
          this.imageSrc = this.imageHistory[this.currentVersion];

          // 将处理后的图片路径转换为 Blob 并更新 this.file
          await this.updateFileFromImageSrc(this.imageSrc);
        } else {
          alert("Image processing failed.");
        }
      } catch (error) {
        console.error("Error:", error);
        alert("An error occurred during image processing.");
      }
    },

    async sendmask() {
      const formData = new FormData();
      formData.append("file", this.file);
      try {
        const response = await fetch("/setmask", {
          method: "POST",
          body: formData,
        });
        if (response.ok) {
          console.error("Mosaic processing succes.");
        } else {
          console.error("Mosaic processing failed.");
        }
      } catch (error) {
        console.error("Error:", error);
      }
    },

    // 切换第一个共享区域的内容（浏览、马赛克、分隔等）
    setProcessSection(section) {
      // 检查是否点击了“浏览”按钮
      if (section === "browse") {
        this.$refs.folderInput.click(); // 触发隐藏的文件夹选择器
      }
      this.processSection = section;
      if (section == "area_mask") this.enableDrawRectListeners();
      if (section == "pinjie") this.openImage1();
      if (section == "tuodong")
      this.enableTuoListeners();
    },
    // 处理文件夹选择并加载所有图片
    // 加载文件夹图片到栈
    handleFolderChange(event) {
      const folder = event.target.files;
      this.imageHistory = [];
      this.filesHistory = [];
      this.currentVersion = 0;
      this.setupCanvas(); // 重置画布
      for (let i = 0; i < folder.length; i++) {
        const file = folder[i];
        if (file.type.match("image.*")) {
          const fileReader = new FileReader();
          fileReader.onload = (e) => {
            this.imageHistory.push(e.target.result); // 推入图片历史
            this.filesHistory.push(file); // 推入文件历史

            if (i === 0) {
              this.imageSrc = e.target.result;
              this.file = file; // 同步文件
            }
          };
          fileReader.readAsDataURL(file);
        }
      }
    },
    /// 推入历史栈
    pushToHistory(imageSrc, file) {
      this.imageHistory.push(imageSrc);
      this.filesHistory.push(file);
      this.currentVersion = this.imageHistory.length - 1; // 更新到最新的版本
    },

    // 上一页：切换到前一张图片
    async upPage() {
      if (this.currentVersion > 0) {
        this.currentVersion--; // 向前切换
        this.imageSrc = this.imageHistory[this.currentVersion]; // 获取上一张图片
        await this.updateFileFromImageSrc(this.imageSrc); // 更新文件
      }
    },

    // 下一页：切换到后一张图片
    async downPage() {
      if (this.currentVersion < this.imageHistory.length - 1) {
        this.currentVersion++; // 向后切换
        this.imageSrc = this.imageHistory[this.currentVersion]; // 获取下一张图片
        await this.updateFileFromImageSrc(this.imageSrc); // 更新文件
      }
    },

    // 保留的函数，控制第二个共享区域的内容（基本、滤镜、文字、水印等）
    setActiveSection(section) {
      this.activeSection = section;
    },
    async processImage(action) {
      //executeImageProcessing
      if (!this.file) {
        alert("Please upload an image first.");
        return;
      }

      const formData = new FormData();
      formData.append("file", this.file);
      formData.append("action", action);
      formData.append("version", this.imageHistory.length); // 发送新的版本号
      try {
        const response = await fetch("/process", {
          method: "POST",
          body: formData,
        });

        if (response.ok) {
          const data = await response.json();

          // 添加新处理的图片路径到栈
          this.imageHistory.push(`${data.filepath}?t=${new Date().getTime()}`);
          // Set the image source with a timestamp to avoid caching issues
          // 更新当前版本号并展示最新处理结果
          this.currentVersion = this.imageHistory.length - 1;
          this.imageSrc = this.imageHistory[this.currentVersion];

          // 将处理后的图片路径转换为 Blob 并更新 this.file
          await this.updateFileFromImageSrc(this.imageSrc);
        } else {
          alert("Image processing failed.");
        }
      } catch (error) {
        console.error("Error:", error);
        alert("An error occurred during image processing.");
      }
    },

    // 撤销图片操作
    async undoImage() {
      if (this.currentVersion > 0) {
        // 通过减少 currentVersion 来回退到上一个版本
        this.currentVersion--;
        this.imageSrc = this.imageHistory[this.currentVersion];
        const img = new Image();
          img.src = this.imageSrc;//////////////////////////////////////////////////////
          console.log("imgck");

          img.onload = () => {
          console.log(img.width);
          this.imageWidth = img.width;
          this.imageHeight = img.height;
          this.zeroHeight = img.height;
          this.zeroWidth = img.width;
          this.rotationPic=0;
          console.log("wi", this.imageWidth);
          console.log("hi:", this.imageHeight);
           };
        // 将回退的图片路径转换为 Blob 并更新 this.file
        await this.updateFileFromImageSrc(this.imageSrc);
      } else {
        alert("No more actions to undo.");
      }
    },

    // 恢复撤销操作的图片
    async redoImage() {
      if (this.currentVersion < this.imageHistory.length - 1) {
        // 增加 currentVersion 恢复到下一张图片
        this.currentVersion++;
        this.imageSrc = this.imageHistory[this.currentVersion];
        const img = new Image();
          img.src = this.imageSrc;//////////////////////////////////////////////////////
          console.log("imgck");

          img.onload = () => {
          console.log(img.width);
          this.imageWidth = img.width;
          this.imageHeight = img.height;
          this.zeroHeight = img.height;
          this.zeroWidth = img.width;
          this.rotationPic=0;
          console.log("wi", this.imageWidth);
          console.log("hi:", this.imageHeight);
           };
        // 将恢复的图片路径转换为 Blob 并更新 this.file
        await this.updateFileFromImageSrc(this.imageSrc);
      } else {
        alert("No more actions to redo.");
      }
    },

    // 从当前显示的图片路径更新 this.file
    async updateFileFromImageSrc(imageSrc) {
      try {
        const response = await fetch(imageSrc);
        const blob = await response.blob();

        // 从 Blob 的 MIME 类型获取文件扩展名
        const mimeType = blob.type;
        let extension = "";
        if (mimeType === "image/jpeg") {
          extension = "jpg";
        } else if (mimeType === "image/png") {
          extension = "png";
        } else if (mimeType === "image/gif") {
          extension = "gif";
        } else {
          // 如果是其他格式，默认使用原始格式
          extension = mimeType.split("/")[1];
        }

        // 使用正确的文件扩展名生成新的 File 对象
        this.file = new File(
          [blob],
          `image_v${this.currentVersion}.${extension}`,
          { type: mimeType }
        );
      } catch (error) {
        console.error("Error updating file from imageSrc:", error);
      }
    },

    saveImage() {
      if (!this.imageSrc) {
        alert("Please upload an image first.");
        return;
      }

      const link = document.createElement("a");
      link.href = this.imageSrc;
      link.download = "edited-image.png"; // 下载处理后的图片
      link.click();
    },
    moreOptions() {
      alert("More options functionality is not implemented yet.");
    },
    // 基本、滤镜、文字、水印按钮的功能，切换第二个共享区域的内容
    basic() {
      this.setActiveSection("basic");
    },
    filters() {
      this.setActiveSection("filters");
    },
    word() {
      this.setActiveSection("word");
    },
    reset() {
      this.setActiveSection("watermark");
    },
  },
});
