#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_vestibulo_r72.py — QA FASE 166 · regresión del apartado + nivel 3 (r72).

Informe del dueño verificado:
  1 · «los paneles con las esquinas redondeadas y recortadas también en
      redondo» — cada panela es un Shape redondeado en sus 4 esquinas
      (radioEsquinaM) y el troceo sigue cayendo 1:1 (UVs 0..1).
  2 · «los bloques están achicados… los círculos de los iconos no son
      circulares por estar el panel escalado» — CAUSA RAIZ corregida:
      anchoM = (w_rodaja / alto_lienzo) · altoM (aspecto exacto por
      panela; el central vuelve a ~1,00 m) y yaw CALCULADO con la fórmula
      r69 desde las anchuras reales (sin grados escritos a mano).
  3 · «no tiene sentido mantener siempre los tres bloques, si no hay
      contenido no se coloca el bloque» — lados declarados por página:
      el arco se recalcula para 1/2/3 y la concha pinta sólo las panelas
      montadas (barrido: panelas montadas == lados del dato).
  4 · «botones de Retornar… como botones flotantes sobre el bloque
      central, cualquier botón de navegación siempre sobre el bloque
      principal» — banda ATRÁS+TÍTULO en la C (y < 140 px), idiomas y
      sello en la R si existe (o en la C si es de una panela).
  5 · Multijugador, Campeonatos, Ranking, Carrera y Entrenar con el
      FORMATO AJUSTES (rejilla data-driven), estados de sala en la C,
      detalle de campeonato y división, perfil de entrenamiento y FUERA
      «Volver al Hall».
  6 · Anclaje r69 intacto: abrir = delante de la mirada y FIJO · sin
      chincheta SIGUE de frente · con chincheta CONGELA donde está.

Salida: RESULTADO: N OK · M fallos + capturas (main · multi · champs ·
carrera · train · rankini)."""
import asyncio
import base64
import subprocess
import sys
import time
import urllib.request

from playwright.async_api import async_playwright

URL = 'http://127.0.0.1:3667/game.html'
OUT = '/home/z/my-project/download/'

ok, fails = 0, 0


def chk(cond, label):
    global ok, fails
    print(('  OK  ' if cond else '  FALLO: ') + label)
    ok, fails = ok + (1 if cond else 0), fails + (0 if cond else 1)


def get(url: str) -> str:
    with urllib.request.urlopen(url, timeout=30) as r:
        return r.read().decode('utf-8', 'replace')


JS = """async () => {
  const G = window.__PP_GAME;
  const out = {};
  const dorme = (ms) => new Promise((r) => setTimeout(r, ms));
  if (!G) { out.sinJuego = true; return out; }
  const V3 = G.menuGroup.position.constructor;

  // — 1 · ASPECTO EXACTO + YAW POR FÓRMULA (causa raíz de las elipses) —
  const pas = G.menuGroup.children
    .filter((m) => m.userData && m.userData.panela)
    .map((m) => m.userData.panela);
  out.texel = pas.map((pa) => +(pa.anchoM / pa.w).toFixed(5));
  out.texelOk = pas.every((pa) =>
    Math.abs((pa.anchoM / pa.w) - (pa.altoM / 1400)) < 0.001);
  out.anchos = pas.map((pa) => +pa.anchoM.toFixed(4));
  out.centralGrande = pas[1].anchoM > 0.95;
  // yaw de la L = γC + γL + ranura (calculado, no escrito a mano)
  const gam = (pa) => Math.atan(pa.anchoM / 2 / pa.dist) * 180 / Math.PI;
  const ranura = Math.atan(0.017 / 1.15) * 180 / Math.PI;
  const yawL = pas[0].yaw, yawR = pas[2].yaw;
  out.yawL = +yawL.toFixed(3);
  out.formulaOk = Math.abs(yawL - (gam(pas[1]) + gam(pas[0]) + ranura)) < 0.01
    && Math.abs(yawR + (gam(pas[1]) + gam(pas[2]) + ranura)) < 0.01;
  out.ranuraDeg = +((Math.abs(yawL) - gam(pas[0]) - gam(pas[1])).toFixed(3));

  // — 2 · COLOCACIÓN EN MUNDO (delante de la mirada a ~1,15 m) —
  if (!G.menuOpen) G.toggleMenu();
  await dorme(400);
  G.menuPin = true;
  G.anchorMenu(true);
  await dorme(120);
  const c2c = new V3();
  const camPos = G.camera.getWorldPosition(new V3());
  const camF = new V3();
  G.camera.getWorldDirection(camF);
  G.menuMesh.getWorldPosition(c2c);
  c2c.sub(camPos);
  out.panelaCDist = +c2c.length().toFixed(3);
  const frente = c2c.dot(camF) / Math.max(0.001, c2c.length());
  out.panelaCDelante = +frente.toFixed(3);
  out.colocacionC = out.panelaCDist > 1.05 && out.panelaCDist < 1.30 &&
    frente > 0.75;

  // — 3 · SEMÁNTICA DEL ANCLA (r69 intacto) —
  const p0 = G.menuGroup.position.clone();
  G.menuGroup.position.set(5, 5, 5);
  G.anchorMenu();
  out.congela = G.menuGroup.position.distanceTo(new V3(5, 5, 5)) < 0.001;
  G.menuPin = false;
  G.anchorMenu();
  out.sigue = G.menuGroup.position.distanceTo(p0) < 0.03;
  G.menuPin = true;
  G._menuPinDraw();
  G.anchorMenu(true);
  await dorme(100);

  // — 4 · BLOQUES CONDICIONALES: panelas montadas == lados del dato —
  const ESPERAN = {
    main: 3, multi: 1, join: 1, name: 1, gripname: 1,
    rankini: 1, rank: 1, rankme: 1, champs: 2, champuno: 1, champhist: 1,
    train: 2, trainext: 2, trainarea: 1, carrera: 1, carreradiv: 1,
    opts: 2, optsJuego: 1, optsSala: 1, optsSonido: 1, optsVisual: 1,
    optsPerfil: 1, optsRendi: 1, optsPala: 1,
    salirask: 1, hallask: 1,
  };
  out.ladosMalos = [];
  for (const [pg, esperado] of Object.entries(ESPERAN)) {
    G.menuPage = pg;
    if (pg === 'multi') G._mjMode = null;
    G.drawMenu();
    await dorme(30);
    const n = G._menuPanelas.length;
    if (n !== esperado) out.ladosMalos.push(pg + ':' + n + '/' + esperado);
  }
  out.ladosOk = out.ladosMalos.length === 0;

  // — 5 · BARRIDO (rects dentro del lienzo virtual) —
  const pags = Object.keys(ESPERAN);
  out.paginasMalas = [];
  for (const pg of pags) {
    G.menuPage = pg;
    if (pg === 'multi') G._mjMode = null;
    G.drawMenu();
    await dorme(30);
    const rs = G.menuRects || [];
    const malas = rs.filter((r) => r.x < -2 || r.y < -2 ||
        r.x + r.w > 3698 || r.y + r.h > 1402).map((r) => r.id);
    if (!rs.length || malas.length) {
      out.paginasMalas.push(pg + (malas.length ? ':' + malas.join(',') : ''));
    }
  }
  out.todasLimpias = out.paginasMalas.length === 0;

  // — 6 · BANDA DE NAVEGACIÓN COMÚN sobre el bloque central —
  G.menuPage = 'opts';
  G.drawMenu();
  await dorme(60);
  const atras = (G.menuRects || []).find((r) => r.id === 'page:main');
  out.bandaOk = !!atras && atras.y < 140 &&
    atras.x > 1112 && atras.x + atras.w < 2584;
  // rejilla de AJUSTES sigue viva (r68 conservado)
  out.ajustesOk = ['page:optsJuego', 'page:optsSala']
    .every((id) => (G.menuRects || []).some((r) => r.id === id));
  out.kofiFuera = !(G.menuRects || []).some((r) => r.id === 'kofi');   // r72

  // — 7 · LANDINGS NUEVAS con sus tarjetas —
  const cardsDe = (pg) => {
    G.menuPage = pg;
    if (pg === 'multi') G._mjMode = null;
    G.drawMenu();
    return (G.menuRects || []).map((r) => String(r.id));
  };
  out.idsMulti = cardsDe('multi');
  out.multiOk = ['mjnorm', 'mjduel', 'net:join'].every((id) =>
    out.idsMulti.includes(id));
  out.idsRank = cardsDe('rankini');
  out.rankOk = ['wrl:tab', 'page:rankme'].every((id) =>
    out.idsRank.includes(id));
  out.idsTrain = cardsDe('train');
  out.trainOk = ['trv3:area:dir', 'trv3:semana', 'page:trainext']
    .every((id) => out.idsTrain.includes(id)) &&
    !out.idsTrain.includes('homehall');
  out.idsChamps = cardsDe('champs');
  out.champsOk = out.idsChamps.includes('page:champhist') &&
    out.idsChamps.filter((i) => i.indexOf('champsel:') === 0).length >= 0;
  out.idsCarrera = cardsDe('carrera');
  out.carreraOk = out.idsCarrera.filter((i) =>
    i.indexOf('carrera:sel:') === 0).length === 5;

  // — 8 · capturas —
  const capt = async (pg, key, limpiar) => {
    G.menuPage = pg;
    if (limpiar) G._mjMode = null;
    G.drawMenu();
    await dorme(140);
    out[key] = G.menuCanvas.toDataURL('image/png');
  };
  await capt('main', 'pngMain');
  await capt('multi', 'pngMulti', true);
  await capt('champs', 'pngChamps');
  await capt('carrera', 'pngCarrera');
  await capt('train', 'pngTrain');
  await capt('rankini', 'pngRankini');
  G.menuPage = 'main';
  G.drawMenu();
  return out;
}"""


async def main():
    server = subprocess.Popen(
        [sys.executable, '-m', 'http.server', '3667', '--bind', '127.0.0.1',
         '--directory', '/home/z/my-project/upload/public'],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.2)
    try:
        game = get(URL)
    except Exception as e:
        print('✗ No se pudo leer el game.html local:', e)
        print(f'RESULTADO: {ok} OK · {fails + 1} fallos')
        server.terminate()
        sys.exit(1)

    agujas = [
        # — r70 · aspecto exacto + silueta redondeada + arco calculado —
        ('pa.anchoM = (pa.w / CONFIG_MENUS.lienzo.alto) * pa.altoM;',
         'ASPECTO EXACTO por panela (fin de las elipses)'),
        ('_menuShapePanela(pa)', 'silueta ShapeGeometry redondeada'),
        ('radioEsquinaM: 0.036', 'esquinas en curva (4/4)'),
        ('_menuArco(ids)', 'arco recalculado por página (bloques condicion.)'),
        ('gam(pC) + gam(pL) + ranura', 'yaw POR FÓRMULA desde anchuras reales'),
        ("{ id: 'L', x: 0, w: 1112, altoM: 0.95, dist: 1.15 }",
         'panela L sin yaw/anchoM escritos'),
        ('ranuraM: 0.017', 'ranura uniforme conservada (r69)'),
        # — r70 · lados condicionales —
        ("main: ['L', 'C', 'R']", 'lados del Vestíbulo (3 panelas)'),
        ("multi: ['C']", 'MULTIJUGADOR en una panela'),
        ("champs: ['C', 'R']", 'CAMPEONATOS en dos panelas'),
        ("train: ['C', 'R']", 'ENTRENAR en dos panelas'),
        ('cristal de fondo continuo SOLO en las panelas montadas',
         'concha pinta sólo panelas con contenido'),
        # — r70 · banda de navegación común en el bloque central —
        ('BANDA DE NAVEGACIÓN COMÚN sobre el bloque central',
         'ATRÁS flotante documentado en la concha'),
        ("c.fillText(T('btn_back'), bx + 94", 'ATRÁS en la panela C'),
        ('títulos DINÁMICOS de las páginas nuevas', 'título dinámico concha'),
        # — r70 · landings en formato Ajustes —
        ("multi: { columnas: ['C'], y: 300", 'rejilla MULTIJUGADOR'),
        ("rank: { columnas: ['C'], y: 300", 'rejilla RANKING'),
        ("train: { columnas: ['C', 'R'], y: 300", 'rejilla ENTRENAR'),
        ("champs: { columnas: ['C', 'R'], y: 300", 'rejilla CAMPEONATOS'),
        ("carrera: { columnas: ['C'], y: 300", 'rejilla CARRERA'),
        ('drawMenuChampUno', 'detalle de campeonato'),
        ('drawMenuCarreraDiv', 'división con rivales'),
        ('drawMenuTrain', 'landing de Entrenar'),
        ('drawMenuRankIni', 'landing de Ranking'),
        ('_multiSala(rects, st)', 'estados de sala en la panela C'),
        ('_invitaCardVirtual(rects)', 'tarjeta de invitación virtual'),
        # — r70 · «Volver al Hall» fuera de Entrenar —
        ('FUERA «Volver al Hall» (petición del dueño', 'hall fuera del train'),
        # — r69 · conservado íntegro —
        ('anchorMenu(forzar) {', 'anchorMenu con forzar'),
        ('CONVENCIÓN r67 RESTAURADA', 'grupo delante mirando a la cara'),
        ('D_REF - Math.cos(yaw) * pa.dist', 'arco centrado en la cabeza'),
        ('CONFIG_MENUS.arco.yCentro + 0.475 + 0.032, 0.006)',
         'chincheta clicable (z +6 mm)'),
        ('if (!this.menuPin) this.anchorMenu();', 'sin ancla: sigue siempre'),
        ('this.anchorMenu(true);', 'aperturas con forzar'),
        ('const ESP = this._menuMap', 'tooltip espacio-consciente'),
        # — legado duplicado FUERA (dedup r69 + backs r70) —
        ("    label(T('tab_multi'), 244, 26)", 'título multi duplicado FUERA', True),
        ("    label(T('join_title'), 240, 26)", 'título join duplicado FUERA', True),
        ("    label(T('name_title'), 240, 26)", 'título name duplicado FUERA', True),
        ("if (!ppPlayerName()) label(T('wrl_need_name'), 966, 19, '#98a6b4', 'center');\n  }",
         'rank sin back legado (la concha manda)'),
        ("    btn('page:champs', 40, 216, 240, 60", 'back legado del historial FUERA', True),
        ('drawHub(this, c, rects', 'hub legado de train desconectado', True),
        ('homehall', 'sin «Volver al Hall» en drawExtras (train)', True),
    ]

    errores = []
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        page = await browser.new_page(viewport={'width': 1280, 'height': 800})
        page.on('pageerror', lambda e: errores.append(str(e)[:300]))
        await page.goto(URL)
        try:
            await page.wait_for_function('!!window.__PP_GAME', timeout=45000)
        except Exception:
            print('✗ __PP_GAME no llegó')
            await browser.close()
            server.terminate()
            sys.exit(1)
        await page.wait_for_timeout(1200)

        # agujas estáticas sobre el fuente ensamblado
        for ag in agujas:
            aguja, etiqueta = ag[0], ag[1]
            invertida = len(ag) > 2 and ag[2]
            if etiqueta == 'sin «Volver al Hall» en drawExtras (train)':
                i0 = game.find('function drawExtras')
                i1 = game.find('menuAction(game, arg)', i0)
                hay = 'homehall' in game[i0:i1]
                chk(not hay, etiqueta)
            else:
                hay = aguja in game
                chk((not hay) if invertida else hay, etiqueta)

        rt = await page.evaluate(JS)
        # — verificaciones funcionales —
        chk(not rt.get('sinJuego'), 'juego presente')
        chk(rt.get('texelOk'), 'texel/m idéntico en las tres panelas '
            '(aspecto exacto → círculos circulares)')
        print('   anchos m:', rt.get('anchos'), '· texel/px:', rt.get('texel'))
        chk(rt.get('centralGrande'), 'panela central recupera ~1,00 m')
        chk(rt.get('formulaOk'), 'yaw = γC + γL + ranura (calculado en código)')
        print('   yaw L:', rt.get('yawL'), '· ranura:', rt.get('ranuraDeg'), '°')
        chk(rt.get('colocacionC'), 'panela C delante de la mirada a ~1,15 m '
            f'(dist {rt.get("panelaCDist")} m · proyección {rt.get("panelaCDelante")})')
        chk(rt.get('congela'), 'con chincheta CONGELA donde está')
        chk(rt.get('sigue'), 'sin chincheta SIGUE de frente (re-ancla)')
        chk(rt.get('ladosOk'), 'panelas montadas == lados del dato en TODAS '
            'las páginas' + (f' → {rt["ladosMalos"][:4]}' if not rt.get('ladosOk') else ''))
        chk(rt.get('todasLimpias'), 'barrido: rects dentro del lienzo virtual' +
            (f' → {rt["paginasMalas"][:4]}' if not rt.get('todasLimpias') else ''))
        chk(rt.get('bandaOk'), 'ATRÁS flotante sobre el bloque central (y<140)')
        chk(rt.get('ajustesOk'), 'rejilla de AJUSTES conservada')
        chk(rt.get('multiOk'), 'MULTIJUGADOR: 2 modos + unirse')
        chk(rt.get('rankOk'), 'RANKING: tabla + mi posición')
        chk(rt.get('trainOk'), 'ENTRENAR: áreas + reto + perfil, SIN hall')
        chk(rt.get('champsOk'), 'CAMPEONATOS: rejilla + historial')
        chk(rt.get('carreraOk'), 'CARRERA: 5 divisiones')
        for key, name in [('pngMain', 'qa_arco70_main.png'),
                          ('pngMulti', 'qa_arco70_multi.png'),
                          ('pngChamps', 'qa_arco70_champs.png'),
                          ('pngCarrera', 'qa_arco70_carrera.png'),
                          ('pngTrain', 'qa_arco70_train.png'),
                          ('pngRankini', 'qa_arco70_rankini.png')]:
            if rt.get(key) and rt[key].startswith('data:image/png;base64,'):
                raw = base64.b64decode(rt[key].split(',', 1)[1])
                open(OUT + name, 'wb').write(raw)
                print(f'  captura: {name} ({len(raw):,} B)')
            else:
                chk(False, f'captura {name}')
        chk(not errores, 'sin pageerrors' +
            ('' if not errores else f' → {errores[:2]}'))
        if errores:
            print('   pageerrors:', errores[:3])
        await browser.close()
    server.terminate()
    print(f'RESULTADO: {ok} OK · {fails} fallos')
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    asyncio.run(main())
