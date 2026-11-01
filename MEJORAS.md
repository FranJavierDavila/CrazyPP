# CRAZY PING PONG · ROADMAP MAESTRO DE MEJORAS (M1 → M8)

> **Memoria viva del proyecto** — creada r106 (nov 2026). El dueño mandó
> implementar TODAS las mejoras del análisis crítico; Z (arquitecto) fija el
> orden **de más sencillo a más complicado**. Este fichero se actualiza al
> cerrar cada hito: marca `[x]`, anota la ronda/versión en la que se cerró y
> queda señalado cuál es la SIGUIENTE. Persiste en el repo (GitHub) y en el
> sandbox — nunca se pierde entre sesiones.
>
> Regla de oro: **cada hito = rondas QA→bump→empaquetar→deploy→verificación
> tres vías** completas, como siempre. Nada se da por hecho sin agujas verdes.

## Cola de ejecución (estado)

| # | Hito | Esfuerzo | Estado |
|---|------|----------|--------|
| M1 | Game feel · capas de sonido + hápticas calibradas | ★☆☆ | ✅ HECHA r106 · v3.6.98-SDK6 en producción |
| M2 | Arnés anti-regresión + alarmas de telemetría | ★★☆ | ⏳ SIGUIENTE (r107) |
| M3 | PWA instalable (adiós `?v=`, icono en el casco) | ★★☆ | ⬜ pendiente |
| M4 | Onboarding < 60 s (rally demo + JUGAR + saque guiado) | ★★☆ | ⬜ pendiente |
| M5 | IA con estilos (8-12 personalidades) + escalera de carrera | ★★★ | ⬜ pendiente |
| M6 | Identidad "locura + entrenador" (power-ups, 2v2, campeonatos) | ★★★ | ⬜ pendiente |
| M7 | Matchmaking + ELO online + reto diario/torneo semanal | ★★★★ | ⬜ pendiente |
| M8 | Port nativo a tienda (App Lab / Horizon) | ★★★★★ | ⬜ pendiente (decisión estratégica) |

---

## M1 · GAME FEEL — capas de sonido de impacto + hápticas calibradas ✅ HECHA (r106 · v3.6.98-SDK6)

> **CORRECCIÓN DE AUDITORÍA (r106):** el análisis crítico inicial se hizo sobre
> un árbol reciclado a r35 por error del sandbox. El juego r105 YA TRAE desde
> la r62 «SFX REALES»: muestras físicas modales (cáscara 40 mm + transitorio +
> cuerpo) para mesa/pala/canto/red/suelo, playbackRate mapeado a la velocidad,
> jitter ±1,5 % y fallback sintético. La mitad de AUDIO de M1 estaba hecha.
> Lo que quedaba vivo era la HÁPTICA del bote (0,18 fija, fuera del guard
> anti-spam) — eso es lo que r106 implementa.

**Alcance:**
- [x] Capas por material ≥3 variantes × 2 alturas + jitter — **YA EXISTÍA
      (r62 SFX REALES)**: 5 muestras físicas (mesa/pala/canto/red/suelo),
      rate 0,84→1,34 por velocidad, jitter ±1,5 %; verificado en r106.
- [x] Hápticas calibradas (r106): bote de mesa proporcional a velocidad
      (0,08+0,16·s · 50–80 ms) y DENTRO del guard de 60 ms (antes: 0,18 fija
      en cada evento = ametralladora en ráfagas esquina+canto).
- [x] Canto distinguible al tacto (r106): pico más alto (0,14+0,16·s) y seco
      (28 ms) frente al bote llano.
- [x] Red palpable (r106): vibración sutil 0,15/45 ms al roce de la malla
      (eventos raros: sin riesgo de spam).
- [x] Háptica de pala ya escalada (r62: intensidad 0,35+0,65·s y duración
      34–96 ms por velocidad) — intacta; anti-ametralladora por diseño.

**Criterios de aceptación:** 12 golpes seguidos suenan distintos (r62 ya
cumple: jitter + rate por velocidad) · háptica bote suave≠bote fuerte≠canto
percibible · net-cord se siente · sin regresión de FPS (cascada presupuesto) ·
agujas r106 en producción.

---

## M2 · ARNÉS ANTI-REGRESIÓN + ALARMAS DE TELEMETRÍA

**Por qué segundo:** protege TODAS las rondas futuras. Hoy 208 verificaciones
estáticas no juegan; el dueño descubre las regresiones (saque roto, deriva del
puntero, FPS). Que juegue la máquina primero.

**Alcance:**
- [ ] Arnés headless que JUEGA: 200 rallies simulados (saque→bote→golpeo→punto
      con la física real), barrido completo de menús (cada página, cada botón,
      sliders a extremos) y verificación de invariants por frame (bola dentro
      de mundo, pala rival anclada, sin NaN).
- [ ] Alarmas de telemetría: FPS p95 por sesión, tasa de fallo de saque,
      caídas/errores JS — umbrales con alarma en el resumen del worker.
- [ ] Gate de ronda: si el arnés roja, NO se despliega.

**Criterios de aceptación:** el arnés detecta al menos 1 bug sembrado a
propósito (test canario) · alarmas visibles en el visor analítico.

---

## M3 · PWA INSTALABLE

**Por qué:** mata el mayor matador de retención (URL + `?v=` + caché del Quest)
sin esperar el port nativo. Icono en el casco, arranque en 2 clics, actualización
por service worker.

**Alcance:**
- [ ] `manifest.webmanifest` + iconos 192/512 + service worker con estrategia
      cache-first por versión (el bump ya existente gobierna la caché).
- [ ] Página/aviso "instalar en el casco" y detección de standalone.
- [ ] Deploy compatible con GitHub Pages bajo `/CrazyPP/`.

**Criterios de aceptación:** instalada desde el navegador del Quest, arranca
desde el icono sin teclear URL · el bump de versión invalida la caché sola.

---

## M4 · ONBOARDING < 60 SEGUNDOS

**Alcance:**
- [ ] Rally demostración IA-vs-IA en vivo de fondo en el menú principal.
- [ ] Botón único **JUGAR** por delante de todo lo demás.
- [ ] Saque guiado la primera vez (fantasma del gesto + texto de una línea),
      marcado como visto en localStorage.
- [ ] Idioma y altura de mesa detectados/recordados antes del primer toque.

**Criterios de aceptación:** un jugador nuevo está en un rally real en <60 s
sin tocar nada más que JUGAR (medible con telemetría: evento primer_rally_ts).

---

## M5 · IA CON ESTILOS + ESCALERA DE CARRERA

**Alcance:**
- [ ] 8-12 personalidades con parámetros y tácticas propias SOBRE la física
      compartida (sin trampas): Looper (lift desde lejos), Chopero (slice
      profundo), Bloqueador (pegado, reflejos), Atacante (smash temprano),
      Defensivo (lobs), Cortador de dejadas, All-round, Joven nervioso,
      Veterano frío, Gigante (alcance), Pequeño rápido…
- [ ] Cada estilo = perfil (posición de casa, profundidad, pesos de selección
      de golpe, errStd, velocidad, estética de swing) + UI con retrato/nombre.
- [ ] Escalera de carrera: divisiones de bronce→leyenda, rivales concretos por
      división, progreso guardado, rematches con revancha.
- [ ] Integración con campeonatos existentes (los rivales heredan estilos).

**Criterios de aceptación:** la IA juega por las MISMA reglas físicas (agujas
de no-trampa) · 12 rivales distinguibles jugando 1 minuto contra cada uno.

---

## M6 · IDENTIDAD "LOCURA + ENTRENADOR"

**Alcance:**
- [ ] Modo fiesta: power-ups (bola loca, mesa encogida, pala gigante…) 1v1/2v2
      local + online-ready.
- [ ] 2-3 campeonatos temáticos nuevos (heredando champloader).
- [ ] PRO TRAINING expandido: nuevos ejercicios, progresión semanal y TARJETA
      DE PROGRESO compartible (captura con stats del mes).

**Criterios de aceptación:** los tres frentes jugables y con agujas; el
entrenador diferencia frente a Eleven (nuestro estandarte de marketing).

---

## M7 · MATCHMAKING + ELO ONLINE + COMPETICIÓN

**Alcance:**
- [ ] Backend de emparejamiento en el worker Cloudflare (D1): cola por nivel
      ELO + región, salas efímeras, señalización PeerJS asistida (el anfitrión
      publica su ID; el guest lo recibe del servidor — sin compartir códigos).
- [ ] ELO server-side con antifraude básico (firma de resultados, tasas sospechosas).
- [ ] Reto diario (semilla por fecha) + torneo semanal con tabla.
- [ ] Lista de amigos (códigos persistentes) e historial de rivales.

**Criterios de aceptación:** dos cascos se encuentran solos por nivel en <30 s ·
ELO persiste y sube/baja correctamente · el modo por códigos sigue intacto.

---

## M8 · PORT NATIVO A TIENDA

**La decisión estratégica mayor.** Evaluar: empaquetado nativo del motor propio
(WebXR→OpenXR) vs reconstrucción. Incluye assets de tienda, cumplimiento de
políticas, logros/plataforma, precio. Se abre el análisis cuando M1-M4 estén
cerradas (mejora el producto a presentar) y M7 decida si el online va en web o
nativo.

---

## Registro de cierre de hitos

| Hito | Ronda(s) | Versión | Fecha | Notas |
|------|----------|---------|-------|-------|
| M1 · game feel | r106 | 3.6.98-SDK6 (FASE 100) | 2026-11-01 | Audio r62 verificado como regresión · háptica del bote calibrada dentro del guard · canto distinguible · red palpable · QA 35/0 · cascada verde · tres vías 24/0 |
