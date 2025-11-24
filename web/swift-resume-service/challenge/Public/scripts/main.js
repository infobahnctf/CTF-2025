
document.addEventListener( 'DOMContentLoaded', function () {
	document.getElementById( 'templateDrop').onchange = function(e) { 
		if (this.value === '_custom') {
			document.getElementById( 'templateIn').style.display = 'block';
		} else {
			document.getElementById( 'templateIn').style.display = 'none';
			document.getElementById( 'template').value = this.value;
		}
	};
} )
