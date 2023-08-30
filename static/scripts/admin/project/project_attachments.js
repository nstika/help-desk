$(document).ready(function () {
  let action = "insert";

  $("#upload_btn_shower").on("click", function () {
    action = "insert";
    document.querySelector("#upload_file_form").reset();
    $(".upload_file").modal("show");
    $("#File").parent().removeClass("d-none");
  });

  let file = "";
  $("#File").on("change", function (e) {
    file = e.target.files[0];
  });

  $("#upload_file_form").on("submit", function (e) {
    e.preventDefault();

    let formData = new FormData();
    let link;

    if (action == "insert") {
      link = BASE_URL + "project/manage_project_attachments/" + 0;
    } else {
      link =
        BASE_URL + "project/manage_project_attachments/" + $("#fileID").val();
    }

    let title = $("#FileName").val();
    let project = $("#FileName").attr("projectID");
    formData.append("title", title);
    formData.append("project", project);
    formData.append("file", file);

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

  $("#project_files tbody").on("click", "#delete_file", function (e) {
    e.preventDefault();
    const id = $(this).attr("row_id");
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
          url: BASE_URL + "project/manage_project_attachments/" + id,
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

  $("#project_files tbody").on("click", "#edit_file", function (e) {
    e.preventDefault();
    const id = $(this).attr("row_id");
    $("#File").parent().addClass("d-none");
    action = "update";
    $.ajax({
      method: "GET",
      url: BASE_URL + "project/manage_project_attachments/" + id,
      headers: { "X-CSRFToken": csrftoken },
      async: true,
      success: function (response) {
        if (!response.isError) {
          $(".upload_file").modal("show");
          response = response.Message;
          $("#FileName").val(response.title);
          $("#fileID").val(response.id);
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

  $("#ManagerName").on("click", function (e) {
    document.getElementById("searchEngineInput").focus();
    $(this).val("");
    $("#searchModal").modal("show");
  });

  $(".users-body .list").on("click", ".item", function () {
    $("#ManagerName").val(
      $(this).attr("username") +
        " - " +
        $(this).attr("name") +
        " (" +
        $(this).attr("type") +
        ")"
    );
    $("#ManagerName").attr("userid", $(this).attr("userid"));
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

  $("#changeManagerBTN").on("click", function (e) {
    e.preventDefault();

    let formData = new FormData();

    let user = $("#ManagerName").attr("userid");
    let project = $("#ManagerName").attr("projectID");

    formData.append("user", user);
    formData.append("project", project);

    $.ajax({
      method: "POST",
      url: BASE_URL + "project/manage_project/change-manager",
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
});
