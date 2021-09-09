const wsNotificationUp = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/notification/'
);

wsNotificationUp.onmessage = function (e) {
    const data = JSON.parse(e.data);
    const id = `#${data.room_slug}`;
    let chatRoom = document.querySelector(id);
    if (chatRoom) {
        document.querySelector(id).remove();
    }

    let htmlDialog = document.createElement('a');
    htmlDialog.className = 'dialog__link dialog__notification';
    htmlDialog.href = data.url;
    htmlDialog.id = data.room_slug;
    htmlDialog.innerHTML = data.html_dialog;

    document.querySelector('.dialog__content').prepend(htmlDialog);
}