document.getElementById("submit-button").addEventListener("click", function (e) {
    // 获取表单中的内容
    var content = document.getElementById("content").value;

    // 判断内容是否为空
    if (content === "") {
        alert("请不要提交空的内容.");
        e.preventDefault();  // 阻止表单的提交
    } else {
        // 正常提交表单
    }
});



