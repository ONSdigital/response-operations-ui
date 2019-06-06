const UglifyJsPlugin = require('uglifyjs-webpack-plugin')

module.exports = {
    devtool: 'source-map',
    optimization: {
        minimizer: [new UglifyJsPlugin()],
    },
};
