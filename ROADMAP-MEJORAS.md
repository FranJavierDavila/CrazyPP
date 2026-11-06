# ROADMAP DE MEJORAS · CRAZY PING PONG

> Archivo de memoria persistente (petición del dueño): plan de 7 mejoras autorizadas,
> ordenadas de SIMPLE a COMPLEJO. Al cerrar cada mejora: marcar `[x]`, apuntar versión
> y ronda, y `git push` (el dueño pidió subir a GitHub para salvaguardar los avances).
> Regla permanente: avanzar sin preguntar; cada mejora pasa por la Pipeline completa
> (QA → bump → build → release → sello → qa_todo → commit+push → deploy_pages →
> verificación de producción → worklog).

Estado de partida: **V3.6.27-SDK6 (FASE 29 · Hall Of Fame) en producción**, pages `4548e7eca`.
Token de despliegue: `scripts/worker-tele/.github-pat` (GIT_TOKEN). Repo: `FranJavierDavila/CrazyPP`.

---

## M1 · Capas de sonido de golpeo + háptica calibrada  ☑ CERRADA (r62)

**Qué**: el golpe ya suena; ahora debe SONAR COMO PING PONG REAL y sentirse en la mano.
- [x] Sub-layers de impacto de pala: volumen/filtro según velocidad de impacto (toque suave · golpe normal · drive potente) + timbre distinto para golpe limpio del centro vs golpe de borde/mal contacto. *(r62 · 3.6.54-SDK6 · qa_r62 VERDE — ver registro.)*
- [x] Sonidos propios ya existentes respetados: mesa, red, suelo, fuera (no romper nada de lo probado). *(r62.)*
- [x] Háptica calibrada: intensidad de la vibración proporcional a la velocidad del impacto (toque ≈ suave, remate ≈ fuerte), con techo para no saturar el mando y mínimo perceptible. *(r62; escalada por velocidad del saque r62, nota háptica.)*
- [x] Todo con la SDK de audio de la casa (c03) y sin assets nuevos (variar parámetros del motor, cero peso de red). *(r62.)*
- **Criterio de aceptación**: CUMPLIDO EN PRODUCCIÓN DESDE 3.6.54 (marcado en r119 por higiene de memoria — los checkboxes estaban caducos frente al registro).

## M2 · Guía de primera vez (onboarding)  ☑ CERRADA (r111)

**Qué**: quien entra por primera vez sabe jugar en 60 segundos sin leer un manual.
- [x] Panel de bienvenida la PRIMERA vez (localStorage `ppxr_tut_v1`): 3–4 pasos ilustrados (agarre del mando · golpeo · saque · dónde está el marcador) + botón «Entendido, a jugar». *(r111 · 3.6.101-SDK6 · qa_r111 VERDE — ver registro.)*
- [x] Pistas contextuales ligeras en la cancha (no invasivas): cartel flotante de recordatorio de saque si el jugador se queda quieto >8 s con el saque pendiente. *(r111.)*
- [x] Re-mostrable desde el menú (botón «Cómo se juega»), y saltado automáticamente si ya se completó. *(r111.)*
- [x] i18n ES/EN completo. *(r111.)*
- **Criterio de aceptación**: CUMPLIDO EN PRODUCCIÓN DESDE 3.6.101 (marcado en r119 por higiene de memoria).

## M3 · IA con estilos (8–12 personalidades, SIN trampas)  ☑ CERRADA (r112)

**Qué**: los rivales dejan de ser clónicos. Mismo motor físico honesto (usa `errStd`, `missBase`, `maxShotSpeed`, `predictInterval` y decisiones de golpeo EXISTENTES — nada de leer la bola por detrás ni velocidades imposibles).
- [x] Definir 10 estilos con nombre y carácter. *(M5a r112 · 3.6.102-SDK6: 12 personalidades OPPONENT_STYLES — ver registro.)*
- [x] Cada estilo = preset de parámetros EXISTENTES + nombre visible en el marcador/HUD. *(r112: multiplicadores ACOTADOS sobre la cfg por el canal r95 (colocación/celebración); selector ‹ › en AJUSTES › JUEGO.)*
- [x] Reparto por dificultad + torneo mezcla estilos. *(r112/r115: el canal estilo sirve a la escalera de carrera y a la herencia de los campeonatos.)*
- [x] i18n ES/EN de nombres y una línea de descripción. *(r112.)*
- **Criterio de aceptación**: CUMPLIDO EN PRODUCCIÓN DESDE 3.6.102 — arnés de estilos 12×30 rallies (0 desviaciones, sin trampas) en el gate QA TOTAL (marcado en r119 por higiene de memoria).

## M4 · Matchmaking + ELO completo + bucle diario/semanal

**Qué**: razón para volver cada día.
- [x] ELO unificado (local vs IA y P2P cuando exista) con K distinto por modo, guardado en stats.data. *(M4, r118: K IA 24 · escalera 20 · humano 32; historial 40 cambios + mejor día; llamadas legacy de 2 args intactas.)*
- [x] Matchmaking local por ELO: el rival propuesto queda cerca de tu nivel (±120) con variedad. *(M4, r118: botón «Rival a tu nivel» en AJUSTES › JUEGO — bandas easy/medium/hard + k acotado 0.7-1.6, jamás propone un muro; la escalera de carrera manda si está activa.)*
- [x] Reto diario y reto semanal (semilla del día/semana + rival con estilo de M3 + premio de insignia). *(Diario vivo desde r76; semanal nuevo en r118: septana lunes→domingo, objetivo base+2 con subida semanal (tope 4), insignia acumulable + 120/30 pts, en el hueco 6 del hub.)*
- [x] Panel de ranking personal (histórico de ELO, racha, mejor día). *(M4, r118: página MI RANKING desde AJUSTES › JUEGO — ELO + último delta, marca, rachas, mejor día y últimos 8 cambios.)*
- **Criterio de aceptación**: dos días seguidos propone retos distintos y el ELO sube/baja coherente; todo local, sin servidor nuevo. *(QA r118: 29 OK · 0 fallos — matchmaking con 28 rivales distintos en 30 propuestas; ELO sube/baja según rival y modo.)*

## M5 · Arnés anti-regresión + alertas de telemetría

**Qué**: que ninguna versión futura rompa lo que ya funciona.
- [x] Arnés de regresión automatizado: arranque del game.html en Playwright + 30 checks invariantes (versión, audio SDK, menú, cancha, saque, IA responde, HUD, hall).
- [x] Compara JSON de checks contra línea base (`tests/baseline_checks.json`) y FALLA si algo se mueve sin justificación.
- [x] Alertas de telemetría: si FPS medio < 60 sostenido, errores JS > 0, o golpes sin sonido en producción → reporte `scripts/alerta_telemetria.py` con salida clara para el dueño. *(M5b, r117: alarma `sin_sonido` en el worker + reporte del dueño con códigos de salida 0/1/2/3 — fps_bajo/errores_js/vr_cortas ya vivían desde la ronda 18.)*
- **Criterio de aceptación**: romper a propósito una aguja hace fallar el arnés; suite < 3 min.

## M6 · PWA instalable  ☑ CERRADA (r109)

**Qué**: CRAZY PING PONG desde el menú de apps del Quest, sin escribir URL.
- [x] `manifest.webmanifest` + service worker cache-first con sello por versión (`const CACHE` gobernado por el bump). *(r109 · 3.6.99-SDK6 · qa_r109 VERDE — ver registro; en el gate QA TOTAL desde entonces.)*
- [x] Icono/og-image generados de la identidad de la casa (palas cruzadas + bola). *(r109.)*
- [x] Verificación: instalable, portada instaladora (diálogo nativo o camino manual), arranque offline de la cáscara. *(r109: runtime SW activo en scope raíz + toasts en portada.)*
- **Criterio de aceptación**: CUMPLIDO EN PRODUCCIÓN DESDE 3.6.99 (marcado en r119 por higiene de memoria).

## M7 · Contenido e identidad (el grande, en fases)  ← EN CURSO (queda M7e)

**Qué**: más juego, más personalidad. Requiere las anteriores asentadas. SE DIVIDE:
- [x] M7a · Torneos temáticos: al menos 1 temática nueva jugable de principio a fin. *(5 campeonatos vivos: locura · magia · oeste · estacion_orbital · halloween (rival ZOMBI del dueño, r85-r97); marcado en r119 por higiene de memoria — el contenido sigue creciendo por rondas del dueño.)*
- [x] M7b · SuperPalas como power-ups de modo crazy. *(5 poderes vivos con iconos del dueño: MEGA/Crece · EFECTO · IMÁN · PORTAL · CLON — verificado en c12 en r119; marcado por higiene de memoria.)*
- [x] M7c · 2v2 (doble local + IA) — investigación y prototipo. *(M7c r119 · 3.6.108-SDK6: investigación = árbitro ya de equipos + OpponentAI simétrico por sign; prototipo = botón «DOBLES 2v2» en AJUSTES › JUEGO, compañero IA + rival 2 con ARBITRAJE DE ALCANCE 0,50 m, física y árbitro del 1v1 intactos (cero cambios en c04/c05/c06), vive SOLO un partido, qa_r119 26/0 + QA TOTAL verde.)*
- [x] M7d · PRO TRAINING extendido (más ejercicios, medallas por ejercicio). *(M7d r120 · 3.6.109-SDK6: t1c ESQUINA EXACTA y t5b METRÓNOMO LOCO (11 ejercicios) + medallas BRONCE/PLATA/ORO derivadas y RETROACTIVAS (habilidad: estrellas+precisión · rally: la marca) con medallero por área en el hub + logro MEDALLERO DE ORO (n/10); PLAN_POOL congela los retos r76/r118 byte-idénticos; re-ancladas en el camino vivo las estrellas y m50/m100 del metrónomo (muertos desde v3.0.2).)*
- [ ] M7e · Persistencia completa (perfil con piel/pala elegida recordada, historial de torneos).
- **Criterio de aceptación**: cada sub-fase se despliega por separado con su propia ronda; nada se queda a medias en producción. *(M7a/b/c cumplidos; la investigación r119 dejó documentado que el 2v2 completo — reglas ITTF de alternancia intra-equipo y marcador de 4 nombres — puede crecer sin tocar el núcleo.)*

---

## Registro de cierre (para no perder la memoria)

| Mejora | Versión | Ronda/Task | Estado | Fecha |
|---|---|---|---|---|
| (partida) | 3.6.27-SDK6 | ronda 35 · Task 135 | producción | 2026-10-20 |
| M1 sonido real + háptica | 3.6.54-SDK6 | r62 · qa_r62 VERDE | ☑ producción | 2026-10 |
| M2 onboarding <60 s | 3.6.101-SDK6 | r111 · qa_r111 VERDE | ☑ producción | 2026-11 |
| M3 estilos de IA (12) | 3.6.102-SDK6 | r112 · arnés 12/0 | ☑ producción | 2026-11 |
| M4 ELO completo (unificado + matchmaking + reto semanal + MI RANKING) | 3.6.107-SDK6 | r118 · Task 223 · qa_r118 29/0 | ☑ producción | 2026-11-04 |
| M5 arnés físico+vivo + alertas de telemetría (M5b: `sin_sonido` + `alerta_telemetria.py`) | vivo | test_local 67/0 · deploy worker 2026-11-04 | ☑ producción | 2026-11-04 |
| M6 PWA instalable | 3.6.99-SDK6 | r109 · qa_r109 VERDE | ☑ producción | 2026-11 |
| M7 contenido (5 campeonatos) | continuo | FASE 20-107 | ☐ en curso | — |
| Ajustes del dueño: física fuerte + CPU + superpoderes justos + Locura etapa 4 | 3.6.103-SDK6 | r113 · Task 218 | ☑ producción | 2026-11-03 |
| Ajustes del dueño: chincheta por estancia + fuera el diorama | 3.6.104-SDK6 | r114 · Task 219 | ☑ producción | 2026-11-04 |
| Ajustes del dueño: fuera la repetición del mejor punto + superpoder EN EL GOLPEO rival (+ M5B escalera de carrera y herencia de estilos de la sesión perdida) | 3.6.105-SDK6 | r115 · Task 220 | ☑ producción | 2026-11-04 |
| Ajustes del dueño: Academia paso 4 sin bloqueos + «PASE BAJO»/logros del PRO TRAINING (regla de casa: QA dirigida por cambio) | 3.6.106-SDK6 | r116 · Task 221 | ☑ producción | 2026-11-04 |
| M5b · alertas de telemetría: alarma `sin_sonido` en el worker (errores con marcador audio + futuro `golpe_sin_sonido`) + reporte del dueño `scripts/alerta_telemetria.py` (salidas 0/1/2/3) | worker (infra) | r117 · Task 222 | ☑ producción | 2026-11-04 |
| M4 · ELO completo: unificado con K por modo (IA 24/escalera 20/humano 32) + matchmaking «Rival a tu nivel» ±120 + reto de la semana con insignia + página MI RANKING | 3.6.107-SDK6 | r118 · Task 223 | ☑ producción | 2026-11-04 |
| M7c · DOBLES 2v2 prototipo: investigación (árbitro ya de equipos + OpponentAI simétrico) + prototipo jugable (compañero IA + rival 2, arbitraje de alcance 0,50 m, cero cambios en física/árbitro) | 3.6.108-SDK6 | r119 · Task 224 | ☑ producción | 2026-11-04 |
| M7d · PRO TRAINING extendido: 2 ejercicios nuevos (ESQUINA EXACTA + METRÓNOMO LOCO) + medallas BRONCE/PLATA/ORO por ejercicio (retroactivas, medallero en el hub) + logro MEDALLERO DE ORO + m50/m100 re-anclados al juez vivo | 3.6.109-SDK6 | r120 · Task 225 · qa_r120 39/0 | ☑ producción | 2026-11-05 |
| M-RED · multijugador verificado al 100% (requisito Nº 1 del dueño): 2 bugs reales del validador reparados (pose fantasma con hueco de pose → POSE_FRESH_MS ±150 ms bidireccional; cadencia contaba el lanzamiento) + saque del INVITADO con rotación ITTF en banco S3 y batería de 4 puntos (P1 67 · P2 68 · P3 69, 0 fallos, verde también a 120 ms ±40/5 %) | 3.6.110-SDK6 | r121 · Task 226 · banco 18/0 · qa_r81 136/0 · qa_r82 48/0 | ☑ producción | 2026-11-05 |
| M-RED2 · revisión completa del netcode (petición del dueño): FIX CRÍTICO resync SIN perspectiva (el invitado quedaba con el marcador DEL REVÉS y podía coronar victoria/ELO falsos) + gameOpener en el resync · guardia de estado ante HIT atrasados · resync-req (un rechazo legal ya no atasca el lado) · claim SIN autoridad (divergencia detectable) · toss caído re-arma el HELD · higiene RTC (_helloTO, AudioContext, markSent en SNAP, carrera de invitados) · fuga del 2v2 a la academia cerrada · PULSO/reto semanal en el camino vivo (deuda v3.0.2) | 3.6.111-SDK6 | r122 · Task 227 · QA completa 75 capas verde · batería P1 67/0 · P2 68/0 · P3 69/0 · test_red_nucleo 60/0 | ☑ producción | 2026-11-05 |
| M-RED3 · segunda ronda de análisis multijugador: endurecimiento del decodificador fast — cap de eventos al máximo del protocolo (spec §5, los emisores ya sellaban a 8) + escudo try/catch en el canal fast (un paquete malformado ya no aborta el handler: eco NTP/acks/reloj/pérdida intactos) · test_f1_decode nuevo 6/0 · arnés con volcado diagnóstico al fallar HANDOFF · dualidad de espejos posFromNet/posFromNetPose auditada (correcta, convención dual r81/v2.91) | 3.6.112-SDK6 | r123 · Task 228 · test_red_nucleo 60/0 · qa_r79 59/0 · qa_r80 81/0 · qa_r81 136/0 · qa_r82 48/0 · duelo VERDE · descargas 208/0 | ☑ producción | 2026-11-05 |

### Pipeline estándar (recordatorio para cada ronda)
1. Explorar módulos afectados (c12 con base64: leer SOLO por rangos con python3).
2. Implementar en `src/game/core/` + i18n en c00. `node --check` a cada módulo tocado.
3. QA dev: qa_todo (o capas afectadas) + arnés runtime si toca conducta.
4. `python3 scripts/bump_version.py 3.6.XX-SDK6 --fase N --fase-nombre "…" [--sdk 1.5.4]`
5. `qa_rendimiento --update` · `gen_release_vNNN.py` · `build_zip` (4 ZIPs) · `sella_rNNN.py`
6. QA TOTAL verde → commit+push → `GIT_TOKEN=$(cat scripts/worker-tele/.github-pat) python3 scripts/deploy_pages.py --push --release --backup`
7. Verificación de producción (curl: PAGES-VERSION, agujas en game.html servido, champ_sdk SDK_VERSION, tamaños).
8. worklog.md (Task N) + marcar checkbox aquí + commit «worklog · roadmap» + push.
