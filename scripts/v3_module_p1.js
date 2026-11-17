/* =====================================================================
 *  v3.0 · PRO TRAINING — CENTRO DE ALTO RENDIMIENTO (CRAZY PING PONG)
 *  ---------------------------------------------------------------------
 *  Módulo AUTOCONTENIDO y AISLADO. Añade al apartado de entrenamiento:
 *   · Subapartado 0: posición de la pala (el panel de siempre, ahora
 *     plegado dentro del hub como un modo más).
 *   · 5 áreas profesionales × 2 modos (dirección, altura, efecto,
 *     saque y ritmo) con jueces propios, máquina de bolas con efecto
 *     real (Magnus incluido en el solver) y objetivos encadenados.
 *   · Feedback técnico: marcas de bote, línea de tiro real, indicador
 *     de efecto sobre la bola y panel flotante con el progreso.
 *   · Puntos → perfil (localStorage) → PIELS de pala desbloqueables
 *     seleccionables en TODOS los modos (única vía de salida).
 *   · Iconos de efecto en AMBAS caras de la pala (cosmética global,
 *     activa también en campeonatos: el efecto ya existía en la
 *     física del núcleo; aquí se HACE VISIBLE sin tocar la física).
 *  NUNCA modifica física, árbitro, IA ni campeonatos. Todo vive en
 *  window.__PP_TRAIN y en su grupo de escena propio (trainGrp).
 *  ===================================================================== */
const PP_TRAIN = (() => {
  'use strict';

  /* ---------------- almacenamiento del perfil ---------------- */
  const KEY = 'ppxr_train_v1';
  const DEF = {
    pts: 0, best: {}, done: {}, unlocked: ['clasica'],
    skin: 'clasica', fb: { marks: 1, line: 1, spin: 1 },
  };
  let S = (() => {
    try {
      const raw = localStorage.getItem(KEY);
      if (!raw) return JSON.parse(JSON.stringify(DEF));
      const d = Object.assign(JSON.parse(JSON.stringify(DEF)), JSON.parse(raw));
      d.fb = Object.assign({ marks: 1, line: 1, spin: 1 }, d.fb || {});
      if (!Array.isArray(d.unlocked) || !d.unlocked.length) d.unlocked = ['clasica'];
      return d;
    } catch (e) { return JSON.parse(JSON.stringify(DEF)); }
  })();
  const save = () => { try { localStorage.setItem(KEY, JSON.stringify(S)); } catch (e) { /* */ } };

  /* ---------------- i18n mínima del módulo ---------------- */
  let LANG = (typeof __ppLang !== 'undefined' && __ppLang) || 'es';
  const TR = {
    es: {
      hub_t: 'PRO TRAINING', hub_s: 'Centro de alto rendimiento · CRAZY PING PONG',
      perfil: 'PERFIL', pts: 'puntos', nivel: 'Nivel', volver: '‹ Volver', menu: '‹ Menú',
      a_dir: 'DIRECCIÓN', a_dir_s: 'Profundidad y colocación',
      a_alt: 'ALTURA', a_alt_s: 'Control sobre la red',
      a_spin: 'EFECTO', a_spin_s: 'Lee y devuelve el giro',
      a_saq: 'SAQUE', a_saq_s: 'Corto de doble bote y largo',
      a_rit: 'RITMO', a_rit_s: 'Regularidad y consistencia',
      a_pala: 'POSICIÓN DE LA PALA', a_pala_s: 'Ajusta el agarre sobre tu mano',
      fb_t: 'AYUDAS TÉCNICAS', fb_marks: 'Marcas de bote', fb_line: 'Línea de tiro', fb_spin: 'Flecha de efecto',
      skins_t: 'PIEL DE LA PALA', skin_sel: 'Elegida', skin_lock: 'puntos',
      obj: 'Objetivo', mejor: 'Mejor', iniciar: '▶ INICIAR', activo: 'EN CURSO', parar: '■ Detener entrenamiento',
      seg: 'seguidas',
      m_t1a: 'MESA MARCADA', m_t1a_d: 'Lleva la bola {n} veces seguidas a la zona dorada. El centro (rojo) es la zona fácil del rival: evítala.',
      m_t1b: 'JUNTO A LA LÍNEA', m_t1b_d: 'Coloca {n} bolas seguidas rozando las bandas laterales o el fondo. Cuanto más cerca de la línea, más difícil es para el rival.',
      m_t2a: 'PASE BAJO', m_t2a_d: 'Golpea drives profundos pasando ENTRE la red y la cinta naranja (17 cm). Si pasas por encima, el rival te remata.',
      m_t2b: 'GLOBO DEFENSIVO', m_t2b_d: 'Levanta {n} globos seguidos por encima del aro y que boten en el fondo rival. Gana tiempo cuando estás en apuros.',
      m_t3a: 'LEER EL CORTADO', m_t3a_d: 'La máquina lanza bolas con corte pesado. Devuélvelas {n} veces seguidas con la pala abierta: sin tocar la red y sin levantarla.',
      m_t3b: 'BLOQUEAR EL TOPSPIN', m_t3b_d: 'Bolas con lift fuerte y velocidad variable. Bloquea o contraataca {n} veces seguidas con la pala cerrada.',
      m_t4a: 'SAQUE CORTO · DOBLE BOTE', m_t4a_d: 'Saca y consigue que la bola BOTE DOS VECES en la zona marcada junto a la red. El saque corto evita el ataque rival.',
      m_t4b: 'SAQUE LARGO · AL FONDO', m_t4b_d: 'Coloca {n} primeros botes en la franja de los últimos 15 cm. Saque rápido y tenso pegado al fondo.',
      m_t5a: 'METRÓNOMO', m_t5a_d: 'Bolas a ritmo constante: devuelve el máximo número seguidas. Hitos a 30 · 50 · 100 con bonus.',
      hud_racha: 'RACHA', hud_meta: 'META', hud_bote: 'BOTES', hud_rally: 'RALLY', hud_sesion: 'Sesión', hud_total: 'Total',
      ok_zona: '¡ZONA!', ok_banda: '¡A LA LÍNEA!', ok_bajo: '¡PASE BAJO!', ok_globo: '¡GLOBO!', ok_leido: '¡BIEN LEÍDO!', ok_bloqueo: '¡BLOQUEO!', ok_doble: '¡DOBLE BOTE!', ok_fondo: '¡AL FONDO!', ok_beat: '¡RITMO!',
      mal_alto: 'MUY ALTO · te rematan', mal_corta: 'CORTA · al centro', mal_red: 'A LA RED', mal_fuera: 'FUERA', mal_larga: 'LARGO', mal_pierde: 'SE PIERDE',
      hecho: '¡COMPLETADO! +{n} pts', nuevo_skin: 'PIEL NUEVA: {s} · elígela en el hub', hito: '¡HITO {n} RALLY! +{n2} pts',
      sirve: 'Pulsa el gatillo y golpea la bola para sacar', fin_rally: 'Rally terminado: {n}',
      lvl0: 'Novato', lvl1: 'Amateur', lvl2: 'Competidor', lvl3: 'Maestro', lvl4: 'Leyenda',
    },
    en: {
      hub_t: 'PRO TRAINING', hub_s: 'High performance center · CRAZY PING PONG',
      perfil: 'PROFILE', pts: 'points', nivel: 'Level', volver: '‹ Back', menu: '‹ Menu',
      a_dir: 'DIRECTION', a_dir_s: 'Depth and placement',
      a_alt: 'HEIGHT', a_alt_s: 'Net clearance control',
      a_spin: 'SPIN', a_spin_s: 'Read and return the spin',
      a_saq: 'SERVE', a_saq_s: 'Short double-bounce and long',
      a_rit: 'RHYTHM', a_rit_s: 'Consistency and regularity',
      a_pala: 'PALA POSITION', a_pala_s: 'Fit the grip to your hand',
      fb_t: 'TECH AIDS', fb_marks: 'Bounce marks', fb_line: 'Shot line', fb_spin: 'Spin arrow',
      skins_t: 'PALA SKIN', skin_sel: 'Selected', skin_lock: 'points',
      obj: 'Goal', mejor: 'Best', iniciar: '▶ START', activo: 'RUNNING', parar: '■ Stop training',
      seg: 'in a row',
      m_t1a: 'MARKED TABLE', m_t1a_d: 'Hit {n} balls in a row into the gold zone. The center (red) is the opponent\u2019s easy zone: avoid it.',
      m_t1b: 'HUG THE LINE', m_t1b_d: 'Place {n} balls in a row grazing the side bands or the baseline. The closer to the line, the harder to return.',
      m_t2a: 'LOW PASS', m_t2a_d: 'Hit deep drives passing BETWEEN the net and the orange ribbon (17 cm). Over it and they smash you.',
      m_t2b: 'DEFENSIVE LOB', m_t2b_d: 'Lift {n} lobs in a row above the hoop landing deep. Buy time when you are in trouble.',
      m_t3a: 'READ THE CHOP', m_t3a_d: 'The machine fires heavy backspin. Return them {n} times in a row with an open blade: no net, no pop-up.',
      m_t3b: 'BLOCK THE TOPSPIN', m_t3b_d: 'Strong topspin at varying speed. Block or counter {n} times in a row with a closed blade.',
      m_t4a: 'SHORT SERVE · DOUBLE BOUNCE', m_t4a_d: 'Serve so the ball BOUNCES TWICE in the marked zone near the net. Short serves prevent attacks.',
      m_t4b: 'LONG SERVE · DEEP', m_t4b_d: 'Land {n} first bounces in the last 15 cm strip. Fast, tight serves to the baseline.',
      m_t5a: 'METRONOME', m_t5a_d: 'Balls at a steady beat: return as many as you can in a row. Milestones at 30 · 50 · 100 with bonuses.',
      hud_racha: 'STREAK', hud_meta: 'GOAL', hud_bote: 'BOUNCES', hud_rally: 'RALLY', hud_sesion: 'Session', hud_total: 'Total',
      ok_zona: 'ZONE!', ok_banda: 'ON THE LINE!', ok_bajo: 'LOW PASS!', ok_globo: 'LOB!', ok_leido: 'WELL READ!', ok_bloqueo: 'BLOCK!', ok_doble: 'DOUBLE BOUNCE!', ok_fondo: 'DEEP!', ok_beat: 'RHYTHM!',
      mal_alto: 'TOO HIGH · they smash', mal_corta: 'SHORT · center', mal_red: 'INTO THE NET', mal_fuera: 'OUT', mal_larga: 'LONG', mal_pierde: 'LOST',
      hecho: 'COMPLETED! +{n} pts', nuevo_skin: 'NEW SKIN: {s} · pick it in the hub', hito: 'MILESTONE {n} RALLY! +{n2} pts',
      sirve: 'Pull the trigger and hit the ball to serve', fin_rally: 'Rally over: {n}',
      lvl0: 'Rookie', lvl1: 'Amateur', lvl2: 'Contender', lvl3: 'Master', lvl4: 'Legend',
    },
  };
  const t = (k, vars) => {
    let s = (TR[LANG] && TR[LANG][k]) || TR.es[k] || k;
    if (vars) for (const kk of Object.keys(vars)) s = s.split('{' + kk + '}').join(String(vars[kk]));
    return s;
  };

  /* ---------------- niveles y skins ---------------- */
  const LEVELS = [
    { min: 0, k: 'lvl0' }, { min: 150, k: 'lvl1' }, { min: 400, k: 'lvl2' },
    { min: 800, k: 'lvl3' }, { min: 1500, k: 'lvl4' },
  ];
  const levelOf = (p) => { let l = LEVELS[0]; for (const it of LEVELS) if (p >= it.min) l = it; return l; };

  const SKINS = [
    { id: 'clasica', name: { es: 'Clásica', en: 'Classic' }, min: 0, ring: 0xd8d2c4, grip: 0x6b4a2f },
    { id: 'fuego', name: { es: 'Fuego', en: 'Fire' }, min: 150, ring: 0xff5a2a, grip: 0xc22a12 },
    { id: 'hielo', name: { es: 'Hielo', en: 'Ice' }, min: 400, ring: 0x35c4e8, grip: 0x1479a3 },
    { id: 'oro', name: { es: 'Oro', en: 'Gold' }, min: 800, ring: 0xf2c14e, grip: 0xb8860b },
    { id: 'arcoiris', name: { es: 'Arcoíris', en: 'Rainbow' }, min: 1500, ring: -1, grip: 0x8e44ad },
  ];

  /* ---------------- registro de modos ---------------- */
  const AREAS = [
    { id: 'dir', ik: 'a_dir', sk: 'a_dir_s', g0: '#2b6cb0', g1: '#16324f', col: '#63b3ed' },
    { id: 'alt', ik: 'a_alt', sk: 'a_alt_s', g0: '#2f855a', g1: '#1a4433', col: '#68d391' },
    { id: 'spin', ik: 'a_spin', sk: 'a_spin_s', g0: '#805ad5', g1: '#44337a', col: '#d6bcfa' },
    { id: 'saque', ik: 'a_saq', sk: 'a_saq_s', g0: '#c05621', g1: '#652a12', col: '#f6ad55' },
    { id: 'rit', ik: 'a_rit', sk: 'a_rit_s', g0: '#b83280', g1: '#5f1e42', col: '#f687b3' },
  ];
  const MODES = {
    t1a: { area: 'dir', nk: 'm_t1a', dk: 'm_t1a_d', n: 5, ok: 'ok_zona', pts: 1, bonus: 15 },
    t1b: { area: 'dir', nk: 'm_t1b', dk: 'm_t1b_d', n: 5, ok: 'ok_banda', pts: 2, bonus: 20 },
    t2a: { area: 'alt', nk: 'm_t2a', dk: 'm_t2a_d', n: 5, ok: 'ok_bajo', pts: 2, bonus: 20 },
    t2b: { area: 'alt', nk: 'm_t2b', dk: 'm_t2b_d', n: 4, ok: 'ok_globo', pts: 2, bonus: 20 },
    t3a: { area: 'spin', nk: 'm_t3a', dk: 'm_t3a_d', n: 5, ok: 'ok_leido', pts: 2, bonus: 20 },
    t3b: { area: 'spin', nk: 'm_t3b', dk: 'm_t3b_d', n: 6, ok: 'ok_bloqueo', pts: 2, bonus: 25 },
    t4a: { area: 'saque', nk: 'm_t4a', dk: 'm_t4a_d', n: 3, ok: 'ok_doble', pts: 3, bonus: 15 },
    t4b: { area: 'saque', nk: 'm_t4b', dk: 'm_t4b_d', n: 3, ok: 'ok_fondo', pts: 3, bonus: 15 },
    t5a: { area: 'rit', nk: 'm_t5a', dk: 'm_t5a_d', n: 30, ok: 'ok_beat', pts: 1, bonus: 15 },
  };
