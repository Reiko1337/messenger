const roomSlug = JSON.parse(document.querySelector('#room-slug').textContent);
const contentType = JSON.parse(document.querySelector('#content-type').textContent);

const wsSendMessage = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/messages/'
    + contentType
    + '/'
    + roomSlug
    + '/'
)


let sendInput = document.querySelector('#send-message__input');
let sendButton = document.querySelector('#send-message__button');

sendInput.focus();

sendInput.onkeyup = function (e) {
    if (e.keyCode === 13) {
        sendButton.click();
    }
};

sendButton.onclick = function (e) {
    const message = sendInput.value;
    wsSendMessage.send(JSON.stringify({
        'message': message
    }));
    sendInput.value = '';
};

wsSendMessage.onmessage = function (e) {
    const data = JSON.parse(e.data);
    document.querySelector('.chat-room').innerHTML += data.html_message;
    let helpText = document.querySelector('.help-text');
    if (helpText) {
        helpText.style.display = 'none';
    }
}


wsSendMessage.onclose = function (event) {
    if (!event.wasClean) {
        alert('Обрыв соединения.');
    }
};
