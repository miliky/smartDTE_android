"""Fail a publication build on any non-16KB ELF or unintended native wheel."""
from argparse import ArgumentParser
from pathlib import Path
from io import BytesIO
from zipfile import ZipFile
import hashlib,json
from elf16k import elf

def digest_file(path):
    value=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):value.update(block)
    return value.hexdigest()

def inspect(apk,manifest):
    expected={(r['abi'],r['library']):r for r in manifest['wheels']};found={};rows=[]
    def check(name,raw,abi=None):
        info=elf(raw)
        rows.append({'name':name,'aligned16k':info['aligned16k'],'loadSegments':info['loadSegments']})
        key=(abi,name.rsplit('/',1)[-1])
        if key in expected:
            wanted=expected[key];sha=hashlib.sha256(raw).hexdigest()
            assert key not in found,'Duplicate native library: '+name
            assert sha==wanted['librarySha256'],'Unexpected native library bytes: '+name
            assert info['soname']==wanted['soname'],'Unexpected SONAME: '+name
            assert info['versionDefinitions']==wanted['versionDefinitions'],'Unexpected symbol versions: '+name
            found[key]={'abi':abi,'library':key[1],'sha256':sha,'soname':info['soname']}
    with ZipFile(apk) as outer:
        for name in outer.namelist():
            if name.endswith('.so'):
                parts=name.split('/');check(name,outer.read(name),parts[1] if parts[0]=='lib' else None)
            if name.endswith('.imy'):
                abi=next((abi for abi in ('arm64-v8a','x86_64') if name.endswith('requirements-'+abi+'.imy')),None)
                with ZipFile(BytesIO(outer.read(name))) as inner:
                    for member in inner.namelist():
                        if member.endswith('.so'):check(name+'!'+member,inner.read(member),abi)
    failures=[row for row in rows if not row['aligned16k']]
    assert set(found)==set(expected),'Missing rebuilt native libraries'
    return {'apkSha256':digest_file(apk),'libraries':len(rows),'allLoadSegments16k':not failures,'rebuiltLibraries':list(found.values()),'failures':failures}

if __name__=='__main__':
    parser=ArgumentParser();parser.add_argument('apk',type=Path);parser.add_argument('manifest',type=Path);parser.add_argument('--output',type=Path)
    args=parser.parse_args();report=inspect(args.apk,json.loads(args.manifest.read_text(encoding='utf-8')))
    encoded=json.dumps(report,indent=2)+'\n'
    if args.output:args.output.write_text(encoded,encoding='utf-8')
    print(encoded)
    if not report['allLoadSegments16k']:raise SystemExit('Native ELF alignment must be corrected before publication')
