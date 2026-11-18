#!/usr/bin/env python3
"""peek.py <file> <start> <end> [maxlen] — read line range with truncation of huge lines."""
import sys
path, a, b = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
mx = int(sys.argv[4]) if len(sys.argv) > 4 else 400
lines = open(path, encoding='utf-8').read().split('\n')
for i in range(a, min(b + 1, len(lines) + 1)):
    l = lines[i - 1]
    if len(l) > mx:
        l = l[:mx] + f'  ...[{len(l)} chars]'
    print(f'{i}: {l}')
