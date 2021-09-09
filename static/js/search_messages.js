let requestUrl = '/messages/search/';

$('.dialog__search-input').change(function (e) {
    $.ajax({
        url: requestUrl,
        data: {
            'q': $(this).val()
        },
        success: function (data) {
            $('.dialog__content').html(data.htmlData);
        }
    });
})



