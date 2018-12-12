const { GulpError } = require('./GulpError');

function returnNotImplemented() {
    throw new GulpError('This function is not yet implemented!')
}

module.exports = {
    returnNotImplemented
};
