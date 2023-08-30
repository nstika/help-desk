$(document).ready(function () {
  // GetReport();

  $("#RoleType").on("change", function () {
    GetReport();
  });

  $("#search_user").on("click", function () {
    $("#rolesList tbody").html("");
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
      beforeSend: function () {
        $("#SearchBTN").addClass("btn-loading");
      },
      async: true,
      headers: { "X-CSRFToken": csrftoken },
      success: function (data) {
        $("#SearchBTN").removeClass("btn-loading");
        $(".users-body .list").html("");
        data.Message.forEach((user) => {
          $(".users-body .list").append(`
            <div class="col-md-12 item" type = ${user.Type} name='${user.Name}' username=${user.Username} phone = ${user.Phone} userid = ${user.ID}>
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

  $(".users-body .list").on("click", ".item", function () {
    $("#search_user").val(
      $(this).attr("username") +
        " - " +
        $(this).attr("name") +
        " (" +
        $(this).attr("type") +
        ")"
    );
    $("#search_user").attr("username", $(this).attr("username"));
    $("#search_user").attr("userid", $(this).attr("userid"));
    $("#searchModal").modal("hide");

    if ($("#search_user").val() !== "") {
      GetReport();
    }
  });

  function GetReport() {
    let formData = new FormData();
    formData.append("type", "GetUserReport");
    formData.append("user", $("#search_user").attr("userid"));
    formData.append("report", $("#RoleType").val());

    $.ajax({
      method: "POST",
      url: BASE_URL + "users/manage_permission_report",
      processData: false,
      contentType: false,
      headers: { "X-CSRFToken": csrftoken },
      data: formData,
      async: false,
      success: function (data) {
        var table1 = "",
          table2 = "";
        if ($("#RoleType").val() == "Role") {
          $("#rolesList").removeClass("d-none");
          $("#groupsList").addClass("d-none");
          table1 = $("#rolesList").DataTable().clear().draw();
          table2 = $("#groupsList").DataTable().clear().destroy();
        } else {
          $("#rolesList").addClass("d-none");
          $("#groupsList").removeClass("d-none");
          table1 = $("#rolesList").DataTable().clear().destroy();
          table2 = $("#groupsList").DataTable().clear().draw();
        }

        data.Message.forEach((item) => {
          if ($("#RoleType").val() == "Role") {
            table1.row.add([item.App, item.Model, item.Codename]).draw();
          } else {
            table2.row
              .add([
                item.GroupName,
                item.Permissions,
                `<button type="button" class="btn btn-success  showPerms" GroupID = ${item.GroupID}>
            <i class="bx bx-show-alt"></i>
            </button>`,
              ])
              .draw();
          }
        });
      },
    });
  }

  $("#groupsList tbody").on("click", ".showPerms", function (e) {
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
            let rows = "";
            for (let i = 0; i < data.Message.length; i++) {
              rows += `
                  <tr>
                      <td>${data.Message[i].Model}</td>
                      <td>${data.Message[i].Name}</td>
                      <td>${data.Message[i].Codename}</td>
                      </tr>
                `;
            }

            $("#group_permisions_rolesTable tbody").html(rows);
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
