$.ajax({
    url: "{{ path }}",
    contentType: "application/json; charset=utf-8",
    dataType: "json",
    headers: {
        Authorization: 'Token <token>',
    },
    success: function (data) {
        $.each(data.results, function(index, item){
            console.log(item);
        });
    }
});