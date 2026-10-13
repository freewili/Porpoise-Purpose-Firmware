import copy, hashlib, json, struct, tempfile, unittest
from pathlib import Path
from package_release import PRODUCT, image_version, package, validate

def uf2(identity):
    data = bytearray(1024)
    for index in range(2):
        struct.pack_into('<8I',data,index*512,0x0a324655,0x9e5d5157,0x2000,0x10000000+index*256,256,index,2,0xe48bff59)
        struct.pack_into('<I',data,index*512+508,0x0ab16f30)
    data[32:32+len(identity)] = identity
    return data

class Packaging(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.folder = self.root/'v1'
        (self.folder/'firmware').mkdir(parents=True)
        self.data = uf2(b'WILi Industrial v01' if PRODUCT == 'T1Sim' else b'WILiProbe v1')
        self.path = f'firmware/{PRODUCT}.uf2'
        self.manifest = dict(schema=1,product=PRODUCT,release='v1',title='Test',files=[dict(component='main',file=self.path,size=len(self.data),sha256=hashlib.sha256(self.data).hexdigest(),version=image_version(self.data))])
        (self.folder/self.path).write_bytes(self.data)
        (self.folder/'README.md').write_text('Test release')
        self.save()
    def tearDown(self):
        self.temp.cleanup()
    def save(self):
        (self.folder/'manifest.json').write_text(json.dumps(self.manifest))
    def test_valid_and_reproducible(self):
        first = package(self.folder,self.root/'a').read_bytes()
        self.assertEqual(first,package(self.folder,self.root/'b').read_bytes())
    def test_wrong_product(self):
        self.manifest['product']='Other'; self.save()
        with self.assertRaises(ValueError): validate(self.folder)
    def test_hash_and_version(self):
        for field,value in [('sha256','0'*64),('version','v999')]:
            old = self.manifest['files'][0][field]
            self.manifest['files'][0][field]=value; self.save()
            with self.assertRaises(ValueError): validate(self.folder)
            self.manifest['files'][0][field]=old
    def test_wrong_board(self):
        with self.assertRaises(ValueError): image_version(uf2(b'WILiProbe v1' if PRODUCT == 'T1Sim' else b'WILi Industrial v01'))
    def test_data_partition_and_incomplete(self):
        data=copy.copy(self.data); struct.pack_into('<I',data,512+12,0x10800000)
        with self.assertRaises(ValueError): image_version(data)
        with self.assertRaises(ValueError): image_version(self.data[:512])
    def test_extra_file(self):
        (self.folder/'extra.txt').write_text('x')
        with self.assertRaises(ValueError): validate(self.folder)
if __name__ == '__main__': unittest.main()
