function checkCI(file){

	var type = file.type;

	if( type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' ){

		$("#ciFileErrorPanel").removeClass("panel");
		$("#ciFileErrorPanel").removeClass("panel--simple");
		$("#ciFileErrorPanel").removeClass("panel--error");

		$("#ciFileErrorPanelBody").removeClass("panel__body");
		$("#ciFileErrorPanelBody p").addClass("hidden");

		$("#btn-add-ci").removeClass("unready");

	}else{

		//alert("that's not an xlsx :(");

		$("#ciFileErrorPanel").addClass("panel");
		$("#ciFileErrorPanel").addClass("panel--simple");
		$("#ciFileErrorPanel").addClass("panel--error");

		$("#ciFileErrorPanelBody").addClass("panel__body");
		$("#ciFileErrorPanelBody p").removeClass("hidden");

		$("#btn-add-ci").addClass("unready");

	}


}

function checkSelectedCI(files){

	// Check for the various File API support.
	if (window.FileReader) {
		// FileReader are supported.
		checkCI(files[0]);
	} else {
		alert('FileReader is not supported in this browser.');
	}

}