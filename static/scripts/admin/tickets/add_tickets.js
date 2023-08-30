$(document).ready(function () {
  GetAllCategory();

  let Image = "";
  $("#Image").on("change", function (e) {
    Image = e.target.files[0];
  });
  $("#Save").on("click", function (e) {
    e.preventDefault();
    let formData = new FormData();
    let title = $("#ticket_title").val();
    let client = $("#ticket_client").attr("userID");
    let category = $("#Category").val();
    let priority = $("#Priority").val();
    let description = $("#description").val();

    formData.append("title", title);
    formData.append("userid", client);
    formData.append("category", category);
    formData.append("priority", priority);
    formData.append("descrption", description);
    formData.append("ticket_image", Image);
    formData.append("Type", "AddTicket");
    if (title == "") {
      Swal.fire("Error!!", "Please Enter Title", "error");
    } else if (client == "") {
      Swal.fire("Error!!", "Please Enter Client", "error");
    } else if (priority == "") {
      Swal.fire("Error!!", "Please Select Priority", "error");
    } else if (category == "") {
      Swal.fire("Error!!", "Please Select Category", "error");
    } else if (description == "") {
      Swal.fire("Error!!", "Please Select Description", "error");
    } else {
      Swal.fire({
        title: "Are you sure to save?",
        text: "make sure",
        icon: "warning",
        showCancelButton: !0,
        confirmButtonColor: "#2ab57d",
        cancelButtonColor: "#fd625e",
        confirmButtonText: "Yes, save it!",
      }).then(function (e) {
        if (e.value) {
          $.ajax({
            method: "POST",
            url: BASE_URL + "tickets/manage_tickets/" + "0",
            headers: { "X-CSRFToken": csrftoken },
            processData: false,
            contentType: false,
            data: formData,
            async: true,
            success: function (response) {
              if (!response.isError) {
                Swal.fire({
                  title: "Successfully!!!",
                  text: response.Message,
                  icon: "success",
                  confirmButtonText: "Ok!!",
                  confirmButtonClass: "btn btn-success mt-2",
                  buttonsStyling: !1,
                }).then(function (e) {
                  if (e.value) {
                    Swal.DismissReason.cancel;
                    location.reload();
                  }
                });
              } else {
                Swal.fire("Something Wrong!!", response.Message, "error");
              }
            },
            error: function (response) {},
          });
        }
      });
    }
  });

  function GetAllCategory() {
    var rows = "";
    let formData = new FormData();
    formData.append("Type", "get_all_categories");
    formData.append("Category", "Ticket");
    $.ajax({
      method: "POST",
      url: BASE_URL + "users/get_users_links",
      processData: false,
      contentType: false,
      data: formData,
      headers: { "X-CSRFToken": csrftoken },
      async: false,
      success: function (response) {
        rows = response.Message;
      },
      error: function (response) {},
    });

    var dataRow = "";
    if (rows.length > 0) {
      dataRow += `<option value=''>Select Category</option>`;
      for (var i = 0; i < rows.length; i++) {
        dataRow +=
          `
                  <option value='` +
          rows[i].id +
          `'>` +
          rows[i].name +
          `</option>
                  `;
      }
      $("#Category").html(dataRow);
    }
  }

  $("#ticket_client").on("click", function (e) {
    document.getElementById("searchEngineInput").focus();
    $(this).val("");
    $("#searchModal").modal("show");
  });

  $(".users-body .list").on("click", ".item", function () {
    $("#ticket_client").val(
      $(this).attr("username") +
        " - " +
        $(this).attr("name") +
        " (" +
        $(this).attr("type") +
        ")"
    );
    $("#ticket_client").attr("username", $(this).attr("username"));
    $("#ticket_client").attr("userID", $(this).attr("userid"));
    $("#searchModal").modal("hide");
  });

  $("#searchEngineInput").on("input", function () {
    $(".users-body .list").html("");
  });

  $("#SearchBTN").click(function (e) {
    e.preventDefault();
    if ($("#searchEngineInput").val() != "") {
      SearchEngine($("#searchEngineInput").val());
    } else {
      Swal.fire("Warning", "Type your search", "warning");
    }
  });

  function SearchEngine(letter) {
    $.ajax({
      method: "GET",
      url: BASE_URL + "users/search_engine/" + letter + "/" + "CL",
      async: false,
      headers: { "X-CSRFToken": csrftoken },
      success: function (data) {
        $(".users-body .list").html("");
        data.Message.forEach((user) => {
          $(".users-body .list").append(`
            <div class="col-md-12 item" type = ${user.Type} name='${user.Name}' username=${user.Username} userid = ${user.ID}>
            <div class="row">
                <div class="col-md-12">
                    <h5 id="userName">${user.Username} - ${user.Name} - (${user.Type})</h5>
                </div>
                <div class="col-md-12">
                    <p class="userEmail">${user.Email}</p>
                </div>
                <div class="col-md-12" style="margin-bottom:10px;">
                    <p class="userPhone">${user.Phone}</p>
                </div>
            </div>
        </div>
          `);
        });

        if (data.Message.length == 0) {
          $(".users-body .list").html("No users matched the search...");
        }
      },
    });
  }
});
