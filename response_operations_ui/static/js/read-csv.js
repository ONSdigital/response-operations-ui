(function(window) {
    function drawOutput(businessCount, ciCount) {
        // Clear previous data
        document.getElementById('sample-preview').innerHTML = '';

        let preview = '';
        preview += '<div class=\'panel panel--info\'>';
        preview += '  <div class=\'panel__header\'>';
        preview += '    <h3 class=\'u-fs-r--b\'>Sample contents</h3>';
        preview += '  </div>';
        preview += '  <div class=\'panel__body\'>';
        preview += '    <div id=\'sample-preview-businesses\'>Number of businesses: ' + businessCount + '</div>';
        preview += '    <div id=\'sample-preview-ci\'>Collection instruments: ' + ciCount + '</div>';
        preview += '  </div>';
        preview += '</div>';

        document.getElementById('sample-preview').innerHTML = preview;
        document.getElementById('btn-check-sample-contents').style.display = 'none';
        document.getElementById('btn-load-sample').style.display = 'inline-block';
        document.getElementById('btn-cancel-load-sample').style.display = 'inline-block';
    }

    function errorHandler(evt) {
        if (evt.target.error.name == 'NotReadableError') {
            alerts.error('Error Uploading file', 'The selected file was not readable.');
        }
    }

    function handleFiles(files, classifiers) {
        if (_browserHasFileLoaderCapability()) {
            const reader = new FileReader();

            reader.onload = function(evt) {
                processFile(evt, classifiers);
            };

            reader.onerror = errorHandler;

            reader.readAsText(files[0]);
        } else {
            alerts.warn('Your browser does not support file uploading.  Uploading of samples will not be possible.');
        }
    }

    function processFile(event, classifiers) {
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

        drawOutput(lines.length, ciCount);
    }

    function cancelLoadSample() {
        document.getElementById('sample-preview').innerHTML = '';
        document.getElementById('form-load-sample').reset();
        document.getElementById('btn-check-sample-contents').style.display = 'block';
        document.getElementById('btn-load-sample').style.display = 'none';
        document.getElementById('btn-cancel-load-sample').style.display = 'none';
        $('#file').focus();
    }

    function _browserHasFileLoaderCapability() {
        return window.hasOwnProperty('FileReader');
    }

    window.handleFiles = handleFiles;
    window.cancelLoadSample = cancelLoadSample;
}(window));
