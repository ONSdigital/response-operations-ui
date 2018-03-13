function checkCI(file){

	var type = file.type;

	if( type === "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" ){

		$("#ciFileErrorPanel").removeClass("panel");
		$("#ciFileErrorPanel").removeClass("panel--simple");
		$("#ciFileErrorPanel").removeClass("panel--error");

		$("#ciFileErrorPanelBody").removeClass("panel__body");
		$("#ciFileErrorPanelBody p").addClass("hidden");

		$("#btn-load-ci").removeClass("unready");

	} else{

		$("#ciFileErrorPanel").addClass("panel");
		$("#ciFileErrorPanel").addClass("panel--simple");
		$("#ciFileErrorPanel").addClass("panel--error");

		$("#ciFileErrorPanelBody").addClass("panel__body");
		$("#ciFileErrorPanelBody p").removeClass("hidden");

		$("#btn-load-ci").addClass("unready");

	}


}

function checkSelectedCI(files){

	// Check for the various File API support.
	if (window.FileReader) {
		// FileReader are supported.
		checkCI(files[0]);
	}

}