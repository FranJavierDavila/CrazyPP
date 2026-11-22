#!/usr/bin/env python3
"""V2.137 — Hough circles sobre el mapa wizard nuevo para medir los anillos."""
import cv2
import numpy as np

SRC = '/home/z/my-project/upload/Mapa.png'
img = cv2.imread(SRC)
H, W = img.shape[:2]
gray = cv2.medianBlur(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), 5)

circles = cv2.HoughCircles(
    gray, cv2.HOUGH_GRADIENT, dp=1.2, minDist=150,
    param1=110, param2=52, minRadius=80, maxRadius=160,
)
out = img.copy()
if circles is not None:
    cs = np.round(circles[0]).astype(int)
    cs = sorted(cs.tolist(), key=lambda c: -c[2])
    print(f'{len(cs)} círculos:')
    for x, y, r in cs:
        print(f'  centro=({x},{y})  r={r}')
        cv2.circle(out, (x, y), r, (0, 0, 255), 3)
        cv2.drawMarker(out, (x, y), (0, 255, 0), cv2.MARKER_CROSS, 24, 3)
cv2.imwrite('/home/z/my-project/scripts/wizard_mapa_hough.png', out)
print('guardado scripts/wizard_mapa_hough.png')
