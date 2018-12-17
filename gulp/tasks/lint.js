const { registerTask } = require('../gulpHelper');

module.exports = (context) => {
    registerTask(context, ['lint'], ['csslint', 'jslint']);
};
