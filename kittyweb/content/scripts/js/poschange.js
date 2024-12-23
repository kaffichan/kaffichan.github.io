window.addEventListener('DOMContentLoaded', (event) => {
	var oldMarginTop = "30px";
	var newMarginTop = "135px";
	
	function toggleMarginTop() {
		var bottomDiv = document.getElementById('bottomDiv');
		
		if(window.getComputedStyle(bottomDiv).marginTop === oldMarginTop) {
			bottomDiv.style.marginTop = newMarginTop;
		} else {
			bottomDiv.style.marginTop = oldMarginTop;
		}
	}
	
	window.addEventListener('load', toggleMarginTop);
	document.querySelector('#button').addEventListener('click', toggleMarginTop);
});
