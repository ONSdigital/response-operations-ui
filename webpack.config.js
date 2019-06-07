const { join } = require('path');

module.exports = {
    entry: './response_operations_ui/assets/js/main.js',
    output: {
        path: join(__dirname, 'response_operations_ui', 'static', 'js'),
        filename: 'main.min.js'
    },
    devtool: 'source-map',
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
