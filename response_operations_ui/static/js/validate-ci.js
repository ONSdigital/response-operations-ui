window.validateCI = {
    __private__: {
        nodeClassesChange: function nodeClassesChange(node, classes, action) {
            if (typeof classes === 'string') classes = [classes];

            if (!(node instanceof HTMLElement)) throw new Error('Expected HTMLElement as first argument');

            if (!Array.isArray(classes)) throw new Error('Expected Array as second argument');

            if (['add', 'remove'].indexOf(action) === -1) throw new Error('Expected add or remove as third parameter');

            classes.map(c => node.classList[action](c));
        },

        arrayLikeToArray: function arrayLikeToArray(arrayLike) {
            if (!('length' in arrayLike) && !('size' in arrayLike)) throw new Error('Expected array-like object as argument');

            return Array.prototype.slice.call(arrayLike);
        },
    },

    checkCI: function checkCI(file) {
        const type = file.type;
        const errorPanel = document.getElementById('ciFileErrorPanel');
        const errorPanelBody = document.getElementById('ciFileErrorPanelBody');
        const button = document.getElementById('btn-load-ci');

        const fileIsODS = type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';
        const mainAction = fileIsODS ? 'remove' : 'add';
        const buttonAction = fileIsODS ? 'add' : 'remove';

        this.__private__.nodeClassesChange(errorPanel, ['panel', 'panel--simple', 'panel--error'], mainAction);
        this.__private__.nodeClassesChange(errorPanelBody, ['panel', 'panel--simple', 'panel--error'], mainAction);
        this.__private__.nodeClassesChange(button, ['unready'], buttonAction);

        this.__private__.arrayLikeToArray(errorPanelBody.querySelectorAll('p')).forEach(el => {
            this.__private__.nodeClassesChange(el, ['hidden'], mainAction);
        });
    },

    checkSelectedCI: function checkSelectedCI(files) {
        // Check for the various File API support.
        if (window.FileReader) {
            // FileReader is supported.
            validateCI.checkCI(files[0]);
        }
    }
};
