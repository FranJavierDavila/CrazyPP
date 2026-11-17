
(function () {
  function paint() {
    var on = false;
    try { on = String(localStorage.getItem('pp_player_name') || '').trim().toLowerCase() === 'foro3d'; } catch (e) { /* */ }
    var el2 = document.getElementById('ppdbg');
    if (el2) el2.style.display = on ? 'block' : 'none';
  }
  paint();
  document.addEventListener('pp-lang', paint);
  window.__ppDbg2D = paint;   // el núcleo la llama al guardar el nombre
})();
