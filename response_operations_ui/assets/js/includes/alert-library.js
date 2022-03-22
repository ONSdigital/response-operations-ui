(function(window) {
    const publicFunctions = {};
    const privateFunctions = {};

    privateFunctions._getErrorContainer = function() {
        return document.getElementById('error-alerts');
    };

    privateFunctions._clearAlerts = function() {
        privateFunctions._getErrorContainer().innerHTML = '';
    };

    privateFunctions._getPanelTemplateHtml = function(title, message, panelClass) {
        let markUp = '';

        markUp += '<div class="ons-u-mt-l ons-panel ons-panel--' + (panelClass || 'error') + '">';
        markUp += '    <div class="ons-panel__header">';
        markUp += '        <div class="ons-u-fs-r--b">' + title + '</div>';
        markUp += '    </div>';
        markUp += '    <div class="ons-panel__body">';
        markUp += '        <div>' + message + '</div>';
        markUp += '    </div>';
        markUp += '</div>';

        return markUp;
    };

    privateFunctions._getSimplePanelTemplateHtml = function(message, panelClass) {
        let markUp = '';

        markUp += '<div class="ons-u-mt-l ons-panel ons-panel--simple ons-panel--' + (panelClass || 'error') + '">';
        markUp += '    <div class="ons-panel__body">';
        markUp += '        <div>' + message + '</div>';
        markUp += '    </div>';
        markUp += '</div>';

        return markUp;
    };


    privateFunctions._showAlert = function(title, message, className) {
        privateFunctions._clearAlerts();

        if (title) {
            return privateFunctions._getErrorContainer().innerHTML = privateFunctions._getPanelTemplateHtml(title, message, className || false);
        }

        return privateFunctions._getErrorContainer().innerHTML = privateFunctions._getSimplePanelTemplateHtml(message, className || false);
    };


    ['success', 'error', 'warn', 'info'].forEach(function(alertFunctionName) {
        publicFunctions[alertFunctionName] = function(title, message) {
            privateFunctions._showAlert(title, message, alertFunctionName);
        };
    });

    // Add all public functions to global object
    window.alerts = {
        __private__: {}
    };
    Object.keys(publicFunctions).forEach(function(key) {
        window.alerts[key] = publicFunctions[key];
    });
    Object.keys(privateFunctions).forEach(function(key) {
        window.alerts.__private__[key] = privateFunctions[key];
    });
}(window));
