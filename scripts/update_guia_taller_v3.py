#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""update_guia_taller_v3.py — la guía de campeonatos describe el flujo REAL del
Taller V3.0.3 (paquete montable con manifest + módulo + assets), no el fantasma
de Netlify. También alinea versiones: el juego sigue V3.0.2, el Taller pasa a
V3.0.3 y el callout del PRO TRAINING queda intacto."""
import pathlib, re, sys

GUIA = pathlib.Path("/home/z/my-project/public/descargas/guia-campeonatos-crazy-pingpong.html")
s = GUIA.read_text(encoding="utf-8")

def rep(old, new, n=1):
    global s
    c = s.count(old)
    assert c == n, f"ANCLA x{c} (esperaba {n}): {old[:80]!r}"
    s = s.replace(old, new)

# 1 · campeonatos intocables: los reales
rep("Partido, Entrenamiento y Supervivencia son intocables: crear campeonatos nuevos <strong>nunca</strong> modifica sus cajas. Si para crear uno nuevo quieres apoyarte en uno de ellos (por ejemplo, para usar a su rival o su sala como punto de partida), el sistema hace <strong>una copia limpia</strong> y trabaja sobre la copia. El original queda tal cual, para siempre.",
    "La Locura, Magia, el Salvaje Oeste y Estación Orbital son intocables: crear campeonatos nuevos <strong>nunca</strong> toca sus carpetas. Sus etiquetas están reservadas en el Taller y sus carpetas quedan fuera de alcance. Si quieres apoyarte en uno de ellos como inspiración, las plantillas del Taller te dan un punto de partida limpio y equivalente.")

# 2 · estado publicado junto a los reales
rep("Aparece en el menú del juego final para todos los jugadores, junto a Partido, Entrenamiento y Supervivencia.",
    "Aparece en el menú del juego final para todos los jugadores, junto a La Locura, Magia, el Salvaje Oeste y Estación Orbital.")

# 3 · Laboratorio: el paquete REAL
rep("Probar un campeonato <strong>nunca</strong> se hace sobre el juego que ya usan los jugadores. Se hace en una <strong>copia paralela</strong>: una versión de pruebas que contiene el juego de siempre más tu campeonato nuevo marcado como «en pruebas». Esta copia vive en una <strong>dirección web privada</strong>, distinta de la dirección definitiva. Piensa en un restaurante: la puerta principal es la dirección definitiva, por donde entra todo el mundo; la puerta de servicio es la dirección de pruebas, por donde solo entra quien está trabajando.",
    "Probar un campeonato <strong>nunca</strong> se hace sobre el juego que ya usan los jugadores. El Taller genera el <strong>paquete de pruebas</strong>: un .zip con la carpeta real del campeonato (manifest oficial, módulo con duelos y pruebas, arte y música, y el índice championships.json) marcado como <strong>«listo»</strong> — en ese estado el juego lo lanza bajo demanda pero <strong>no aparece en el menú público</strong>. Piensa en un restaurante: la puerta principal es el juego publicado; la puerta de servicio es abrir el campeonato con su dirección secreta.")

rep("Cuando el campeonato está «Listo para probar», se pide al sistema el <strong>paquete de pruebas</strong>: un único archivo que contiene el juego completo con tu campeonato nuevo dentro, pero solo visible en ese paquete. Se puede generar tantas veces como se necesite, cada vez con los últimos cambios.",
    "Cuando el campeonato está «Listo para probar», se pide al sistema el <strong>paquete de pruebas</strong>: un único archivo .zip con la <strong>carpeta championships/tu-campeonato</strong> completa (manifest, módulo, assets e índice) más un LEEME con los pasos exactos. Se puede generar tantas veces como se necesite, cada vez con los últimos cambios.")

rep("Desde el navegador de un ordenador, entra en <strong>app.netlify.com/drop</strong> y <strong>arrastra el archivo</strong> a la página. En unos segundos te entrega una dirección web (una URL) que empieza por HTTPS. Esa es tu <strong>dirección de pruebas</strong>: privada, solo para quien tú se la des.",
    "Descomprime el paquete y <strong>copia la carpeta championships/</strong> dentro de la carpeta del juego (al lado del index.html del juego): se fusiona con la que ya hay y tu campeonato se <strong>añade</strong> — los demás no se tocan. Sube el juego a tu alojamiento de pruebas (por ejemplo <strong>app.netlify.com/drop</strong>, que te da una dirección privada en segundos) o ábrelo en local.")

rep("Ponte las gafas Meta Quest 3, abre el <strong>Meta Quest Browser</strong> (el navegador de las gafas), escribe la dirección de pruebas y pulsa el gran botón <strong>ENTRAR EN VR</strong>. Ya estás dentro de la copia de pruebas: verás el menú de siempre… y el campeonato nuevo.",
    "Ponte las gafas Meta Quest 3, abre el <strong>Meta Quest Browser</strong> (el navegador de las gafas) y escribe la dirección del juego terminada en <strong>?champ=etiqueta</strong> (ejemplo: <strong>https://tu-direccion/?champ=valle_neon</strong>) y pulsa el gran botón <strong>ENTRAR EN VR</strong>. El campeonato arranca directamente, incluso estando «en pruebas»: es la puerta de servicio.")

rep("""      <li>El campeonato nuevo <strong>aparece en el menú</strong> con su nombre y su sala.</li>
      <li>Los tres campeonatos de siempre&nbsp;— <strong>Partido, Entrenamiento y Supervivencia</strong>&nbsp;— funcionan exactamente igual que antes.</li>""",
    """      <li>El campeonato nuevo <strong>arranca</strong> (con ?champ=etiqueta, o en el menú CAMPEONATOS si está publicado).</li>
      <li>Los cuatro campeonatos del juego&nbsp;— <strong>La Locura, Magia, el Salvaje Oeste y Estación Orbital</strong>&nbsp;— funcionan exactamente igual que antes.</li>""")

# 4 · Estadio: publicar = paquete definitivo + montar
rep("El juego final es la <strong>versión publicada</strong>: la que reúne todos los campeonatos aprobados y vive en <strong>una única dirección web oficial</strong>. Publicar la versión definitiva se hace igual que crear el enlace de pruebas&nbsp;— arrastrando el paquete final a la misma página&nbsp;— solo que esta vez el resultado es la dirección que usarán <strong>todos los jugadores</strong>. Primero, la publicación; después, la partida.",
    "El juego final es la <strong>versión publicada</strong>: la que reúne todos los campeonatos aprobados y vive en <strong>una única dirección web oficial</strong>. Publicar se hace con el <strong>PAQUETE DEFINITIVO</strong> del Taller: el mismo paquete pero con el campeonato marcado <strong>«publicado»</strong> — en cuanto su carpeta se copia al juego, aparece en el menú CAMPEONATOS para todos. Primero, la publicación; después, la partida.")

rep("<div class=\"pill-note\"><b>A&nbsp;· Publicar la versión definitiva (3 pasos):</b> ① generar el paquete definitivo con todos los campeonatos publicados; ② arrastrarlo a <b>app.netlify.com/drop</b> y copiar la dirección que entrega&nbsp;— esa es «la dirección del estadio»; ③ compartirla: es la que usarán todos los jugadores desde sus gafas.</div>",
    "<div class=\"pill-note\"><b>A&nbsp;· Publicar la versión definitiva (3 pasos):</b> ① generar el <b>PAQUETE DEFINITIVO</b> en el Taller (sale con el campeonato marcado «publicado»); ② copiar su carpeta <b>championships/</b> al juego — se fusiona — y subir el juego a tu alojamiento (<b>app.netlify.com/drop</b> u otro); ③ la dirección del juego no cambia: al abrirla, el campeonato aparece en el menú CAMPEONATOS para todos los jugadores.</div>")

# 5 · versiones: juego V3.0.2 · Taller V3.0.3 (7 menciones del juego siguen siendo ciertas)
s = s.replace("V3.0.1", "V3.0.2")   # la mención suelta del fix del casco
rep("</title>", "</title>", 1)      # no-op de seguridad del ancla

GUIA.write_text(s, encoding="utf-8")
restos = s.count("Partido, Entrenamiento")
print(f"guía actualizada ({len(s)} B) · restos 'Partido, Entrenamiento': {restos} · netlify: {s.count('netlify')} (solo como ejemplo de alojamiento)")
