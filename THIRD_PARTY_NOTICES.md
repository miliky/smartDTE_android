# Componentes de terceros

Las versiones Python de esta tabla se obtienen de los metadatos del APK distribuido. Los textos conservados se encuentran en `licenses/`. La licencia funcional de smartDTE por NRC es independiente de las licencias de estas bibliotecas.

| Componente | Versión | Licencia indicada por el proyecto | Sitio / código fuente |
|---|---|---|---|
| attrs | 25.3.0 | MIT | [Proyecto](https://www.attrs.org/) |
| chaquopy-freetype | 2.9.1 | FreeType License (FTL) |  |
| chaquopy-libjpeg | 1.5.3 | Véase texto adjunto |  |
| defusedxml | 0.7.1 | PSFL | [Proyecto](https://github.com/tiran/defusedxml) |
| docopt | 0.6.2 | MIT | [Proyecto](http://docopt.org) |
| et_xmlfile | 2.0.0 | MIT | [Proyecto](https://foss.heptapod.net/openpyxl/et_xmlfile) |
| fonttools | 4.55.3 | MIT | [Proyecto](http://github.com/fonttools/fonttools) |
| fpdf2 | 2.8.2 | LGPL-3.0-or-later | [Proyecto](https://py-pdf.github.io/fpdf2/) |
| jsonschema | 4.17.3 | MIT | [Proyecto](https://github.com/python-jsonschema/jsonschema) |
| num2words | 0.5.14 | LGPL | [Proyecto](https://github.com/savoirfairelinux/num2words) |
| openpyxl | 3.1.5 | MIT | [Proyecto](https://openpyxl.readthedocs.io) |
| pillow | 11.0.0 | MIT-CMU | [Proyecto](https://github.com/python-pillow/Pillow/blob/main/CHANGES.rst) |
| pyelftools | 0.26 | Public domain | [Proyecto](https://github.com/eliben/pyelftools) |
| pypdf | 6.1.0 | BSD-3-Clause | [Proyecto](https://github.com/py-pdf/pypdf/issues) |
| pyrsistent | 0.20.0 | MIT | [Proyecto](https://github.com/tobgu/pyrsistent/) |
| qrcode | 8.0 | BSD | [Proyecto](https://github.com/lincolnloop/python-qrcode) |
| rfc3339-validator | 0.1.4 | MIT license | [Proyecto](https://github.com/naimetti/rfc3339-validator) |
| setuptools | 68.2.2 | Véase texto adjunto | [Proyecto](https://github.com/pypa/setuptools) |
| six | 1.17.0 | MIT | [Proyecto](https://github.com/benjaminp/six) |
| xlrd | 2.0.2 | BSD | [Proyecto](http://www.python-excel.org/) |

Otros componentes de la aplicación:

- CPython 3.13: licencia PSF y avisos del runtime; `licenses/python-runtime/PSF-LICENSE.txt`.
- Chaquopy 17.0.0: MIT, [código fuente](https://github.com/chaquo/chaquopy/tree/17.0.0); `licenses/native/CHAQUOPY-MIT.txt`.
- AndroidX: Apache 2.0, [proyecto Android](https://android.googlesource.com/platform/frameworks/support/); `licenses/native/APACHE-2.0.txt`.
- FreeType: partes de este software están protegidas por copyright © The FreeType Project (www.freetype.org). Todos los derechos reservados. Se incluye su licencia en `licenses/native/FREETYPE-FTL.txt`.
- FreeType 2.9.1 y libjpeg-turbo 1.5.3: reconstrucción Android build 3 para alineación de memoria de 16 KB, con la adaptación SONAME de Chaquopy. Fuentes, parches y recetas están identificados en `native-16k-manifest.json` y `NATIVE_LIBRARIES.md`.
- DejaVu / Bitstream Vera: fuente utilizada en documentos; `licenses/fonts/DejaVu-LICENSE.txt`.

Los proyectos y sus versiones publican su código fuente y condiciones en los enlaces indicados. Se conservan los textos de licencia incluidos en los archivos de la aplicación. Las bibliotecas fpdf2 y num2words mantienen sus condiciones LGPL; la distribución de smartDTE no modifica esas bibliotecas.
