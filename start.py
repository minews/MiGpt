#!/usr/bin/env python3
import os
import sys

# 环境变量必须在 import xiaogpt 之前设置，否则 Config dataclass 的默认值无法读取到
os.environ['MI_DID'] = '329996831'

from xiaogpt.cli import main

if __name__ == "__main__":
    main()
