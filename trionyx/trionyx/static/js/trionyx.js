function trionyxInitialize() {
    $('.select').select2({
        escapeMarkup: function(markup) {
            return markup;
        }
    });
    $('.selectmultiple').select2({
        escapeMarkup: function(markup) {
            return markup;
        }
    });
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
    window.trionyx_locale

    $('.summernote').summernote({
        lang: window.summernote_language,
        height: 200,
        dialogsInBody: true,
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

function randomString(length) {
   var result           = '';
   var characters       = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
   var charactersLength = characters.length;
   for ( var i = 0; i < length; i++ ) {
      result += characters.charAt(Math.floor(Math.random() * charactersLength));
   }
   return result;
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
            var ctrlDown = false;
            var ctrlKey = 17;
            var cmdKey = 91;
            $(document).keydown(function(e) {
                if (e.keyCode === ctrlKey || e.keyCode === cmdKey) ctrlDown = true;
            }).keyup(function(e) {
                if (e.keyCode === ctrlKey || e.keyCode === cmdKey) ctrlDown = false;
            });


            $(window).keypress(function (event) {
                var activeElement = $(document.activeElement);
                if (!ctrlDown && activeElement.is('body') && event.charCode > 0) {
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

/* Tasks */
function initTrionyxTasks(taskUrl) {
    return new Vue({
        el: '#trionyx-app-tasks',
        delimiters: ['[[', ']]'],
        data: {
            taskUrl: taskUrl,
            ajaxCall: null,

            tasks: [],
        },
        computed: {
            openTasks: function () {
                return this.tasks.reduce(function (value, task) {
                    if (task.status === 10 || task.status === 20 || task.status === 30 || task.status === 40) {
                        return value + 1;
                    }
                    return value;
                }, 0);
            }
        },
        methods: {
            getLabelClass(task) {
                if (task.status === 10) {
                    return 'label-warning';
                } else if (task.status === 50) {
                    return 'label-success';
                } else if (task.status === 99) {
                    return 'label-danger';
                }
                return 'label-info';
            },
            load: function() {
                var self = this;

                $.ajax({
                    type: 'GET',
                    url: this.taskUrl,
                }).done(function(response) {
                    if (response.status !== 'success') {
                        return;
                    }

                    self.tasks = response.data;
                    var timeout = 60;

                    var runningTasks = self.tasks.reduce(function (value, task) {
                        if (task.status === 20 || task.status === 30 || task.status === 40) {
                            return value + 1;
                        }

                        return value;
                    }, 0);

                    if (runningTasks > 0) {
                        timeout = 1;
                    }

                    setTimeout(function () {
                        self.load();
                    }, 1000 * timeout);
                });
            }
        },
        created: function() {
            this.load();
        },
    });
}

/* Dialog */
function openDialog(url, options) {
    new TrionyxDialog(url, options);
    return false;
};

function TrionyxDialog(url, options) {
    var self = this;
    self.url = url;
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
                self.url = data.url;
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
            $('<button type="button" class="btn btn-flat btn-default pull-left" data-dismiss="modal">' + window.trionyx_translations.close + '</button>')
        ).append(
            $('<img src="/static/img/spinners/spinner2.gif" style="display:none; margin-right: 10px" />')
        );

        if (data.submit_label) {
            footer.append(
                $('<input type="submit" class="btn btn-flat btn-success" value="' + data.submit_label + '"/>')
            );
        }
    };

    // Build dialog
    var dialogSizeClass = '';
    if ('size' in options && options.size === 'full') {
        dialogSizeClass = 'modal-full';
    } else if ('size' in options && options.size === 'extra-large') {
        dialogSizeClass = 'modal-xl';
    } else if ('size' in options && options.size === 'large') {
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
    if ('post' in options) {
       $.ajax({
            url: url,
            data: options.post,
            type: "POST",
        }).done(function(data){
            self.processResponse(data);
        });
    } else {
        $.get(url, function(response){
            self.processResponse(response);
        });
    }
};

/* Sidebar */
function openSidebar(url) {
    var $sidebar = $('#trionyx-control-sidebar');

    $.get(url, function(response){
        if (response.status !== 'success') {
            alert('Sidebar error');
            return;
        }

        var data = response.data;

        var theme = 'theme' in data ? data.theme : 'light';
        if (theme === 'light') {
            $sidebar.removeClass('control-sidebar-dark').addClass('control-sidebar-light');
        } else {
            $sidebar.removeClass('control-sidebar-light').addClass('control-sidebar-dark');
        }

        // Set actions
        var actions = 'actions' in data ? data.actions : [];
        var $actionsUl = $('#trionyx-sidebar-controls .dropdown-menu');
        $actionsUl.html('');
        $.each(actions, function (index, action) {
           var button = $("<a href='#'>" + action.label + "</a>");
           if ('class' in action) {
               button.addClass(action.class);
           }
           button.on('click', function () {
               if (action.dialog) {
                   var options = action.dialog_options;
                   if (action.reload) {
                       options.callback = function (data, dialog) {
                           if (data.success) {
                               openSidebar(url);
                               dialog.close();
                           }
                       }
                   }
                   openDialog(action.url, options);
               } else {
                   window.location.href = action.url;
               }
           });

           if ('divider' in action && action.divider) {
               $actionsUl.append($('<li class="divider"></li>'));
           }

           $actionsUl.append(
               $('<li></li>').append(button)
           );
        });

        if (actions.length > 0) {
            $('#trionyx-sidebar-controls .btn-group').removeClass('hide');
        } else {
            $('#trionyx-sidebar-controls .btn-group').addClass('hide');
        }


        // Set content
        $('#trionyx-sidebar-title').html('title' in data ? data.title : '');
        $('#trionyx-sidebar-top-content').html('fixed_content' in data ? data.fixed_content : '');
        $('#trionyx-sidebar-content').html('content' in data ? data.content : '');

        // fix content top margin
        var height = $('#trionyx-sidebar-top').height();
        $('#trionyx-sidebar-content').css('margin-top', height + 'px');
        $sidebar.css('padding-bottom', height  + 'px');

        if ('hover' in data && data.hover) {
            $sidebar.addClass('control-sidebar-open');
        } else {
            $('body').addClass('control-sidebar-open');
        }

        // Store active sidebar
        var activeSidebars = localStorage.getItem('trionyxActiveSidebar');
        activeSidebars = activeSidebars ? JSON.parse(activeSidebars) : {};
        activeSidebars[window.location.pathname] = url;
        localStorage.setItem("trionyxActiveSidebar", JSON.stringify(activeSidebars));
    });
}

function addActiveSidebar(path, url) {
    // Activate sidebar on other page before you go to that page
    var activeSidebars = localStorage.getItem('trionyxActiveSidebar');
    activeSidebars = activeSidebars ? JSON.parse(activeSidebars) : {};
    activeSidebars[path] = url;
    localStorage.setItem("trionyxActiveSidebar", JSON.stringify(activeSidebars));
}

function reloadSidebar(){
    var activeSidebars = localStorage.getItem('trionyxActiveSidebar');
    activeSidebars = activeSidebars ? JSON.parse(activeSidebars) : {};

    if (window.location.pathname in activeSidebars) {
       openSidebar(activeSidebars[window.location.pathname]);
   }
}

function closeSidebar() {
    $('#trionyx-sidebar-content').html('');
    $('#trionyx-control-sidebar').removeClass('control-sidebar-open');
    $('body').removeClass('control-sidebar-open');

    // Remove sidebar from active sidebars
    var activeSidebars = localStorage.getItem('trionyxActiveSidebar');
    activeSidebars = activeSidebars ? JSON.parse(activeSidebars) : {};
    delete activeSidebars[window.location.pathname];
    localStorage.setItem("trionyxActiveSidebar", JSON.stringify(activeSidebars));
}

$(function(){
   reloadSidebar();
});

/* layout */
function txUpdateLayout(id, component) {
    if (id in window.trionyx_layouts) {
        var url = window.trionyx_layouts[id] + '?layout_id=' + id;
        if (typeof component !== 'undefined' && component) {
            url += '&component=' + component;
        }

        $.get(url, function(response) {
            if (response.status === 'success') {
                var htmlId = '#' + id;
                if (typeof component !== 'undefined' && component) {
                    htmlId += ' #component-' + component;
                    var tempDiv = $('<div></div>').html(response.data);
                    $(htmlId).html($(tempDiv).find('#component-' + component).html());
                } else {
                    $(htmlId).html(response.data);
                }

                trionyxInitialize();
            }
        });
    }
}

/* Form depend */
function trionyxFormDepend(selector, dependencies) {
    function trionyxFormDependenciesChange() {
        var show = true;
        for (index in dependencies) {
            let dep = dependencies[index];
            show = show && $('#id_' + dep[0]).val().match(dep[1]);
        }
        if (show) {
            $(selector).slideDown();
        } else {
            $(selector).slideUp();
        }
    }

    for (index in dependencies) {
        $('#id_' + dependencies[index][0]).change(function () {
            trionyxFormDependenciesChange();
        });
    }
    trionyxFormDependenciesChange();
}