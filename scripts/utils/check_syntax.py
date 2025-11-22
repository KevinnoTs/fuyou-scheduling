#!/usr/bin/env python3
try:
    with open('database_init_data.py', 'r', encoding='utf-8') as f:
        content = f.read()

    compile(content, 'database_init_data.py', 'exec')
    print(" 语法检查通过！")
except SyntaxError as e:
    print(f" 语法错误在第{e.lineno}行: {e.msg}")
    print(f"错误行内容: {e.text.strip() if e.text else 'N/A'}")
    print()
    print("错误附近的代码:")
    lines = content.split('\n')
    start = max(0, e.lineno - 3)
    end = min(len(lines), e.lineno + 2)
    for i in range(start, end):
        prefix = ">>> " if i == e.lineno - 1 else "    "
        print(f"{prefix}{i+1:3d}: {lines[i]}")
except Exception as e:
    print(f" 其他错误: {e}")