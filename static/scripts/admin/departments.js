$(document).ready(function () {
  const per_edit = $("#DepartmentPerms").attr("edit");
  const per_delete = $("#DepartmentPerms").attr("delete");
  GetAllDepartments();

  let insertType = "Insert";
  $("#add_new_dept").click(function () {
    $("#ModalLabel").text("Add Department");
    $("#Department_Name").val("");
    $("#Department_ID").val("");
    $("#DepartmentModal").modal("show");

    insertType = "Insert";
  });

  $("#submit_department").on("click", function (e) {
    e.preventDefault();
    let formData = new FormData();
    let method, link;
    if (insertType == "Insert") {
      method = "POST";
      link = BASE_URL + "users/manage_departments/" + 0;
    } else {
      let id = $("#Department_ID").val();
      method = "POST";
      link = BASE_URL + "users/manage_departments/" + id;
    }

    let name = $("#Department_Name").val();
    formData.append("name", name);
    if (name == "") {
      Swal.fire("Error!!", "This feild is required", "error");
    } else {
      $.ajax({
        method: method,
        url: link,

        headers: { "X-CSRFToken": csrftoken },
        processData: false,
        contentType: false,
        data: formData,
        async: true,
        success: function (response) {
          if (!response.isError) {
            insertType = "Insert";
            GetAllDepartments();
            $("#DepartmentModal").modal("hide");
            $("#PositionModalForm").trigger("reset");

            Swal.fire({
              title: "Successfully",
              text: response.Message,
              icon: "success",
              confirmButtonClass: "btn btn-primary w-xs mt-2",
              buttonsStyling: !1,
              showCloseButton: !0,
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

  $("#department_table").on("click", ".delete", function (e) {
    e.preventDefault();
    const ID = $(this).attr("deleteID");
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
          url: BASE_URL + "users/manage_departments/" + ID,
          headers: { "X-CSRFToken": csrftoken },
          async: false,
          success: function (data) {
            if (!data.isError) {
              Swal.fire("Deleted!", data.Message, "success");
              GetAllDepartments();
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

  $("#department_table").on("click", ".edit", function (e) {
    e.preventDefault();
    const ID = $(this).attr("editID");

    insertType = "Update";
    $.ajax({
      method: "GET",
      url: BASE_URL + "users/manage_departments/" + ID,
      headers: { "X-CSRFToken": csrftoken },
      async: false,
      success: function (data) {
        if (!data.isError) {
          $("#DepartmentModal").modal("show");
          $("#ModalLabel").text("Update Department");
          $("#Department_Name").val(data.Message.name);
          $("#Department_ID").val(data.Message.id);

          insertionType = "Update";
        } else {
          Swal.fire("Something Wrong!!", data.Message, "error");
        }
      },
      error: function (error) {
        error;
      },
    });
  });

  function GetAllDepartments() {
    $.ajax({
      method: "GET",
      url: BASE_URL + "users/manage_departments/" + 0,
      headers: { "X-CSRFToken": csrftoken },
      async: false,
      success: function (data) {
        if (!data.isError) {
          if (data.Message.length != "") {
            let rowData = [];
            let num = 1;
            let data_table = $("#department_table").DataTable().clear();

            for (let i = 0; i < data.Message.length; i++) {
              let rowData = [
                num++,
                data.Message[i].name,
                data.Message[i].created_at,
                data.Message[i].modified_at,
              ];

              let buttons = "";
              if (per_edit == "True" || per_delete == "True") {
                buttons = '<div class="hstack gap-3 fs-15">';
              }

              if (per_edit == "True") {
                buttons += `<button class="btn btn-success waves-effect waves-light edit" editID=${data.Message[i].id}><i class="ri-edit-box-line" ></i></button>`;
              }

              if (per_delete == "True") {
                buttons += `<button class="btn btn-danger waves-effect waves-light delete" deleteID=${data.Message[i].id}><i class="ri-delete-bin-5-line" ></i></button>`;
              }

              if (per_edit == "True" || per_delete == "True") {
                buttons += "</div>";
                rowData.push(buttons);
              }

              data_table.row.add(rowData).draw();
            }
          } else {
            $("#department_table").DataTable().clear().draw();
            $("#department_table tbody").html(
              `<td colspan="4" class="btn-danger" style="font-size:20px"><center> No Data is Available </center></td>`
            );
          }
        } else {
          data_table = $("#department_table").DataTable().clear();
          Swal.fire("Something Wrong!!", data.Message, "error");
        }
      },
      error: function (error) {},
    });
  }
});
