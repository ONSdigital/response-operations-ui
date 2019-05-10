(function(window) {
    function nodeClassesChange(node, classes, action) {
        if (!(node instanceof HTMLElement)) throw new Error('Expected HTMLElement as first argument');

        if (!Array.isArray(classes)) throw new Error('Expected Array as second argument');

        if (!['add', 'remove'].includes(action)) throw new Error('Expected add or remove as third parameter');

        classes.map(c => node.classList[action](c));
    }

    function checkCI(file) {
        const type = file.type;
        const errorPanel = document.getElementById('ciFileErrorPanel');
        const errorPanelBody = document.getElementById('ciFileErrorPanelBody');

        const action = (type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet') ? 'remove' : 'add';
//TODO pick up here
        if ( type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' ) {
            nodeClassesRemove(errorPanel, ['panel', 'panel--simple', 'panel--error']);
            nodeClassesRemove(errorPanelBody, ['panel__body']);

            // Create array from NodeList
            paragraphsToRemoveClassFrom = Array.prototype.slice.call(errorPanelBody.querySelectorAll('p'));

            // Iterate array of DOM elements to remove hidden class from child paragraphs
            paragraphsToRemoveClassFrom.forEach(function(element) {
                nodeClassesAdd(element, ['hidden']);
            });

            nodeClassesRemove(document.getElementById('btn-load-ci'), ['unready']);
        } else {
            nodeClassesAdd(errorPanel, ['panel', 'panel--simple', 'panel--error']);

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
    window.__private__ = {
        nodeClassesRemove: nodeClassesChange
    };
}(window));

