$(document).ready(function () {
  $("#DataNumber").val($("#DataNumber").attr("DataNumber"));
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
        `tickets/${url}?DataNumber=${entries}&SearchQuery=${search}&page=${page}`
    );
  }

  let insertType = "Insert";
  $("#add_new_category").click(function () {
    $("#ModalLabel").text("Add Category");
    $("#Category_Name").val("");
    $("#Category_ID").val("");
    $("#CategoryModal").modal("show");

    insertType = "Insert";
  });

  $("#submit_category").on("click", function (e) {
    e.preventDefault();
    let formData = new FormData();
    let method, link;
    if (insertType == "Insert") {
      method = "POST";
      link = BASE_URL + "tickets/manage_category/" + 0;
    } else {
      let id = $("#Category_ID").val();
      method = "POST";
      link = BASE_URL + "tickets/manage_category/" + id;
    }

    let name = $("#Category_Name").val();
    formData.append("name", name);
    formData.append("type", categoryType);
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

            $("#CategoryModal").modal("hide");
            $("#CategoryModalForm").trigger("reset");

            Swal.fire({
              title: "Successfully",
              text: response.Message,
              icon: "success",
              confirmButtonClass: "btn btn-primary w-xs mt-2",
              buttonsStyling: !1,
              showCloseButton: !0,
            }).then(function (e) {
              location.reload();
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

  $("#category_table").on("click", "#delete", function (e) {
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
          url: BASE_URL + "tickets/manage_category/" + ID,
          headers: { "X-CSRFToken": csrftoken },
          async: false,
          success: function (data) {
            if (!data.isError) {
              Swal.fire("Deleted!", data.Message, "success").then(function (e) {
                location.reload();
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

  $("#category_table").on("click", "#edit", function (e) {
    e.preventDefault();
    const ID = $(this).attr("editID");
    insertType = "Update";
    $.ajax({
      method: "GET",
      url: BASE_URL + "tickets/manage_category/" + ID,
      headers: { "X-CSRFToken": csrftoken },
      async: false,
      success: function (data) {
        if (!data.isError) {
          $("#CategoryModal").modal("show");
          $("#ModalLabel").text("Update Category");
          $("#Category_Name").val(data.Message.name);
          $("#Category_ID").val(data.Message.id);

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
});
