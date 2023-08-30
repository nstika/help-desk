$(document).ready(function () {
  GetAllPositions();
  GetAllDepartment();

  let Image = "";
  $("#Image").on("change", function (e) {
    Image = e.target.files[0];
  });
  $("#Save").on("click", function (e) {
    e.preventDefault();
    let formData = new FormData();
    let FName = $("#FName").val();
    let LName = $("#LName").val();
    let Phone = $("#Phone").val();
    let Email = $("#Email").val();
    let Position = $("#Position").val();
    let Department = $("#Department").val();
    let Gender = $("#Gender").val();
    let UserType = $("#UserType").val();
    formData.append("fname", FName);
    formData.append("lname", LName);
    formData.append("phone", Phone);
    formData.append("email", Email);
    formData.append("position", Position);
    formData.append("department", Department);
    formData.append("gender", Gender);

    formData.append("image", Image);
    formData.append("type", UserType);
    if (FName == "") {
      Swal.fire("Error!!", "Please Enter first name", "error");
    } else if (LName == "") {
      Swal.fire("Error!!", "Please Enter last name", "error");
    } else if (Email == "") {
      Swal.fire("Error!!", "Please Enter email", "error");
    } else if (UserType == "") {
      Swal.fire("Error!!", "Please Select User type", "error");
    } else if (Position == "") {
      Swal.fire("Error!!", "Please Select position", "error");
    } else if (Department == "") {
      Swal.fire("Error!!", "Please Select department", "error");
    } else if (Gender == "") {
      Swal.fire("Error!!", "Please Select gender", "error");
    } else if (Image == "") {
      Swal.fire("Error!!", "Please upload client image", "error");
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
            url: BASE_URL + "users/manage_users/" + 0,
            headers: { "X-CSRFToken": csrftoken },
            processData: false,
            contentType: false,
            data: formData,
            async: true,
            success: function (response) {
              if (!response.isError) {
                Swal.fire({
                  title: "Success",
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
                Swal.fire("Error!!", response.Message, "error");
              }
            },
            error: function (response) {},
          });
        }
      });
    }
  });

  function GetAllPositions() {
    var rows = "";
    let formData = new FormData();
    formData.append("Type", "get_all_position");
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
      dataRow += `<option value=''>Select Positon</option>`;
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
      $("#Position").html(dataRow);
    }
  }
  function GetAllDepartment() {
    var rows = "";
    let formData = new FormData();
    formData.append("Type", "get_all_department");
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
      dataRow += `<option value=''>Select Department</option>`;
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
      $("#Department").html(dataRow);
    }
  }
});
