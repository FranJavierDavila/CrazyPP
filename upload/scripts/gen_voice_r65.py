#!/usr/bin/env python3
"""r65 · Genera los átomos de voz de LA ACADEMIA GAMIFICADA con Piper TTS.

Mismo narrador que el resto del juego (banco v2.20/2.27):
  ES: es_ES-davefx-medium · EN: en_US-lessac-medium
Salida: WAV 22050 Hz mono (nativo Piper) → OGG Opus 28k mono (banco).

Átomos: tutv0a..tutv10b (narración por paso, frases cortas) + tutok + tutotra.
Regenerar:  python3 scripts/gen_voice_r65.py
"""
import os, subprocess, sys

BASE = "/home/z/my-project"
M = f"{BASE}/scripts/voice_r65/models"
OUT_WAV = f"{BASE}/scripts/voice_r65/wav"
OUT_ES = f"{BASE}/scripts/voice_r65/ogg_es"
OUT_EN = f"{BASE}/scripts/voice_r65/ogg_en"
PIPER = "/home/z/.local/bin/piper"

for d in (OUT_WAV, OUT_ES, OUT_EN):
    os.makedirs(d, exist_ok=True)

ES = {
    "tutv0a": "Bienvenido a la Academia de Crazy Ping Pong.",
    "tutv0b": "Soy tu entrenador: escucha, haz lo que te pida, y avanza cuando lo domines.",
    "tutv1a": "Este es tu mando de verdad.",
    "tutv1b": "Empieza apretando el gatillo: así golpeas la bola.",
    "tutv1c": "Bien. Ahora aprieta el botón lateral.",
    "tutv1d": "Ahora inclina el stick en todas direcciones.",
    "tutv1e": "Y por último, pulsa el botón A.",
    "tutv2a": "La pala es la prolongación de tu mano.",
    "tutv2b": "Muévela de lado a lado con firmeza.",
    "tutv3a": "El partido va a once puntos, y hay que ganar por dos.",
    "tutv3b": "Cada intercambio ganado suma un punto: mira cómo sube el marcador.",
    "tutv4a": "Cada jugador saca dos veces seguidas, y el saque rota.",
    "tutv4b": "Si hay empate a diez, el saque cambia en cada punto.",
    "tutv4c": "Y ojo: el saque debe botar en tu campo, y después en el del rival.",
    "tutv5a": "Tu turno: lanza la bola y golpéala en el punto muerto para cruzar la red.",
    "tutv5b": "Necesito tres saques válidos. ¡Vamos!",
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
    "tutv0b": "I'm your coach: listen, do what I ask, and move on when you've got it.",
    "tutv1a": "This is your real controller.",
    "tutv1b": "Start by squeezing the trigger: that's how you hit the ball.",
    "tutv1c": "Good. Now squeeze the side grip button.",
    "tutv1d": "Now tilt the thumbstick in every direction.",
    "tutv1e": "And finally, press the A button.",
    "tutv2a": "The paddle is an extension of your hand.",
    "tutv2b": "Swing it side to side, firmly.",
    "tutv3a": "A game goes to eleven points, and you must win by two.",
    "tutv3b": "Every rally you win scores a point: watch the scoreboard climb.",
    "tutv4a": "Each player serves twice in a row, then the serve rotates.",
    "tutv4b": "At ten all, the serve changes every single point.",
    "tutv4c": "Careful: the serve must bounce on your side, then on the opponent's side.",
    "tutv5a": "Your turn: toss the ball and hit it at the dead point to cross the net.",
    "tutv5b": "I need three valid serves. Let's go!",
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
        if not os.path.exists(wav):
            r = subprocess.run([PIPER, "-m", model, "-f", wav], input=txt,
                               capture_output=True, text=True)
            if r.returncode != 0 or not os.path.exists(wav):
                sys.exit(f"FALLO piper {tag}:{k}: {r.stderr[:200]}")
        # WAV 22050 mono → OGG Opus 28k mono (formato del banco v2.20)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav,
                        "-c:a", "libopus", "-b:a", "28k", "-ac", "1",
                        "-ar", "48000", ogg], check=True)
        total += os.path.getsize(ogg)
        print(f"  {tag}:{k}  {os.path.getsize(ogg)/1024:.1f} KB")
    print(f"OK {tag}: {len(atoms)} átomos · {total/1024:.0f} KB OGG")


if __name__ == "__main__":
    print("· ES (davefx)…")
    synth(ES, f"{M}/es_ES-davefx-medium.onnx", OUT_ES, "es")
    print("· EN (lessac)…")
    synth(EN, f"{M}/en_US-lessac-medium.onnx", OUT_EN, "en")
    print("LISTO")
