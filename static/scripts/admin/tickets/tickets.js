$(document).ready(function () {
  // Update The Entries Selection
  $("#DataNumber").val($("#DataNumber").attr("DataNumber"));
  $("#FilterStatus").val($("#FilterStatus").attr("FilterStatus"));


 
  GetAllCategory();

  $("#DataNumber").change(function () {
    RefreshPage();
  });

  $("#SearchQuery").on("change", function () {
    RefreshPage();
  });

  $("#SearchQueryBTN").on("click", function () {
    RefreshPage();
  });

  $(".pagination .page-item").on("click", function () {
    const pageNumber = $(this).attr("page");
    $(".activePage").attr("activePage", pageNumber);
    RefreshPage();
  });

  $("#FilterStatus").change(function () {
    RefreshPage();
  });

  function RefreshPage() {
    let page = $(".activePage").attr("activePage");
    let search = $("#SearchQuery").val();
    let entries = $("#DataNumber").val();
    let FilterStatus = $("#FilterStatus").val();

    window.location.replace(
      BASE_URL +
      `tickets/tickets?DataNumber=${entries}&SearchQuery=${search}&page=${page}&FilterStatus=${FilterStatus}`
    );
  }

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

  $("#client").on("click", function (e) {
    document.getElementById("searchEngineInput").focus();
    // $(this).val("");
    $("#searchModal").modal("show");
  });

  $(".users-body .list").on("click", ".item", function () {
    $("#client").val(
      $(this).attr("username") +
        " - " +
        $(this).attr("name") +
        " (" +
        $(this).attr("type") +
        ")"
    );
    $("#client").attr("username", $(this).attr("username"));
    $("#client").attr("userID", $(this).attr("userid"));
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

  $("#tickets_table tbody").on("click", ".edit-ticket", function (e) {
    e.preventDefault();
   
    const id = $(this).attr("ticketid");

    $.ajax({
      method: "GET",
      url: BASE_URL + "tickets/manage_tickets/" + id,
      headers: { "X-CSRFToken": csrftoken },
      async: true,
      success: function (response) {
        if (!response.isError) {
          $("#ticketModal").modal("show");
          $("#ticketID").val(response.Message.id);
          $("#title").val(response.Message.title);
          $("#client").val(response.Message.client);
          $("#Category").val(response.Message.category);
          $("#ticket_priority").val(response.Message.priority);
          $("#ticket_description").val(response.Message.description);

          $("#client").val(
            response.Message.client.username +
              " - " +
              response.Message.client.name +
              " (Client)"
          );
          $("#client").attr("username", response.Message.client.username);
          $("#client").attr("userID", response.Message.client.id);
        } else {
          Swal.fire({
            title: "Something Wrong!!",
            text: response.Message,
            icon: "error",
            confirmButtonClass: "btn btn-primary w-xs mt-2",
            buttonsStyling: !1,
            showCloseButton: !0,
          });
        }
      },
      error: function (response) {},
    });
  });

  $("#tickets_table tbody").on("click", ".delete-ticket", function () {
    const id = $(this).attr("id");
    Swal.fire({
      title: "Are you sure?",
      text: "You won't be able to get it after!",
      icon: "warning",
      showCancelButton: !0,
      confirmButtonColor: "#2ab57d",
      cancelButtonColor: "#fd625e",
      confirmButtonText: "Yes, delete it!",
    }).then(function (e) {
      if (e.value) {
        $.ajax({
          method: "DELETE",
          url: BASE_URL + "tickets/manage_tickets/" + id,
          headers: { "X-CSRFToken": csrftoken },
          async: false,
          success: function (data) {
            if (!data.isError) {
              Swal.fire("Deleted!", data.Message, "success").then((e) => {
                e.value && RefreshPage();
              });
              GetAllPositions();
            } else {
              Swal.fire("Something Wrong!!", data.Message, "error");
            }
          },
          error: function (error) {
            //(error);
          },
        });
      }
    });
  });

  $("#change_ticket").on("click", function (e) {
    e.preventDefault();
    let formData = new FormData();
    let id = $("#ticketID").val();
    let title = $("#title").val();
    let client = $("#client").attr("userID");
    let category = $("#Category").val();
    let priority = $("#ticket_priority").val();
    let description = $("#ticket_description").val();
    formData.append("title", title);
    formData.append("userid", client);
    formData.append("category", category);
    formData.append("priority", priority);
    formData.append("description", description);
    formData.append("Type", "change");
    if (title == "") {
      Swal.fire("Error!!", "Please Enter Title", "error");
    } else if (client == "") {
      Swal.fire("Error!!", "Please Enter Client", "error");
    } else if (category == "") {
      Swal.fire("Error!!", "Please Select Category", "error");
    } else if (priority == "") {
      Swal.fire("Error!!", "Please Select Priority", "error");
    } else if (description == "") {
      Swal.fire("Error!!", "Please Enter description", "error");
    } else {
      $.ajax({
        method: "POST",
        url: BASE_URL + "tickets/manage_tickets/" + id,
        headers: { "X-CSRFToken": csrftoken },
        processData: false,
        contentType: false,
        data: formData,
        async: true,
        success: function (response) {
          $("#customerModal").modal("hide");
          if (!response.isError) {
            Swal.fire({
              title: "Successfully",
              text: response.Message,
              icon: "success",
              confirmButtonClass: "btn btn-primary w-xs mt-2",
              buttonsStyling: !1,
              showCloseButton: !0,
            }).then((e) => {
              e.value && RefreshPage();
            });
          } else {
            Swal.fire({
              title: "Something Wrong!!",
              text: response.Message,
              icon: "error",
              confirmButtonClass: "btn btn-primary w-xs mt-2",
              buttonsStyling: !1,
              showCloseButton: !0,
            });
          }
        },
        error: function (response) {},
      });
    }
  });

  $("#postComment").on("click", function (e) {
    e.preventDefault();

    let data = new FormData();
    data.append("ticketID", $(this).attr("ticketID"));
    data.append("userID", $(this).attr("userID"));
    data.append("message", $("#comment_message").val());
    var url = "/tickets/manage_replies/0";
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
