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

## M1 · Capas de sonido de golpeo + háptica calibrada  ← SIGUIENTE (al abrir esta ronda)

**Qué**: el golpe ya suena; ahora debe SONAR COMO PING PONG REAL y sentirse en la mano.
- [ ] Sub-layers de impacto de pala: volumen/filtro según velocidad de impacto (toque suave · golpe normal · drive potente) + timbre distinto para golpe limpio del centro vs golpe de borde/mal contacto.
- [ ] Sonidos propios ya existentes respetados: mesa, red, suelo, fuera (no romper nada de lo probado).
- [ ] Háptica calibrada: intensidad de la vibración proporcional a la velocidad del impacto (toque ≈ suave, remate ≈ fuerte), con techo para no saturar el mando y mínimo perceptible.
- [ ] Todo con la SDK de audio de la casa (c03) y sin assets nuevos (variar parámetros del motor, cero peso de red).
- **Criterio de aceptación**: en la cancha, un toque suave y un remate se distinguen de oído y por la vibración; QA en verde; producción verificada.

## M2 · Guía de primera vez (onboarding)

**Qué**: quien entra por primera vez sabe jugar en 60 segundos sin leer un manual.
- [ ] Panel de bienvenida la PRIMERA vez (localStorage `ppxr_tut_v1`): 3–4 pasos ilustrados (agarre del mando · golpeo · saque · dónde está el marcador) + botón «Entendido, a jugar».
- [ ] Pistas contextuales ligeras en la cancha (no invasivas): cartel flotante de recordatorio de saque si el jugador se queda quieto >8 s con el saque pendiente.
- [ ] Re-mostrable desde el menú (botón «Cómo se juega»), y saltado automáticamente si ya se completó.
- [ ] i18n ES/EN completo.
- **Criterio de aceptación**: primera partida arranca con la guía; segunda ya no sale; el botón del menú la reabre; QA en verde.

## M3 · IA con estilos (8–12 personalidades, SIN trampas)

**Qué**: los rivales dejan de ser clónicos. Mismo motor físico honesto (usa `errStd`, `missBase`, `maxShotSpeed`, `predictInterval` y decisiones de golpeo EXISTENTES — nada de leer la bola por detrás ni velocidades imposibles).
- [ ] Definir 10 estilos con nombre y carácter (p. ej. Muro — bloquea bajo y espera el error · Cañonera — vive del drive · Lobera — bolas altas y lejos · Cortadora — juego cortado y lento · Loca del Efecto — spin por todos lados · Pescadora — coloca a las esquinas · Metrónomo — ritmo perfecto y sin florituras · Impaciente — se abovega y falla más pero pega fuerte · Diplomática — adaptativa: sube el ritmo si tú bajas · Acosadora — devuelve todo hasta el extrema rally).
- [ ] Cada estilo = preset de parámetros EXISTENTES (más selección de zona de colocación y clearance de red si el motor ya lo decide así) + nombre visible en el marcador/HUD.
- [ ] Reparto por dificultad: Nv.1 usa estilos suaves, Nv.2 medios, Nv.3 los duros; el torneo mezcla estilos según ronda.
- [ ] i18n ES/EN de nombres y una línea de descripción.
- **Criterio de aceptación**: jugando 3 partidos seguidos se NOTAN personalidades distintas (ritmo, altura, colocación); sin datos nuevos de red; QA en verde.

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

## M6 · PWA instalable

**Qué**: CRAZY PING PONG desde el menú de apps del Quest, sin escribir URL.
- [ ] `manifest.webmanifest` (nombre, iconos 192/512, display fullscreen, orientación landscape) + service worker con estrategia cache-first para game.html y assets grandes pas-through.
- [ ] Icono/og-image generados de la identidad de la casa (palas cruzadas + bola).
- [ ] Verificación con Lighthouse/Playwright: instalable, arranca offline la cáscara (el peso grande sigue siendo online-first para no engañar).
- **Criterio de aceptación**: en el Quest Browser aparece «Instalar app» y abre a pantalla completa sin barra; QA en verde.

## M7 · Contenido e identidad (el grande, en fases)

**Qué**: más juego, más personalidad. Requiere las anteriores asentadas. SE DIVIDE:
- M7a · Torneos temáticos con los assets del dueño ya en `upload/` (calabaza, gelatina, monticulo, mesa, Pizarra, derecha/izquierda…): al menos 1 temática nueva jugable de principio a fin.
- M7b · SuperPalas (assets `SuperPala_*.png` del dueño: Clon, Crece, Efecto, Imán, Portal) como power-ups de modo crazy.
- M7c · 2v2 (doble local + IA) — investigación y prototipo.
- M7d · PRO TRAINING extendido (más ejercicios, medallas por ejercicio).
- M7e · Persistencia completa (perfil con piel/pala elegida recordada, historial de torneos).
- **Criterio de aceptación**: cada sub-fase se despliega por separado con su propia ronda; nada se queda a medias en producción.

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

### Pipeline estándar (recordatorio para cada ronda)
1. Explorar módulos afectados (c12 con base64: leer SOLO por rangos con python3).
2. Implementar en `src/game/core/` + i18n en c00. `node --check` a cada módulo tocado.
3. QA dev: qa_todo (o capas afectadas) + arnés runtime si toca conducta.
4. `python3 scripts/bump_version.py 3.6.XX-SDK6 --fase N --fase-nombre "…" [--sdk 1.5.4]`
5. `qa_rendimiento --update` · `gen_release_vNNN.py` · `build_zip` (4 ZIPs) · `sella_rNNN.py`
6. QA TOTAL verde → commit+push → `GIT_TOKEN=$(cat scripts/worker-tele/.github-pat) python3 scripts/deploy_pages.py --push --release --backup`
7. Verificación de producción (curl: PAGES-VERSION, agujas en game.html servido, champ_sdk SDK_VERSION, tamaños).
8. worklog.md (Task N) + marcar checkbox aquí + commit «worklog · roadmap» + push.
