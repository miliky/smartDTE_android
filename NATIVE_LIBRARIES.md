# Bibliotecas nativas

FreeType 2.9.1 y libjpeg-turbo 1.5.3 fueron reconstruidos desde fuente para páginas de 16 KB, conservando ABI, SONAME y API. [Manifiesto de fuentes y huellas](native-16k-manifest.json). La [receta reproducible](native16k/README.md) y sus parches están en `native16k/`; los archivos descargados y herramientas de compilación se obtienen de las fuentes indicadas, no se incluyen aquí.

El APK se verificó estáticamente y se probó carga/rasterizado/JPEG en una Tab A9 de páginas de 4 KB. La aceptación en hardware de páginas de 16 KB permanece pendiente. Los avisos y licencias están en [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
