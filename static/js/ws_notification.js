const wsNotification = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/notification/'
);

let url = new URL(document.URL)
let urlPathname = url.pathname.split('/').slice(1, -1);

wsNotification.onmessage = function (e) {
    const data = JSON.parse(e.data);
    console.log(data.room_slug);
    console.log(urlPathname);
    if (data.room_slug != urlPathname[2]) {
        document.querySelector('.notification').innerHTML = data.html_notification;
        let notification = document.querySelector('.notification__container');
        document.querySelector('.notification__close').addEventListener('click', function () {
            notification.style.display = 'none';
        })
    }
}

let notificationClose = document.querySelectorAll('.notification__close');

for (let index = 0; index < notificationClose.length; index++) {
    notificationClose[index].addEventListener('click', function () {
        notificationClose[index].parentElement.style.display = 'none';
    });
}


