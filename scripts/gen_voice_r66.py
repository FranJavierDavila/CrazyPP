#!/usr/bin/env python3
"""r66 · Regenera TODOS los átomos de voz de LA ACADEMIA con Piper TTS,
MÁS PAUSADOS y con mejor entonación (petición del dueño: «las voces deberían
ser más pausadas, con algo más de tiempo para escucharlas, y mejorar la
entonación»).

Cambios r66 sobre r65:
  · --length-scale 1.16 (habla más lenta y pausada)
  · --sentence-silence 0.55 (respiro entre frases dentro del átomo)
  · guion NUEVO para los pasos rediseñados (mandos duales, saque demo sobre
    la mesa, intercambio con rotación, marcador a 11 por 2 y 10-10) y
    puntuación cuidada (comas y puntos guían la prosodia de Piper).
  · Narador idéntico al banco de la casa: es_ES-davefx-medium · en_US-lessac-medium.

Salida: WAV 22050 Hz mono → OGG Opus 28k mono (formato del banco v2.20).
Insertar después:  python3 scripts/insertar_voz_r66.py
"""
import os, subprocess, sys

BASE = "/home/z/my-project"
M = f"{BASE}/scripts/voice_r65/models"
OUT_WAV = f"{BASE}/scripts/voice_r65/wav"
OUT_ES = f"{BASE}/scripts/voice_r65/ogg_es"
OUT_EN = f"{BASE}/scripts/voice_r65/ogg_en"
PIPER = "/home/z/.local/bin/piper"
LENGTH_SCALE = "1.16"      # r66 · más pausado
SENT_SILENCE = "0.55"      # r66 · respiro entre frases

for d in (OUT_WAV, OUT_ES, OUT_EN):
    os.makedirs(d, exist_ok=True)

ES = {
    "tutv0a": "Bienvenido a la Academia de Crazy Ping Pong.",
    "tutv0b": "Soy tu entrenador. Escucha, haz lo que te pida, y avanza cuando lo domines.",
    "tutv1a": "Estos son tus mandos de verdad. El izquierdo, con los botones Y y X. Y el derecho, con B y A.",
    "tutv1b": "Empieza apretando el gatillo. Así golpeas la bola.",
    "tutv1c": "Bien. Ahora, el botón lateral. El grip.",
    "tutv1d": "Ahora inclina el stick en todas direcciones.",
    "tutv1e": "Y por último, pulsa el botón A.",
    "tutv1f": "Y mira: tu mando se convierte en tu raqueta.",
    "tutv2a": "La pala es la prolongación de tu mano.",
    "tutv2b": "Muévela de lado a lado, con firmeza.",
    "tutv3a": "Vamos con el saque. Mira la mesa: la bola descansa en la mano libre, y el gatillo la suelta.",
    "tutv3b": "El saque debe botar primero en tu campo, y después en el del rival.",
    "tutv3c": "Si el rival no la devuelve… punto para ti. Mira el ejemplo.",
    "tutv3d": "Ahora tú. Aprieta el gatillo, y golpéala en el punto muerto. Necesito tres saques válidos.",
    "tutv4a": "Otro saque. Ahora el rival devuelve… y el intercambio empieza.",
    "tutv4b": "Cuando alguien pierde el intercambio, es punto del otro. Y cada dos saques, rota el sacador: dos tuyos, dos del rival.",
    "tutv5a": "El partido va a once puntos, y hay que ganar por dos.",
    "tutv5b": "Si empatáis a diez, el saque cambia en cada punto, y gana el primero que saque dos de ventaja.",
    "tutv6a": "Ahora el intercambio: te lanzo bolas suaves, y tú devuélvemelas.",
    "tutv6b": "Seis devoluciones y superas el paso.",
    "tutv7a": "En pleno juego, pulsa A para cambiar la pala de mano.",
    "tutv8a": "Te esperan seis modos de juego: partido, supervivencia, multijugador, y más.",
    "tutv9a": "Crazy, ranking y entrenamiento completan el circuito, con poderes locos en cada mesa.",
    "tutv10a": "Ya lo sabes todo. Pulsa jugar ya, y nos vemos en la mesa.",
    "tutv10b": "¡Bienvenido al circuito, campeón!",
    "tutok": "¡Muy bien!",
    "tutotra": "Otra vez: tú puedes.",
}

EN = {
    "tutv0a": "Welcome to the Crazy Ping Pong Academy.",
    "tutv0b": "I'm your coach. Listen, do what I ask, and move on when you've got it.",
    "tutv1a": "These are your real controllers. The left one, with the Y and X buttons. And the right one, with B and A.",
    "tutv1b": "Start by squeezing the trigger. That's how you hit the ball.",
    "tutv1c": "Good. Now, the side button. The grip.",
    "tutv1d": "Now tilt the thumbstick in every direction.",
    "tutv1e": "And finally, press the A button.",
    "tutv1f": "And look: your controller becomes your racket.",
    "tutv2a": "The paddle is an extension of your hand.",
    "tutv2b": "Swing it side to side, firmly.",
    "tutv3a": "Let's talk about the serve. Watch the table: the ball rests in your free hand, and the trigger releases it.",
    "tutv3b": "The serve must bounce on your side first, and then on the opponent's side.",
    "tutv3c": "If the opponent doesn't return it… that's a point for you. Watch the example.",
    "tutv3d": "Now it's your turn. Squeeze the trigger, and hit it at the dead point. I need three valid serves.",
    "tutv4a": "One more serve. Now the opponent returns it… and the rally begins.",
    "tutv4b": "When someone loses the rally, the other scores. And every two serves, the server rotates: two yours, two theirs.",
    "tutv5a": "A game goes to eleven points, and you must win by two.",
    "tutv5b": "At ten all, the serve changes every single point, and the first to lead by two wins.",
    "tutv6a": "Now the rally: I'll feed you soft balls, and you return them.",
    "tutv6b": "Six returns and you pass the step.",
    "tutv7a": "Mid-game, press A to switch the paddle hand.",
    "tutv8a": "Six game modes are waiting: match, survival, multiplayer, and more.",
    "tutv9a": "Crazy, ranked and training complete the circuit, with wild powers on every table.",
    "tutv10a": "You know it all now. Press play, and see you at the table.",
    "tutv10b": "Welcome to the circuit, champion!",
    "tutok": "Well done!",
    "tutotra": "Try again: you can do it.",
}


def synth(atoms, model, ogg_dir, tag):
    total = 0
    for k, txt in atoms.items():
        wav = f"{OUT_WAV}/{tag}_{k}.wav"
        ogg = f"{ogg_dir}/{k}.ogg"
        # r66: los WAV se regeneran SIEMPRE (el guion y el ritmo cambian);
        # borra el wav viejo para forzar la resíntesis con los nuevos ajustes.
        if os.path.exists(wav):
            os.remove(wav)
        r = subprocess.run(
            [PIPER, "-m", model, "--length-scale", LENGTH_SCALE,
             "--sentence-silence", SENT_SILENCE, "-f", wav],
            input=txt, capture_output=True, text=True)
        if r.returncode != 0 or not os.path.exists(wav):
            sys.exit(f"FALLO piper {tag}:{k}: {r.stderr[:200]}")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav,
                        "-c:a", "libopus", "-b:a", "28k", "-ac", "1",
                        "-ar", "48000", ogg], check=True)
        total += os.path.getsize(ogg)
        print(f"  {tag}:{k}  {os.path.getsize(ogg)/1024:.1f} KB")
    print(f"OK {tag}: {len(atoms)} átomos · {total/1024:.0f} KB OGG")


if __name__ == "__main__":
    print("· ES (davefx, más pausado)…")
    synth(ES, f"{M}/es_ES-davefx-medium.onnx", OUT_ES, "es")
    print("· EN (lessac, más pausado)…")
    synth(EN, f"{M}/en_US-lessac-medium.onnx", OUT_EN, "en")
    print("LISTO")
