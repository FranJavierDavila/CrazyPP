
(function () {
  var ov = document.getElementById('introov');
  var vid = document.getElementById('introvid');
  var btn = document.getElementById('introbtn');
  if (!ov || !vid) return;
  // v2.58: marca si la INTRO pausó la música de portada (si la pausó la
  // sesión VR vía onXRState, la INTRO NO la reanuda al cerrarse)
  var musicDucked = false;
  function duckMusic() {
    if (musicDucked || !window.__ppMusic) return;
    window.__ppMusic.pause();
    musicDucked = true;
  }
  function unduckMusic() {
    if (!musicDucked) return;          // no la pausó la INTRO: no se toca
    musicDucked = false;
    if (window.__ppMusic) window.__ppMusic.resume();  // respeta pp_music
  }
  function playWithSound() {
    // v2.58: el clic es un gesto de usuario → el navegador permite audio
    vid.muted = false;
    try { vid.volume = 1; } catch (err) { /* */ }
    duckMusic();
    var p = vid.play();
    if (p && p.catch) p.catch(function () {
      // red de seguridad: si el navegador bloqueara el audio, mudo y sigue
      vid.muted = true;
      var q = vid.play();
      if (q && q.catch) q.catch(function () { /* requiere otro gesto */ });
    });
  }
  function close() {
    if (!ov.classList.contains('open')) return;
    ov.classList.remove('open');
    try { vid.pause(); } catch (e) { /* */ }
    unduckMusic();
  }
  function open() {
    if (vid.error) {
      var st = document.getElementById('status');
      if (st) st.textContent = '⚠ assets/intro.mp4 no está disponible';
      return;
    }
    ov.classList.add('open');
    try { vid.currentTime = 0; } catch (err) { /* */ }
    playWithSound();
  }
  if (btn) btn.addEventListener('click', function (e) {
    e.stopPropagation();
    open();
  });
  // v2.58: pulsar directamente sobre el vídeo también lo (re)inicia con sonido
  vid.addEventListener('click', function (e) {
    e.stopPropagation();
    if (vid.error) return;
    vid.muted = false;                // por si quedara mudo: al instante suena
    try { vid.volume = 1; } catch (err) { /* */ }
    if (vid.paused) {
      try { vid.currentTime = 0; } catch (err) { /* */ }
      playWithSound();
    }
  });
  document.getElementById('introclose').addEventListener('click', close);
  vid.addEventListener('ended', close);
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') close(); });
  // al entrar en VR la música la gestiona onXRState: aquí NO se reanuda
  var vr = document.getElementById('vrbtn');
  if (vr) vr.addEventListener('click', function () {
    ov.classList.remove('open');
    try { vid.pause(); } catch (e) { /* */ }
    musicDucked = false;              // onXRState(true) la mantiene pausada
  });
  window.__ppIntro = { close: close, open: open };
})();
