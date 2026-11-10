# Bibliotecas Pillow compatibles con páginas de 16 KB

Se reconstruyen FreeType 2.9.1 y libjpeg-turbo 1.5.3 desde sus fuentes C,
con el Android NDK r28c (28.2.13676358), conservando versiones, API 21, ABI
arm64-v8a/x86_64 y SONAME que esperan los wheels oficiales de Chaquopy.
No se alteran segmentos ELF ni instrucciones de bibliotecas precompiladas.

`build.sh` aplica los mismos parámetros de las recetas Chaquopy: FreeType sin
HarfBuzz/PNG y JPEG sin TurboJPEG/SIMD. El parche `jpeg-soname.patch` procede de
Chaquopy y se aplica al `configure` de la fuente antes de compilar, para conservar
`libjpeg_chaquopy.so`. Ambos enlaces usan `-z max-page-size=16384` y
`-z common-page-size=16384`. `llvm-strip` elimina símbolos de depuración, como
parte de una compilación normal.

## Reconstrucción

1. Descargar las fuentes/wheels oficiales indicadas por el manifiesto y verificar
   `sources.lock.json`. Conservar exactamente sus nombres. Los wheels originales
   aportan encabezados/licencias y la referencia de metadatos/API, no los nuevos ELF.
2. Descargar `https://dl.google.com/android/repository/android-ndk-r28c-linux.zip`
   como `android-ndk-r28c-linux-complete.zip`. `build.sh` comprueba el SHA-1 oficial
   `a7b54a5de87fecd125a17d54f73c446199e72a64` antes de extraerlo.
3. Desde esta carpeta, construir el contenedor y montar exclusivamente esta carpeta:

   ```powershell
   docker build -t smartdte-native16k-builder:local .
   docker volume create smartdte-native16k-toolchain-r28c
   docker run --rm -v "${PWD}:/work" -v smartdte-native16k-toolchain-r28c:/toolchain `
     -e SMARTDTE_TOOLCHAIN_ROOT=/toolchain smartdte-native16k-builder:local sh /work/build.sh
   python repack.py
   ```

4. `export/wheels` contiene cuatro wheels build **3**. `repack.py` conserva los
   archivos oficiales, sustituye únicamente cada biblioteca por el ELF recién
   compilado, actualiza WHEEL/RECORD y usa fechas ZIP deterministas. Comprueba
   segmentos PT_LOAD, SONAME y símbolos anteriores. El manifiesto registra
   cualquier dependencia de sistema que lld haya dejado de enlazar por no usarla.
5. Incorporar los cuatro wheels a `tools/wheels` de Android y añadir los paquetes
   explícitos en el bloque Gradle **pip de Android**, manteniendo el archivo de
   requisitos de Python host sin dependencias exclusivas de Android. Los build 3
   locales tienen prioridad sobre los build 1/2 del índice con igual versión.
6. Reconstruir el APK y verificar que las cuatro bibliotecas extraídas coincidan
   con SHA-256 de `native-16k-manifest.json`; comprobar todos los ELF y ZIP 16 KB.
   Ejecutar `NativeImageTests` en Android para cargar FreeType, dibujar texto y
   guardar/leer JPEG con las bibliotecas realmente empaquetadas.

La estructura ELF y una prueba funcional en un dispositivo de páginas de 4 KB
son evidencias distintas de ejecutar la app en un dispositivo/emulador de 16 KB.
Registrar esa aceptación por separado cuando se realice.

Fuentes primarias: recetas
[FreeType](https://github.com/chaquo/chaquopy/tree/master/server/pypi/packages/chaquopy-freetype)
y [libjpeg](https://github.com/chaquo/chaquopy/tree/master/server/pypi/packages/chaquopy-libjpeg),
[descargas oficiales NDK](https://github.com/android/ndk/wiki/Unsupported-Downloads#r28c)
y [páginas Android 16 KB](https://developer.android.com/guide/practices/page-sizes).
