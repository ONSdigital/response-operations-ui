(function(window) {
    function checkCI(file) {
        const type = file.type;
        const errorPanel = document.getElementById('ciFileErrorPanel');
        const errorPanelBody = document.getElementById('ciFileErrorPanelBody');

        if ( type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' ) {
            errorPanel.classList.remove('panel');
            errorPanel.classList.remove('panel--simple');
            errorPanel.classList.remove('panel--error');

            errorPanelBody.classList.remove('panel__body');

            // Create array from NodeList
            paragraphsToRemoveClassFrom = Array.prototype.slice.call(errorPanelBody.querySelectorAll('p'));

            // Iterate array of DOM elements to remove hidden class from child paragraphs
            paragraphsToRemoveClassFrom.forEach(function(element) {
                element.classList.add('hidden');
            });

            document.getElementById('btn-load-ci').classList.remove('unready');
        } else {
            errorPanel.classList.add('panel');
            errorPanel.classList.add('panel--simple');
            errorPanel.classList.add('panel--error');

            errorPanelBody.classList.add('panel__body');
            paragraphsToAddClassTo = Array.prototype.slice.call(errorPanelBody.querySelectorAll('p'));

            paragraphsToAddClassTo.forEach(function(element) {
                element.classList.remove('hidden');
            });

            document.getElementById('btn-load-ci').classList.add('unready');
        }
    }

    function checkSelectedCI(files) {
        // Check for the various File API support.
        if (window.FileReader) {
            // FileReader are supported.
            checkCI(files[0]);
        }
    }

    window.checkCI = checkCI;
    window.checkSelectedCI = checkSelectedCI;
}(window));

