const { resolve } = require('path');

const UglifyJsPlugin = require('uglifyjs-webpack-plugin');

module.exports = {
    entry: resolve(__dirname, 'response_operations_ui', 'assets', 'assets', 'js', 'main.js'),
    output: {
        path: resolve(__dirname, 'response_operations_ui', 'static', 'js'),
        filename: '[name].min.js'
    },
    devtool: 'source-map',
    optimization: {
        minimizer: [new UglifyJsPlugin()],
    },
    module: {
        rules: [{
            test: /\.m?js$/,
            exclude: /(node_modules)/,
            use: {
                loader: 'babel-loader',
                options: {
                    presets: ['@babel/preset-env']
                }
            }
        }]
    }
};
