$(document).ready(function () {
  GetAllCategory();
  GetAllProject();

  let Documents = "";
  $("#Document").on("change", function (e) {
    Documents = e.target.files[0];
  });
  //Add Task
  $("#Save").on("click", function (e) {
    e.preventDefault();
    let formData = new FormData();
    let ProjectName = $("#ProjectName").val();
    let Title = $("#TaskTitle").val();
    let Agent = $("#TaskAgent").attr("userID");
    let StartDate = $("#StartDate").val();
    let EndDate = $("#EndDate").val();

    let Category = $("#Category").val();
    let Priority = $("#TaskPriority").val();
    let Description = $("#TaskDescription").val();

    formData.append("ProjectName", ProjectName);
    formData.append("title", Title);
    formData.append("Agent", Agent);
    formData.append("StartDate", StartDate);
    formData.append("EndDate", EndDate);
    formData.append("Category", Category);
    formData.append("Priority", Priority);
    formData.append("Description", Description);
    formData.append("Documents", Documents);
    formData.append("Type", "Addtask");
    if (ProjectName == "") {
      Swal.fire("Error!!", "Please Enter Project name", "error");
    } else if (Title == "") {
      Swal.fire("Error!!", "Please Enter Title", "error");
    } else if (Agent == "") {
      Swal.fire("Error!!", "Please Enter Agent", "error");
    } else if (StartDate == "") {
      Swal.fire("Error!!", "Please Enter Start Date", "error");
    } else if (EndDate == "") {
      Swal.fire("Error!!", "Please Enter End Date", "error");
    } else if (Category == "") {
      Swal.fire("Error!!", "Please Select Category", "error");
    } else if (Priority == "") {
      Swal.fire("Error!!", "Please Select Priority", "error");
    } else if (Documents == "") {
      Swal.fire("Error!!", "Please Enter Documents", "error");
    } else if (Description == "") {
      Swal.fire("Error!!", "Please Enter Description", "error");
    } else if (EndDate < StartDate) {
      Swal.fire(
        "Error!!",
        "Please end date must greater than or equal to  start date",
        "error"
      );
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
            url: BASE_URL + "project/manage_tasks/" + "0",
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

  // Save updated Tasks
  $("#SaveChanges").on("click", function (e) {
    e.preventDefault();
    let formData = new FormData();
    const ID = $("#tasksId").val();
    let ProjectName = $("#EProjectName").val();
    let Title = $("#ETaskTitle").val();
    let StartDate = $("#EStartDate").val();
    let EndDate = $("#EEndDate").val();
    let Category = $("#ECategory").val();
    let Priority = $("#ETaskPriority").val();
    let Description = $("#ETaskDescription").val();
    formData.append("ProjectName", ProjectName);
    formData.append("title", Title);
    formData.append("StartDate", StartDate);
    formData.append("EndDate", EndDate);
    formData.append("Category", Category);
    formData.append("Priority", Priority);
    formData.append("Description", Description);
    formData.append("Type", "change");
    if (ProjectName == "") {
      Swal.fire("Error!!", "Please Enter Project name", "error");
    } else if (Title == "") {
      Swal.fire("Error!!", "Please Enter Title", "error");
    } else if (StartDate == "") {
      Swal.fire("Error!!", "Please Enter Start Date", "error");
    } else if (EndDate == "") {
      Swal.fire("Error!!", "Please Enter End Date", "error");
    } else if (Category == "") {
      Swal.fire("Error!!", "Please Select Category", "error");
    } else if (Priority == "") {
      Swal.fire("Error!!", "Please Select Priority", "error");
    } else if (Description == "") {
      Swal.fire("Error!!", "Please Enter Description", "error");
    } else if (EndDate < StartDate) {
      Swal.fire(
        "Error!!",
        "Please end date must greater than or equal to start date",
        "error"
      );
    } else {
      Swal.fire({
        title: "Are you sure to change?",
        text: "make sure",
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

  $("#tasks_table tbody").on("click", ".edit-item-btn ", function (e) {
    e.preventDefault();

    const id = $(this).attr("taskid");

    $.ajax({
      method: "GET",
      url: BASE_URL + "project/manage_tasks/" + id,
      headers: { "X-CSRFToken": csrftoken },
      async: true,
      success: function (response) {
        if (!response.isError) {
          $("#EditTaskModal").modal("show");
          $("#EProjectName").val(response.Message.projectID);
          $("#ETaskTitle").val(response.Message.title);
          $("#EStartDate").val(response.Message.start);
          $("#EEndDate").val(response.Message.end);
          $("#ECategory").val(response.Message.category);
          $("#ETaskPriority").val(response.Message.priority);
          $("#ETaskDescription").val(response.Message.description);
          $("#tasksId").val(response.Message.id);
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

  $("#tasks_table tbody").on("click", ".delete-task ", function (e) {
    e.preventDefault();
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
          url: BASE_URL + "project/manage_tasks/" + ID,
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

  function GetAllCategory() {
    var rows = "";
    let formData = new FormData();
    formData.append("Type", "get_all_categories");
    formData.append("Category", "Task");
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
      $("#ECategory").html(dataRow);
    }
  }
  function GetAllProject() {
    var rows = "";
    let formData = new FormData();
    formData.append("Type", "get_all_projects");
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
      dataRow += `<option value=''>Select Project</option>`;
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
      $("#ProjectName").html(dataRow);
      $("#EProjectName").html(dataRow);
    }
  }

  $("#TaskAgent").on("click", function (e) {
    document.getElementById("searchEngineInput").focus();
    $(this).val("");
    $("#searchModal").modal("show");
  });

  $(".users-body .list").on("click", ".item", function () {
    $("#TaskAgent").val(
      $(this).attr("username") +
        " - " +
        $(this).attr("name") +
        " (" +
        $(this).attr("type") +
        ")"
    );
    $("#TaskAgent").attr("username", $(this).attr("username"));
    $("#TaskAgent").attr("userID", $(this).attr("userid"));
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
});
