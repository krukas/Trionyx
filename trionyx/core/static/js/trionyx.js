$(function(){
    function fixHeader(transiton){
        var leftSize = '0px';

        var open = $('body').hasClass('sidebar-open');
        var windowWidth = $( window ).width();

        if (windowWidth >= 768) {
            var collapsed = $('body').hasClass('sidebar-collapse');
            leftSize = collapsed ? '50px' : '230px';
        } else {
            var open = $('body').hasClass('sidebar-open');
            sideBarSize = open ? '230px' : '0px';
        }

        $('.content-header-affix').css('left', leftSize);
    }
    fixHeader();

    $( window ).resize(function() {
        fixHeader();
    });

    $(document).on('expanded.pushMenu', function(e){
        fixHeader();

    });
    $(document).on('collapsed.pushMenu', function(e){
        fixHeader();
    });

    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!(/^(GET|HEAD|OPTIONS|TRACE)$/.test(settings.type)) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
            }
        }
    });
});

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function setCookie(cname, cvalue, exdays) {
    var d = new Date();
    d.setTime(d.getTime() + (exdays*24*60*60*1000));
    var expires = "expires="+d.toUTCString();
    document.cookie = cname + "=" + cvalue + "; " + expires + "; path=/";
}

