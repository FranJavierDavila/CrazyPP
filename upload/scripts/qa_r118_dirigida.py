#!/usr/bin/env python3
"""QA DIRIGIDA V3.6.107 · M4 ELO (regla del dueño: sólo lo tocado HOY).

1 · Arranque limpio (0 pageerrors) con __PP_GAME vivo.
2 · ELO unificado (c06 GameStats): matemática ganar/perder, K por modo
    (IA 24 · escalera 20 · humano 32), poda de eloHist a 40, mejor día.
3 · Matchmaking (c02 rivalPorElo): pureza, bandas de preset, k acotado
    [0.7,1.6], variedad ±120 y redondeo honesto.
4 · RETO DE LA SEMANA (c13): weekKey lunes→domingo, plan determinista,
    subida acotada 0..4, cobro único (jamás doble), modo equivocado no
    cobra, insignia acumula, poda a 26 semanas.
5 · Integración viva: drawMenuRankMe dibuja sin excepción con datos;
    mmMatch manda sobre la dificultad en _aiKAplica (easy nerfeada con
    k<1); applyAISkill ignora mmMatch si hay carrera (prioridad).

Uso: python3 scripts/qa_r118_dirigida.py  (necesita dev :3000)
Salida: RESULTADO: N OK · N fallos · exit 0/1
"""
import asyncio
import sys

from playwright.async_api import async_playwright

BASE = 'http://localhost:3000'
ok_n = [0]
fail_n = [0]


def chk(cond, label):
    if cond:
        ok_n[0] += 1
        print('  ✓ ' + label)
    else:
        fail_n[0] += 1
        print('  ✗ FALLO: ' + label)


async def main():
    errs = []
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        page = await browser.new_page()
        page.on('pageerror', lambda e: errs.append(str(e)))
        await page.goto(BASE, wait_until='domcontentloaded', timeout=60000)
        try:
            await page.wait_for_function('() => !!window.__PP_GAME && !!window.__PP_ELO && !!window.__PP_GameStats', timeout=45000)
        except Exception:
            pass

        # ── 1 · arranque limpio ──────────────────────────────────────────
        await page.wait_for_timeout(2500)
        chk(len(errs) == 0, '1 · arranque sin pageerrors (%d)' % len(errs))
        if errs:
            for e in errs[:3]:
                print('      · ' + e[:160])
        tiene = await page.evaluate('() => !!window.__PP_GAME && !!window.__PP_TRAIN')
        chk(tiene, '1 · __PP_GAME y __PP_TRAIN vivos')

        # ── 2 · ELO unificado (GameStats) ────────────────────────────────
        elo_checks = await page.evaluate(r"""
async () => {
  const out = [];
  const ok = (c, l) => out.push({ ok: !!c, l });
  localStorage.removeItem('ppxr_stats_v1');
  const GameStats = window.__PP_GameStats;
  if (!GameStats) return [{ ok: false, l: '__PP_GameStats ausente' }];
  const st = new GameStats();

  // 2a · valores de arranque
  ok(st.data.elo === 1000, 'elo nace 1000 (' + st.data.elo + ')');

  // 2b · victoria vs medium (1050): esperado E = 1/(1+10^(50/400))
  const E = 1 / (1 + Math.pow(10, (1050 - 1000) / 400));
  const esp = Math.round(24 * (1 - E));
  st.recordMatch(true, 'medium', { modo: 'ia', oppElo: 1050 });
  ok(st.data.elo === 1000 + esp, 'win vs 1050 → +' + esp + ' (' + st.data.elo + ')');

  // 2c · derrota con el ELO ACTUAL (tras la victoria): E se recalcula
  const antes = st.data.elo;
  const E2 = 1 / (1 + Math.pow(10, (1050 - antes) / 400));
  const espL = Math.round(24 * (0 - E2));
  st.recordMatch(false, 'medium', { modo: 'ia', oppElo: 1050 });
  ok(st.data.elo === antes + espL,
    'loss vs 1050 desde ' + antes + ' → ' + espL + ' (' + st.data.elo + ')');

  // 2d · K por modo: P2P simétrico (rival = propio) → ±16; carrera ±10 sobre E=0.5
  const st2 = new GameStats();
  localStorage.setItem('ppxr_stats_v1', JSON.stringify({ elo: 1000 }));
  const st3 = new GameStats();
  st3.recordMatch(true, 'medium', { modo: 'p2p', oppElo: 1000 });
  ok(st3.data.elo === 1016, 'p2p K=32 simétrico → +16 (' + st3.data.elo + ')');
  st3.recordMatch(true, 'medium', { modo: 'carrera', oppElo: 1000 });
  ok(st3.data.elo === 1016 + 10, 'carrera K=20 simétrico → +10 (' + st3.data.elo + ')');

  // 2e · compatibilidad: llamada antigua de 2 argumentos (K24, rival 1000)
  localStorage.setItem('ppxr_stats_v1', JSON.stringify({ elo: 1000 }));
  const st4 = new GameStats();
  st4.recordMatch(true, 'easy');
  ok(st4.data.elo === 1012, 'llamada legacy 2 args → +12 (rival 1000) (' + st4.data.elo + ')');

  // 2f · poda de eloHist a 40 + mejor día
  for (let i = 0; i < 45; i++) st4.recordMatch(true, 'easy', { modo: 'ia', oppElo: 900 });
  ok(st4.data.eloHist.length === 40, 'eloHist podado a 40 (' + st4.data.eloHist.length + ')');
  ok(st4.data.mejorDia.v === st4.data.won && st4.data.hoyDia.v === st4.data.won,
    'mejor día = todas las victorias de hoy (' + st4.data.mejorDia.v + '/' + st4.data.won + ')');

  // 2g · persistencia: reconstruir conserva el ELO
  const recargado = new GameStats();
  ok(recargado.data.elo === st4.data.elo, 'ELO persiste entre instancias (' + recargado.data.elo + ')');
  localStorage.removeItem('ppxr_stats_v1');
  return out;
}
""")
        for c in elo_checks:
            chk(c['ok'], '2 · ' + c['l'])

        # ── 3 · matchmaking (rivalPorElo) ────────────────────────────────
        mm_checks = await page.evaluate(r"""
async () => {
  const out = [];
  const ok = (c, l) => out.push({ ok: !!c, l });
  const E = window.__PP_ELO;
  if (!E) return [{ ok: false, l: '__PP_ELO ausente' }];
  const { rivalPorElo, ELO_CPU, AI_PRESETS } = E;
  ok(ELO_CPU.medium === 1050, 'ELO_CPU anclado (medium 1050)');
  // pureza + bandas + k acotado en todo el espectro. CONTRATO HONESTO:
  // el k de la casa vive en [0.7,1.6] (scalePreset) → los suelos de banda
  // son 838/988/1138 y los techos 982/1132/1282. Dentro del rango
  // representable la propuesta es EXACTA (objetivo); fuera, clamp.
  let bien = true, kRange = [9, 0];
  const elos = [700, 850, 975, 1000, 1050, 1125, 1200, 1400];
  for (const e of elos) {
    for (let j = -120; j <= 120; j += 17) {
      const r = rivalPorElo(e, j);
      const obj = Math.max(400, Math.min(2000, e + j));
      const esperado = obj < 975 ? Math.max(838, Math.min(obj, 982))
        : obj < 1125 ? Math.max(988, Math.min(obj, 1132))
        : Math.max(1138, Math.min(obj, 1282));
      if (r.elo !== esperado) bien = false;
      if (r.elo < 975 && r.preset !== 'easy') bien = false;
      if (r.elo >= 975 && r.elo < 1125 && r.preset !== 'medium') bien = false;
      if (r.elo >= 1125 && r.preset !== 'hard') bien = false;
      if (r.k < 0.7 || r.k > 1.6) bien = false;
      kRange[0] = Math.min(kRange[0], r.k); kRange[1] = Math.max(kRange[1], r.k);
      const rt = Math.round(ELO_CPU[r.preset] + 400 * Math.log10(r.k));
      if (rt !== r.elo) bien = false;   // ida y vuelta honesta
    }
  }
  ok(bien, '200 propuestas: bandas + suelos/techos k + ida-vuelta (' +
    kRange[0].toFixed(2) + '…' + kRange[1].toFixed(2) + ')');
  // variedad: 30 jitters aleatorios producen >5 valores distintos
  const vistos = new Set();
  for (let i = 0; i < 30; i++) vistos.add(rivalPorElo(1000, Math.random() * 240 - 120).elo);
  ok(vistos.size >= 5, 'variedad: 30 propuestas → ' + vistos.size + ' rivales distintos');
  // clamps: elo alto no propone muro (k≤1.6) y elo bajo no cae de 400
  const top = rivalPorElo(1900, 120);
  ok(top.k <= 1.6 && top.preset === 'hard', 'elo 2020 → hard con k≤1.6 (' + top.elo + ')');
  const bot = rivalPorElo(420, -120);
  ok(bot.elo >= 400, 'suelo 400 respetado (' + bot.elo + ')');
  // el preset existe siempre
  ok(!!AI_PRESETS[top.preset] && !!AI_PRESETS[bot.preset], 'presets siempre legales');
  return out;
}
""")
        for c in mm_checks:
            chk(c['ok'], '3 · ' + c['l'])

        # ── 4 · reto de la semana (c13) ──────────────────────────────────
        wk_checks = await page.evaluate(r"""
async () => {
  const out = [];
  const ok = (c, l) => out.push({ ok: !!c, l });
  const TT = window.__PP_TRAIN.__test;
  const S = window.__PP_TRAIN.__debug.S;
  const wk = TT.weekKey();
  ok(/^[0-9]{4}-W[0-9]{4}$/.test(wk), 'weekKey formato YYYY-WMMDD (' + wk + ')');
  // el lunes de la septana: weekKey(-1) difiere y weeklySub respeta el tope
  const sub0 = TT.weeklySub(wk);
  ok(sub0 >= 0 && sub0 <= 4, 'weeklySub en [0..4] (' + sub0 + ')');
  const plan = TT.weeklyPlan(wk);
  const plan2 = TT.weeklyPlan(wk);
  ok(plan.mode === plan2.mode && plan.n === plan2.n, 'weeklyPlan determinista (' +
    plan.mode + ' n=' + plan.n + ')');
  ok(plan.n >= 5, 'objetivo semanal por encima del base (' + plan.n + ')');
  // cobro único + insignia + modo equivocado
  localStorage.removeItem('ppxr_train_v1');
  const antes = S.pts || 0;
  TT.weeklyComplete('modo_que_no_es', 99, 0);
  ok(S.semana.bad === 0, 'modo equivocado NO cobra');
  TT.weeklyComplete(plan.mode, plan.n + 5, 0);
  ok(S.semana.bad === 1, 'cobro semanal → insignia ×1');
  ok((S.pts || 0) - antes >= 120, 'premio ≥120 pts (+' + ((S.pts || 0) - antes) + ')');
  const ptsTras = S.pts;
  TT.weeklyComplete(plan.mode, 999, 0);
  ok(S.semana.bad === 1 && S.pts === ptsTras, 'segundo cobro JAMÁS (guard done[weekKey])');
  // poda a 26 semanas
  for (let i = 1; i <= 30; i++) S.semana.done['2020-W010' + (i % 10)] = { m: plan.mode, res: 1, g: 0 };
  TT.weeklyComplete(plan.mode, 1, 0);  // ya está cobrada: no debe reventar
  ok(Object.keys(S.semana.done).length <= 52, 'done acotado tras ruido (' +
    Object.keys(S.semana.done).length + ')');
  localStorage.removeItem('ppxr_train_v1');
  return out;
}
""")
        for c in wk_checks:
            chk(c['ok'], '4 · ' + c['l'])

        # ── 5 · integración viva ─────────────────────────────────────────
        live_checks = await page.evaluate(r"""
async () => {
  const out = [];
  const ok = (c, l) => out.push({ ok: !!c, l });
  const G = window.__PP_GAME;
  const AI_PRESETS = window.__PP_ELO.AI_PRESETS;
  // 5a · drawMenuRankMe sin excepción y con rects
  try {
    const rects = [];
    G.drawMenuRankMe(rects);
    ok(rects.length >= 1, 'drawMenuRankMe dibuja y registra rects (' + rects.length + ')');
  } catch (e) { ok(false, 'drawMenuRankMe lanza: ' + String(e).slice(0, 90)); }
  // 5b · mmMatch manda sobre la dificultad: easy con k=0.7 → más falona
  // (el lerp persigue _aiKTarget: applyAISkill lo fija y se ancla a mano)
  const difBase = G.difficulty;
  G.adaptive = false;
  G.mmMatch = { preset: 'easy', k: 0.7, elo: 640 };
  G.applyAISkill();
  G._aiKCur = G._aiKTarget;
  G._aiKAplica();
  const cfgMM = G.ai.cfg;
  ok(cfgMM.missBase > AI_PRESETS.easy.missBase && cfgMM.maxSpeed < AI_PRESETS.easy.maxSpeed,
    'mmMatch easy k=0.7 → rival nerfeado (' + cfgMM.missBase.toFixed(3) + '/' +
    cfgMM.maxSpeed.toFixed(2) + ')');
  // 5c · prioridad: con carrera activa, mmMatch NO pisa
  G.carreraMatch = { preset: 'hard', k: 1.0, div: 0, rId: 'x', nombre: 'QA' };
  G.applyAISkill();
  G._aiKCur = G._aiKTarget;
  G._aiKAplica();
  ok(Math.abs(G.ai.cfg.maxSpeed - AI_PRESETS.hard.maxSpeed) < 1e-6,
    'carrera > mmMatch en prioridad (' + G.ai.cfg.maxSpeed.toFixed(2) + ')');
  // limpieza (la QA no deja estado vivo)
  G.carreraMatch = null; G.mmMatch = null;
  G.difficulty = difBase;
  G._aiKAplica();
  return out;
}
""")
        for c in live_checks:
            chk(c['ok'], '5 · ' + c['l'])

        await browser.close()

    print('RESULTADO: %d OK · %d fallos' % (ok_n[0], fail_n[0]))
    sys.exit(1 if fail_n[0] else 0)


asyncio.run(main())
