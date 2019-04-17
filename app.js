// создать подключение
var socket = new WebSocket("ws://localhost:8081");
var nickname;

// отправить сообщение из формы publish
document.forms.publish.onsubmit = function() {
  var outgoingMessage = this.message.value;
  socket.send(outgoingMessage);
  return false;
};

const connect = document.getElementById('connect');
const disconnect = document.getElementById('disconnect');

connect.addEventListener('click', function(){
    nickname = document.getElementById('nickname').value;
    document.getElementById('nickname').style.display = "none";
    document.getElementById('subm').style.display = "inline-block";
    disconnect.style.display = "inline-block";
    connect.style.display = "none";
    console.log(nickname);
    socket.send(nickname);
});

disconnect.addEventListener('click', function(){
    socket.close(1000, "User disconnected");
    connect.style.display = "inline-block"
    disconnect.style.display = 'none';
    document.getElementById('nickname').style.display = "inline-block";
    document.getElementById('subm').style.display = "none";
});

socket.onmessage = function(event) {
    var incomingMessage = event.data;
    showMessage(incomingMessage);
};

// показать сообщение в div#subscribe
function showMessage(message) {
  var messageElem = document.createElement('div');
  messageElem.appendChild(document.createTextNode(message));
  document.getElementById('subscribe').appendChild(messageElem);
}