(function(window) {
    function nodeClassesChange(node, classes, action) {
        if (!(node instanceof HTMLElement)) throw new Error('Expected HTMLElement as first argument');

        if (!Array.isArray(classes)) throw new Error('Expected Array as second argument');

        if (!['add', 'remove'].includes(action)) throw new Error('Expected add or remove as third parameter');

        classes.map(c => node.classList[action](c));
    }

    function arrayLikeToArray(arrayLike) {
        if (!arrayLike.hasOwnProperty('length') && !arrayLike.hasOwnProperty('size')) throw new Error('Expected array like object');

        return Array.prototype.slice.call(arrayLike);
    }

    function checkCI(file) {
        const type = file.type;
        const errorPanel = document.getElementById('ciFileErrorPanel');
        const errorPanelBody = document.getElementById('ciFileErrorPanelBody');
        const button = document.getElementById('btn-load-ci');

        const fileIsODS = type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';
        const mainAction = fileIsODS ? 'remove' : 'add';
        const buttonAction = fileIsODS ? 'remove' : 'add';

        nodeClassesChange(errorPanel, ['panel', 'panel--simple', 'panel--error'], mainAction);
        nodeClassesChange(errorPanelBody, ['panel', 'panel--simple', 'panel--error'], mainAction);
        nodeClassesChange(button, ['unready'], buttonAction);

        arrayLikeToArray(errorPanelBody.querySelectorAll('p')).forEach(el => {
            nodeClassesChange(el, ['hidden'], mainAction);
        });
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
        nodeClassesRemove: nodeClassesChange,
        arrayLikeToArray: arrayLikeToArray
    };
}(window));

