import codecs
import re

path = 'taskrebuild/extension/src/popup/components/GraphTab.tsx'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("import React, { useState, useEffect, useCallback, useMemo } from 'react';", "import React, { useState, useEffect, useCallback } from 'react';")

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

def fix_newlines(path):
    with open(path, 'rb') as f:
        file_content = f.read()
    file_content = file_content.replace(b'\r\n', b'\n').replace(b'\r', b'')
    with open(path, 'wb') as f:
        f.write(file_content)
fix_newlines(path)
