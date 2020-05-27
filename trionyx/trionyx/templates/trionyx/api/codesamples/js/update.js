$.ajax({
    url: "{{ path }}",
    type: 'PUT',
    data: JSON.stringify({
        /* Item data */
    }),
    contentType: "application/json; charset=utf-8",
    dataType: "json",
    headers: {
        Authorization: 'Token <token>',
    },
    success: function (item) {
        console.log(item);
    },
});