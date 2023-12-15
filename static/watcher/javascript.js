function openCity(sectionName) {
	var i;
	var x = document.getElementsByClassName("items");
	for (i = 0; i < x.length; i++) {
	  x[i].style.display = "none";
	}
	document.getElementById(sectionName).style.display = "flex";
  }