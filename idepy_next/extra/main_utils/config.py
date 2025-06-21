import json
import os.path

import pydash


# 打包程序配置
class SoftConfig:

    def __init__(self, config_file_path="./config.json"):
        super().__init__()
        self.config_file_path = config_file_path
        self.config = {}
        self.load()

    def load(self):
        if not os.path.exists(self.config_file_path):
            self.config = {}
            return {}
        with open(self.config_file_path, mode='r', encoding='utf8') as f:
            data = f.read()
            data = json.loads(data)
            self.config = data
            f.close()
            return self.config

    def get(self, key_path, default=""):
        return pydash.objects.get(self.config, key_path, default)

    def update(self, key_path, value):
        pydash.objects.update(self.config, key_path, value)
        self.save()
        return True

    def save(self):
        with open(self.config_file_path, mode='w', encoding='utf8') as f:
            f.write(json.dumps(self.config, ensure_ascii=False, indent=4))
            f.close()
        self.load()
