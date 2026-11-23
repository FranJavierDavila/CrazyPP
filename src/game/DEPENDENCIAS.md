# CRAZY PING PONG · GRAFO DE DEPENDENCIAS DEL NÚCLEO (fase 2)

Generado por `scripts/mod_fase2_analizar.mjs` (acorn, scopes AST). Golden: `# SHA256 del gam…`

## Qué declara, exporta e importa cada subsistema

| Fichero | Líneas | Declara | Exporta | Importa desde | Biblioteca |
|---|---|---|---|---|---|
| c00_pre_three.js | 3855 | 15 | 13 | — | — |
| c01_modelos_3d.js | 306 | 16 | 8 | — | — |
| c02_cfg_escena.js | 1438 | 41 | 36 | — | * as THREE ← three |
| c03_audio_voz.js | 2068 | 6 | 1 | c02(1) · c00(3) | — |
| c04_fisica_ccd.js | 541 | 65 | 45 | c02(2) | * as THREE ← three |
| c05_colisiones_ia_golpeo.js | 1402 | 32 | 11 | c04(37) · c02(2) · c00(1) | * as THREE ← three |
| c06_logros_stats_ia_rival.js | 1809 | 37 | 4 | c02(4) · c05(2) · c04(3) | * as THREE ← three |
| c07_escena_sala.js | 1449 | 15 | 12 | c02(3) · c04(1) | * as THREE ← three |
| c08_hall_hud.js | 2925 | 43 | 16 | c00(2) · c02(2) | * as THREE ← three |
| c09_red_netlink.js | 2683 | 1 | 1 | c02(2) · c00(1) · c09(1) · c01(3) · c05(1) | * as THREE ← three |
| c09b_red_nucleo.js | 955 | 1 | 1 | — | — |
| c09c_red_social.js | 389 | 1 | 1 | c00(2) | — |
| c10_menu_saque.js | 111 | 42 | 36 | — | * as THREE ← three |
| c11_champloader.js | 1112 | 18 | 14 | c02(1) · c00(3) · c10(15) | * as THREE ← three |
| c12_pingponggame.js | 22149 | 195 | 7 | c03(1) · c06(4) · c00(9) · c02(30) · c04(9) · c09(1) · c09(1) · c07(12) · c08(16) · c01(4) · c11(14) · c09(1) · c05(11) · c10(22) · c13(1) | * as THREE ← three, GLTFLoader ← three/addons/loaders/GLTFLoader.js, RoomEnvironment ← three/addons/environments/RoomEnvironment.js |
| c13_ui_arranque.js | 6842 | 4 | 1 | c00(8) · c12(7) · c01(5) · c09(1) · c09(1) · c04(7) · c05(8) · c02(11) · c10(1) | * as THREE ← three, GLTFLoader ← three/addons/loaders/GLTFLoader.js |

## Detalle de imports entre ficheros


### c00_pre_three.js — exporta 13, importa 0
- **exporta:** PP_ICONS, T, TLang, VOICE_B64, VOICE_B64_EN, WORLDRANK, __PP_TELE, __ppLang, applyLangDOM, ppDebugMode, ppPlayerName, setLang, wrlBadgeImg
- globales del navegador que usa (top): c×467, y×168, x×168, st×82, Math×61, window×46, i×28, e×19

### c01_modelos_3d.js — exporta 8, importa 0
- **exporta:** PALA_BLADE_Y, PALA_GRIP_Y, PALA_SCALE, fixInvertedMeshes, loadGunModel, loadPaddleModel, makeGunVisual, makePaddleVisual
- globales del navegador que usa (top): THREE×34, m×27, i×20, o×14, idx×11, model×10, resolve×8, g×8

### c02_cfg_escena.js — exporta 36, importa 0
- **exporta:** AI_PRESETS, ARCANO_CFG, BOLA_ASPECTOS, CARRERA_DIVISIONES, COLORS, CONFIG_AUDIO, CONFIG_DIFICULTAD, CONFIG_LOGROS, CONFIG_MEDALLAS, CONFIG_MENU, CONFIG_MENUS, CONFIG_PIELES, CONFIG_RALLY, CONFIG_SECCIONES, CONFIG_TORNEOS, DIMS, ELO_CPU, HALL_VARIANTES, ICONOS_MENUS, MESA_ALTOS, MESA_ALTO_MAX, MESA_ALTO_MIN, MESA_ASPECTOS, MESA_NET_H, MOUNT_QUAT_RIGHT, OPPONENT_STYLES, ROOM_THEMES, SERVE_ASSIST_TIERS, SERVE_TUNE, bolaAspectoPorId, estiloAplicar, estiloDePersonalidad, hallVariantePorId, mountQuatFor, rivalPorElo, scalePreset
- globales del navegador que usa (top): E×27, cfg×21, Math×21, THREE×16, M×10, kk×9, m×9, cl×6

### c03_audio_voz.js — exporta 1, importa 4
- **exporta:** GameAudio
- de `c02_cfg_escena.js`: CONFIG_AUDIO
- de `c00_pre_three.js`: TLang, VOICE_B64, VOICE_B64_EN
- globales del navegador que usa (top): Math×100, t×91, g×86, src×55, ctx×53, now×53, window×36, i×35

### c04_fisica_ccd.js — exporta 45, importa 2
- **exporta:** BOTE_TUNE, CCD_TUNE, MAX_SUBSTEP_DT, SOLVER_TUNE, applyAerodynamics, applyBounceSpin, bladeNormalLocal, bounceOnTable, ccdC0, ccdC1, ccdNL, ccdNrmA, ccdNrmB, ccdP, ccdPosA, ccdPosB, ccdRgtA, ccdRgtB, ccdUpA, ccdUpB, createPaddleSim, crossPoint, integraVuelo, ipNormal, ipRight, ipUp, padPos, paddlePerkFor, relVel, sdfBlade, setPaddleBasis, sweepBallVsBlade, sweepBallVsCapsuleY, tmpD, tmpM, tmpMountQ, tmpN, tmpPrev, tmpR, tmpS, tmpSurf, tmpT, tmpTarget, tmpV, updatePaddleSim
- de `c02_cfg_escena.js`: DIMS, SERVE_TUNE
- globales del navegador que usa (top): THREE×53, ps×51, Math×23, a×21, spin×18, o×18, vel×17, dt×16

### c05_colisiones_ia_golpeo.js — exporta 11, importa 40
- **exporta:** __ppServeTelemetry, applyServeProgressiveAssist, collidePaddle, collidePaddleSweep, computeShotVelocity, computeShotVelocityReal, findServeVelocity, predictStrike, simulateServePath, stepPhysics, testPaddleContact
- de `c04_fisica_ccd.js`: BOTE_TUNE, CCD_TUNE, MAX_SUBSTEP_DT, SOLVER_TUNE, applyBounceSpin, bladeNormalLocal, bounceOnTable, ccdC0, ccdC1, ccdNL, ccdNrmA, ccdNrmB, ccdP, ccdPosA, ccdPosB, ccdRgtA, ccdRgtB, ccdUpA, ccdUpB, crossPoint, integraVuelo, ipNormal, ipRight, ipUp, padPos, paddlePerkFor, relVel, sweepBallVsBlade, sweepBallVsCapsuleY, tmpD, tmpM, tmpN, tmpPrev, tmpR, tmpS, tmpSurf, tmpT
- de `c02_cfg_escena.js`: DIMS, SERVE_TUNE
- de `c00_pre_three.js`: T
- globales del navegador que usa (top): ball×161, pos×113, vel×79, Math×77, pad×66, out×36, rp×32, THREE×29

### c06_logros_stats_ia_rival.js — exporta 4, importa 9
- **exporta:** ACHIEVEMENTS, GameStats, OpponentAI, Rules
- de `c02_cfg_escena.js`: CONFIG_DIFICULTAD, CONFIG_LOGROS, CONFIG_TORNEOS, DIMS
- de `c05_colisiones_ia_golpeo.js`: computeShotVelocityReal, predictStrike
- de `c04_fisica_ccd.js`: tmpD, tmpT, tmpTarget
- ⚠ **reasigna (sin import — ámbito compartido en el ensamblado):** T (declarado en c00_pre_three.js)
- globales del navegador que usa (top): ch×153, Math×115, THREE×57, ball×52, vivo×38, dt×20, v×20, sign×20

### c07_escena_sala.js — exporta 12, importa 4
- **exporta:** applyBallSkin, createBall, createBlobShadow, createChampDecor, createChispas, createCristalesCripto, createEstelaPoder, createNubePrismas, createOndaEsfera, createRoom, createTable, relayoutMesa
- de `c02_cfg_escena.js`: COLORS, DIMS, bolaAspectoPorId
- de `c04_fisica_ccd.js`: tmpV
- globales del navegador que usa (top): Math×148, THREE×140, i×129, c×123, s×97, g×59, L×59, p×57

### c08_hall_hud.js — exporta 16, importa 4
- **exporta:** HALL, applyHallVariant, createBounceMarkers, createCalibPanel, createChampRoom, createConfetti, createFanfareBanner, createHall, createScoreboard, drawArcanoPanel, drawArcanoSalir, drawHallGloria, drawHallSign, montarArcano, updateArcanoFx, updateHallFx
- de `c00_pre_three.js`: T, TLang
- de `c02_cfg_escena.js`: ARCANO_CFG, DIMS
- globales del navegador que usa (top): x×511, THREE×206, Math×161, W×131, ctx×119, i×111, H×94, d×77

### c09_red_netlink.js — exporta 1, importa 8
- **exporta:** NetLink
- de `c02_cfg_escena.js`: DIMS, mountQuatFor
- de `c00_pre_three.js`: T
- de `c09b_red_nucleo.js`: PPNET
- de `c01_modelos_3d.js`: PALA_BLADE_Y, PALA_GRIP_Y, PALA_SCALE
- de `c05_colisiones_ia_golpeo.js`: stepPhysics
- globales del navegador que usa (top): g×142, r×116, m×82, d×58, e×48, performance×45, ev×42, Math×35

### c09b_red_nucleo.js — exporta 1, importa 0
- **exporta:** PPNET
- globales del navegador que usa (top): r×60, i×50, out×45, Math×42, VP×35, a×32, p×31, w×30

### c09c_red_social.js — exporta 1, importa 2
- **exporta:** RedSocial
- de `c00_pre_three.js`: T, ppPlayerName
- globales del navegador que usa (top): r×20, net×13, e×10, g×10, base×8, window×7, j×7, nuevo×6

### c10_menu_saque.js — exporta 36, importa 0
- **exporta:** AIM_BLADE, AIM_BX, AIM_BY, AIM_BZ, AIM_FACE, AIM_FWD, AIM_RIGHT, AIM_XA, AIM_Z, AI_TOSS_T, BALL_HAND_LIFT, CHAMPS_STATE, MENU_LOGO_SRC, SWING_POSE, _dbQ1, _dbQ2, _dbV1, _rbQ, _rbV1, _rbV2, _rbV3, _rbV4, _rpSize, _rpV1, aimM, aimPitchQ, aimRollQ, closAx, closQ, closX, poseQ, rpDir, rpOrigin, rpQuat, rpRaycaster, swingV
- globales del navegador que usa (top): THREE×37

### c11_champloader.js — exporta 14, importa 19
- **exporta:** ChampLoader, NORMAS_SKIN, muDir, muGrip, muHead, muQ, muRaycaster, netTmpP, netTmpQ, netTmpV, pcA, pcC, pcN, pcT
- de `c02_cfg_escena.js`: CONFIG_TORNEOS
- de `c00_pre_three.js`: T, __ppLang, ppDebugMode
- de `c10_menu_saque.js`: CHAMPS_STATE, _dbQ1, _dbQ2, _dbV1, _rbQ, _rbV1, _rbV2, _rbV3, _rbV4, _rpSize, _rpV1, rpDir, rpOrigin, rpQuat, rpRaycaster
- globales del navegador que usa (top): m×99, e×72, id×58, g×38, THREE×31, console×23, man×22, raw×18

### c12_pingponggame.js — exporta 7, importa 136
- **exporta:** PingPongGame, arBtn, overlay, playEn, playEs, statusEl, vrbtn
- de `c03_audio_voz.js`: GameAudio
- de `c06_logros_stats_ia_rival.js`: ACHIEVEMENTS, GameStats, OpponentAI, Rules
- de `c00_pre_three.js`: PP_ICONS, T, TLang, WORLDRANK, __PP_TELE, __ppLang, ppPlayerName, setLang, wrlBadgeImg
- de `c02_cfg_escena.js`: AI_PRESETS, ARCANO_CFG, BOLA_ASPECTOS, CARRERA_DIVISIONES, CONFIG_DIFICULTAD, CONFIG_MENU, CONFIG_MENUS, CONFIG_SECCIONES, CONFIG_TORNEOS, DIMS, ELO_CPU, HALL_VARIANTES, ICONOS_MENUS, MESA_ALTOS, MESA_ALTO_MAX, MESA_ALTO_MIN, MESA_ASPECTOS, MESA_NET_H, MOUNT_QUAT_RIGHT, OPPONENT_STYLES, ROOM_THEMES, SERVE_ASSIST_TIERS, SERVE_TUNE, bolaAspectoPorId, estiloAplicar, estiloDePersonalidad, hallVariantePorId, mountQuatFor, rivalPorElo, scalePreset
- de `c04_fisica_ccd.js`: CCD_TUNE, applyAerodynamics, createPaddleSim, sweepBallVsBlade, sweepBallVsCapsuleY, tmpMountQ, tmpTarget, tmpV, updatePaddleSim
- de `c09_red_netlink.js`: NetLink
- de `c09b_red_nucleo.js`: PPNET
- de `c07_escena_sala.js`: applyBallSkin, createBall, createBlobShadow, createChampDecor, createChispas, createCristalesCripto, createEstelaPoder, createNubePrismas, createOndaEsfera, createRoom, createTable, relayoutMesa
- de `c08_hall_hud.js`: HALL, applyHallVariant, createBounceMarkers, createCalibPanel, createChampRoom, createConfetti, createFanfareBanner, createHall, createScoreboard, drawArcanoPanel, drawArcanoSalir, drawHallGloria, drawHallSign, montarArcano, updateArcanoFx, updateHallFx
- de `c01_modelos_3d.js`: PALA_BLADE_Y, PALA_GRIP_Y, PALA_SCALE, makePaddleVisual
- de `c11_champloader.js`: ChampLoader, NORMAS_SKIN, muDir, muGrip, muHead, muQ, muRaycaster, netTmpP, netTmpQ, netTmpV, pcA, pcC, pcN, pcT
- de `c09c_red_social.js`: RedSocial
- de `c05_colisiones_ia_golpeo.js`: __ppServeTelemetry, applyServeProgressiveAssist, collidePaddle, collidePaddleSweep, computeShotVelocity, computeShotVelocityReal, findServeVelocity, predictStrike, simulateServePath, stepPhysics, testPaddleContact
- de `c10_menu_saque.js`: AIM_BLADE, AIM_BX, AIM_BY, AIM_BZ, AIM_FACE, AIM_FWD, AIM_RIGHT, AIM_XA, AIM_Z, AI_TOSS_T, BALL_HAND_LIFT, CHAMPS_STATE, MENU_LOGO_SRC, SWING_POSE, aimM, aimPitchQ, aimRollQ, closAx, closQ, closX, poseQ, swingV
- de `c13_ui_arranque.js`: wrapText
- globales del navegador que usa (top): c×1463, Math×660, THREE×394, e×290, i×262, m×255, y×233, S×218

### c13_ui_arranque.js — exporta 1, importa 49
- **exporta:** wrapText
- de `c00_pre_three.js`: PP_ICONS, T, TLang, WORLDRANK, __ppLang, applyLangDOM, ppPlayerName, setLang
- de `c12_pingponggame.js`: PingPongGame, arBtn, overlay, playEn, playEs, statusEl, vrbtn
- de `c01_modelos_3d.js`: fixInvertedMeshes, loadGunModel, loadPaddleModel, makeGunVisual, makePaddleVisual
- de `c09_red_netlink.js`: NetLink
- de `c09b_red_nucleo.js`: PPNET
- de `c04_fisica_ccd.js`: CCD_TUNE, bladeNormalLocal, createPaddleSim, sdfBlade, setPaddleBasis, sweepBallVsBlade, tmpPrev
- de `c05_colisiones_ia_golpeo.js`: __ppServeTelemetry, applyServeProgressiveAssist, collidePaddleSweep, computeShotVelocityReal, findServeVelocity, simulateServePath, stepPhysics, testPaddleContact
- de `c02_cfg_escena.js`: AI_PRESETS, CONFIG_LOGROS, CONFIG_MEDALLAS, CONFIG_MENUS, CONFIG_PIELES, CONFIG_RALLY, CONFIG_TORNEOS, DIMS, SERVE_ASSIST_TIERS, SERVE_TUNE, scalePreset
- de `c10_menu_saque.js`: BALL_HAND_LIFT
- globales del navegador que usa (top): c×652, G×374, g×273, st×258, Math×235, S×190, b×173, THREE×171

## Candidatos a núcleo SDK (Fase 3)

Símbolos más importados entre subsistemas — la columna vertebral del núcleo compartido que la Fase 3 extraerá para los 5 campeonatos:

- `DIMS` — lo importan 8 ficheros
- `T` — lo importan 7 ficheros
- `TLang` — lo importan 4 ficheros
- `SERVE_TUNE` — lo importan 4 ficheros
- `CONFIG_TORNEOS` — lo importan 4 ficheros
- `CCD_TUNE` — lo importan 3 ficheros
- `sweepBallVsBlade` — lo importan 3 ficheros
- `computeShotVelocityReal` — lo importan 3 ficheros
- `PPNET` — lo importan 3 ficheros
- `stepPhysics` — lo importan 3 ficheros
- `ppPlayerName` — lo importan 3 ficheros
- `__ppLang` — lo importan 3 ficheros
- `tmpPrev` — lo importan 2 ficheros
- `sweepBallVsCapsuleY` — lo importan 2 ficheros
- `bladeNormalLocal` — lo importan 2 ficheros
- `tmpD` — lo importan 2 ficheros
- `tmpT` — lo importan 2 ficheros
- `CONFIG_LOGROS` — lo importan 2 ficheros
- `CONFIG_DIFICULTAD` — lo importan 2 ficheros
- `predictStrike` — lo importan 2 ficheros

Sin declaraciones duplicadas entre ficheros ✓

## Ciclos de importación (informativo — el ensamblado conserva el orden semántico)

- c12_pingponggame.js → c13_ui_arranque.js → c12_pingponggame.js

## Limitaciones conocidas

- Las referencias sombreadas por bindings locales anidados pueden generar un import sobrante (legal e inofensivo en ESM; el build de inserción lo elimina).
- Un símbolo REASIGNADO desde otro fichero no se importa (los imports de ESM no son reasignables); se lista como «reasigna» y sigue viviendo en el ámbito compartido del ensamblado.
- La ejecución REAL del juego sigue siendo el ensamblado en un solo ámbito (build de inserción, orden semántico preservado). Los módulos son la fuente con dependencias explícitas.
