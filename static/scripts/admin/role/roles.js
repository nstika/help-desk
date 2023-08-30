$(document).ready(function () {
  $("#staffID").on("click", function (e) {
    $("#table").attr("hidden", true);
    $("#permissions tbody").html("");
    document.getElementById("searchEngineInput").focus();
    $(this).val("");
    $("#searchModal").modal("show");
  });

  $(".users-body .list").on("click", ".item", function () {
    $("#search_student").val(
      $(this).attr("username") +
      " - " +
      $(this).attr("name") +
      " (" +
      $(this).attr("type") +
      ")"
    );
    $("#search_student").attr("username", $(this).attr("username"));
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
    showModels($("#staffID").attr("username"), $("#AppType").val());
    showPermisisons($(this).attr("username"));
    $("#searchModal").modal("hide");
  });

  function showGroups(id) {
    $.ajax({
      method: "GET",
      url: BASE_URL + "users/manage_permission/" + id,
      headers: { "X-CSRFToken": csrftoken },
      async: false,
      success: function (data) {
        if (!data.isError) {
          let dataRow = "";
          $("#AppType").html("");
          if (data.Message.length > 0) {
            let temp = [];
            for (let i = 0; i < data.Message.length; i++) {
              !temp.includes(data.Message[i].App) &&
                $("#AppType").append(`
                <option  ${i + 1 == data.Message.length ? "selected" : ""
                  } value="${data.Message[i].App}">${data.Message[i].App}</option>
                `);
              temp.push(data.Message[i].App);
            }
          }
        } else {
          Swal.fire("error", data.Message, "error");
          $("#permissions tbody").html("");
        }
      },
    });
  }

  function showModels(id, app) {
    $.ajax({
      method: "GET",
      url: BASE_URL + "users/manage_permission/" + id,
      headers: { "X-CSRFToken": csrftoken },
      async: false,
      success: function (data) {
        if (!data.isError) {
          let dataRow = "";
          $("#ModelType").html("");
          if (data.Message.length > 0) {
            let temp = [];
            $("#ModelType").append(`
                <option App = ${app} value="All">All Models</option>
                `);
            for (let i = 0; i < data.Message.length; i++) {
              if (
                !temp.includes(data.Message[i].Model) &&
                data.Message[i].App == app
              ) {
                $("#ModelType").append(`
                <option App = ${app} value="${data.Message[i].Model}">${data.Message[i].Model}</option>
                `);
              }
              temp.push(data.Message[i].Model);
            }
          }
        } else {
          Swal.fire("error", data.Message, "error");
          $("#permissions tbody").html("");
        }
      },
    });
  }

  function showPermisisons(id) {
    $.ajax({
      method: "GET",
      url: BASE_URL + "users/manage_permission/" + id,
      headers: { "X-CSRFToken": csrftoken },
      async: false,
      success: function (data) {
        if (!data.isError) {
          let dataRow = "";
          if (data.Message.length > 0) {
            for (let i = 0; i < data.Message.length; i++) {
              if (
                ($("#ModelType").val() == data.Message[i].Model ||
                  $("#ModelType").val() == "All") &&
                $("option:selected", "#ModelType").attr("app") ==
                data.Message[i].App
              ) {
                dataRow += `<tr><td>${data.Message[i].Model}</td>`;
                let track = 0;
                for (let x = 0; x < data.Message[i].Actions.length; x++) {
                  track++;

                  if (track > 4) {
                    dataRow += `</tr><tr><td></td>`;
                    track = 1;
                  }

                  dataRow += `
                <td>

                <div ActionID = ${data.Message[i]["Actions"][x]["ID"]
                    } class="form-check form-switch form-switch-md" dir="ltr">
                    <input  id=${"someSwitchOption" + data.Message[i]["Actions"][x].ID
                    }  ${data.Message[i]["Actions"][x]["isPermitted"]
                      ? "checked"
                      : ""
                    } ${data.Message[i]["Actions"][x]["isSuperuser"]
                      ? "disabled"
                      : ""
                    } name='RolesInputs' type="checkbox" class="form-check-input">
                    <label for=${"someSwitchOption" + data.Message[i]["Actions"][x].ID
                    } class="form-check-label" for="customSwitchsizemd">${data.Message[i]["Actions"][x]["Action"]
                    }</label>
                </div>

              
                `;
                }
                dataRow += `</tr>`;
              }
            }

            $("#permissions tbody").html(dataRow);
          } else {
            $("#permissions tbody").html("");
          }
        } else {
          Swal.fire("error", data.Message, "error");
          $("#permissions tbody").html("");
        }
      },
    });
  }

  $("#AppType").on("change", function () {
    $("#permissions tbody").html("");
    showModels($("#staffID").attr("username"), $("#AppType").val());
    showPermisisons($("#staffID").attr("username"));
  });

  $("#ModelType").on("change", function () {
    $.ajax({
      method: "GET",
      url:
        BASE_URL + "users/manage_permission/" + $("#staffID").attr("username"),
      headers: { "X-CSRFToken": csrftoken },
      async: false,
      success: function (data) {
        if (!data.isError) {
          let dataRow = "";
          if (data.Message.length > 0) {
            for (let i = 0; i < data.Message.length; i++) {
              if (
                ($("#ModelType").val() == data.Message[i].Model ||
                  $("#ModelType").val() == "All") &&
                $("option:selected", "#ModelType").attr("app") ==
                data.Message[i].App
              ) {
                dataRow += `<tr><td>${data.Message[i].Model}</td>`;

                let track = 0;
                for (let x = 0; x < data.Message[i].Actions.length; x++) {
                  if (
                    ($("#ModelType").val() == data.Message[i].Model ||
                      $("#ModelType").val() == "All") &&
                    $("option:selected", "#ModelType").attr("app") ==
                    data.Message[i].App
                  ) {
                    track++;

                    if (track > 4) {
                      dataRow += `</tr><tr><td></td>`;
                      track = 1;
                    }

                    dataRow += `
                <td>
                <div ActionID = ${data.Message[i]["Actions"][x]["ID"]
                      } class="form-check form-switch form-switch-md" dir="ltr">
                    <input  id=${"someSwitchOption" + data.Message[i]["Actions"][x].ID
                      }  ${data.Message[i]["Actions"][x]["isPermitted"]
                        ? "checked"
                        : ""
                      } ${data.Message[i]["Actions"][x]["isSuperuser"]
                        ? "disabled"
                        : ""
                      } name='RolesInputs' type="checkbox" class="form-check-input">
                    <label for=${"someSwitchOption" + data.Message[i]["Actions"][x].ID
                      } class="form-check-label" for="customSwitchsizemd">${data.Message[i]["Actions"][x]["Action"]
                      }</label>
                </div>
                  </td>
                `;
                  }
                }
                dataRow += `</tr>`;
              }
            }

            $("#permissions tbody").html(dataRow);
          } else {
            $("#permissions tbody").html("");
          }
        } else {
          Swal.fire("error", data.Message, "error");
          $("#permissions tbody").html("");
        }
      },
    });
  });

  $("#permissions tbody").on("click", "input", function (e) {
    const input = $(this);
    let type = "";
    if ($(this).prop("checked")) {
      type = "Add";
    } else {
      type = "Remove";
    }

    let formData = new FormData();
    formData.append("type", type);
    formData.append("permID", $(this).parent().attr("ActionID"));
    formData.append("user", $("#staffID").attr("username").toUpperCase());
    $.ajax({
      method: "POST",
      url: BASE_URL + "users/manage_permission/0",
      headers: { "X-CSRFToken": csrftoken },
      processData: false,
      contentType: false,
      data: formData,
      async: false,
      success: function (data) {
        if (!data.isError) {
          showMessage(data.Message);
          showPermisisons($("#staffID").attr("username"));
        } else {
          $(input).prop("checked", false);
          Swal.fire("error", data.Message, "error");
        }
      },
    });
  });
});
