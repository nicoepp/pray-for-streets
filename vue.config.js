module.exports = {
  outputDir: 'dist',
  assetsDir: 'static',
  pages: {
    index: 'src/main.js',
    map: 'src/map.js',
  },
  transpileDependencies: [
    'vuetify',
  ],
  devServer: {
    proxy: {
      '/api*': {
        // Forward frontend dev server request for /api to django dev server
        target: 'http://localhost:8000/',
      },
    },
  },
};
