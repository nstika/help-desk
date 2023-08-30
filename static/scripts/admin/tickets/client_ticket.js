$(document).ready(function () {
  GetAllCategory();

  let Image = "";
  $("#Image").on("change", function (e) {
    Image = e.target.files[0];
  });
  $("#Save").on("click", function (e) {
    e.preventDefault();
    let formData = new FormData();
    let title = $("#ticket_title").val();
    let category = $("#Category").val();
    let description = $("#description").val();

    formData.append("title", title);
    formData.append("category", category);
    formData.append("descrption", description);
    formData.append("ticket_image", Image);
    formData.append("Type", "ClientTicket");
    if (title == "") {
      Swal.fire("Error!!", "Please Enter Title", "error");
    } else if (category == "") {
      Swal.fire("Error!!", "Please Select Category", "error");
    } else if (description == "") {
      Swal.fire("Error!!", "Please Select Description", "error");
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
            url: BASE_URL + "tickets/manage_tickets/" + "0",
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

  function GetAllCategory() {
    var rows = "";
    let formData = new FormData();
    formData.append("Type", "get_all_categories");
    formData.append("Category", "Ticket");
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
    }
  }
});
