import struct

def elf(raw):
    assert raw[:6]==b'\x7fELF\x02\x01'
    phoff=struct.unpack_from('<Q',raw,32)[0];phsize,phcount=struct.unpack_from('<HH',raw,54)
    loads=[]
    for i in range(phcount):
        p=phoff+i*phsize
        if struct.unpack_from('<I',raw,p)[0]==1:
            offset,address=struct.unpack_from('<QQ',raw,p+8);alignment=struct.unpack_from('<Q',raw,p+48)[0]
            loads.append({'alignment':alignment,'offsetMatches16k':(address-offset)%16384==0})
    shoff=struct.unpack_from('<Q',raw,40)[0];shsize,shcount=struct.unpack_from('<HH',raw,58)
    sections=[struct.unpack_from('<IIQQQQIIQQ',raw,shoff+i*shsize) for i in range(shcount)]
    def text(table,offset):return table[offset:table.index(b'\0',offset)].decode()
    definitions={}
    for s in sections:
        if s[1]!=0x6ffffffd:continue
        strings=sections[s[6]];table=raw[strings[4]:strings[4]+strings[5]];position=s[4]
        while True:
            version,flags,index,count,hash_,aux,next_=struct.unpack_from('<HHHHIII',raw,position)
            name,_=struct.unpack_from('<II',raw,position+aux)
            if not flags&1:definitions[index]=text(table,name)
            if not next_:break
            position+=next_
    exports=set();versions={};needed=[];soname=None
    for section_index,s in enumerate(sections):
        if s[1] not in (6,11):continue
        strings=sections[s[6]];table=raw[strings[4]:strings[4]+strings[5]]
        version_section=next((v for v in sections if v[1]==0x6fffffff and v[6]==section_index),None)
        for ordinal,p in enumerate(range(s[4],s[4]+s[5],s[9])):
            if s[1]==11:
                name,info,other,index,value,size=struct.unpack_from('<IBBHQQ',raw,p)
                if index and info>>4 in (1,2) and other&3 in (0,3):
                    symbol=text(table,name);exports.add(symbol)
                    version_index=struct.unpack_from('<H',raw,version_section[4]+2*ordinal)[0] if version_section else 1
                    versions[symbol]=(definitions.get(version_index&0x7fff),bool(version_index&0x8000))
            else:
                tag,value=struct.unpack_from('<QQ',raw,p)
                if tag==1:needed.append(text(table,value))
                if tag==14:soname=text(table,value)
    return {'loadSegments':loads,'aligned16k':bool(loads) and all(p['alignment']>=16384 and p['offsetMatches16k'] for p in loads),'exports':exports,'symbolVersions':versions,'versionDefinitions':sorted(definitions.values()),'needed':needed,'soname':soname}
