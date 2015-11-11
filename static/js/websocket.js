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
            var no_token = "no_auth_token_user bad_token";

            if (cookie_token) {
                resolve(cookie_token);
            } else {
                // If not found, ask the server for a new one
                $.ajax({
                    url: $SCRIPT_ROOT + "/socket_auth_token",
                    statusCode: {
                        // If we get a gateway error, it probably means nginx is being restarted.
                        // Not much we can do, other than wait a bit and continue with a
                        // fake token.
                        405: function() {
                            setTimeout(function() { resolve(no_token); }, 1000);
                        }
                    }})
                    .done(function(data) {
                        createCookie('auth_token', data);
                        resolve(data);
                    })
                    .fail(function() {
                        // Same situation as with 405.
                        setTimeout(function() { resolve(no_token); }, 1000);
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

        // Ignore heartbeat signals
        if (message === '<3') {
            return;
        }

        var data = JSON.parse(message);
        var id = data["id"];

        switch (id) {
        case "AUTH REQUEST":
            webSocketAuth();
            break;
        case "AUTH FAILED":
            eraseCookie('auth_token');
            break;
        case "AUTH OK":
            $("#connected").empty().append("Online");
            $("#authenticated").empty().append("Yes");
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
