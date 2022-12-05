const request = new XMLHttpRequest();
const url = document.getElementById("image").src;
request.open("GET", url, true);
request.responseType = 'blob';
request.onload = function () {
    const url = window.URL.createObjectURL(request.response);
    const a = document.getElementById("download");
    a.href = url
    a.download = ''
}
request.send();