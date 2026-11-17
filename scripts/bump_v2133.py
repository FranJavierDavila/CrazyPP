#!/usr/bin/env python3
"""V2.133 · bump de VERSION en game.html + entrada de changelog."""
import io

F = "/home/z/my-project/public/game.html"
src = io.open(F, encoding="utf-8").read()

NUEVO = (
    "v2.133 · LA LOCURA: la BOLA DOBLE del CLOWN ya SE VE — el dueño en el casco: "
    "«el poder que saca dos bolas no funciona». Causa raíz reproducida headless: la MALLA del clon "
    "se creaba SÓLO dentro del primer build() del ARKANOID (prueba de las etapas 2/4) y el split "
    "sólo existe en la bolsa del Nv.3 (etapa 5, DUELO JEFE): llegando al duelo final con sesión "
    "fresca (etapa guardada, recarga de página, salto de depuración o rejugada por el mapa) el "
    "arkanoid nunca se había construido → el clon corría físico INVISIBLE (la «malla perezosa» de "
    "v2.120 dependía de _makeCloneMesh, definido también sólo en build) — el cartel prometía "
    "«¡LA BOLA SE DIVIDE EN DOS!», la bola oficial se ponía blanca y la segunda bola JAMÁS "
    "aparecía · FIX: cloneMesh + _makeCloneMesh al CONSTRUCTOR del arkanoid (UNA vez por sesión, "
    "regla Quest de pools intacta) y el lazy de _startSplit queda como cinturón · además el split "
    "ya no se desperdicia en punto muerto: si el aviso termina sin rallye (saque/reposo) se "
    "RE-ARMA 1,2 s y entra en el PRÓXIMO rallye (antes nacía y updateSplit lo mataba en el primer "
    "frame: cartel sin efecto) · módulo de La Locura v19 (manifest v19) · QA por ruta natural: "
    "bolsa por nivel (split sólo en Nv.3), clon VISIBLE con malla y física real, salvación del "
    "punto con el clon, re-arma en saque, smoke 0 pageerrors · antes v2.132 · "
)

OLD = "const VERSION = '2.132.0';   // v2.132 · ESTACIÓN ORBITAL"
NEW = "const VERSION = '2.133.0';   // " + NUEVO + "ESTACIÓN ORBITAL"
n = src.count(OLD)
assert n == 1, f"esperaba 1 aparición del ancla VERSION, hay {n}"
src = src.replace(OLD, NEW)
io.open(F, "w", encoding="utf-8").write(src)
print("VERSION -> 2.133.0 OK")
