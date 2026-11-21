// gen_propuesta_r113.js — documento principal (contenido en español)
const { Document, Packer, Paragraph, TextRun, Header, Footer, PageNumber,
  NumberFormat, AlignmentType, SectionType, TableOfContents, PageBreak,
  buildCoverR1, h1, h2, body, run, tablaTitulo, tabla, P, FONT, fs } =
  require("/home/z/my-project/scripts/gen_propuesta_r113_lib.js");

const SALIDA = "/home/z/my-project/download/Propuesta_limpieza_repositorio_r113.docx";

// ── Portada (R1 + GO-1) ───────────────────────────────────────────
const portada = buildCoverR1({
  title: "Limpieza y organización del repositorio",
  subtitle: "Propuesta por fases para las ramas main y pages — sin romper nada de lo construido",
  englishLabel: "REPOSITORY CLEANUP PROPOSAL R113",
  metaLines: [
    "Proyecto: CRAZY PING PONG — github.com/FranJavierDavila/CrazyPP",
    "Inventario analizado: 2.837 ficheros trackeados · 537,2 MB en main",
    "Fecha: 21 de noviembre de 2026",
    "Estado: PENDIENTE DE APROBACIÓN — no se ha ejecutado ningún cambio",
  ],
  footerLeft: "CRAZY PING PONG", footerRight: "r113 · 2026-11-21",
});

// ── Índice ────────────────────────────────────────────────────────
const indice = [
  new Paragraph({
    alignment: AlignmentType.CENTER, spacing: { before: 480, after: 360 },
    children: [new TextRun({ text: "Índice", bold: true, size: 32, font: FONT, color: P.headInk })],
  }),
  new TableOfContents("Índice", { hyperlink: true, headingStyleRange: "1-2" }),
  new Paragraph({
    spacing: { before: 200 },
    children: [new TextRun({
      text: "Nota: este índice se genera mediante campos de Word. Tras abrir el documento, haga clic derecho sobre el índice y elija «Actualizar campos» para refrescar los números de página.",
      italics: true, size: 18, color: "888888", font: FONT })],
  }),
  // Sin PageBreak final: el cuerpo está en su propia sección (NEXT_PAGE) y un
  // salto extra crearía una página en blanco (postcheck blank-pages).
];

// ── Cuerpo ────────────────────────────────────────────────────────
const c = [];

// 1 · Resumen ejecutivo
c.push(h1("1. Resumen ejecutivo"));
c.push(body("El presente documento responde a la petición del dueño de eliminar copias, carpetas temporales y archivos innecesarios del repositorio GitHub (ramas main y pages), dejando el árbol de ficheros organizado sin romper nada de lo ya construido. Se analizó el árbol trackeado completo de main (2.837 ficheros, 537,2 MB), la rama desplegada pages (507 ficheros), la antigüedad de cada fichero según su último commit y las referencias que el código vivo mantiene hacia cada candidato. El análisis es solo de lectura: ningún fichero se ha movido, modificado o borrado."));
c.push(body([run("El diagnóstico principal es doble. Primero, la rama pages está "), run("ya limpia", true), run(": es un sitio 100 % generado (507 ficheros regenerados en cada release con historia aplastada), no contiene basura histórica y no requiere intervención. Segundo, la rama main concentra el desorden en tres bloques concretos: la raíz del proyecto (imágenes pegadas de chat sin referencia, 21 archivos de medios cuyos bytes ya existen en public/ o en el respaldo del dueño, y 5 paquetes ZIP de eras antiguas), la carpeta tmp_owner_backup/ (104 ficheros, 87,7 MB que duplican material ya presente o guardan originales de fuente) y scripts/ (2.029 ficheros, 187 MB, de los cuales solo unas tres decenas están vivos: arneses de prueba r93-r109, baterías, despliegue y el kit de empaquetado).")]));
c.push(body([run("La propuesta se organiza en seis fases reversibles que liberan entre 17 y 50 MB del árbol visible, reorganizan unos 250 MB en carpetas con nombre claro (fuentes/, scripts/archivo/) y reducen el directorio visible de unos 60 elementos de primer nivel a una estructura legible. "), run("El juego, el relay, el kit de release y todo el material operativo quedan explícitamente blindados", true), run(", y cada fase termina con la batería de verificación de la casa (núcleo 9/9, golden byte-exacto, smoke del juego) antes de pasar a la siguiente. La ejecución solo comienza tras la aprobación del dueño (sección 9).")]));

// 2 · Estado actual
c.push(h1("2. Estado actual del repositorio"));
c.push(body("El repositorio tiene dos ramas. La rama main contiene la aplicación Next.js, el juego en public/, el kit de despliegue y una acumulación histórica de material de trabajo. La rama pages es el sitio desplegado en GitHub Pages, generado íntegramente por scripts/deploy_pages.py en cada release mediante un commit huérfano de historia aplastada: su contenido se reconstruye desde cero en cada publicación, por lo que no conserva residuos. La tabla 1 resume el peso por carpeta en main."));
c.push(tablaTitulo("Tabla 1: peso trackeado por carpeta en main (git ls-tree)"));
c.push(tabla(
  ["Carpeta", "Ficheros", "Tamaño", "Qué es"],
  [
    ["public/", "527", "210,2 MB", "El juego: game.html, assets, 5 campeonatos (INTOCABLE)"],
    ["scripts/", "2.029", "187,2 MB", "Arneses vivos + ~1.500 ficheros legacy de eras r30-r112"],
    ["tmp_owner_backup/", "104", "87,7 MB", "Respaldo temporal del dueño (2026-11-17): duplicados + originales"],
    ["Raíz (ficheros sueltos)", "46", "29,9 MB", "Medios duplicados, 6 imágenes pegadas, 5 ZIPs fuente, configs"],
    ["src/", "104", "18,7 MB", "Aplicación Next.js + módulos del juego (INTOCABLE)"],
    ["Resto (mockups, three-pkg, docs…)", "55", "3,4 MB", "Varios: se analiza en 4.4"],
    ["Total main", "2.837", "537,2 MB", ""],
  ],
  [30, 12, 14, 44]));
c.push(body("Sobre lo que ya está limpio conviene fijar el contexto para no repetir trabajo: la limpieza del remoto se cerró en la ronda r112-ops — quedan las ramas main y pages, unos 45 tags (los 140 antiguos ya se eliminaron con amparo en tags rescate/), 41 releases de la última semana y el tag v3.6.209-SDK6 apuntando al HEAD actual. El desorden que observa el dueño está, por tanto, dentro del árbol de ficheros de main, no en la estructura de ramas, tags ni releases.", { after: 200 }));

// 3 · Metodología
c.push(h1("3. Metodología del análisis"));
c.push(body("Todo el inventario se calculó con código persistido en scripts/ (inventario_limpieza_r113.py y analisis_fino_r113.py) sobre el propio repositorio sincronizado con el remoto, sin clonar ni duplicar datos. Se aplicaron cuatro métodos complementarios. Primero, git ls-tree -r -l sobre main para obtener el tamaño exacto de cada blob trackeado, agrupado por carpeta. Segundo, una única pasada de git log --name-only para fechar el último commit de cada fichero (8.961 ficheros con historia, incluidos los ya borrados). Tercero, detección de duplicados byte-exactos mediante hash SHA-256 de todos los ficheros trackeados menores de 8 MB: se identificaron 105 grupos de archivos idénticos. Cuarto, y más importante para el blindaje, un escaneo de referencias activas: los 27 candidatos de la raíz se buscaron por nombre dentro de los 2.621 ficheros de texto del código vivo (src/, public/, mini-services/, scripts/ activos y configuración), clasificando cada mención como ruta de carga real, comentario histórico o referencia a la copia de public/. La verificación de seguridad se completó comprobando que ningún secreto está trackeado (la clave de producción del worker no lo está; el .env solo contiene una ruta de base de datos local)."));

// 4 · Hallazgos
c.push(h1("4. Hallazgos por bloques"));
c.push(h2("4.1 Raíz del repositorio: 27 candidatos"));
c.push(body("La raíz mezcla configuración viva (package.json, .env, configs de build) con residuos de tres tipos. El primero son las seis imágenes pasted_image_*.png (2,45 MB), restos de pegados de chat sin una sola referencia en el código. El segundo son los archivos de medios sueltos (mp3, png, jpg, glb): sus referencias en el código del juego resultaron ser comentarios históricos o cargas relativas que resuelven dentro de public/assets/ (la variable vbase de c08_hall_hud.js apunta a public/assets/hall/...); en producción (rama pages) los ficheros de raíz ni siquiera se sirven. Verificado byte a byte, 14 de ellos son duplicados exactos del asset vivo en public/ y 6 son variantes fuente cuyo contenido idéntico existe en tmp_owner_backup/. El tercero son los 5 ZIP (paredes, rascacielos, partido, troqueles, recortables; 9,3 MB), paquetes fuente de eras anteriores que el manifiesto de halloween solo menciona como procedencia documental."));
c.push(tablaTitulo("Tabla 2: veredicto por categoría de la raíz"));
c.push(tabla(
  ["Categoría", "Ficheros", "Tamaño", "Veredicto propuesto"],
  [
    ["Imágenes pegadas (pasted_image_*)", "6", "2,45 MB", "Borrar (0 referencias en todo el repo)"],
    ["Medios duplicados del asset vivo en public/", "14", "11,9 MB", "Borrar (la copia viva queda intacta)"],
    ["Variantes fuente (solo existen en tmp_owner_backup)", "6", "4,4 MB", "Mover a fuentes/dueno/ (sin pérdida)"],
    ["ZIPs fuente de eras antiguas", "5", "9,3 MB", "Mover a fuentes/ y actualizar el LEEME"],
    ["tmp_pages_version.txt (vacío, duplica un .gitkeep)", "1", "0 B", "Borrar"],
  ],
  [40, 12, 14, 34]));
c.push(h2("4.2 tmp_owner_backup/: el bloque mayor de residuo organizado"));
c.push(body("Esta carpeta (104 ficheros, 87,7 MB, fechados el 2026-11-17) es un respaldo temporal que se tomó durante la resolución de conflictos de subida del dueño. El análisis por hash muestra que 33,3 MB son duplicados byte-exactos de ficheros que ya viven en public/ (arcano.mp3, candado.png, intro.mp4 entre otros) y que 37 ficheros son únicos (~54 MB): las texturas originales de paredes (_ext/paredes/), Melodia.mp3, burla.zip, Mando.glb y las variantes de fuente citadas en 4.1. Es material del dueño, no basura: por eso la propuesta no es borrarlo sino darles un hogar con nombre propio. Las dos opciones (trasladar la carpeta entera a fuentes/dueno/ o extraer los 37 únicos y borrar los duplicados) se presentan en la fase F2 para decisión del dueño."));
c.push(h2("4.3 scripts/: 2.029 ficheros y solo unas tres decenas vivos"));
c.push(body("scripts/ acumula once eras de trabajo (r30 a r112). Los ficheros vivos identificados por nombre y fecha son los arneses de prueba r93-r109 (arnes_*.mjs, tocados por la batería hasta el 21-11), las baterías y regolden r60-r62, el despliegue (deploy_pages.py, limpieza_github_r109.py, backup_completo.py), los checks y arneses de la ronda actual (check_live_service_igualdad.py, test_r112_live_service.mjs, test_worker_r169.mjs), la telemetría (diag/probe/alerta), el kit de empaquetado release-v36209/ (fuente de los ZIPs) y worker-tele/ (código del worker de telemetría). Todo lo demás — unos 1.500 ficheros sueltos (1.009 .py, 184 .png, 91 .mjs, 58 .json) y las subcarpetas de capturas y arte de eras pasadas (qa_shots_r104-r110, _r85_arte, _r30_assets, tmp_pala, _r73, _backup_r45_local, backup_r57, _poder35, _checkglobal_shots; ~31 MB) — es material de archivo: scripts de una sola ejecución cuyo contexto histórico ya vive en worklog.md."));
c.push(tablaTitulo("Tabla 3: desglose de scripts/ por bloques"));
c.push(tabla(
  ["Bloque", "Ficheros", "Tamaño", "Veredicto"],
  [
    ["Vivos: arneses r93-r109, baterías r60-r62, deploy, checks, kit, worker-tele", "~40", "0,6 MB", "Mantener en el sitio"],
    ["render_brazos/ (r93-95, en uso por los arneses de brazos)", "7", "2,3 MB", "Mantener"],
    ["Subcarpetas de capturas y arte de eras (qa_shots_*, _r85_arte, _r30_assets…)", "~80", "31,0 MB", "Mover a scripts/archivo/capturas/"],
    ["One-off de eras antiguas (gen_leeme_v*, gen_release_v*, _r*, test_r*, qa_*)", "~1.500", "150 MB aprox.", "Mover a scripts/archivo/<era>/"],
  ],
  [48, 12, 14, 26]));
c.push(h2("4.4 Carpetas menores"));
c.push(body("three-pkg/ (2 ficheros, 1,3 MB, 17-11) es una copia local de three.js que no aparece en ninguna configuración de build ni en el importmap del juego — que de hecho carga three desde CDN (jsdelivr) —: huérfano. examples/ (2 ficheros del 01-10) son demos de websocket sin referencias locales: las 42 menciones detectadas eran URLs del CDN de three que contienen la palabra examples, un falso positivo del escaneo. tests/ (3 shell scripts del 01-10) repite el database-runtime-build.sh que ya existe en .zscripts/. db/custom.db (0,02 MB) está VIVO: el .env trackeado apunta a él como base de datos de desarrollo de Prisma, así que se conserva. mockups/ (4 PNG, 2,0 MB, 20-11) y docs/SUPERPODER-DE-PALA.md son materiales recientes del dueño: se mantienen tal cual. .zscripts/ es la infraestructura de arranque del entorno (build.sh, dev.sh, start.sh): intocable."));
c.push(h2("4.5 Seguridad del árbol"));
c.push(body("Dos comprobaciones con resultado favorable. La clave de producción del worker (scripts/worker-tele/.clave-produccion) NO está trackeada en git: en GitHub solo están worker.js, wrangler.toml, el LEEME y los arneses de test. El fichero .env trackeado contiene únicamente DATABASE_URL apuntando a la base SQLite local (db/custom.db), sin secretos; aun así, la propuesta recomienda añadir .env al .gitignore en una futura ronda para evitar que algún día se le añada una credencial real sin darse cuenta."));
c.push(h2("4.6 Rama pages y material solo local"));
c.push(body("La rama pages (507 ficheros: championships 435, assets 54, raíz 15, vendor 2, ugc 1) es la salida regenerada del último release; no contiene basura y no requiere limpieza. Fuera de GitHub quedan los directorios de trabajo locales, invisibles para el dueño en el remoto pero relevantes para el disco: los tres staging de empaquetado (~195 MB cada uno, regenerables por build_zip.py), pages-site/ (197 MB, regenerable por deploy_pages.py) y download/ (851 MB de entregables históricos). De ellos se propone una limpieza local opcional en la fase F5, sin tocar el remoto."));

// 5 · Plan por fases
c.push(h1("5. Plan propuesto por fases"));
c.push(body("Cada fase es un commit independiente y reversible (git revert o git mv inverso), se verifica con la batería de la casa antes de continuar y ninguna toca public/ ni src/, por lo que el juego publicado no cambia y no se requiere nueva release. El orden va del riesgo mínimo al organizativo."));
c.push(tablaTitulo("Tabla 4: las seis fases"));
c.push(tabla(
  ["Fase", "Acción", "Ficheros", "Efecto en el árbol", "Reversibilidad"],
  [
    ["F1", "Borrar residuos seguros de la raíz (pasted, duplicados byte-exactos con copia viva, tmp_pages_version)", "21", "−14,4 MB", "git revert del commit"],
    ["F2", "Crear fuentes/: mover 5 ZIPs + 6 variantes fuente + tmp_owner_backup (opción A: carpeta entera; opción B: solo los 37 únicos)", "115", "Reorganiza 101 MB (opción B libera además 33,3 MB)", "git mv inverso"],
    ["F3", "Crear scripts/archivo/<era>/ y scripts/archivo/capturas/: mover los ~1.500 one-off y las capturas; los vivos quedan en su sitio", "~1.580", "Reorganiza ~180 MB (opción C libera ~40 MB borrando capturas y logs)", "git mv inverso"],
    ["F4", "three-pkg/, examples/ y tests/ a scripts/archivo/; scripts_release_r122_manual.py igualmente", "8", "−1,3 MB", "git mv inverso"],
    ["F5", "Housekeeping local: eliminar ~137 tags locales muertos, git gc; (opcional) borrar staging regenerables y download/ antiguo", "0 en git", "Solo disco local", "Regenerable"],
    ["F6", "Verificación integral y push: batería núcleo 9/9, golden byte-exacto, smoke del juego, checks r112, commit y push final", "—", "—", "—"],
  ],
  [7, 40, 10, 24, 19]));
c.push(body([run("Regla de oro aplicada en todas las fases: "), run("solo se borra lo que tiene copia byte-exacta viva en el repo o cero referencias; todo lo demás se archiva con git mv", true), run(", que conserva la historia y permite restaurar cualquier fichero con un comando. La antigüedad por sí sola no es criterio de borrado: el worklog y el núcleo del juego son viejos y se quedan; el criterio real es referencia + duplicación + regenerabilidad.")]));

// 6 · Blindaje
c.push(h1("6. Lo que no se toca (blindaje)"));
c.push(body("El requisito del dueño es que nada construido quede 100 % blindado. Estos bloques quedan fuera de toda fase, con su razón de ser verificada durante el análisis:"));
c.push(tablaTitulo("Tabla 5: bloques blindados y su función verificada"));
c.push(tabla(
  ["Bloque", "Por qué es intocable"],
  [
    ["public/ completo (527)", "El juego vivo: game.html byte-exacto con el golden, assets y 5 campeonatos con identidad verificada"],
    ["src/ completo", "Aplicación Next.js y módulos del juego que la batería compila y prueba"],
    ["mini-services/live-service/", "Fuente de verdad del relay (N1): el kit se empaqueta desde aquí"],
    ["scripts/release-v36209/ y build_zip.py", "Kit de empaquetado de la versión: genera los 4 ZIPs de cada release"],
    ["scripts/worker-tele/", "Código del worker de telemetría de producción"],
    ["Arneses r93-r109 y baterías r60-r62", "La batería de la casa los ejecuta; su fecha de último commit es 2026-11-21"],
    ["deploy_pages.py, limpieza, backup, checks r112-r113", "Operación viva del repo (release, limpieza, verificación)"],
    ["worklog.md, mockups/, docs/", "Memoria histórica y materiales recientes del dueño"],
    [".zscripts/, db/custom.db, .env", "Infraestructura del entorno y configuración viva (verificado 4.4 y 4.5)"],
    ["Rama pages", "Sitio publicado: se regenera entero en cada release; no lleva residuos"],
  ],
  [42, 58]));

// 7 · Riesgos
c.push(h1("7. Riesgos y mitigaciones"));
c.push(body("El riesgo principal de cualquier limpieza en git es creer que el borrado libera espacio en GitHub: no lo hace. Los blobs eliminados siguen vivos en la historia del repositorio, así que el beneficio real de este plan es de organización, claridad y velocidad de trabajo — que es lo que el dueño pidió — y no de reducción del peso del remoto. Una reducción física exigiría reescribir la historia (BFG o git filter-repo), operación de alto riesgo que rompería los SHA de los commits, invalidaría los tags rescate/ y obligaría a re-forzar todas las ramas: expresamente NO se propone. Si algún día se quisiera, el paso previo obligatorio sería el bundle completo que scripts/backup_completo.py ya genera."));
c.push(body("Los riesgos operativos del plan son menores y están mitigados por diseño. Que un fichero movido a scripts/archivo/ sea necesario para una era futura: mitigado porque git mv preserva la historia y cualquier fichero se restaura en segundos. Que un arnés vivo resulte clasificado como legacy por error de nombre: mitigado porque la lista de vivos se fijó por nombre y fecha de último commit (toca la batería), y la fase F3 publica la lista completa de movidos en el commit para revisión antes del push. Que la batería falle tras una fase: es la puerta de parada — cada fase termina con batería núcleo 9/9, golden byte-exacto y smoke del juego; si algo falla, se revierte la fase y no se continúa. Finalmente, el PAT usado para el push debe rotarse al cerrar la ronda porque pasó por el chat."));

// 8 · Beneficios
c.push(h1("8. Beneficios esperados y verificación final"));
c.push(body("Tras las seis fases, la raíz de main pasa de unos 60 elementos a una treintena legible sin sueltos sueltos: los ZIPs y las variantes de fuente viven en fuentes/dueno/, los scripts muertos en scripts/archivo/ organizados por era, y los vivos quedan donde estaban. El árbol visible se aclara en unos 14,4 MB de residuo puro borrado y hasta 73 MB liberados si el dueño elige las opciones B y C de las fases F2 y F3, con más de 280 MB reorganizados bajo nombres con significado. Ningún cambio afecta a public/ ni a la rama pages, así que el sitio publicado, el SW y el golden permanecen byte-exactos y no se necesita release."));
c.push(body("La verificación final (F6) reproduce la rutina completa de la casa: batería núcleo 9/9, golden SHA-256 byte-exacto contra src/game/GOLDEN_SHA256.txt, smoke del juego con Playwright, checks r112 (igualdad del relay y E2E del live-service) y push de main con el PAT en el entorno. El resultado queda registrado en worklog.md con la lista exacta de ficheros movidos y borrados por fase."));

// 9 · Decisión
c.push(h1("9. Decisión pendiente del dueño"));
c.push(body("Ningún cambio se ha ejecutado. Para proceder, marque en la tabla 6 las fases aprobadas (y la opción A/B en F2 y la opción con/sin borrado definitivo en F3). Con la aprobación por escrito, la ejecución completa de las fases F1-F6 se estima en una única sesión de trabajo con verificación entre fases."));
c.push(tablaTitulo("Tabla 6: hoja de aprobación"));
c.push(tabla(
  ["Fase", "Contenido", "Decisión del dueño"],
  [
    ["F1", "Borrar 21 residuos seguros de la raíz (−14,4 MB)", "【Aprobar / No aprobar】"],
    ["F2 opción A", "fuentes/dueno/ con la carpeta tmp_owner_backup entera (0 pérdida)", "【Aprobar / No aprobar】"],
    ["F2 opción B", "Extraer los 37 únicos a fuentes/dueno/ y borrar los 33,3 MB duplicados", "【Aprobar / No aprobar】"],
    ["F3", "scripts/archivo/ por eras (opción C: borrar capturas y logs, −40 MB)", "【Aprobar / No aprobar】"],
    ["F4", "Archivar three-pkg/, examples/, tests/ y el script suelto de raíz", "【Aprobar / No aprobar】"],
    ["F5", "Housekeeping local (tags locales, git gc, staging regenerables)", "【Aprobar / No aprobar】"],
    ["F6", "Verificación integral + push", "【Aprobar / No aprobar】"],
  ],
  [14, 56, 30]));

// ── Documento ─────────────────────────────────────────────────────
const footerNum = () => new Footer({
  children: [new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ children: [PageNumber.CURRENT], size: 18, color: "808080", font: FONT })],
  })],
});
const headerCorto = new Header({
  children: [new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: "Propuesta de limpieza y organización del repositorio · r113", size: 18, color: "808080", font: FONT })],
  })],
});
const pgSize = { width: 11906, height: 16838 };
const pgMargin = { top: 1440, bottom: 1440, left: 1701, right: 1417 };

const doc = new Document({
  styles: { default: {
    document: { run: { font: FONT, size: 24, color: "000000" },
                paragraph: { spacing: { line: 312 } } },
    heading1: { run: { font: FONT, size: 32, bold: true, color: P.headInk },
                paragraph: { spacing: { before: 360, after: 160, line: 312 }, outlineLevel: 0 } },
    heading2: { run: { font: FONT, size: 28, bold: true, color: P.headInk },
                paragraph: { spacing: { before: 240, after: 120, line: 312 }, outlineLevel: 1 } },
  }},
  sections: [
    { properties: { page: { size: pgSize, margin: { top: 0, bottom: 0, left: 0, right: 0 } } },
      children: portada },
    { properties: { type: SectionType.NEXT_PAGE,
        page: { size: pgSize, margin: pgMargin,
                pageNumbers: { start: 1, formatType: NumberFormat.UPPER_ROMAN } } },
      footers: { default: footerNum() }, children: indice },
    { properties: { type: SectionType.NEXT_PAGE,
        page: { size: pgSize, margin: pgMargin,
                pageNumbers: { start: 1, formatType: NumberFormat.DECIMAL } } },
      headers: { default: headerCorto }, footers: { default: footerNum() },
      children: c },
  ],
});

Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync(SALIDA, buf);
  console.log("✓ escrito:", SALIDA, (buf.length / 1024).toFixed(0) + " KB");
});
