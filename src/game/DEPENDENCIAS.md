# CRAZY PING PONG · GRAFO DE DEPENDENCIAS DEL NÚCLEO (fase 2)

Generado por `scripts/mod_fase2_analizar.mjs` (acorn, scopes AST). Golden: `# SHA256 del gam…`

## Qué declara, exporta e importa cada subsistema

| Fichero | Líneas | Declara | Exporta | Importa desde | Biblioteca |
|---|---|---|---|---|---|
| c00_pre_three.js | 2589 | 15 | 13 | — | — |
| c01_modelos_3d.js | 306 | 16 | 8 | — | — |
| c02_cfg_escena.js | 324 | 13 | 9 | — | * as THREE ← three |
| c03_audio_voz.js | 1774 | 6 | 1 | c00(3) | — |
| c04_fisica_ccd.js | 351 | 52 | 42 | c02(2) | * as THREE ← three |
| c05_colisiones_ia_golpeo.js | 1018 | 21 | 11 | c04(35) · c02(2) · c00(1) | * as THREE ← three |
| c06_logros_stats_ia_rival.js | 841 | 11 | 4 | c02(1) · c05(2) · c04(3) | * as THREE ← three |
| c07_escena_sala.js | 496 | 5 | 5 | c02(2) · c04(1) | * as THREE ← three |
| c08_hall_hud.js | 1144 | 24 | 10 | c02(1) · c00(2) | * as THREE ← three |
| c09_red_netlink.js | 1676 | 1 | 1 | c02(2) · c00(1) · c01(3) · c09(1) · c05(1) | * as THREE ← three |
| c09b_red_nucleo.js | 764 | 1 | 1 | — | — |
| c10_menu_saque.js | 105 | 39 | 33 | — | * as THREE ← three |
| c11_champloader.js | 940 | 17 | 15 | c00(3) · c10(15) | * as THREE ← three |
| c12_pingponggame.js | 9465 | 87 | 7 | c03(1) · c06(4) · c02(8) · c04(9) · c09(1) · c07(5) · c08(10) · c01(4) · c11(15) · c00(9) · c09(1) · c05(11) · c10(19) · c13(1) | * as THREE ← three, RoomEnvironment ← three/addons/environments/RoomEnvironment.js |
| c13_ui_arranque.js | 5732 | 4 | 1 | c00(8) · c12(7) · c01(5) · c09(1) · c09(1) · c04(7) · c05(8) · c02(5) · c10(1) | * as THREE ← three, GLTFLoader ← three/addons/loaders/GLTFLoader.js |

## Detalle de imports entre ficheros


### c00_pre_three.js — exporta 13, importa 0
- **exporta:** PP_ICONS, T, TLang, VOICE_B64, VOICE_B64_EN, WORLDRANK, __PP_TELE, __ppLang, applyLangDOM, ppDebugMode, ppPlayerName, setLang, wrlBadgeImg
- globales del navegador que usa (top): c×384, y×143, x×143, st×63, Math×57, window×35, i×28, e×17

### c01_modelos_3d.js — exporta 8, importa 0
- **exporta:** PALA_BLADE_Y, PALA_GRIP_Y, PALA_SCALE, fixInvertedMeshes, loadGunModel, loadPaddleModel, makeGunVisual, makePaddleVisual
- globales del navegador que usa (top): THREE×34, m×27, i×20, o×14, idx×11, model×10, resolve×8, g×8

### c02_cfg_escena.js — exporta 9, importa 0
- **exporta:** AI_PRESETS, COLORS, DIMS, MOUNT_QUAT_RIGHT, ROOM_THEMES, SERVE_ASSIST_TIERS, SERVE_TUNE, mountQuatFor, scalePreset
- globales del navegador que usa (top): Math×14, THREE×13, cfg×10, kk×9, k×1, roll×1, rollQ×1, pitch×1

### c03_audio_voz.js — exporta 1, importa 3
- **exporta:** GameAudio
- de `c00_pre_three.js`: TLang, VOICE_B64, VOICE_B64_EN
- globales del navegador que usa (top): Math×79, g×77, t×76, now×53, ctx×50, src×48, window×33, i×33

### c04_fisica_ccd.js — exporta 42, importa 2
- **exporta:** CCD_TUNE, MAX_SUBSTEP_DT, applyAerodynamics, applyBounceSpin, bladeNormalLocal, bounceOnTable, ccdC0, ccdC1, ccdNL, ccdNrmA, ccdNrmB, ccdP, ccdPosA, ccdPosB, ccdRgtA, ccdRgtB, ccdUpA, ccdUpB, createPaddleSim, crossPoint, ipNormal, ipRight, ipUp, padPos, paddlePerkFor, relVel, sdfBlade, setPaddleBasis, sweepBallVsBlade, sweepBallVsCapsuleY, tmpD, tmpM, tmpMountQ, tmpN, tmpPrev, tmpR, tmpS, tmpSurf, tmpT, tmpTarget, tmpV, updatePaddleSim
- de `c02_cfg_escena.js`: DIMS, SERVE_TUNE
- globales del navegador que usa (top): THREE×46, ps×34, Math×19, t×12, vel×11, spin×10, p×9, y×8

### c05_colisiones_ia_golpeo.js — exporta 11, importa 38
- **exporta:** __ppServeTelemetry, applyServeProgressiveAssist, collidePaddle, collidePaddleSweep, computeShotVelocity, computeShotVelocityReal, findServeVelocity, predictStrike, simulateServePath, stepPhysics, testPaddleContact
- de `c04_fisica_ccd.js`: CCD_TUNE, MAX_SUBSTEP_DT, applyAerodynamics, applyBounceSpin, bladeNormalLocal, bounceOnTable, ccdC0, ccdC1, ccdNL, ccdNrmA, ccdNrmB, ccdP, ccdPosA, ccdPosB, ccdRgtA, ccdRgtB, ccdUpA, ccdUpB, crossPoint, ipNormal, ipRight, ipUp, padPos, paddlePerkFor, relVel, sweepBallVsBlade, sweepBallVsCapsuleY, tmpD, tmpM, tmpN, tmpPrev, tmpR, tmpS, tmpSurf, tmpT
- de `c02_cfg_escena.js`: DIMS, SERVE_TUNE
- de `c00_pre_three.js`: T
- globales del navegador que usa (top): pos×105, ball×93, vel×69, Math×59, pad×54, out×36, C×27, from×26

### c06_logros_stats_ia_rival.js — exporta 4, importa 6
- **exporta:** ACHIEVEMENTS, GameStats, OpponentAI, Rules
- de `c02_cfg_escena.js`: DIMS
- de `c05_colisiones_ia_golpeo.js`: computeShotVelocityReal, predictStrike
- de `c04_fisica_ccd.js`: tmpD, tmpT, tmpTarget
- ⚠ **reasigna (sin import — ámbito compartido en el ensamblado):** T (declarado en c00_pre_three.js)
- globales del navegador que usa (top): Math×53, ball×48, intents×19, sign×17, THREE×17, winner×13, ctx×13, cause×12

### c07_escena_sala.js — exporta 5, importa 3
- **exporta:** createBall, createBlobShadow, createChampDecor, createRoom, createTable
- de `c02_cfg_escena.js`: COLORS, DIMS
- de `c04_fisica_ccd.js`: tmpV
- globales del navegador que usa (top): THREE×83, p×49, g×30, Math×26, nctx×12, topY×11, game×11, pc×10

### c08_hall_hud.js — exporta 10, importa 3
- **exporta:** HALL, createBounceMarkers, createCalibPanel, createChampRoom, createConfetti, createFanfareBanner, createHall, createReplayBanner, createScoreboard, updateHallFx
- de `c02_cfg_escena.js`: DIMS
- de `c00_pre_three.js`: T, TLang
- globales del navegador que usa (top): x×188, ctx×124, THREE×65, W×63, i×53, H×51, d×46, Math×37

### c09_red_netlink.js — exporta 1, importa 8
- **exporta:** NetLink
- de `c02_cfg_escena.js`: DIMS, mountQuatFor
- de `c00_pre_three.js`: T
- de `c01_modelos_3d.js`: PALA_BLADE_Y, PALA_GRIP_Y, PALA_SCALE
- de `c09b_red_nucleo.js`: PPNET
- de `c05_colisiones_ia_golpeo.js`: stepPhysics
- globales del navegador que usa (top): g×111, r×99, d×47, e×46, performance×37, m×35, out×32, ev×31

### c09b_red_nucleo.js — exporta 1, importa 0
- **exporta:** PPNET
- globales del navegador que usa (top): r×59, i×47, out×42, Math×40, VP×34, a×32, w×29, b×28

### c10_menu_saque.js — exporta 33, importa 0
- **exporta:** AIM_BLADE, AIM_BX, AIM_BY, AIM_BZ, AIM_FACE, AIM_FWD, AIM_RIGHT, AIM_XA, AIM_Z, AI_TOSS_T, BALL_HAND_LIFT, CHAMPS_STATE, MENU_LOGO_SRC, SWING_POSE, _dbQ1, _dbQ2, _dbV1, _rbQ, _rbV1, _rbV2, _rbV3, _rbV4, _rpSize, _rpV1, aimM, aimPitchQ, aimRollQ, poseQ, rpDir, rpOrigin, rpQuat, rpRaycaster, swingV
- globales del navegador que usa (top): THREE×34

### c11_champloader.js — exporta 15, importa 18
- **exporta:** ChampLoader, NORMAS_SKIN, muDir, muGrip, muHead, muQ, muRaycaster, netTmpP, netTmpQ, netTmpQ2, netTmpV, pcA, pcC, pcN, pcT
- de `c00_pre_three.js`: T, __ppLang, ppDebugMode
- de `c10_menu_saque.js`: CHAMPS_STATE, _dbQ1, _dbQ2, _dbV1, _rbQ, _rbV1, _rbV2, _rbV3, _rbV4, _rpSize, _rpV1, rpDir, rpOrigin, rpQuat, rpRaycaster
- globales del navegador que usa (top): m×96, e×68, id×48, g×36, THREE×31, console×22, raw×18, cx×18

### c12_pingponggame.js — exporta 7, importa 98
- **exporta:** PingPongGame, arBtn, overlay, playEn, playEs, statusEl, vrbtn
- de `c03_audio_voz.js`: GameAudio
- de `c06_logros_stats_ia_rival.js`: ACHIEVEMENTS, GameStats, OpponentAI, Rules
- de `c02_cfg_escena.js`: AI_PRESETS, DIMS, MOUNT_QUAT_RIGHT, ROOM_THEMES, SERVE_ASSIST_TIERS, SERVE_TUNE, mountQuatFor, scalePreset
- de `c04_fisica_ccd.js`: CCD_TUNE, applyAerodynamics, createPaddleSim, sweepBallVsBlade, sweepBallVsCapsuleY, tmpMountQ, tmpTarget, tmpV, updatePaddleSim
- de `c09_red_netlink.js`: NetLink
- de `c07_escena_sala.js`: createBall, createBlobShadow, createChampDecor, createRoom, createTable
- de `c08_hall_hud.js`: HALL, createBounceMarkers, createCalibPanel, createChampRoom, createConfetti, createFanfareBanner, createHall, createReplayBanner, createScoreboard, updateHallFx
- de `c01_modelos_3d.js`: PALA_BLADE_Y, PALA_GRIP_Y, PALA_SCALE, makePaddleVisual
- de `c11_champloader.js`: ChampLoader, NORMAS_SKIN, muDir, muGrip, muHead, muQ, muRaycaster, netTmpP, netTmpQ, netTmpQ2, netTmpV, pcA, pcC, pcN, pcT
- de `c00_pre_three.js`: PP_ICONS, T, TLang, WORLDRANK, __PP_TELE, __ppLang, ppPlayerName, setLang, wrlBadgeImg
- de `c09b_red_nucleo.js`: PPNET
- de `c05_colisiones_ia_golpeo.js`: __ppServeTelemetry, applyServeProgressiveAssist, collidePaddle, collidePaddleSweep, computeShotVelocity, computeShotVelocityReal, findServeVelocity, predictStrike, simulateServePath, stepPhysics, testPaddleContact
- de `c10_menu_saque.js`: AIM_BLADE, AIM_BX, AIM_BY, AIM_BZ, AIM_FACE, AIM_FWD, AIM_RIGHT, AIM_XA, AIM_Z, AI_TOSS_T, BALL_HAND_LIFT, CHAMPS_STATE, MENU_LOGO_SRC, SWING_POSE, aimM, aimPitchQ, aimRollQ, poseQ, swingV
- de `c13_ui_arranque.js`: wrapText
- globales del navegador que usa (top): c×825, Math×250, THREE×194, e×194, S×192, c2×144, i×132, y×131

### c13_ui_arranque.js — exporta 1, importa 43
- **exporta:** wrapText
- de `c00_pre_three.js`: PP_ICONS, T, TLang, WORLDRANK, __ppLang, applyLangDOM, ppPlayerName, setLang
- de `c12_pingponggame.js`: PingPongGame, arBtn, overlay, playEn, playEs, statusEl, vrbtn
- de `c01_modelos_3d.js`: fixInvertedMeshes, loadGunModel, loadPaddleModel, makeGunVisual, makePaddleVisual
- de `c09_red_netlink.js`: NetLink
- de `c09b_red_nucleo.js`: PPNET
- de `c04_fisica_ccd.js`: CCD_TUNE, bladeNormalLocal, createPaddleSim, sdfBlade, setPaddleBasis, sweepBallVsBlade, tmpPrev
- de `c05_colisiones_ia_golpeo.js`: __ppServeTelemetry, applyServeProgressiveAssist, collidePaddleSweep, computeShotVelocityReal, findServeVelocity, simulateServePath, stepPhysics, testPaddleContact
- de `c02_cfg_escena.js`: AI_PRESETS, DIMS, SERVE_ASSIST_TIERS, SERVE_TUNE, scalePreset
- de `c10_menu_saque.js`: BALL_HAND_LIFT
- globales del navegador que usa (top): c×589, G×350, g×251, st×229, Math×208, b×166, THREE×160, S×155

## Candidatos a núcleo SDK (Fase 3)

Símbolos más importados entre subsistemas — la columna vertebral del núcleo compartido que la Fase 3 extraerá para los 5 campeonatos:

- `DIMS` — lo importan 8 ficheros
- `T` — lo importan 6 ficheros
- `TLang` — lo importan 4 ficheros
- `SERVE_TUNE` — lo importan 4 ficheros
- `CCD_TUNE` — lo importan 3 ficheros
- `sweepBallVsBlade` — lo importan 3 ficheros
- `computeShotVelocityReal` — lo importan 3 ficheros
- `PPNET` — lo importan 3 ficheros
- `stepPhysics` — lo importan 3 ficheros
- `__ppLang` — lo importan 3 ficheros
- `tmpPrev` — lo importan 2 ficheros
- `sweepBallVsCapsuleY` — lo importan 2 ficheros
- `bladeNormalLocal` — lo importan 2 ficheros
- `tmpT` — lo importan 2 ficheros
- `tmpD` — lo importan 2 ficheros
- `applyAerodynamics` — lo importan 2 ficheros
- `predictStrike` — lo importan 2 ficheros
- `tmpTarget` — lo importan 2 ficheros
- `tmpV` — lo importan 2 ficheros
- `mountQuatFor` — lo importan 2 ficheros

Sin declaraciones duplicadas entre ficheros ✓

## Ciclos de importación (informativo — el ensamblado conserva el orden semántico)

- c12_pingponggame.js → c13_ui_arranque.js → c12_pingponggame.js

## Limitaciones conocidas

- Las referencias sombreadas por bindings locales anidados pueden generar un import sobrante (legal e inofensivo en ESM; el build de inserción lo elimina).
- Un símbolo REASIGNADO desde otro fichero no se importa (los imports de ESM no son reasignables); se lista como «reasigna» y sigue viviendo en el ámbito compartido del ensamblado.
- La ejecución REAL del juego sigue siendo el ensamblado en un solo ámbito (build de inserción, orden semántico preservado). Los módulos son la fuente con dependencias explícitas.
