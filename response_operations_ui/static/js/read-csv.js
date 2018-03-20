
function drawOutput(businessCount, ciCount){

	//Clear previous data
	document.getElementById("sample-preview").innerHTML = "";

	var preview = "";
	preview = preview + "<div class='panel panel--info'>";
	preview = preview + "  <div class='panel__header'>";
	preview = preview + "    <h3 class='venus'>Sample contents</h3>";
	preview = preview + "  </div>";
	preview = preview + "  <div class='panel__body'>";
	preview = preview + "    <div id='sample-preview-businesses'>Number of businesses: " + businessCount + "</div>";
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

function handleFiles(files, classifiers) {
	// Check for the various File API support.
	if (window.FileReader) {
		// FileReader are supported.
		var reader = new FileReader();

        // Handle errors load
        reader.onload = function(evt) {
            processFile(evt, classifiers);
        };
        reader.onerror = errorHandler;

        // Read file into memory as UTF-8
        reader.readAsText(files[0]);

	} else {
		alert('FileReader is not supported in this browser.');
	}
}

function processFile(event, classifiers) {
    var csv = event.target.result;
    var allTextLines = csv.split(/\r\n|\n/);
    var classifierColumn = [];
    var lines = [];
    var ciCount;

    while (allTextLines.length) {
        var line = allTextLines.shift().split(":")
        if (line && line.length && line[0]) {
            lines.push(line);
        }
    }

    if (classifiers.indexOf('RU_REF') > -1) {
        ciCount = lines.length  // each line should be a distinct RU_REF (sampleUnitRef)
    } else if (classifiers.indexOf('FORM_TYPE') > -1){
        // Put the form types into their own separate array, so we can interrogate it faster
        for (var i = 0; i < lines.length; i++) {
            classifierColumn.push(lines[i][lines[i].length - 2]);
        }

        ciCount = classifierColumn.filter(function(val, i, arr) {
            return arr.indexOf(val) === i;
        }).length;
    }

    drawOutput(lines.length, ciCount);
}

function cancelLoadSample(){

	document.getElementById("sample-preview").innerHTML = "";
	document.getElementById("form-load-sample").reset();
	document.getElementById("btn-check-sample-contents").style.display = "block";
	document.getElementById("btn-load-sample").style.display = "none";
	document.getElementById("btn-cancel-load-sample").style.display = "none";
	$("#file").focus();
}
