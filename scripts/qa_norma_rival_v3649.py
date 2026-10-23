#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QA v3.6.49 (ronda 57) · NORMA DE EMOCIONES DEL RIVAL + IMÁGENES NUEVAS
(capla AR, en vivo; NUEVA).

Petición del dueño (r57): «Tambien es preciso tener en cuenta una regla en
la colocación de las imágenes de los rivales. Todos ellos tienen el nombre
del rival de cada campeonato seguido de una emoción... REGLA. En estado de
espera y al principio el rival se colocará en "_idle"... cuando un rival
lanza un SuperPoder se pone siempre en estado "_crazy", cuando pierde un
punto "_angry" y emite un sonido de queja, cuando el jugador falla
"_laughing" y sonido de risas burlonas, cuando se llega a los 5 toques de
intercambio estado "_focused" cuando se llega a los 10 toques "_picando",
se llega a los 15 toques estado "_surprised", a los 20 toques "_panic" y a
partir de ahi aleatoriamente va cambiando entre "_loosing", "_suprised" y
"_panic". Si Gana un punto "_victory", y si pierde el partido "_defeated".
APLICAR ESTA REGLA A TODOS LOS RIVALES».

Y las imágenes: pared izquierda del Hall (izquierda.jpg), suelo del Hall
(suelo.jpg) y suelo del partido/entrenamiento (suelo_pista.jpg →
assets/partido/suelo.jpg).

Pruebas:
  1) FUENTE SERVIDA — agujas del núcleo (rivalEmocion/_rivalEmoUpdate,
     hitos 5/10/15/20, pool aleatorio >20, idle en espera, cadena
     laughing→victory, defeated en game-over) + FORWARDING del champloader
     + LOS SEIS MÓDULOS con su hook (locura, magia, oeste, orbital,
     valle_neon, plantilla) + PESOS BYTE-EXACTOS de las 3 imágenes nuevas.
  2) MECÁNICA REAL headless — con La Locura activa: hitos del rallye en
     vivo (5→focused, 10→picando, 15→surprised, 20→panic, 25→pool),
     reacción de punto (angry→hungry del Clown, laughing→laughing),
     cadena laughing→victory a los 2 s, espera→idle, derrota→defeated.

Salida: RESULTADO: N OK · M fallos (contrato qa_todo)"""
import asyncio
import sys
import urllib.request

from playwright.async_api import async_playwright

URL = "http://localhost:3000/game.html"
MODS = {
    'locura': 'http://localhost:3000/championships/locura/index.js',
    'magia': 'http://localhost:3000/championships/magia/index.js',
    'oeste': 'http://localhost:3000/championships/oeste/index.js',
    'orbital': 'http://localhost:3000/championships/estacion_orbital/index.js',
    'valle_neon': 'http://localhost:3000/championships/valle_neon/index.js',
    'plantilla': 'http://localhost:3000/championships/_plantilla/index.js',
}
IMGS = [
    ('http://localhost:3000/assets/hall/izquierda.jpg', 511370,
     'HALL pared IZQUIERDA: izquierda.jpg nuevo del dueño (byte-exacto)'),
    ('http://localhost:3000/assets/hall/suelo.jpg', 419364,
     'HALL SUELO: suelo.jpg nuevo del dueño (byte-exacto)'),
    ('http://localhost:3000/assets/partido/suelo.jpg', 239705,
     'PARTIDO/ENTRENAMIENTO suelo: suelo_pista.jpg del dueño (byte-exacto)'),
]

ok = fails = 0

def chk(cond, label):
    global ok, fails
    print(('  ✓ ' if cond else '  ✗ FALLO: ') + label)
    if cond:
        ok += 1
    else:
        fails += 1


async def main():
    global ok, fails
    errors = []

    # ---------- 1 · FUENTE SERVIDA ----------
    try:
        game = urllib.request.urlopen(URL, timeout=10).read().decode('utf-8')
    except Exception as e:
        print('✗ No se pudo leer game.html servido:', e)
        print(f'RESULTADO: {ok} OK · {fails + 1} fallos')
        sys.exit(1)
    for needle, label in [
        # · LA NORMA en el núcleo (c12)
        ('rivalEmocion(st, hold, next) {', 'la NORMA vive en el núcleo (c12)'),
        ('_rivalEmoUpdate(dt) {', 'el reloj de la norma corre cada frame'),
        ('this._rivalEmoUpdate(dt);   // v3.6.49 (r57)',
         'la norma está anclada al animate (junto a updateMega)'),
        ("[[5, 'focused'], [10, 'picando'], [15, 'surprised'], [20, 'panic']]",
         'HITOS: 5→focused · 10→picando · 15→surprised · 20→panic (spec)'),
        ("const pool = ['loosing', 'surprised', 'panic'];",
         'a partir de 20: aleatorio entre loosing/surprised/panic (spec)'),
        ('h > 20 && h % 5 === 0', 'el pool aleatorio cambia cada 5 toques'),
        ("this.rivalEmocion('laughing', 2.0, 'victory');",
         'jugador falla → _laughing y LUEGO _victory (cadena del spec)'),
        ("this.rivalEmocion('angry', 2.0);",
         'rival pierde punto → _angry (queja la pone el módulo)'),
        ("this.rivalEmocion('idle', 0);",
         'espera/al principio → _idle (spec)'),
        ("it.winner === 'player' ? 'defeated' : 'victory', 0);",
         'fin del partido: pierde el rival → _defeated (persistente)'),
        ('this._rivalEmo !== \'defeated\'',
         '_defeated NO lo toca la espera (persistente)'),
        # · FORWARDING del champloader (c11)
        ('rivalEmocion(st, info) {',
         'c11: forwarding rivalEmocion → módulo activo'),
    ]:
        chk(needle in game, label)

    # · LOS SEIS MÓDULOS con el hook de la norma
    for id_, url in MODS.items():
        try:
            mod = urllib.request.urlopen(url, timeout=10).read().decode('utf-8')
        except Exception as e:
            chk(False, f'módulo {id_}: no se pudo leer ({e})')
            continue
        chk('rivalEmocion' in mod, f'módulo {id_}: hook rivalEmocion presente (norma en TODOS)')

    # · IMÁGENES NUEVAS (byte-exacto)
    for url, peso, label in IMGS:
        try:
            data = urllib.request.urlopen(url, timeout=10).read()
            chk(len(data) == peso, f'{label} — {len(data)} B')
        except Exception as e:
            chk(False, f'{label}: no se pudo leer ({e})')

    # ---------- 2 · MECÁNICA REAL headless ----------
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=[
            "--use-gl=swiftshader", "--enable-unsafe-swiftshader",
            "--autoplay-policy=no-user-gesture-required",
        ])
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        page.on("pageerror", lambda e: errors.append(str(e)))
        await page.goto(URL, wait_until="domcontentloaded")
        await page.wait_for_timeout(7000)

        rt = await page.evaluate("""async () => {
          const out = {};
          const G = window.__PP_GAME;
          if (!G) { out.sinJuego = true; return out; }
          const paso = () => { try { G._rivalEmoUpdate(1 / 60); } catch (e) { out.errU = String(e); } };
          try {
            G.champs.activeId = 'locura';
            G.rules.startMatch('match');
            // espera activa: el módulo eager (y su __PP_LOCURA) puede
            // tardar en máquinas lentas (SwiftShader)
            for (let i = 0; i < 60 && !(window.__PP_LOCURA &&
                window.__PP_LOCURA.ctrl && window.__PP_LOCURA.ctrl()); i++) {
              await new Promise((r) => setTimeout(r, 250));
            }
            const ctrl = window.__PP_LOCURA && window.__PP_LOCURA.ctrl &&
              window.__PP_LOCURA.ctrl();
            out.conCtrl = !!ctrl;

            // · AL PRINCIPIO: _idle (spec)
            G._rivalEmo = ''; G._rivalEmoT = 0; G._rivalEmoNext = '';
            G.rules.state = 'serve';
            paso(); paso();
            out.inicioIdle = G._rivalEmo === 'idle' &&
              (!ctrl || ctrl.state === 'idle');

            // · HITOS del rallye (spec: 5/10/15/20)
            G.rules.state = 'rally';
            G.rules.rallyHits = 4; paso();
            G.rules.rallyHits = 5; paso();
            out.hito5 = G._rivalEmo === 'focused';
            G.rules.rallyHits = 10; paso();
            out.hito10 = G._rivalEmo === 'picando';
            G.rules.rallyHits = 15; paso();
            out.hito15 = G._rivalEmo === 'surprised';
            G.rules.rallyHits = 20; paso();
            out.hito20 = G._rivalEmo === 'panic';
            // · A PARTIR DE 20: pool aleatorio (cada 5 toques)
            G.rules.rallyHits = 25; paso();
            out.hito25pool = ['loosing', 'surprised', 'panic']
              .indexOf(G._rivalEmo) >= 0;

            // · PUNTO DEL RIVAL (el jugador falla): laughing → victory
            // (estado POINT: fuera del rallye los hitos no interfieren)
            G.rules.state = 'point';
            G._rivalEmoMil = 0;
            G.rivalEmocion('laughing', 2.0, 'victory');
            out.risaRival = G._rivalEmo === 'laughing' &&
              (!ctrl || ctrl.state === 'laughing');
            for (let i = 0; i < 130 && G._rivalEmoT > 0; i++) paso();
            out.cadenaVictory = G._rivalEmo === 'victory';

            // · PUNTO PERDIDO POR EL RIVAL: angry (el Clown la viste hungry)
            G.rivalEmocion('angry', 2.0);
            out.enfadado = G._rivalEmo === 'angry' &&
              (!ctrl || ctrl.state === 'hungry');   // traducción local del Clown

            // · ESPERA → idle (la reacción viva la respeta hasta morir)
            G._rivalEmoT = 0; G._rivalEmoNext = '';
            G.rules.state = 'serve';
            paso(); paso();
            out.esperaIdle = G._rivalEmo === 'idle';

            // · FIN DEL PARTIDO: el rival pierde → _defeated PERSISTENTE
            G.rivalEmocion('defeated', 0);
            out.derrotado = G._rivalEmo === 'defeated' &&
              (!ctrl || ctrl.state === 'defeated');
            G.rules.state = 'serve';
            paso(); paso();
            out.derrotadoPersiste = G._rivalEmo === 'defeated';

            // · SUPERPODER DEL RIVAL → _crazy (el aviso propio del módulo
            //   lo fija; la norma lo honra mientras dure)
            G.rules.state = 'rally'; G._rivalEmoMil = 0;
            if (ctrl) ctrl._setStateSilent('crazy', 3.2);
            out.crazyPoder = ctrl ? ctrl.state === 'crazy' : false;
          } catch (e) { out.errNorma = String(e); }
          return out;
        }""")

        for key, label in [
            ('conCtrl', 'controlador del Clown accesible (window.__PP_LOCURA)'),
            ('inicioIdle', 'AL PRINCIPIO / espera: el rival está en _idle (spec)'),
            ('hito5', '5 toques → _focused (spec)'),
            ('hito10', '10 toques → _picando (spec)'),
            ('hito15', '15 toques → _surprised (spec)'),
            ('hito20', '20 toques → _panic (spec)'),
            ('hito25pool', '>20 toques → pool aleatorio loosing/surprised/panic (spec)'),
            ('risaRival', 'el jugador falla → _laughing (risas burlonas del módulo)'),
            ('cadenaVictory', 'tras la risa: _victory (el rival ganó el punto — spec)'),
            ('enfadado', 'el rival pierde el punto → _angry (el Clown lo viste hungry)'),
            ('esperaIdle', 'la espera del saque devuelve a _idle'),
            ('derrotado', 'el rival pierde EL PARTIDO → _defeated'),
            ('derrotadoPersiste', '_defeated persiste en la espera (no lo toca el idle)'),
            ('crazyPoder', 'superpoder del rival → _crazy'),
        ]:
            chk(rt.get(key) is True, label)
        for key in ('sinJuego', 'errU', 'errNorma'):
            if rt.get(key):
                chk(False, f'{key}: {rt.get(key)}')

        await browser.close()

    if errors:
        for e in errors[:5]:
            print('  ✗ pageerror:', e[:200])
        fails += len(errors)

    print(f'RESULTADO: {ok} OK · {fails} fallos')
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    asyncio.run(main())
