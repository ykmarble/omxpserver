$(".playable").click(function () {
    $.post("/queue/add", {path: $(this).attr("href").slice(1)}, function (data) {
        alert(data)
    })
})
