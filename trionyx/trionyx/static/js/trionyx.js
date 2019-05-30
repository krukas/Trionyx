function trionyxInitialize() {
    $('.select').select2();
    $('.selectmultiple').select2();
    $('.datetimepicker').each(function(index, input) {
        $(input).datetimepicker(getDataOptions(input, [
            'format',
            'locale',
            'dayViewHeaderFormat',
            'stepping',
            'minDate',
            'maxDate',
            'useCurrent',
            'defaultDate',
            'sideBySide',
            'viewMode',
            'toolbarPlacement',
            'showTodayButton',
            'showClear',
            'showClose',
        ]));
    });
};

function getDataOptions(node, validOptions) {
    var options = {};
    $.each($(node).data(), function(key, value) {
        if (validOptions.indexOf(key) >= 0) {
            options[key] = value;
        }
    });
    return options;
}

$(function(){
    function fixHeader(transiton){
        var leftSize = '0px';

        var open = $('body').hasClass('sidebar-open');
        var windowWidth = $( window ).width();

        if($('body').hasClass('sidebar-expanded-on-hover')) {
            leftSize = '230px';
        } else if (windowWidth >= 768) {
            var collapsed = $('body').hasClass('sidebar-collapse');
            leftSize = collapsed ? '50px' : '230px';
        } else {
            var open = $('body').hasClass('sidebar-open');
            leftSize = open ? '230px' : '0px';
        }


        $('.content-header-affix').css('left', leftSize);
    }
    fixHeader();

    $( window ).resize(function() {
        fixHeader();
    });

    $(document).on('expanded.pushMenu', function(e){
        setCookie('menu.state', 'expanded');
        fixHeader();
    });
    $(document).on('collapsed.pushMenu', function(e){
        setCookie('menu.state', 'collapsed');
        fixHeader();
    });
    $(document).on('pushMenu.hover', function(e){
        fixHeader();
    });

    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!(/^(GET|HEAD|OPTIONS|TRACE)$/.test(settings.type)) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
            }
        }
    });

    trionyxInitialize();
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

jQuery.extend({
    arrayCompare: function (a, b) {
        if (a === b) return true;
        if (a == null || b == null) return false;
        if (a.length != b.length) return false;

        for (var i = 0; i < a.length; ++i) {
            if (a[i] !== b[i]) {
                return false;
            }
        }
        return true;
    },
    arrayUnique: function(a) {
        return a.reduce(function(p, c) {
            if (p.indexOf(c) < 0) p.push(c);
            return p;
        }, []);
    }
});


/* Global search */
function initGlobalSearch(searchUrl) {
    return new Vue({
        el: '#trionyx-global-search-app',
        delimiters: ['[[', ']]'],
        data: {
            searchUrl: searchUrl,
            search: '',
            show: false,
            ajaxCall: null,

            results: [],
        },
        watch: {
            search: function(search) {
                var self = this;
                if (this.ajaxCall) {
                    this.ajaxCall.abort();
                }

                if (!search) {
                    this.results = [];
                    return;
                }

                this.ajaxCall = $.ajax({
                    type: 'GET',
                    url: this.searchUrl + '?search=' + this.search,
                }).done(function(response) {
                    if (response.status !== 'success') {
                        return;
                    }

                    self.results = response.data;
                }).always(function () {
                    self.ajaxCall = null;
                });
            }
        },
        methods: {
            close: function(){
              this.search = '';
              this.show = false;
            },
            open: function(){
                this.show = true;
            },
            itemClick: function(url){
                window.location.href = url;
            }
        },
        created: function() {
            var self = this;
            $(window).keypress(function (event) {
                var activeElement = $(document.activeElement);
                if (activeElement.is('body') && event.charCode > 0) {
                    self.show = true;
                    self.search += String.fromCharCode(event.charCode);
                }
            });

            $(window).keydown(function(event){
                event = event ? event : window.event;
                var activeElement = $(document.activeElement);

                if (self.show && event.keyCode === 27) {
                    self.search = ''
                    self.show = false;
                } else if (self.show && self.search && activeElement.is('body') && event.keyCode ===  8) {
                    self.search = self.search.slice(0, -1);
                } else if (self.show && !self.search && event.keyCode == 8) {
                    self.search = '';
                    self.show = false;
                }
            });
        }
    });
}

/* Dialog */
function openDialog(url, options) {
    new TrionyxDialog(url, options);
    return false;
};

function TrionyxDialog(url, options) {
    var self = this;
    options = typeof options !== 'undefined' ? options : {};
    var dialog = $('<div class="modal fade" data-backdrop="static" data-keyboard="false">');
    var form = $('<form method="POST" enctype="multipart/form-data" novalidate>');
    var title = $('<h4 class="modal-title">');
    var body = $('<div class="modal-body">');
    var footer = $('<div class="modal-footer">');

    $(dialog).on('hidden.bs.modal', function () {
        dialog.remove();
    });

    $(dialog).on('shown.bs.modal', function () {
        trionyxInitialize();
    });

    self.close = function(){
        dialog.modal('hide');
    };

    form.submit(function (event) {
        event.preventDefault();
        footer.find('img').css('display', 'inline-block');

        $.ajax({
            url: $(this).attr('action'),
            data: new FormData(form[0]),
            processData: false,
            contentType: false,
            type: "POST",
        }).done(function(data){
            self.processResponse(data);
        });
    });

    self.processResponse = function(data){
        /* Set default values when not set */
        data.title = 'title' in data ? data.title : '';
        data.content = 'content' in data ? data.content : '';
        data.submit_label = 'submit_label' in data ? data.submit_label : '';
        data.redirect_url=  'redirect_url' in data ? data.redirect_url : '';
        data.url = 'url' in data ? data.url : '';
        data.close = 'close' in data ? data.close : false;


        if(data.close){
            dialog.modal('hide');
        } else if(data.redirect_url != '') {
            window.location.href = data.redirect_url;
        } else {
            if (data.url) {
                form.attr('action', data.url);
            }

            self.setTitle(data);
            self.setBody(data);
            self.setFooter(data);
            trionyxInitialize();

            if ('callback' in options) {
                options.callback(data, self);
            }
        }
    };

    self.setTitle = function(data) {
        title.html(data.title);
    };

    self.setBody = function(data){
        body.html(data.content);
    };

    self.setFooter = function(data){
        footer.html('');
        footer.append(
            $('<button type="button" class="btn btn-default pull-left" data-dismiss="modal">Close</button>')
        ).append(
            $('<img src="/static/img/spinners/spinner2.gif" style="display:none; margin-right: 10px" />')
        );

        if (data.submit_label) {
            footer.append(
                $('<input type="submit" class="btn btn-success" value="' + data.submit_label + '"/>')
            );
        }
    };

    // Build dialog
    var dialogSizeClass = '';
    if ('size' in options && options.size === 'large') {
        dialogSizeClass = 'modal-lg';
    } else if ('size' in options && options.size === 'small') {
        dialogSizeClass = 'modal-sm';
    }

    dialog.append(
        $('<div class="modal-dialog ' + dialogSizeClass + '">').append(
            $('<div class="modal-content">').append(
                form.append(
                    $('<div class="modal-header">').append(
                        $('<button type="button" class="close" data-dismiss="modal" aria-label="Close">').append(
                            $('<span aria-hidden="true">&times;</span>')
                        )
                    ).append(
                        title
                    )
                ).append(
                    body.append(
                        $("<img src='/static/img/grid-loader.svg' style='position:relative;left: 50%;margin-left: -20px;padding: 20px 0px; width: 40px' />")
                    )
                ).append(
                    footer
                )
            )
        )
    );

    // Append dialog
    $('body').append(dialog);
    $(dialog).modal('show');

    // Load dialog
    $.get(url, function(response){
        self.processResponse(response);
    });
};