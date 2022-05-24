window.readCSV = {
    __private__: {}
};

window.readCSV.__private__.getOutputTemplate = function(businessCount, ciCount) {
    let preview = '';

    preview += '<div class=\'panel panel--info\'>';
    preview += '  <div class=\'panel__header\'>';
    preview += '    <h3 class=\'u-fs-r--b u-mb-no\'>Sample contents</h3>';
    preview += '  </div>';
    preview += '  <div class=\'panel__body\'>';
    preview += '    <div id=\'sample-preview-businesses\'>Number of businesses: ' + businessCount + '</div>';
    preview += '    <div id=\'sample-preview-ci\'>Collection instruments: ' + ciCount + '</div>';
    preview += '  </div>';
    preview += '</div>';

    return preview;
};

window.readCSV.__private__.renderUI = function(businessCount, ciCount) {
    document.getElementById('sample-preview').innerHTML = window.readCSV.__private__.getOutputTemplate(businessCount, ciCount);
    document.getElementById('btn-upload-sample').disabled = false;
};

window.readCSV.__private__.errorHandler = function(evt) {
    if (evt.target.error.name == 'NotReadableError') {
        alerts.error('Error Uploading file', 'The selected file was not readable.');
    }
};

window.readCSV.__private__.browserHasFileLoaderCapability = function() {
    return window.hasOwnProperty('FileReader');
};

window.readCSV.__private__.processFile = function(event, classifiers) {
    const csv = event.target.result;
    const allTextLines = csv.split(/\r\n|\n/);
    const classifierColumn = [];
    const lines = [];
    let ciCount;

    while (allTextLines.length) {
        const line = allTextLines.shift().split(':');
        if (line && line.length && line[0]) {
            lines.push(line);
        }
    }

    if (classifiers.indexOf('RU_REF') > -1) {
        ciCount = lines.length; // each line should be a distinct RU_REF (sampleUnitRef)
    } else if (classifiers.indexOf('FORM_TYPE') > -1) {
        // Put the form types into their own separate array, so we can interrogate it faster
        for (let i = 0; i < lines.length; i++) {
            classifierColumn.push(lines[i][lines[i].length - 2]);
        }

        ciCount = classifierColumn.filter(function(val, i, arr) {
            return arr.indexOf(val) === i;
        }).length;
    }

    window.readCSV.__private__.renderUI(lines.length, ciCount);
};

window.readCSV.handleFiles = function(files, classifiers) {
    if (window.readCSV.__private__.browserHasFileLoaderCapability()) {
        const reader = new FileReader();

        reader.onload = function(evt) {
            window.readCSV.__private__.processFile(evt, classifiers);
        };

        reader.onerror = window.readCSV.__private__.errorHandler;

        reader.readAsText(files[0]);
    } else {
        alerts.warn('Your browser does not support file uploading.  Uploading of samples will not be possible.');
    }
};

window.readCSV.handleFileUpload = function() {
    document.getElementById('btn-upload-sample').classList.add('is-loading');
    document.getElementById('btn-upload-sample').style.pointerEvents = "none";
    document.getElementById('btn-upload-sample').disabled = false;
};
