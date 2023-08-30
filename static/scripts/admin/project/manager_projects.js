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
      `project/manager_projects?DataNumber=${entries}&SearchQuery=${search}&page=${page}`
    );
  }
});
