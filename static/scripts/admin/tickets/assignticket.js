$(document).ready(function () {
  $("#staffID").on("click", function (e) {
    $("#table").attr("hidden", true);
    document.getElementById("searchEngineInput").focus();
    $(this).val("");
    $("#searchModal").modal("show");
  });

  $(".users-body .list").on("click", ".item", function () {
    $("#staffID").val(
      $(this).attr("username") +
        " - " +
        $(this).attr("name") +
        " (" +
        $(this).attr("type") +
        ")"
    );
    $("#staffID").attr("userID", $(this).attr("userid"));
    $("#searchModal").modal("hide");
  });

  $("#searchEngineInput").on("input", function () {
    $(".users-body .list").html("");
  });
  $("#SearchBTN").click(function () {
    if ($("#searchEngineInput").val() != "") {
      SearchEngine($("#searchEngineInput").val());
    } else {
      Swal.fire("Warning", "Type your search", "warning");
    }
  });

  function SearchEngine(letter) {
    $.ajax({
      method: "GET",
      url: BASE_URL + "users/search_engine/" + letter + "/" + "AG",
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

  $("#save_changes").on("click", function (e) {
    e.preventDefault();

    let ticketID = $("#ticketID").val();

    let Agent = $("#staffID").attr("userID");
    let formData = new FormData();
    formData.append("user", Agent);
    formData.append("ticket", ticketID);
    if (Agent == "") {
      Swal.fire("Error!!", "This feild is required", "error");
    } else {
      $.ajax({
        method: "POST",
        url: BASE_URL + "tickets/assign_tickets/" + 0,
        headers: { "X-CSRFToken": csrftoken },
        processData: false,
        contentType: false,
        data: formData,
        async: true,
        success: function (response) {
          if (!response.isError) {
            $("#AssignTicket").modal("hide");

            Swal.fire({
              title: "Successfully!!!!!",
              text: response.Message,
              icon: "success",
              confirmButtonColor: "#2ab57d",
              cancelButtonColor: "#fd625e",
              confirmButtonText: "Ok!",
            }).then(function (e) {
              if (e.value) {
                window.location.reload();
              }
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

  $(".btnstatus").on("click", function () {
    $("#StatusName").val($("#t-status").text());
    $("#Status").modal("show");
  });
  $(".btnpriority").on("click", function () {
    $("#PriorityName").val($("#t-priority").text());
    $("#Priority").modal("show");
  });
  $("#AsignAgent").on("click", function () {
    $("#AssignTicket").modal("show");
  });

  $("#tickets_table").on("click", ".assign_ticket", function () {
    const ID = $(this).attr("id");
    window.location.replace(BASE_URL + "tickets/view_tickets/" + ID);
  });

  $(".Row").on("click", ".Delete", function () {
    const ID = $(this).attr("id");
    Swal.fire({
      title: "Are you sure?",
      text: "You won't be able to get it after!",
      icon: "warning",
      showCancelButton: !0,
      confirmButtonColor: "#2ab57d",
      cancelButtonColor: "#fd625e",
      confirmButtonText: "Yes, remove it!",
    }).then(function (e) {
      if (e.value) {
        $.ajax({
          method: "DELETE",
          url: BASE_URL + "tickets/assign_tickets/" + ID,
          headers: { "X-CSRFToken": csrftoken },
          async: false,
          success: function (data) {
            if (!data.isError) {
              Swal.fire({
                title: "Successfully!!!!!",
                text: data.Message,
                icon: "success",
                confirmButtonColor: "#2ab57d",
                cancelButtonColor: "#fd625e",
                confirmButtonText: "Ok it!",
              }).then(function (e) {
                if (e.value) {
                  window.location.reload();
                }
              });
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

  $("#save_status").on("click", function (e) {
    e.preventDefault();
    let formData = new FormData();
    const ID = $("#ticketID").val();
    let status = $("#StatusName").val();
    formData.append("status", status);
    formData.append("Type", "Changestatus");
    Swal.fire({
      title: "Are you sure",
      text: "to Change ?",
      icon: "warning",
      showCancelButton: !0,
      confirmButtonColor: "#2ab57d",
      cancelButtonColor: "#fd625e",
      confirmButtonText: "Yes, change it!",
    }).then(function (e) {
      if (e.value) {
        $.ajax({
          method: "POST",
          url: BASE_URL + "tickets/manage_tickets/" + ID,
          headers: { "X-CSRFToken": csrftoken },
          processData: false,
          contentType: false,
          data: formData,
          async: true,
          success: function (data) {
            if (!data.isError) {
              Swal.fire({
                title: "Successfully!!!!!",
                text: data.Message,
                icon: "success",
                confirmButtonColor: "#2ab57d",
                cancelButtonColor: "#fd625e",
                confirmButtonText: "Ok it!",
              }).then(function (e) {
                if (e.value) {
                  window.location.reload();
                }
              });
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

  $("#client_reopen").on("click", function (e) {
    e.preventDefault();
    let formData = new FormData();
    const ID = $("#ticketID").val();
    formData.append("Type", "ClientReopen");
    Swal.fire({
      title: "Are you sure",
      text: "to Change ?",
      icon: "warning",
      showCancelButton: !0,
      confirmButtonColor: "#2ab57d",
      cancelButtonColor: "#fd625e",
      confirmButtonText: "Yes, change it!",
    }).then(function (e) {
      if (e.value) {
        $.ajax({
          method: "POST",
          url: BASE_URL + "tickets/manage_tickets/" + ID,
          headers: { "X-CSRFToken": csrftoken },
          processData: false,
          contentType: false,
          data: formData,
          async: true,
          success: function (data) {
            if (!data.isError) {
              Swal.fire({
                title: "Successfully!!!!!",
                text: data.Message,
                icon: "success",
                confirmButtonColor: "#2ab57d",
                cancelButtonColor: "#fd625e",
                confirmButtonText: "Ok it!",
              }).then(function (e) {
                if (e.value) {
                  window.location.reload();
                }
              });
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

  $("#save_priority").on("click", function (e) {
    e.preventDefault();
    let formData = new FormData();
    const ID = $("#ticketID").val();
    let priority = $("#PriorityName").val();
    formData.append("priority", priority);
    formData.append("Type", "Changepriority");
    Swal.fire({
      title: "Are you sure",
      text: "to Change ?",
      icon: "warning",
      showCancelButton: !0,
      confirmButtonColor: "#2ab57d",
      cancelButtonColor: "#fd625e",
      confirmButtonText: "Yes, change it!",
    }).then(function (e) {
      if (e.value) {
        $.ajax({
          method: "POST",
          url: BASE_URL + "tickets/manage_tickets/" + ID,
          headers: { "X-CSRFToken": csrftoken },
          processData: false,
          contentType: false,
          data: formData,
          async: true,
          success: function (data) {
            if (!data.isError) {
              Swal.fire({
                title: "Successfully!!!!!",
                text: data.Message,
                icon: "success",
                confirmButtonColor: "#2ab57d",
                cancelButtonColor: "#fd625e",
                confirmButtonText: "Ok it!",
              }).then(function (e) {
                if (e.value) {
                  window.location.reload();
                }
              });
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
  $("#Accepts").on("click", function (e) {
    e.preventDefault();
    let formData = new FormData();
    const ID = $("#ticketID").val();

    formData.append("Type", "Accept");
    Swal.fire({
      title: "Are you sure",
      text: "to Accepts ?",
      icon: "warning",
      showCancelButton: !0,
      confirmButtonColor: "#2ab57d",
      cancelButtonColor: "#fd625e",
      confirmButtonText: "Yes, change it!",
    }).then(function (e) {
      if (e.value) {
        $.ajax({
          method: "POST",
          url: BASE_URL + "tickets/manage_tickets/" + ID,
          headers: { "X-CSRFToken": csrftoken },
          processData: false,
          contentType: false,
          data: formData,
          async: true,
          success: function (data) {
            if (!data.isError) {
              Swal.fire({
                title: "Successfully!!!!!",
                text: data.Message,
                icon: "success",
                confirmButtonColor: "#2ab57d",
                cancelButtonColor: "#fd625e",
                confirmButtonText: "Ok it!",
              }).then(function (e) {
                if (e.value) {
                  window.location.reload();
                }
              });
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
});
