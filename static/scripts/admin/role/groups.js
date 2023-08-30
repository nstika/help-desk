$(document).ready(function () {
  $("#staffID").on("click", function (e) {
    $("#table").attr("hidden", true);
    $("#group_permissions tbody").html("");

    document.getElementById("searchEngineInput").focus();
    $(this).val("");
    $("#searchModal").modal("show");
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
      url: BASE_URL + "users/search_engine/" + letter + "/" + "AD,AG,CL",
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

  $(".users-body .list").on("click", ".item", function () {
    $("#staffID").val(
      $(this).attr("username") +
        " - " +
        $(this).attr("name") +
        " (" +
        $(this).attr("type") +
        ")"
    );
    $("#staffID").attr("username", $(this).attr("username"));
    showGroups($(this).attr("username"));
    $("#searchModal").modal("hide");
  });

  function showGroups(id) {
    $.ajax({
      method: "GET",
      url: BASE_URL + "users/manage_group_permission/" + id + "/0",
      headers: { "X-CSRFToken": csrftoken },
      async: false,
      success: function (data) {
        if (!data.isError) {
          let dataRows = "";
          if (data.Message.length > 0) {
            for (var i = 0; i < data.Message.length; i++) {
              dataRows += `
              <tr>
                <td>${data.Message[i].Name}</td>
                <td>${data.Message[i].Count}</td>
                <td>
                <div GroupID = ${
                data.Message[i].ID
                } class="form-check form-switch form-switch-md" dir="ltr">
                    <input type="checkbox" id=${
                "someSwitchOption" + data.Message[i].ID
                }   ${data.Message[i].IsSuper || data.Message[i].IsJoined
                  ? "checked"
                  : ""
                } ${data.Message[i].IsSuper ? "disabled" : ""} class="form-check-input" id="customSwitchsizemd">
                    <label class="form-check-label" for=${
                "someSwitchOption" + data.Message[i].ID
                }></label>
                </div>
                </td>
                <td>
                <button  type="button" class="btn btn-success  showPerms" GroupID = ${
                  data.Message[i].ID
                }>
                  <i class="bx bx-show-alt"></i>
                  </button>
                </td>
              </tr>
              `;
            }
          } else {
            $("#group_permissions tbody").html("");
          }

          $("#group_permissions tbody").html(dataRows);
        } else {
          Swal.fire("error", data.Message, "error");
        }
      },
    });
  }

  $("#group_permissions tbody").on("click", "input", function (e) {
    let type = "";
    if ($(this).prop("checked")) {
      type = "Add";
    } else {
      type = "Remove";
    }

    let formData = new FormData();
    formData.append("type", type);
    formData.append("permID", $(this).parent().attr("GroupID"));
    formData.append("user", $("#staffID").attr("username").toUpperCase());

    $.ajax({
      method: "POST",
      url: BASE_URL + "users/manage_group_permission/0/0",
      headers: { "X-CSRFToken": csrftoken },
      processData: false,
      contentType: false,
      data: formData,
      async: false,
      success: function (data) {
        if (!data.isError) {
          showMessage(data.Message);
          showGroups($("#staffID").attr("username"));
        } else {
          Swal.fire(data.Message);
        }
      },
    });
  });

  $("#group_permissions tbody").on("click", ".showPerms", function (e) {
    $(".group_permisions_roles").modal("show");
    let id = $(this).attr("GroupID");

    $.ajax({
      method: "POST",
      url: BASE_URL + "users/manage_group_permission/" + id.toString() + "/0",
      headers: { "X-CSRFToken": csrftoken },
      async: false,
      success: function (data) {
        if (!data.isError) {
          if (data.Message.length > 0) {
            $("#group_permisions_rolesTable tbody").html("");
            for (let i = 0; i < data.Message.length; i++) {
              $("#group_permisions_rolesTable tbody").append(`
                  <tr>
                      <td>${data.Message[i].Model}</td>
                      <td>${data.Message[i].Name}</td>
                      <td>${data.Message[i].Codename}</td>
                  </tr>
                `);
            }
          } else {
            $("#group_permisions_rolesTable tbody").html("No Data");
          }
        } else {
          $("#group_permisions_rolesTable tbody").html("No Data");
        }
      },
    });
  });
});
