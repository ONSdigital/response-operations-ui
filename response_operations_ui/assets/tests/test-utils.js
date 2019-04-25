/**
 * Useful functions for UI testing
 */

module.exports = {};

module.exports.clickElement = (element) => {
    const event = document.createEvent('HTMLEvents');
    event.initEvent('click', false, true);
    element.dispatch(event);
};
