// создать подключение
var socket = null;
var nickname;

// отправить сообщение из формы publish
document.forms.publish.onsubmit = function() {
  var outgoingMessage = this.message.value;
  socket.send(outgoingMessage);
  return false;
};

// const connect = document.getElementById('connect');
// const disconnect = document.getElementById('disconnect');

const connect = $('#connect');
const disconnect = $('#disconnect');


connect.on('click', function(){
    start();
});

function start() {
    socket = new WebSocket("ws://localhost:8081");

    socket.onmessage = function(event) {
        var incomingMessage = event.data;
        showMessage(incomingMessage);
    };

    socket.onopen = authorizate;
}

function authorizate(){
    $("#subscribe").html("");
    nickname = $('#nickname').val();
    $('#nickname').css("display", "none");
    $('#subm').css("display", "inline-block");
    $("#message").css("display", "inline-block");
    disconnect.css("display", "inline-block");
    connect.css("display", "none");
    console.log(nickname);
    socket.send(nickname);
}

$(window).bind("unload" ,function() {
    socket.send("CLOSE");
});

disconnect.on('click', function(){
    socket.send("CLOSE");
    socket = null;
    //socket.close(1000, "User disconnected");
    connect.css("display", "inline-block");
    disconnect.css("display", 'none');
    $('#nickname').css("display", "inline-block");
    $('#subm').css("display", "none");
});

// показать сообщение в div#subscribe
function showMessage(message) {
    var messageElem = document.createElement('div');
    messageElem.appendChild(document.createTextNode(message));
    document.getElementById('subscribe').appendChild(messageElem);
}
