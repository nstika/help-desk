$(document).ready(function () {
  $("#postComment").on("click", function (e) {
    e.preventDefault();

    let data = new FormData();
    data.append("taskID", $(this).attr("taskID"));
    data.append("userID", $(this).attr("userID"));
    data.append("message", $("#comment_message").val());
    var url = "/project/manage_comments/0";
    if ($("#comment_message").val() == "") {
      Swal.fire("Error!!", "Please Type your message", "warning");
    } else {
      $.ajax({
        method: "POST",
        url: url,
        headers: { "X-CSRFToken": csrftoken },
        processData: false,
        contentType: false,
        data: data,
        async: true,
        success: function (response) {
          if (!response.isError) {
            location.reload();
          } else {
            Swal.fire("Something Wrong!!", response.Message, "error");
          }
        },
      });
    }
  });
});
