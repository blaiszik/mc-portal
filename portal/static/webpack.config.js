var webpack = require('webpack');  
module.exports = {  
  entry: [
    "./js/app.js"
  ],
  output: {
    path: __dirname + '/dist',
    filename: "bundle.js"
  },
  module: {
    loaders: [
      {
        test: /\.js?$/,
        loader: 'babel-loader',
        query: {
          presets: ['es2015', 'react', 'stage-0']
        },
        exclude: /node_modules/
      }
    ]
  },
  plugins: [
  ]
};
