import os
import struct
import io
import mimetypes
import threading

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
class InvalidPasswordError(Exception):
    pass
class ResourcePack:


    def __init__(self, filepath=None, magic=b'RPACK1.0', password=None):
        """
        :param filepath: 资源包文件路径
        :param magic: 文件格式魔数 bytes，默认 b'RPACK1.0'
        :param password: AES加密密码，None表示不加密
        """
        self.filepath = filepath
        self.magic = magic
        self.password = password
        self.fp = None
        self.index = {}   # {filename: (offset, length)}
        self.data_start = 0
        self._lock = threading.Lock()
        if filepath:
            self.load(filepath)

    def _aes_encrypt(self, data):
        key = self._derive_key(self.password)
        iv = b'\x00' * 16  # 你也可以使用 os.urandom(16)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        padded_data = pad(data, AES.block_size)
        return cipher.encrypt(padded_data)

    def _aes_decrypt(self, data):
        key = self._derive_key(self.password)
        iv = b'\x00' * 16
        cipher = AES.new(key, AES.MODE_CBC, iv)
        try:
            padded_data = cipher.decrypt(data)
            return unpad(padded_data, AES.block_size)
        except ValueError as e:
            raise InvalidPasswordError("请确保资源包密码正确。") from e

    def _derive_key(self, password):
        # 简单示范，密码utf8编码后截取或补全32字节为AES256密钥
        bpass = password.encode('utf-8')
        if len(bpass) >= 32:
            return bpass[:32]
        return bpass.ljust(32, b'\0')

    def load(self, path):
        self.fp = open(path, 'rb')
        magic_read = self.fp.read(len(self.magic))
        if magic_read != self.magic:
            raise ValueError("Invalid resource pack file magic header")
        file_count = struct.unpack('<I', self.fp.read(4))[0]
        self.index = {}
        for _ in range(file_count):
            name_len = struct.unpack('<B', self.fp.read(1))[0]

            name = self.fp.read(name_len).decode('utf-8')
            offset, length = struct.unpack('<II', self.fp.read(8))
            self.index[name] = (offset, length)
        self.data_start = self.fp.tell()

    def pack(self, folder_path, output_path):
        files = []
        for root, dirs, filenames in os.walk(folder_path):
            for name in filenames:
                full_path = os.path.join(root, name)
                rel_path = os.path.relpath(full_path, folder_path).replace('\\', '/')
                with open(full_path, 'rb') as f:
                    content = f.read()
                if self.password:
                    content = self._aes_encrypt(content)
                files.append((rel_path, content))

        with open(output_path, 'wb') as out:
            out.write(self.magic)
            out.write(struct.pack('<I', len(files)))

            offset = 0
            index_data = b''
            for path, content in files:
                encoded_path = path.encode('utf-8')
                index_data += struct.pack('<B', len(encoded_path)) + encoded_path
                index_data += struct.pack('<II', offset, len(content))
                offset += len(content)
            out.write(index_data)

            for _, content in files:
                out.write(content)

    def read(self, path):
        if path.startswith('/'):
            path = path[1:]
        if path not in self.index:
            return None
        offset, length = self.index[path]
        with self._lock:
            self.fp.seek(self.data_start + offset)
            data = self.fp.read(length)
        if self.password:
            # print("读取文件", path)
            data = self._aes_decrypt(data)
        return data

    def open(self, path):
        content = self.read(path)
        if content is None:
            return None
        return io.BytesIO(content)

    def list_files(self):
        return list(self.index.keys())

    def close(self):
        if self.fp:
            self.fp.close()
            self.fp = None



if __name__ == '__main__':

    rp = ResourcePack(password='yourpassword123')

    # 打包示例：
    rp.pack('./static/src', 'static.rpak')

    # 加载资源包
    rp.load('static.rpak')

    print(rp.list_files())