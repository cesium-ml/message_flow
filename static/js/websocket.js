function getTime() {
  var date = new Date();
  var n = date.toDateString();
  return date.toLocaleTimeString();
};

function webSocketAuth() {
    var auth_token = new Promise(
        function(resolve, reject) {
            // First, try and read the authentication token from a cookie
            var cookie_token = readCookie('auth_token');

            if (cookie_token) {
                resolve(cookie_token);
            } else {
                // If not found, ask the server for a new one
                $.get($SCRIPT_ROOT + "/socket_auth_token",
                      function(data) {
                          data = JSON.stringify(data);
                          createCookie('auth_token', data, 30);
                          resolve(data);
                      });
            }
        }
    );

    auth_token.then(
        function(token) {
            ws.send(token);
        });
};


function createSocket(url, messageHandler) {
    var ws = new ReconnectingWebSocket(url);

    ws.onopen = function (event) {
        $("#connected").empty().append("Online");
        $("#authenticated").empty().append("No");
    };

    ws.onmessage = function (event) {
        var message = event.data;
        var data = JSON.parse(message);
        var id = data["id"];

        switch (id) {
        case "AUTH REQUEST":
            webSocketAuth();
            break;
        case "AUTH OK":
            $("#connected").empty().append("Online");
            $("#authenticated").empty().append("Yes")
            break;
        default:
            messageHandler(data);
        }
    };

    ws.onclose = function (event) {
        $("#connected").empty().append("Offline");
        $("#authenticated").empty().append("No");
    };

    return ws;
};
