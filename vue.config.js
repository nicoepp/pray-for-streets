module.exports = {
  outputDir: 'dist',
  assetsDir: 'static',
  pages: {
    app: 'src/main.js',
    mapapp: 'src/map.js',
    champion: 'src/champion.js',
  },
  transpileDependencies: [
    'vuetify',
  ],
  devServer: {
    proxy: {
      '/api/*': {
        // Forward frontend dev server request for /api to django dev server
        target: 'http://localhost:8000/',
      },
    },
  },
};
