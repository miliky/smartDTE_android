"""Repackage freshly compiled libraries, preserving official wheel ABI/metadata.

No binary modification is performed here. Libraries are built from upstream C
sources by build.sh with the Android NDK and the official Chaquopy SONAME recipe.
"""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from io import StringIO
import base64,copy,csv,hashlib,json,re,struct
ROOT=Path(__file__).parent
OUTPUT=ROOT/'export';WHEELS=OUTPUT/'wheels';WHEELS.mkdir(parents=True,exist_ok=True)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def file_sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()
from elf16k import elf
rows=[]
for abi,tag in [('arm64-v8a','arm64_v8a'),('x86_64','x86_64')]:
    for name,version,original_build,library in [('freetype','2.9.1',2,'libfreetype.so'),('libjpeg','1.5.3',1,'libjpeg_chaquopy.so')]:
        distribution='chaquopy_'+name
        original=ROOT/f'{distribution}-{version}-{original_build}-py3-none-android_21_{tag}.whl'
        compiled=ROOT/'out'/abi/library
        raw=compiled.read_bytes();current=elf(raw)
        with ZipFile(original) as wheel:
            contents={n:wheel.read(n) for n in wheel.namelist()}
            entries={info.filename:copy.copy(info) for info in wheel.infolist()}
        native='chaquopy/lib/'+library;before=elf(contents[native])
        assert current['aligned16k'],(library,abi,current['loadSegments'])
        assert before['soname']==current['soname']==library,(before['soname'],current['soname'])
        missing=before['exports']-current['exports']
        # GNU ld exposes version namespace labels as synthetic ABS symbols; lld
        # keeps the actual GNU version definitions without those labels. Preserve
        # all API names and their real symbol versions, rather than linker labels.
        synthetic={'_edata','_end','__bss_start','__bss_start__','_bss_end__','__bss_end__','__end__',*before['versionDefinitions']}
        assert current['versionDefinitions']==before['versionDefinitions'],(library,abi,current['versionDefinitions'],before['versionDefinitions'])
        assert not missing-synthetic,(library,abi,sorted(missing))
        for symbol in before['exports']-synthetic:
            assert before['symbolVersions'][symbol]==current['symbolVersions'][symbol],(library,abi,symbol,before['symbolVersions'][symbol],current['symbolVersions'][symbol])
        # Modern lld can omit unused system dependencies emitted by older NDKs.
        assert set(current['needed'])<=set(before['needed']),(library,abi,current['needed'],before['needed'])
        contents[native]=raw
        wheel_name=next(n for n in contents if n.endswith('/WHEEL'))
        metadata=contents[wheel_name].decode()
        metadata=re.sub(r'^Build: \d+$','Build: 3',metadata,flags=re.M)
        metadata=re.sub(r'^Generator: .*$', 'Generator: smartDTE native16k (NDK r28c source rebuild)',metadata,flags=re.M)
        contents[wheel_name]=metadata.encode()
        record=next(n for n in contents if n.endswith('/RECORD'));contents.pop(record)
        output=StringIO();writer=csv.writer(output,lineterminator='\n')
        for n,data in sorted(contents.items()):writer.writerow([n,'sha256='+base64.urlsafe_b64encode(hashlib.sha256(data).digest()).decode().rstrip('='),len(data)])
        writer.writerow([record,'','']);contents[record]=output.getvalue().encode()
        target=WHEELS/f'{distribution}-{version}-3-py3-none-android_21_{tag}.whl'
        with ZipFile(target,'w',ZIP_DEFLATED) as wheel:
            for n,data in sorted(contents.items()):
                info=entries[n];info.date_time=(2026,11,9,0,0,0);info.compress_type=ZIP_DEFLATED
                wheel.writestr(info,data)
        rows.append({'abi':abi,'library':library,'version':version,'wheel':target.name,'wheelSha256':sha(target.read_bytes()),'sourceWheel':original.name,'sourceWheelSha256':sha(original.read_bytes()),'librarySha256':sha(raw),'soname':current['soname'],'needed':current['needed'],'unusedSystemDependenciesOmitted':sorted(set(before['needed'])-set(current['needed'])),'exportsPreserved':len(before['exports'])-len(missing),'apiSymbolVersionsPreserved':True,'versionDefinitions':current['versionDefinitions'],'linkerSyntheticSymbolsOmitted':sorted(missing),'loadSegments':current['loadSegments']})
sources=[]
for filename,url in [('freetype-2.9.1.tar.gz','https://download.savannah.gnu.org/releases/freetype/freetype-2.9.1.tar.gz'),('libjpeg-turbo-1.5.3.tar.gz','https://downloads.sourceforge.net/project/libjpeg-turbo/1.5.3/libjpeg-turbo-1.5.3.tar.gz'),('jpeg-soname.patch','https://raw.githubusercontent.com/chaquo/chaquopy/master/server/pypi/packages/chaquopy-libjpeg/patches/soname.patch')]:
    sources.append({'file':filename,'url':url,'sha256':sha((ROOT/filename).read_bytes())})
ndk=ROOT/'android-ndk-r28c-linux-complete.zip'
result={'ndk':{'version':'28.2.13676358','url':'https://dl.google.com/android/repository/android-ndk-r28c-linux.zip','officialSha1':'a7b54a5de87fecd125a17d54f73c446199e72a64','sha256':file_sha(ndk)},'linkerFlags':['-Wl,-z,max-page-size=16384','-Wl,-z,common-page-size=16384'],'sourceRebuild':True,'sources':sources,'wheels':rows}
(OUTPUT/'native-16k-manifest.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'wheels':len(rows),'all16k':True,'output':str(OUTPUT)},indent=2))
