# -*- coding: utf-8 -*-
import hashlib


# md5加密方法
def get_md5_value(_str):
    if isinstance(_str, str):
        code_url = _str.encode("utf-8")
        m = hashlib.md5()
        m.update(code_url)
        return m.hexdigest()
    else:
        return None
