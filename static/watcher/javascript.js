function openCity(sectionName, clickedElement) {
    var i;
    var x = document.getElementsByClassName("items_showhide");
    for (i = 0; i < x.length; i++) {
        x[i].style.display = "none";
    }
    document.getElementById(sectionName).style.display = "flex";

    // Remove "active" class from all list items
    var listItems = document.querySelectorAll('.content-choose-head ul li');
    listItems.forEach(function (item) {
        item.classList.remove('active');
    });

    // Add "active" class to the clicked list item
    clickedElement.classList.add('active');
}
