#!/usr/bin/env python3
"""Mueve a /home/z/quarantine los directorios ilegibles (root-owned) que
bloquean `git reset --hard` tras el reciclado del sandbox. rename() solo
necesita escritura en los directorios padre, que sí son del usuario z."""
import os

ROOT = '/home/z/my-project'
Q = '/home/z/quarantine'
os.makedirs(Q, exist_ok=True)
moved = []
failed = []


def walk(d):
    try:
        names = sorted(os.listdir(d))
    except OSError:
        return
    for name in names:
        p = os.path.join(d, name)
        readable = os.access(p, os.R_OK) and os.access(p, os.X_OK)
        if os.path.isdir(p) and not readable:
            rel = os.path.relpath(p, ROOT).replace('/', '__')
            dst = os.path.join(Q, rel)
            if os.path.exists(dst):
                dst = os.path.join(Q, rel + '_2')
            try:
                os.rename(p, dst)
                moved.append(rel)
            except OSError as e:
                failed.append((p, str(e)))
        elif os.path.isdir(p):
            walk(p)


walk(ROOT)
print('MOVIDOS A CUARENTENA:', len(moved))
for m in moved:
    print(' -', m)
if failed:
    print('FALLOS:', len(failed))
    for p, e in failed:
        print(' !', p, e)
