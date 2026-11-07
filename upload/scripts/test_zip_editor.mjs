// test_zip_editor.mjs — valida el generador ZIP del editor (crc32 + zipDeArchivos)
import { readFileSync, writeFileSync } from "node:fs";

const src = readFileSync("/home/z/my-project/scripts/editor_src/app3.js", "utf8");

function extraer(nombre){
  const ini = src.indexOf("function " + nombre + "(");
  if(ini < 0) throw new Error("no encontrado: " + nombre);
  // recorte por llaves balanceadas
  let i = src.indexOf("{", ini), depth = 0, end = -1;
  for(; i < src.length; i++){
    if(src[i] === "{") depth++;
    else if(src[i] === "}"){ depth--; if(depth === 0){ end = i + 1; break; } }
  }
  return src.slice(ini, end);
}

const codigo = `
let _crcTabla = null;
${extraer("crc32")}
${extraer("zipDeArchivos")}
`;
const fab = new Function(codigo + "; return {crc32, zipDeArchivos};");
const { zipDeArchivos } = fab();

const archivos = [
  { nombre: "campeonato.json", contenido: JSON.stringify({ schema:"crazy-pingpong-campeonato", prueba:"hola ñandú 🏓", n: 42 }, null, 2) },
  { nombre: "LEEME.txt", contenido: "Línea con acentos: áéíóú Ñ ¿? ¡!\nSegunda línea\n" }
];
const blob = zipDeArchivos(archivos);
const buf = Buffer.from(await blob.arrayBuffer());
writeFileSync("/tmp/test-editor.zip", buf);
console.log("zip bytes:", buf.length, "| firma:", buf.slice(0,2).toString());
console.log("codificado UTF-8 flag:", buf.readUInt16LE(6) === 0x0800);
