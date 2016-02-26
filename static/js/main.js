function getfakelocation() {
    loc = decodeURIComponent(location.pathname)
    return loc.replace("/contents", "")
}

$(".itementry").click(function () {
    $.post("/queue/add", {path: getfakelocation() + $(this).find(".button-text").text()}, function (data) {
        alert(data)
    })
})
