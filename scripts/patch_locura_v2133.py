#!/usr/bin/env python3
"""V2.133 · PATCH del módulo de La Locura (split invisible + re-arma).
4 ediciones quirúrgicas con verificación de conteo (1 sustitución cada una)."""
import io, sys

F = "/home/z/my-project/public/championships/locura/index.js"
src = io.open(F, encoding="utf-8").read()

def rep(old, new, tag):
    global src
    n = src.count(old)
    assert n == 1, f"[{tag}] esperaba 1 aparición, hay {n}"
    src = src.replace(old, new)
    print(f"OK  {tag}")

# ---------- 1 · CABECERA: nota v2.133 ----------
H_OLD = "MÓDULO DE CARPETA v2.74\n *  ---------------------------------------------------------------------\n *  v2.127 (módulo v18)"
H_NEW = ("MÓDULO DE CARPETA v2.74\n *  ---------------------------------------------------------------------\n"
 "*  v2.133 (módulo v19) · LA BOLA DOBLE (split) YA SE VE — el dueño en el\n"
 " *  casco: «el poder de Clown que saca dos bolas no funciona». Causa raíz\n"
 " *  reproducida headless: la MALLA del clon se creaba SÓLO dentro del primer\n"
 " *  build() del ARKANOID (la prueba de las etapas 2/4) y el split sólo está\n"
 " *  en la bolsa del Nv. 3 (etapa 5, DUELO JEFE). Llegando a la etapa 5 con\n"
 " *  sesión fresca (etapa guardada, recarga de página, salto de depuración o\n"
 " *  rejugada por el mapa) el arkanoid NUNCA se había construido → el clon\n"
 " *  corría físico INVISIBLE (la «malla perezosa» de v2.120 dependía de\n"
 " *  _makeCloneMesh, definido también sólo en build): el cartel prometía\n"
 " *  «¡la bola se divide en dos!» y la segunda bola JAMÁS aparecía — y la\n"
 " *  bola oficial se ponía blanca y jugaba rara (salvaciones que no se\n"
 " *  entienden sin ver el clon). FIX: (1) cloneMesh + _makeCloneMesh al\n"
 " *  CONSTRUCTOR (una sola vez por sesión, regla Quest: nada se crea por\n"
 " *  partida); (2) el split ya no se desperdicia en punto muerto: si el\n"
 " *  aviso termina sin rallye se RE-ARMA 1,2 s y entra en el PRÓXIMO rallye\n"
 " *  (antes nacía y updateSplit lo mataba en el primer frame: cartel sin\n"
 " *  efecto). Todo lo demás intacto.\n"
 " *  v2.127 (módulo v18)")
rep(H_OLD, H_NEW, "1-cabecera")

# ---------- 2 · CONSTRUCTOR: cloneMesh + _makeCloneMesh ----------
C_OLD = ("    this._extra = (ball) => this._extraCollide(ball);\n"
 "    this._spot = new THREE.Vector3();\n"
 "    this._tmpA = new THREE.Vector3();\n"
 "    this._tmpB = new THREE.Vector3();\n"
 "  }\n")
C_NEW = ("    this._extra = (ball) => this._extraCollide(ball);\n"
 "    this._spot = new THREE.Vector3();\n"
 "    this._tmpA = new THREE.Vector3();\n"
 "    this._tmpB = new THREE.Vector3();\n"
 "    // v2.133 · BOLA CLON del superpoder (CLOWN Nv. 3: bola doble) — la malla\n"
 "    // se crea AQUÍ (constructor: UNA vez por sesión) y NO en build(): el\n"
 "    // split sólo sale en el DUELO JEFE (Nv. 3) y llegando a la etapa 5 con\n"
 "    // sesión fresca el arkanoid nunca llegó a construirse → clon físico e\n"
 "    // INVISIBLE (reporte del dueño: «el poder de dos bolas no funciona»). Regla\n"
 "    // Quest intacta: nada se crea por partida (esto corre una vez, al montar).\n"
 "    const g0 = this.game;\n"
 "    this.cloneMesh = new THREE.Mesh(\n"
 "      g0.ballMesh ? g0.ballMesh.geometry\n"
 "        : new THREE.SphereGeometry(DIMS.ballRadius, 24, 16),\n"
 "      new THREE.MeshStandardMaterial({\n"
 "        color: 0xffffff, roughness: 0.3, emissive: 0xbfd4ff, emissiveIntensity: 0.55,\n"
 "      }));\n"
 "    this.cloneMesh.castShadow = true;\n"
 "    this.cloneMesh.visible = false;\n"
 "    g0.rig.add(this.cloneMesh);\n"
 "    // cinturón y tirantes: _startSplit puede exigir la malla en cualquier\n"
 "    // momento (idempotente) — antes vivía SÓLO en el primer build()\n"
 "    this._makeCloneMesh = () => {\n"
 "      if (this.cloneMesh) return;\n"
 "      const gg = this.game;\n"
 "      this.cloneMesh = new THREE.Mesh(\n"
 "        gg.ballMesh ? gg.ballMesh.geometry\n"
 "          : new THREE.SphereGeometry(DIMS.ballRadius, 24, 16),\n"
 "        new THREE.MeshStandardMaterial({\n"
 "          color: 0xffffff, roughness: 0.3, emissive: 0xbfd4ff,\n"
 "          emissiveIntensity: 0.55,\n"
 "        }));\n"
 "      this.cloneMesh.castShadow = true;\n"
 "      this.cloneMesh.visible = false;\n"
 "      gg.rig.add(this.cloneMesh);\n"
 "    };\n"
 "  }\n")
rep(C_OLD, C_NEW, "2-constructor")

# ---------- 3 · build(): retirar el bloque duplicado ----------
B_OLD = ("      // v2.44 · BOLA CLON del superpoder (CLOWN Nv. 3: bola doble)\n"
 "      this.cloneMesh = new THREE.Mesh(\n"
 "        g.ballMesh ? g.ballMesh.geometry : new THREE.SphereGeometry(DIMS.ballRadius, 24, 16),\n"
 "        new THREE.MeshStandardMaterial({\n"
 "          color: 0xffffff, roughness: 0.3, emissive: 0xbfd4ff, emissiveIntensity: 0.55,\n"
 "        }));\n"
 "      this.cloneMesh.castShadow = true;\n"
 "      this.cloneMesh.visible = false;\n"
 "      g.rig.add(this.cloneMesh);\n"
 "      // v2.120: creación PEREZOSA (replays de depuración sin build) — la\n"
 "      // usa _startSplit si el arkanoid no llegó a construirse.\n"
 "      this._makeCloneMesh = () => {\n"
 "        if (this.cloneMesh) return;\n"
 "        const gg = this.game;\n"
 "        this.cloneMesh = new THREE.Mesh(\n"
 "          gg.ballMesh ? gg.ballMesh.geometry\n"
 "            : new THREE.SphereGeometry(DIMS.ballRadius, 24, 16),\n"
 "          new THREE.MeshStandardMaterial({\n"
 "            color: 0xffffff, roughness: 0.3, emissive: 0xbfd4ff,\n"
 "            emissiveIntensity: 0.55,\n"
 "          }));\n"
 "        this.cloneMesh.castShadow = true;\n"
 "        this.cloneMesh.visible = false;\n"
 "        gg.rig.add(this.cloneMesh);\n"
 "      };\n")
B_NEW = ("      // v2.133: la BOLA CLON (split) vive en el CONSTRUCTOR — aquí ya no se\n"
 "      // crea (llegar al duelo JEFE sin build del arkanoid dejaba el clon\n"
 "      // invisible). _makeCloneMesh sigue disponible como cinturón.\n")
rep(B_OLD, B_NEW, "3-build-fuera")

# ---------- 4 · _launchPending: re-arma del split en punto muerto ----------
L_OLD = ("      if (g.rules.state === 'over' || g.rules.state === 'arkanoid') {\n"
 "        this._powerCd = 3;\n"
 "        this._rallyFired = false;\n"
 "        return;\n"
 "      }\n"
 "    }\n")
L_NEW = ("      if (g.rules.state === 'over' || g.rules.state === 'arkanoid') {\n"
 "        this._powerCd = 3;\n"
 "        this._rallyFired = false;\n"
 "        return;\n"
 "      }\n"
 "      // v2.133 · BOLA DOBLE necesita rallye VIVO: el clon muere en el primer\n"
 "      // frame fuera del rallye (updateSplit lo extingue con estado ≠ rally) →\n"
 "      // lanzarlo en saque/reposo era un cartel que prometía dos bolas y no\n"
 "      // se veía NINGUNA. Se RE-ARMA 1,2 s y entra en el PRÓXIMO rallye (el\n"
 "      // guard de maybeTriggerPower impide anunciar otro poder mientras el\n"
 "      // aviso siga pendiente, así el split está GARANTIZADO). 'over' y\n"
 "      // 'arkanoid' siguen cortando arriba.\n"
 "      if (cfg.kind === 'split') {\n"
 "        this._pendingPower = cfg;\n"
 "        this._pendT = 1.2;\n"
 "        return;\n"
 "      }\n"
 "    }\n")
rep(L_OLD, L_NEW, "4-rearma")

io.open(F, "w", encoding="utf-8").write(src)
print("PATCH OK — módulo v19 escrito")
