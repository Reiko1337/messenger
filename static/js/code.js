let scrollHeight = Math.max(
    document.body.scrollHeight, document.documentElement.scrollHeight,
    document.body.offsetHeight, document.documentElement.offsetHeight,
    document.body.clientHeight, document.documentElement.clientHeight
);

setTimeout(() => {
    window.scrollTo(0, scrollHeight);
}, 100);

const roomName = JSON.parse(document.querySelector('#room-name').textContent);

const chatSocket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/messages/'
    + roomName
    + '/'
);


chatSocket.onmessage = function (e) {
    const data = JSON.parse(e.data);
    let helpText = document.querySelector('.help-text');
    if (helpText){
        helpText.style.display = 'none';
    }
    document.querySelector('.chat__content').innerHTML += `<div class="chat__message"><p class="chat__user">${ data.user }</p><p class="chat__msg">${ data.message }</p></div>`;
}

document.querySelector('#chat-message-input').focus();
document.querySelector('#chat-message-input').onkeyup = function (e) {
    if (e.keyCode === 13) {  // enter, return
        document.querySelector('#chat-message-submit').click();
    }
};

document.querySelector('#chat-message-submit').onclick = function (e) {
    const messageInputDom = document.querySelector('#chat-message-input');
    const message = messageInputDom.value;
    chatSocket.send(JSON.stringify({
        'message': message
    }));
    messageInputDom.value = '';
};
