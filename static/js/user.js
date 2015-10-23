function generateUserCookie() {
    var username = "test" +
        Math.floor(Math.random() * 9000) + 1000 + "@myservice.org";
    createCookie("username", username);

    return username;
}
