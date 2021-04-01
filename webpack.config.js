const path = require('path');

module.exports = {
    entry: [
        './response_operations_ui/assets/js/main.js',
        './response_operations_ui/assets/scss/main.scss'
    ],
    output: {
        path: path.resolve(__dirname, './response_operations_ui/static'), 
        filename: 'js/main.min.js',
    },
    devtool: 'source-map',
    module: {
        rules: [
            {
                test: /\.js$/,
                use: {
                    loader: 'babel-loader',
                    options: {
                        presets: ['@babel/preset-env']
                    }
                }
            }, {
                test: /\.(sass|scss|svg|png|jpe?g)$/,
                use: [
                    {
                        loader: 'file-loader',
                        options: { outputPath: 'css', name: 'main.css'}
                    },
                    {
                        loader: "css-loader", options: {
                            sourceMap: true
                        }
                    },
                    {
                        loader: "resolve-url-loader",
                        options: {
                          sourceMap: true
                        }
                    },
                    {
                        loader: "sass-loader", options: {
                            sourceMap: true
                        }
                    }
                ]
            }
        ]
    }
};
