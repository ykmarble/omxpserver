function getfakelocation() {
    loc = decodeURIComponent(location.pathname);
    return loc.replace("/contents", "");
}

function revert_loading_icon(dom) {
    $(dom).find(".regular-icon").css("display", "inline-block");
    $(dom).find(".loading-icon").css("display", "none");
}

$(".playable").click(function () {
    var clicked_dom = this;
    $.post("/queue/add",
           {path: getfakelocation() + $(this).find(".button-text").text()},
           function (data) {
               revert_loading_icon(clicked_dom);
               var toast = new Toast();
               toast.show(data);
           });
});

$(".add-all-entry").click(function () {
    var clicked_dom = this;
    var playlist = $(this).nextAll(".playable");
    var num_of_medium = playlist.length;
    playlist.each(function (index) {
        $.post("/queue/add",
               {path: getfakelocation() + $(this).find(".button-text").text()},
               function(data) {
                   var toast = new Toast();
                   toast.show(data);
                   if (index+1 == num_of_medium) {
                       revert_loading_icon(clicked_dom);
                   }
               });
    });
})

$(".has-loading-icon").click(function () {
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
