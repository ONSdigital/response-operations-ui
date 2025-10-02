const path = require('path');

module.exports = {
    entry: {
        selected_ci_functions:  './response_operations_ui/assets/js/selected_ci_functions.js',
		main: [
        './response_operations_ui/assets/js/main.js',
        './response_operations_ui/assets/scss/main.scss'
    ]
	},
    output: {
        path: path.resolve(__dirname, './response_operations_ui/static'), 
        filename: 'js/[name].min.js',
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
                type: "asset/resource",
                use: [
                    {
                        loader: "resolve-url-loader"
                    },
                    {
                        loader: "sass-loader"
                    }
                ]
            }
        ]
    }
};
