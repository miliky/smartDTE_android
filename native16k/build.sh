#!/bin/sh
set -eu
cd /work
toolchain_root=${SMARTDTE_TOOLCHAIN_ROOT:-/work/toolchain}
mkdir -p "$toolchain_root" src build out
echo 'a7b54a5de87fecd125a17d54f73c446199e72a64  android-ndk-r28c-linux-complete.zip' | sha1sum --check
python -c "import hashlib,json,pathlib;locked=json.loads(pathlib.Path('sources.lock.json').read_text());assert all(hashlib.sha256(pathlib.Path(name).read_bytes()).hexdigest()==value for name,value in locked.items()),'Source/wheel checksum mismatch'"
if [ ! -f "$toolchain_root/android-ndk-r28c/.smartdte-complete" ]; then
    echo 'Extracting verified Android NDK r28c'
    unzip -oq android-ndk-r28c-linux-complete.zip -d "$toolchain_root"
    touch "$toolchain_root/android-ndk-r28c/.smartdte-complete"
fi
if [ ! -d src/freetype-2.9.1 ]; then tar -xzf freetype-2.9.1.tar.gz -C src; fi
if [ ! -d src/libjpeg-turbo-1.5.3 ]; then
    tar -xzf libjpeg-turbo-1.5.3.tar.gz -C src
    cd src/libjpeg-turbo-1.5.3
    patch -p1 < /work/jpeg-soname.patch
    cd /work
fi
toolchain="$toolchain_root/android-ndk-r28c/toolchains/llvm/prebuilt/linux-x86_64"
for abi in arm64-v8a x86_64; do
    case "$abi" in
        arm64-v8a) triple=aarch64-linux-android ;;
        x86_64) triple=x86_64-linux-android ;;
    esac
    export CC="$toolchain/bin/${triple}21-clang"
    export CXX="$toolchain/bin/${triple}21-clang++"
    export AR="$toolchain/bin/llvm-ar"
    export RANLIB="$toolchain/bin/llvm-ranlib"
    export STRIP="$toolchain/bin/llvm-strip"
    export NM="$toolchain/bin/llvm-nm"
    export CFLAGS='-O2 -fPIC'
    export CPPFLAGS=''
    export LDFLAGS='-Wl,-z,max-page-size=16384 -Wl,-z,common-page-size=16384'
    mkdir -p "build/$abi-freetype" "build/$abi-jpeg" "out/$abi/freetype" "out/$abi/jpeg"
    cd "/work/build/$abi-freetype"
    /work/src/freetype-2.9.1/configure --host="$triple" --prefix="/work/out/$abi/freetype" --without-harfbuzz --without-png
    make -j4
    make install
    cd "/work/build/$abi-jpeg"
    /work/src/libjpeg-turbo-1.5.3/configure --host="$triple" --prefix="/work/out/$abi/jpeg" --without-turbojpeg --without-simd
    make -j4
    make install
    cd /work
    "$toolchain/bin/llvm-readelf" --program-headers --dynamic "out/$abi/freetype/lib/libfreetype.so" > "out/$abi/freetype.elf.txt"
    # libjpeg-turbo uses lib64 on 64-bit targets.
    jpeg=$(find "/work/out/$abi/jpeg" -name libjpeg.so -type f -o -name libjpeg.so -type l | head -n 1)
    test -n "$jpeg"
    "$toolchain/bin/llvm-readelf" --program-headers --dynamic "$jpeg" > "out/$abi/jpeg.elf.txt"
    cp -L "/work/out/$abi/freetype/lib/libfreetype.so" "/work/out/$abi/libfreetype.so"
    cp -L "$jpeg" "/work/out/$abi/libjpeg_chaquopy.so"
    "$STRIP" --strip-unneeded "/work/out/$abi/libfreetype.so" "/work/out/$abi/libjpeg_chaquopy.so"
done
echo 'Native 16KB compilation complete'
