#!/usr/bin/env python3
"""Post-proceso del informe: formato de los campos PAGE por sección (WPS) + pgNumType vacío fuera.
El pie del índice (romanos) lleva el marcador de color 888887; el del cuerpo (arábigos) el 808080."""
import re
import shutil
import zipfile
from pathlib import Path

DOC = Path('/home/z/my-project/download/Auditoria_calidad_CrazyPP_r109.docx')
TMP = DOC.with_suffix('.tmp.docx')

re_page = re.compile(r'(<w:instrText[^>]*>)\s*PAGE\s*(</w:instrText>)')

with zipfile.ZipFile(DOC, 'r') as zin:
    nombres = zin.namelist()
    datos = {n: zin.read(n) for n in nombres}

cambios = []
for n in nombres:
    if re.match(r'word/footer\d*\.xml$', n):
        xml = datos[n].decode('utf-8')
        if re_page.search(xml):
            if '888887' in xml:   # pie del índice → romanos
                xml = re_page.sub(r'\1 PAGE \\* ROMAN \\* MERGEFORMAT \2', xml)
                cambios.append(f'{n}: PAGE → ROMAN')
            else:                 # pie del cuerpo → arábigos
                xml = re_page.sub(r'\1 PAGE \\* arabic \\* MERGEFORMAT \2', xml)
                cambios.append(f'{n}: PAGE → arabic')
            datos[n] = xml.encode('utf-8')
    if n == 'word/document.xml':
        xml = datos[n].decode('utf-8')
        antes = xml.count('<w:pgNumType/>')
        xml = xml.replace('<w:pgNumType/>', '')
        if antes:
            cambios.append(f'document.xml: {antes} pgNumType vacío eliminado')
        # Deduplicación de entradas del índice: el inyector puede dejar dos
        # párrafos consecutivos para la MISMA entrada (mismo texto de enlace).
        import re as _re
        paras = list(_re.finditer(r'<w:p\b[^>]*>(?:(?!</w:p>).)*?</w:p>', xml, _re.S))
        a_borrar = []
        texto_ant = None
        for m in paras:
            bloq = m.group(0)
            if ('w:leader="dot"' not in bloq) and ('PAGEREF' not in bloq):
                continue
            mm = _re.search(r'<w:t[^>]*>([^<]+)</w:t>', bloq)
            texto = mm.group(1).strip() if mm else None
            if texto and texto == texto_ant:
                a_borrar.append(m)
            texto_ant = texto
        if a_borrar:
            for m in reversed(a_borrar):
                xml = xml[:m.start()] + xml[m.end():]
            cambios.append(f'document.xml: {len(a_borrar)} entrada(s) duplicada(s) del índice eliminada(s)')
        datos[n] = xml.encode('utf-8')

with zipfile.ZipFile(TMP, 'w', zipfile.ZIP_DEFLATED) as zout:
    for n in nombres:
        zout.writestr(n, datos[n])
shutil.move(TMP, DOC)
print('\n'.join(cambios) if cambios else 'sin cambios')
