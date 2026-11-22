#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r45 · PRUEBA EN VIVO de LA VITRINA DEL CIELO (v3.6.139-SDK6):
  A · entrar al espacio arcano (fundido a negro, polling headless).
  B · CANDADO: visible en un poder bloqueado, en la ESQUINA SUPERIOR
      IZQUIERDA del medallón y con la IMAGEN del dueño (candado.png).
  C · CONSTELACIÓN DE PALAS: nace en el cielo (altura > 0, r ~45), el
      trazo AVANZA (tinta creciendo en el lienzo), opacity viva y al
      forzar el fundido se apaga (ciclo completo).
  D · SKIN DE PALA: el puente pinta aiPaddleMesh con 'fuego' (material
      con nombre ppSkin_fuego_*) y 'clasica' devuelve el original.
  E · TELEMETRÍA: el evento firmado lleva pid anónimo + nombre.
  F · 0 errores de página.
Fotos: download/_r45_constelacion.png · _r45_candado.png
Servidor: http://127.0.0.1:8123 (servir upload/public).
NOTA headless: con SwiftShader el render cae a ~1-10 fps y el dt va
clampeado — todo se espera con POLLING, jamás con tiempos fijos."""
import asyncio
import base64
import json
import os

from playwright.async_api import async_playwright

BASE = 'http://127.0.0.1:8123'
OUT = '/home/z/my-project/download'

G = '(window.__PP_GAME||window.__game)'

AL_HALL = """async () => {
  const G = """ + G + """;
  if (G.inHall) return 'ya';
  try { G.enterHall(); } catch (e) { return 'err:' + e; }
  return 'ok';
}"""

ENTRAR = """() => { (""" + G + """)._arconoEntrar(); return true; }"""

CANDADO_ESTADO = """() => {
  const A = (""" + G + """).arcaneGroup.userData.arcono;
  const c = A.candado.grupo;
  const mesh = c.children.find((k) => k.isMesh);
  const map = mesh && mesh.material ? mesh.material.map : null;
  return {
    vis: c.visible,
    x: +c.position.x.toFixed(3), y: +c.position.y.toFixed(3), z: +c.position.z.toFixed(3),
    src: map && map.image && map.image.src ? map.image.src.split('/').pop() : '(vectorial)',
  };
}"""

CONTE_ESTADO = """() => {
  const A = (""" + G + """).arcaneGroup.userData.arcono;
  const M = A.conste, CN = M.userData.conste;
  const p = M.position;
  const x = CN.cv.getContext('2d');
  const d = x.getImageData(0, 0, CN.cv.width, CN.cv.height).data;
  let tinta = 0;
  for (let i = 3; i < d.length; i += 4) if (d[i] > 30) tinta++;
  return {
    vis: M.visible, estado: CN.estado,
    prog: +CN.prog.toFixed(1), total: +CN.total.toFixed(1),
    op: +M.material.opacity.toFixed(3),
    altura: +p.y.toFixed(2), radio: +Math.hypot(p.x, p.y, p.z).toFixed(1),
    tinta,
  };
}"""

CONTE_FUNDIDO = """() => {
  const A = (""" + G + """).arcaneGroup.userData.arcono;
  const CN = A.conste.userData.conste;
  if (CN.estado === 'trazo' || CN.estado === 'sosten') {
    CN.estado = 'fundido'; CN.t = 0.35;
  }
  return CN.estado;
}"""

PALA_PINTA = """() => {
  const G = """ + G + """;
  const antes = [];
  G.aiPaddleMesh.traverse((o) => { if (o.isMesh && o.material) antes.push(Array.isArray(o.material) ? o.material.map((m) => m.name || '?') : (o.material.name || '?')); });
  window.__PP_TRAIN_PINTA_PALA(G.aiPaddleMesh, 'fuego');
  const nombres = [];
  let goma = '';
  G.aiPaddleMesh.traverse((o) => {
    if (!o.isMesh || !o.material) return;
    const ms = Array.isArray(o.material) ? o.material : [o.material];
    for (const m of ms) { nombres.push(m.name || '?'); if ((m.name || '').indexOf('rubber') >= 0) goma = m.name; }
  });
  return { antes, nombres, goma };
}"""

PALA_RESTAURA = """() => {
  const G = """ + G + """;
  window.__PP_TRAIN_PINTA_PALA(G.aiPaddleMesh, 'clasica');
  let originales = 0, total = 0;
  G.aiPaddleMesh.traverse((o) => {
    if (!o.isMesh || !o.material || !o.userData) return;
    const ms = Array.isArray(o.material) ? o.material : [o.material];
    for (const m of ms) {
      if (!o.userData.ppOrigMat) continue;
      total++;
      if (m === o.userData.ppOrigMat) originales++;
    }
  });
  return { originales, total };
}"""

TELE_EV = """() => {
  try {
    localStorage.setItem('pp_pid', 'abc123def4567890');
    localStorage.setItem('pp_player_name', 'QA45');
    window.__PP_TELE.ev('qa_r45', { prueba: 1 });
    const q = window.__PP_TELE.st.q;
    const e = q[q.length - 1];
    return { e: e.e, pid: e.pid || '', n: e.n || '' };
  } catch (err) { return { err: String(err) }; }
}"""

FOTO = """() => {
  const G = """ + G + """;
  G.renderer.render(G.scene, G.camera);
  return G.renderer.domElement.toDataURL('image/png');
}"""


async def main():
    os.makedirs(OUT, exist_ok=True)
    fallos = 0
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=['--enable-unsafe-swiftshader'])
        page = await browser.new_page(viewport={'width': 1280, 'height': 800})
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)))
        await page.add_init_script("try { localStorage.clear(); } catch (e) {}")
        await page.goto(BASE + '/game.html', wait_until='domcontentloaded',
                        timeout=60000)
        await page.wait_for_function('!!(window.__PP_GAME||window.__game)',
                                     timeout=45000)
        print('versión:', await page.evaluate('window.__PP_VERSION || "?"'))

        await page.evaluate(AL_HALL)
        await page.wait_for_function(G + '.inHall === true', timeout=30000)
        print('hall: ok')

        # ── A · ENTRAR (fundido — polling headless) ──
        await page.evaluate(ENTRAR)
        await page.wait_for_function(G + '._arconoOn === true', timeout=60000)
        print('A · entrar al arcano: OK ✓')

        # ── B · CANDADO en un poder bloqueado ──
        # la galería arranca en el índice 0; con el perfil recién limpio
        # los poderes están bloqueados → el candado se enciende solo
        await page.wait_for_function(
            G + '.arcaneGroup.userData.arcono.candado.grupo.visible === true',
            timeout=90000)
        cd = await page.evaluate(CANDADO_ESTADO)
        b64 = await page.evaluate(FOTO)
        with open(OUT + '/_r45_candado.png', 'wb') as f:
            f.write(base64.b64decode(b64.split(',')[1]))
        ok_b = (cd['vis'] and cd['x'] < -0.5 and cd['y'] > 1.5 and
                abs(cd['z'] + 2.28) < 0.01)
        print('B · candado vis=', cd['vis'], '· pos=(', cd['x'], ',', cd['y'],
              ',', cd['z'], ') · textura=', cd['src'], ':',
              'OK ✓' if ok_b else 'FALLO')
        # la IMAGEN del dueño (puede tardar un pelín más que el grupo)
        ok_b2 = await page.wait_for_function(
            G + ".arcaneGroup.userData.arcono.candado.grupo.children.find((k)=>k.isMesh).material.map && String((G0)=>0)==='0' || false",
            timeout=1, ) if False else None
        # comprobación directa y tolerante:
        cd2 = await page.evaluate(CANDADO_ESTADO)
        ok_b2 = cd2['src'] == 'candado.png'
        if not ok_b2:
            await page.wait_for_timeout(1500)
            cd2 = await page.evaluate(CANDADO_ESTADO)
            ok_b2 = cd2['src'] == 'candado.png'
        print('B2 · la IMAGEN del dueño manda (src=', cd2['src'], '):',
              'OK ✓' if ok_b2 else 'FALLO (glifo vectorial de respaldo)')

        # ── C · CONSTELACIÓN DE PALAS ──
        await page.wait_for_function(
            G + '.arcaneGroup.userData.arcono.conste.visible === true',
            timeout=120000)
        c1 = await page.evaluate(CONTE_ESTADO)
        ok_c1 = c1['estado'] in ('trazo', 'sosten') and c1['altura'] > 5 and \
            40 < c1['radio'] < 50 and c1['op'] > 0.3
        print('C1 · constelación viva en el CIELO (estado', c1['estado'],
              '· altura', c1['altura'], 'm · radio', c1['radio'], 'm · op',
              c1['op'], '):', 'OK ✓' if ok_c1 else 'FALLO')
        # tinta creciendo (el bolígrafo dibuja)
        await page.wait_for_function(
            G + '.arcaneGroup.userData.arcono.conste.visible === true', timeout=90000)
        t0 = (await page.evaluate(CONTE_ESTADO))['tinta']
        await page.wait_for_function(
            "(() => { const A = (" + G + ").arcaneGroup.userData.arcono; const CN = A.conste.userData.conste;" +
            " const x = CN.cv.getContext('2d'); const d = x.getImageData(0,0,CN.cv.width,CN.cv.height).data;" +
            " let t=0; for (let i=3;i<d.length;i+=4) if (d[i]>30) t++; return t > " + str(max(200, t0 + 400)) + "; })()",
            timeout=120000)
        c2 = await page.evaluate(CONTE_ESTADO)
        ok_c2 = c2['tinta'] > t0 and c2['prog'] > 0
        print('C2 · el bolígrafo AVANZA (tinta', t0, '→', c2['tinta'],
              '· prog', c2['prog'], '/', c2['total'], '):',
              'OK ✓' if ok_c2 else 'FALLO')
        b64 = await page.evaluate(FOTO)
        with open(OUT + '/_r45_constelacion.png', 'wb') as f:
            f.write(base64.b64decode(b64.split(',')[1]))
        # fundido: se apaga y vuelve a espera
        await page.evaluate(CONTE_FUNDIDO)
        await page.wait_for_function(
            G + '.arcaneGroup.userData.arcono.conste.visible === false',
            timeout=60000)
        c3 = await page.evaluate(CONTE_ESTADO)
        ok_c3 = c3['vis'] is False and c3['estado'] == 'espera'
        print('C3 · el trazo SE DESVANECE (estado', c3['estado'], '· vis',
              c3['vis'], '):', 'OK ✓' if ok_c3 else 'FALLO')

        # ── D · SKIN DE PALA (puente del Pro Training) ──
        pk = await page.evaluate(PALA_PINTA)
        ok_d = any('ppSkin_fuego' in n for n in pk['nombres'])
        print('D · pala remota teñida de FUEGO (goma:', pk['goma'] or '—', '):',
              'OK ✓' if ok_d else 'FALLO ' + json.dumps(pk['nombres'][:6]))
        pr = await page.evaluate(PALA_RESTAURA)
        ok_d2 = pr['total'] > 0 and pr['originales'] == pr['total']
        print('D2 · «clasica» restaura los materiales ORIGINALES (',
              pr['originales'], '/', pr['total'], '):',
              'OK ✓' if ok_d2 else 'FALLO')

        # ── E · TELEMETRÍA con identidad mínima ──
        te = await page.evaluate(TELE_EV)
        ok_e = te.get('e') == 'qa_r45' and te.get('pid') == 'abc123def4567890' \
            and te.get('n') == 'QA45'
        print('E · evento firmado (pid', te.get('pid'), '· nombre', te.get('n'),
              '):', 'OK ✓' if ok_e else 'FALLO ' + json.dumps(te))

        # ── F · cero errores de página ──
        ok_f = not errs
        print('F · errores de página:', len(errs),
              'OK ✓' if ok_f else 'FALLO ' + json.dumps(errs[:3]))

        checks = [True, ok_b, ok_b2, ok_c1, ok_c2, ok_c3, ok_d, ok_d2, ok_e, ok_f]
        fallos = sum(1 for c in checks if not c)
        print(f'\nPROBE r45: {len(checks) - fallos}/{len(checks)} OK · fallos={fallos}')
        await browser.close()
        return 1 if fallos else 0


if __name__ == '__main__':
    raise SystemExit(asyncio.run(main()))
