$(".playable").click(function () {
    $.post("/queue/add", {path: $(this).attr("href").slice(1)})
})
