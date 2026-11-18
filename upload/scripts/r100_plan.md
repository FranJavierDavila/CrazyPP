# RONDA 100 → V3.6.92 (cache-bust ?v=v3692) — Task 205

Parches (en orden de aplicación):
1. c02_cfg_escena.js — DIMS reposo pala-bola (r100):
   paddleRestSpeed 0.65 · paddleRestFric 0.38 · paddleRestDrop 0.09 ·
   paddleRestCarry 0.5 · paddleRestMuS 0.35 (comentario del dueño Eleven).
2. c12 · tossFromHand (línea ~5382): usar velInst si mayor que vel (flick fiel).
   FIX "primer saque limitado" (R100-C).
3. c13 · buildApexRing: aro de globos z C()+0.5 → C() (centro de mesa, R100-B).
4. c05 · R100-D contacto de reposo:
   a) collidePaddleSweep tras vRelN (117): rama reposo (who==='player',
      !serveFlight, cara, -vRelN<=paddleRestSpeed) → proyectar, anular normal,
      fricción tangencial + rodadura, registrar __ppRest* en la bola,
      evento 'restTouch' SOLO si contacto nuevo (__ppRestT caducado), return true.
   b) stepPhysics: transporte ANTES del bucle de subpasos (buscar pala por
      p.index === ball.__ppRestIdx; pegar a la cara con pose nueva si la pala
      va despacio <= paddleRestCarry; gravedad tangencial + fricción estática
      (paddleRestMuS); despegue si pala rápida / bola fuera del disco / edad).
   c) NO tocar testPaddleContact (el reposo vive dentro de collidePaddleSweep).
5. c12 · processEvents: rama 'restTouch' → tap suave + háptica (throttle 0.3 s).
6. c13 · R100-A barra interactiva (t2a):
   - let barraH (default 0.17, persistencia pp_train_barra_v1, clamp 0.05-0.40)
   - RIBBON_Y() = DIMS.netTopY + barraH
   - buildRibbon: sprites ↑/↓ (x local 1.05, y = RIBBON_Y±0.09) + rótulo cm
     sobre la SUPERFICIE DE LA MESA (cm = (netTopY+barraH-tableTopY)*100)
   - barraTick(dt): raycast matemático (ray.distanceToPoint < 0.075) de la mano
     libre (G.rays[G.ballHand]); hover → tintar sprite + haz (Line + dot)
   - serveTrigger hook: barraAjustarHover() consume el gatillo → ±0.01,
     persistir, blip, haptic; sino serveTossFromTee(true)
7. c00 · i18n: m_t2a_d genérico ("ajustable con el rayo de la mano libre"),
   claves nuevas barra_lbl ES/EN.

QA: node --check de c00/c02/c05/c12/c13 · empaquetado game.html v3.6.92 ·
golden · gen_release_v3692 · worklog Task 205 · commit+push · deploy ·
verifica_r100_produccion.py · recordar game.html?v=v3692
