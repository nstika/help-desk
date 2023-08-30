$(document).ready(function () {
    // Update The Entries Selection
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
          `recycle/recycle_users?DataNumber=${entries}&SearchQuery=${search}&page=${page}`
      );
    }
  
  
    $("#users_table").on("click", "#users", function () {
      const ID = $(this).attr("usersid");
      let data = new FormData();
      data.append('Type', "Users")
  
      Swal.fire({
        title: "Are you sure?",
        text: "You won't be able to get it after!",
        icon: "warning",
        showCancelButton: !0,
        confirmButtonColor: "#2ab57d",
        cancelButtonColor: "#fd625e",
        confirmButtonText: "Yes, Recycle it!",
      }).then(function (e) {
        if (e.value) {
          $.ajax({
            method: "POST",
            url: BASE_URL + "recycle/manage_recycle/" + ID,
            headers: { "X-CSRFToken": csrftoken },
            processData: false,
            contentType: false,
            data: data,
            async: false,
            success: function (data) {
              if (!data.isError) {
                Swal.fire("Recycling!", data.Message, "success").then(function (e) {
                  location.reload();
                })
           
              } else {
                Swal.fire("Error", data.Message, "warning");
              }
            },
            error: function (error) {
              //(error);
            },
          });
        }
      });
    });
  });
  