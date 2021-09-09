let requestUrl = '/friends/search/';

$('.friends__search-input').change(function (e) {
    $.ajax({
        url: requestUrl,
        data: {
            'q': $(this).val()
        },
        success: function (data) {
            $('.friends__list').html(data.htmlFriendsData);
            $('.friends__global-list').html(data.htmlFriendsGlobalData);
        }
    });
})



