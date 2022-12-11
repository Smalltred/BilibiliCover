function downloadImage(url) {
    // 获取图片的文件名
    var filename = url.split('/').pop();
    // 创建一个 XMLHttpRequest 对象
    var xhr = new XMLHttpRequest();
    // 设置请求的方法、URL 以及是否异步处理请求
    xhr.open('GET', url, true);
    // 设置响应类型为二进制数据
    xhr.responseType = 'blob';
    // 发送请求
    xhr.send();

    // 监听请求状态的变化
    xhr.onreadystatechange = function () {
        // 如果请求完成且响应就绪
        if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
            // 获取响应的二进制数据
            var blob = xhr.response;
            // 创建一个新的 URL 对象
            var url = URL.createObjectURL(blob);
            // 创建一个链接元素
            var link = document.createElement('a');
            // 设置链接的 href 属性
            link.href = url;
            // 设置链接的下载属性
            link.download = filename;
            // 设置链接的隐藏样式
            link.style = 'display: none';
            // 模拟点击链接
            link.click();
        }
    }
}