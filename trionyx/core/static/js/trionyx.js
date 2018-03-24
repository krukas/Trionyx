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

        $('.content-header-wrapper').css('left', leftSize);
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
});

