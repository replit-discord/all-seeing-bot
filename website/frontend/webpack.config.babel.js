import path from "path";
import VueLoaderPlugin from "vue-loader/lib/plugin";
import HtmlWebpackPlugin from "html-webpack-plugin";
import MiniCssExtractPlugin from "mini-css-extract-plugin";

export default {
  mode: process.env.NODE_ENV === "development" ? "development" : "production",
  entry: "./src/index.js",
  output: {
    path: path.resolve(__dirname, "dist"),
    filename: "output.js"
  },
  plugins: [
    new VueLoaderPlugin(),
    new HtmlWebpackPlugin({
      template: "./index.html"
    }),
    new MiniCssExtractPlugin()
  ],
  resolve: {
    extensions: [".vue", ".ts", ".js"]
  },
  devServer: {
    port: 8081,
    compress: true,
    historyApiFallback: true,
    progress: true,
    proxy: {
      "/api": "http://localhost:3000",
      "/is-authenticated": "http://localhost:3000",
      "/user": "http://localhost:3000"
    }
  },
  module: {
    rules: [
      {
        test: /\.(js)$/,
        loader: "babel-loader",
        exclude: /node_modules/
      },
      {
        test: /\.postcss$/,
        use: [
          process.env.NODE_ENV === "development" ? "style-loader" : MiniCssExtractPlugin.loader,
          "postcss-loader",
          {
            loader: "sass-resources-loader",
            options: {
              resources: "./variables.css"
            }
          }
        ]
      },
      {
        test: /\.css$/,
        use: [
          process.env.NODE_ENV === "development" ? "style-loader" : MiniCssExtractPlugin.loader,
          "css-loader"
        ]
      },
      {
        test: /\.vue$/,
        loader: "vue-loader"
      },
      {
        test: /\.(png|svg|jpg|gif)$/,
        loader: "file-loader"
      },
      {
        test: /\.(woff|woff2|eot|ttf|otf)$/,
        loader: "file-loader"
      }
    ]
  }
};

