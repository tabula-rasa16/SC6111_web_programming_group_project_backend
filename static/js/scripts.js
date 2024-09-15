$(document).ready(function () {
  // Handle login form submission
  $("#loginBtn").click(function (e) {
    e.preventDefault(); // Prevent form from submitting normally

    var username = $("#username").val();
    var password = $("#password").val();

    // Perform AJAX request to submit the login data
    $.ajax({
      type: "POST",
      url: "/users/login", // Backend login URL
      data: JSON.stringify({
        username: username,
        password: password,
      }),
      contentType: "application/json",
      success: function (response) {
        alert("Login successful!");
      },
      error: function (xhr, status, error) {
        alert("Login failed: " + xhr.responseText);
      },
    });
  });

  // Handle register button click
  $("#registerBtn").click(function () {
    var username = $("#username").val();
    var password = $("#password").val();

    // Perform AJAX request to submit the registration data
    $.ajax({
      type: "POST",
      url: "/users/register", // Backend register URL
      data: JSON.stringify({
        username: username,
        password: password,
      }),
      contentType: "application/json",
      success: function (response) {
        alert("Registration successful!");
      },
      error: function (xhr, status, error) {
        alert("Registration failed: " + xhr.responseText);
      },
    });
  });
});
