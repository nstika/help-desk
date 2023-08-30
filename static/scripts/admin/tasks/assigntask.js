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

    let taskID = $("#taskID").val();

    let Agent = $("#staffID").attr("userID");
    let formData = new FormData();
    formData.append("user", Agent);
    formData.append("task", taskID);
    if (Agent == "") {
      Swal.fire("Error!!", "This feild is required", "error");
    } else {
      $.ajax({
        method: "POST",
        url: BASE_URL + "project/assign_task/" + 0,
        headers: { "X-CSRFToken": csrftoken },
        processData: false,
        contentType: false,
        data: formData,
        async: true,
        success: function (response) {
          if (!response.isError) {
            $("#AssignTaskModal").modal("hide");

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
    $("#AssignTaskModal").modal("show");
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
      confirmButtonText: "Yes, delete it!",
    }).then(function (e) {
      if (e.value) {
        $.ajax({
          method: "DELETE",
          url: BASE_URL + "project/assign_task/" + ID,
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
    const ID = $("#taskID").val();
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
          url: BASE_URL + "project/manage_tasks/" + ID,
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
              Swal.fire("Error", data.Message, "warning");
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
    const ID = $("#taskID").val();
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
          url: BASE_URL + "project/manage_tasks/" + ID,
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
              Swal.fire("Error", data.Message, "warning");
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
    const ID = $("#taskID").val();

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
          url: BASE_URL + "project/manage_tasks/" + ID,
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
              Swal.fire("Error", data.Message, "warning");
            }
          },
          error: function (error) {
            //(error);
          },
        });
      }
    });
  });

  // Progress Tasks
  //Add Progress Task
  $("#save_progress").on("click", function (e) {
    e.preventDefault();
    let formData = new FormData();
    const ID = $("#taskID").val();
    let WorkDescription = $("#WorkDescription").val();
    let WorkCompletion = $("#WorkCompletion").val();
    formData.append("Description", WorkDescription);
    formData.append("WorkCompletion", WorkCompletion);
    formData.append("Type", "Progress");
    if (WorkCompletion == "") {
      Swal.fire("Error!!", "Please Enter number of Completion", "error");
    } else if (WorkDescription == "") {
      Swal.fire("Error!!", "Please Enter Progress Description", "error");
    } else {
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
            url: BASE_URL + "project/manage_tasks/" + ID,
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
    }
  });

  // Edit and Show Progress
  $(".editprogress").on("click", ".btnnote", function () {
    const id = $(this).attr("progressid");
    $.ajax({
      method: "GET",
      url: BASE_URL + "project/task_progress/" + id,
      headers: { "X-CSRFToken": csrftoken },
      async: true,
      success: function (response) {
        if (!response.isError) {
          $("#EditTaskProgressModal").modal("show");
          $("#EWorkCompletion").val(response.Message.work_completion);
          $("#EWorkDescription").val(response.Message.description);
          $("#EProgressID").val(response.Message.id);
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

  // Save changes Progress
  $("#save_task_progress").on("click", function (e) {
    e.preventDefault();
    let formData = new FormData();
    const ID = $("#EProgressID").val();
    let WorkDescription = $("#EWorkDescription").val();
    let WorkCompletion = $("#EWorkCompletion").val();
    formData.append("Description", WorkDescription);
    formData.append("WorkCompletion", WorkCompletion);
    formData.append("Type", "Progress");
    if (WorkCompletion == "") {
      Swal.fire("Error!!", "Please Enter number of Completion", "error");
    } else if (WorkDescription == "") {
      Swal.fire("Error!!", "Please Enter Progress Description", "error");
    } else {
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
            url: BASE_URL + "project/task_progress/" + ID,
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
    }
  });
});
