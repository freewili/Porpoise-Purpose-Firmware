"""Validate a release folder and create reproducible GitHub release assets."""
import hashlib, json, re, struct, sys, zipfile
from pathlib import Path

PRODUCT = 'Porpoise-Purpose'
MAX_UF2 = 16 * 1024 * 1024 + 512

def require(ok, message):
    if not ok:
        raise ValueError(message)

def image_version(data):
    require(0 < len(data) <= MAX_UF2 and len(data) % 512 == 0, 'Invalid UF2 size')
    blocks, indexes, total, workaround = {}, set(), None, False
    for offset in range(0, len(data), 512):
        magic, magic2, flags, address, size, index, count, family = struct.unpack_from('<8I', data, offset)
        require((magic, magic2, struct.unpack_from('<I', data, offset+508)[0]) == (0x0a324655,0x9e5d5157,0x0ab16f30), 'Invalid UF2 magic')
        require(size == 256 and address % 256 == 0, 'Invalid UF2 alignment')
        payload = data[offset+32:offset+288]
        if flags == 0xa000:
            require(not workaround and (family,address,index,count) == (0xe48bff57,0x107fff00,0,2) and payload == b'\xef'*256, 'Invalid RP2350-E10 record')
            workaround = True
            continue
        require(flags == 0x2000 and family == 0xe48bff59, 'Wrong UF2 family or flags')
        require(0x10000000 <= address and address+256 <= 0x10800000, 'UF2 writes outside firmware flash')
        if total is None:
            total = count
        require(0 < count <= MAX_UF2//512 and count == total and index < count and index not in indexes and address not in blocks, 'Incomplete or overlapping UF2')
        indexes.add(index)
        blocks[address] = payload
    require(0x10000000 in blocks and len(indexes) == total, 'Missing UF2 blocks or image start')
    require(not workaround or max(blocks) < 0x107ff000, 'Firmware overlaps the RP2350 workaround sector')
    payload, next_address = bytearray(), 0
    for address, block in sorted(blocks.items()):
        if address != next_address:
            payload += b'\0'
        payload += block
        next_address = address + 256
    own = rb'(?:WILi Industrial|WILiIndustrial)' if PRODUCT == 'T1Sim' else rb'WILiProbe'
    other = rb'(?:WILiProbe|Probe)' if PRODUCT == 'T1Sim' else rb'(?:WILi Industrial|WILiIndustrial)'
    versions = set(re.findall(own + rb' (v[0-9][A-Za-z0-9._-]*)', payload))
    require(len(versions) == 1 and not re.search(other + rb' v',payload) and b'FW2 v' not in payload, 'Wrong board or ambiguous firmware version')
    return versions.pop().decode('ascii')

def validate(folder):
    folder = Path(folder)
    manifest = json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
    tag = manifest['release']
    require(re.fullmatch(r'v[0-9][A-Za-z0-9.-]{0,78}',tag) and folder.name == tag, 'Invalid release identity')
    require(manifest['schema'] == 1 and manifest['product'] == PRODUCT and manifest['title'], 'Wrong manifest product or schema')
    require(len(manifest['files']) == 1, 'Expected one firmware image')
    image = manifest['files'][0]
    expected = f'firmware/{PRODUCT}.uf2'
    require(image['component'] == 'main' and image['file'] == expected, 'Invalid firmware path')
    allowed = {'manifest.json','README.md',expected}
    actual = {p.relative_to(folder).as_posix() for p in folder.rglob('*') if p.is_file()}
    require(actual == allowed and not any(p.is_symlink() for p in folder.rglob('*')), 'Unexpected release files or symlinks')
    require((folder/'README.md').stat().st_size <= 65536 and (folder/'manifest.json').stat().st_size <= 65536, 'Release metadata too large')
    data = (folder/expected).read_bytes()
    require(len(data) == image['size'] and hashlib.sha256(data).hexdigest() == image['sha256'], 'Firmware checksum mismatch')
    require(image_version(data) == image['version'], 'Firmware version mismatch')
    return manifest, sorted(actual)

def package(folder, output=Path('dist')):
    folder, output = Path(folder), Path(output)
    manifest, files = validate(folder)
    output.mkdir(parents=True, exist_ok=True)
    tag = manifest['release']
    archive = output/f'{PRODUCT}-{tag}.zip'
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name in files:
            info = zipfile.ZipInfo(name,(2020,1,1,0,0,0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info,(folder/name).read_bytes(),compresslevel=9)
    checksum = f'{hashlib.sha256(archive.read_bytes()).hexdigest()}  {archive.name}\n'
    (output/(archive.name+'.sha256')).write_text(checksum,encoding='utf-8',newline='\n')
    image = manifest['files'][0]
    checksum += f"{image['sha256']}  {Path(image['file']).name}\n"
    (output/f'checksums-{tag}.txt').write_text(checksum,encoding='utf-8',newline='\n')
    return archive

if __name__ == '__main__':
    print(package(sys.argv[1]))
