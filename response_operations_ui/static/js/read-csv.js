
function drawOutput(lines){
	// Put the form types into their own separate array, so we can interrogate it faster
	var formTypes = [];
	for (var i = 0; i < lines.length; i++) {
		formTypes.push(lines[i][lines.length - 1]);
	}

	var ciCount = formTypes.filter(function(val, i, arr) {
        return arr.indexOf(val) === i;
	}).length;


	//Clear previous data
	document.getElementById("sample-preview").innerHTML = "";

	var preview = "";
	preview = preview + "<div class='panel panel--info'>";
	preview = preview + "  <div class='panel__header'>";
	preview = preview + "    <h3 class='venus'>Sample contents</h3>";
	preview = preview + "  </div>";
	preview = preview + "  <div class='panel__body'>";
	preview = preview + "    <div id='sample-preview-businesses'>Number of businesses: " + lines.length + "</div>";
	preview = preview + "    <div id='sample-preview-ci'>Collection instruments: " + ciCount + "</div>";
	preview = preview + "  </div>";
	preview = preview + "</div>";

	document.getElementById("sample-preview").innerHTML = preview;
	document.getElementById("btn-check-sample-contents").style.display = "none";
	document.getElementById("btn-load-sample").style.display = "inline-block";
	document.getElementById("btn-cancel-load-sample").style.display = "inline-block";
}

function errorHandler(evt) {
	if(evt.target.error.name == "NotReadableError") {
		alert("Cannot read file :(");
	}
}

function loadHandler(event) {
    var csv = event.target.result;
	processData(csv);
}

function getAsText(fileToRead) {
	var reader = new FileReader();
	// Handle errors load
	reader.onload = loadHandler;
	reader.onerror = errorHandler;
	// Read file into memory as UTF-8
	reader.readAsText(fileToRead);
}

function handleFiles(files) {
	// Check for the various File API support.
	if (window.FileReader) {
		// FileReader are supported.
		getAsText(files[0]);
	} else {
		alert('FileReader is not supported in this browser.');
	}
}

function processData(csv) {
    var allTextLines = csv.split(/\r\n|\n/);
    var lines = [];

    while (allTextLines.length) {
        var line = allTextLines.shift().split(":")
        if (line && line.length && line[0]) {
            lines.push(line);
        }
    }

    drawOutput(lines);
}

function cancelLoadSample(){

	document.getElementById("sample-preview").innerHTML = "";
	document.getElementById("form-load-sample").reset();
	document.getElementById("btn-check-sample-contents").style.display = "block";
	document.getElementById("btn-load-sample").style.display = "none";
	document.getElementById("btn-cancel-load-sample").style.display = "none";
	$("#file").focus();
}
