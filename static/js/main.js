function getfakelocation() {
    loc = decodeURIComponent(location.pathname)
    return loc.replace("/contents", "")
}

$(".itementry").click(function () {
    var clicked_dom = this;
    $.post("/queue/add",
           {path: getfakelocation() + $(this).find(".button-text").text()},
           function (data) {
               $(clicked_dom).find(".regular-icon").css("display", "inline-block");
               $(clicked_dom).find(".loading-icon").css("display", "none");
               var toast = new Toast();
               toast.show(data)
           })
})

$(".list-button").click(function () {
    $(this).find(".regular-icon").css("display", "none");
    $(this).find(".loading-icon").css("display", "inline-block");
})

var Toast = (function(){
    var timer;
    var speed;
    function Toast() {
        this.speed = 3000;
    }
    // メッセージを表示。表示時間(speed)はデフォルトで3秒
    Toast.prototype.show = function(message, speed) {
        if (speed === undefined) speed = this.speed;
        $('.toast').remove();
        clearTimeout(this.timer);
        $('body').append('<div class="toast">' + message + '</div>');
        var leftpos = $('body').width()/2 - $('.toast').outerWidth()/2;
        $('.toast').css('left', leftpos).hide().fadeIn('fast');

        this.timer = setTimeout(function(){
            $('.toast').fadeOut('slow',function(){
                $(this).remove();
            });
        }, speed);
    };
    return Toast;
})();
