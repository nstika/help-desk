$(document).ready(function () {
  $("#DataNumber").val($("#DataNumber").attr("DataNumber"));
  let action = "insert";

  $("#project-manager").on("click", function (e) {
    document.getElementById("searchEngineInput").focus();
    $(this).val("");
    $("#searchModal").modal("show");
  });

  $(".users-body .list").on("click", ".item", function () {
    $("#project-manager").val(
      $(this).attr("username") +
        " - " +
        $(this).attr("name") +
        " (" +
        $(this).attr("type") +
        ")"
    );
    $("#project-manager").attr("userid", $(this).attr("userid"));
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
      url: BASE_URL + "users/search_engine/" + letter + "/" + "AD",
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

  $("#add-project").on("click", function () {
    action = "insert";
    $("#textproject").text("Create Project");
    $(".add_project_model").modal("show");
    $("#project-thumbnail").parent().removeClass("d-none");
    $("#project-start").parent().removeClass("col-md-6");
    $("#project-end").parent().removeClass("col-md-6");
    $("#project-start").parent().addClass("col-md-4");
    $("#project-end").parent().addClass("col-md-4");
    document.getElementById("new_project_form").reset();
  });

  let thumbnail = "";
  $("#project-thumbnail").on("change", function (e) {
    thumbnail = e.target.files[0];
  });

  $("#new_project_form").on("submit", function (e) {
    e.preventDefault();

    let formData = new FormData();
    let link;

    if (action == "insert") {
      link = BASE_URL + "project/manage_project/0";
    } else {
      link = BASE_URL + "project/manage_project/" + $("#projectID").val();
    }

    let title = $("#project-title").val();
    let category = $("#project-category").val();
    let manager = $("#project-manager").attr("userid");
    let priority = $("#project-priority").val();
    let status = $("#project-status").val();
    let start = $("#project-start").val();
    let end = $("#project-end").val();

    formData.append("title", title);
    formData.append("category", category);
    formData.append("manager", manager);
    formData.append("priority", priority);
    formData.append("status", status);
    formData.append("start", start);
    formData.append("end", end);
    formData.append("thumbnail", thumbnail);

    $.ajax({
      method: "POST",
      url: link,
      headers: { "X-CSRFToken": csrftoken },
      processData: false,
      contentType: false,
      data: formData,
      async: true,
      success: function (response) {
        if (!response.isError) {
          Swal.fire({
            title: "Successfully",
            text: response.Message,
            icon: "success",
            confirmButtonClass: "btn btn-primary w-xs mt-2",
            buttonsStyling: !1,
            showCloseButton: !0,
          }).then((e) => {
            e.value && location.reload();
          });
        } else {
          Swal.fire("Something Wrong!!", response.Message, "error");
        }
      },
      error: function (response) {},
    });
  });

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

  function RefreshPage() {
    let page = $(".activePage").attr("activePage");
    let search = $("#SearchQuery").val();
    let entries = $("#DataNumber").val();

    window.location.replace(
      BASE_URL +
        `project/projects?DataNumber=${entries}&SearchQuery=${search}&page=${page}`
    );
  }

  $("#project_table tbody").on("click", ".edit-project", function (e) {
    e.preventDefault();
    action = "update";
    $("#textproject").text("Update Project");
    const id = $(this).attr("id");
    $("#project-thumbnail").parent().addClass("d-none");
    $("#project-start").parent().removeClass("col-md-4");
    $("#project-end").parent().removeClass("col-md-4");
    $("#project-start").parent().addClass("col-md-6");
    $("#project-end").parent().addClass("col-md-6");
    $.ajax({
      method: "GET",
      url: BASE_URL + "project/manage_project/" + id,
      headers: { "X-CSRFToken": csrftoken },
      async: true,
      success: function (response) {
        if (!response.isError) {
          $(".add_project_model").modal("show");
          response = response.Message;
          $("#projectID").val(response.projectID);
          $("#project-title").val(response.title);
          $("#project-category").val(response.category);
          $("#project-manager").attr("userid", response.manager.id);
          $("#project-manager").val(response.manager.name);
          $("#project-priority").val(response.priority);
          $("#project-status").val(response.status);
          $("#project-start").val(response.start);
          $("#project-end").val(response.end);
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

  $("#project_table tbody").on("click", ".delete-project", function (e) {
    e.preventDefault();
    const id = $(this).attr("id");
    Swal.fire({
      title: "Are you sure?",
      text: "You won't be able to get it after!",
      icon: "warning",
      showCancelButton: !0,
      confirmButtonColor: "#2ab57d",
      cancelButtonColor: "#fd625e",
      confirmButtonText: "Yes, delete it!",
    }).then((e) => {
      if (e.value) {
        $.ajax({
          method: "DELETE",
          url: BASE_URL + "project/manage_project/" + id,
          headers: { "X-CSRFToken": csrftoken },
          async: true,
          success: function (response) {
            if (!response.isError) {
              Swal.fire({
                title: "Success",
                text: response.Message,
                icon: "success",
                confirmButtonClass: "btn btn-primary w-xs mt-2",
                buttonsStyling: !1,
                showCloseButton: !0,
              }).then((e) => {
                e.value && location.reload();
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
  });
});
