
  /* ---------------- pantalla informativa (sección 12) ---------------- */
  _hudDirty() {
    const F = ESC_CFG.fases[this.fase];
    let enem = '';
    if (this.phase === 'combate') {
      if (F.jefe) {
        let vivos = 0;
        for (const c of this.canones) if (!c.dead) vivos++;
        enem = 'CAN' + vivos;
      } else {
        let vivos = 0;
        for (const d of this.drones) if (d.alive) vivos++;
        if (this.centOn) vivos++;
        const total = F.drones + (F.centinela || 0);
        enem = 'EN' + vivos + '/' + total;
      }
    }
    const key = this.phase + '|' + this.fase + '|' + this.hull + '|' + enem + '|' +
      Math.round(this.sobrecarga * 100) + '|' + this.rally + '|' +
      (this._msgT > 0 ? this._msg : '') + '|' + (this._banner ? this._banner.title : '') +
      '|' + (this.centSobreT > 0 ? 'S' : '') + '|' + Math.round(this.faseT);
    if (key === this._hudKey) return;
    this._hudKey = key;
    this._pantalla();
  }

  _msgNova(txt, t) {
    this._msg = txt;
    this._msgSub = 'NOVA · ';
    this._msgT = t || ESC_CFG.msgT;
    this._hudKey = '';
  }

  _pantalla() {
    const c = this.panCv.getContext('2d');
    const W = this.panCv.width, H = this.panCv.height;
    c.clearRect(0, 0, W, H);
    if (this._panImg) {
      c.globalAlpha = 0.96;
      c.drawImage(this._panImg, 0, 0, W, H);
      c.globalAlpha = 1;
    } else {
      c.fillStyle = 'rgba(8,16,30,0.92)';
      c.fillRect(0, 0, W, H);
    }
    c.textAlign = 'center';
    c.textBaseline = 'middle';
    /* cabecera */
    c.fillStyle = '#ffd257';
    c.font = '800 44px system-ui, sans-serif';
    c.fillText('DEFENSA DEL CASCO · NAVE ORBITAL', W / 2, 86);
    const F = ESC_CFG.fases[this.fase];
    const enCombate = this.phase === 'combate';
    /* fila 1: fase + integridad */
    c.font = '700 40px system-ui, sans-serif';
    c.fillStyle = '#e8f2ff';
    c.fillText('FASE ' + (this.fase + 1) + ' / 3', 280, 208);
    const crit = this.hull <= ESC_CFG.alertaUmbral;
    c.fillStyle = crit ? '#ff5a4d' : '#7fd8a8';
    c.fillText('INTEGRIDAD DEL CASCO: ' + Math.round(this.hull) + ' %', 700, 208);
    /* fila 2: enemigos + sobrecarga */
    c.fillStyle = '#e8f2ff';
    if (F.jefe) {
      let vivos = 0;
      for (const cc of this.canones) if (!cc.dead) vivos++;
      c.fillText('CAÑONES: ' + vivos + ' / 3', 280, 296);
    } else {
      let vivos = 0;
      for (const d of this.drones) if (d.alive) vivos++;
      if (this.centOn) vivos++;
      const total = F.drones + (F.centinela || 0);
      c.fillText('ENEMIGOS RESTANTES: ' + vivos + ' / ' + total, 330, 296);
    }
    c.fillStyle = this.sobrecarga >= 1 ? '#ffe27a' : '#8fb8d8';
    c.fillText('SOBRECARGA: ' + Math.round(this.sobrecarga * 100) + ' %', 760, 296);
    /* fila 3: estado + rally */
    const estado = this.phase === 'prep' ? 'PREPARACIÓN'
      : this.phase === 'inter' ? 'REPARACIONES'
      : this.phase === 'result' ? (this._win ? 'VICTORIA' : 'DERROTA')
      : (this.centSobreT > 0 ? '¡NÚCLEO EXPUESTO!' : 'COMBATE');
    c.fillStyle = this.centSobreT > 0 ? '#35ff9d' : '#e8f2ff';
    c.fillText('ESTADO: ' + estado, 330, 384);
    if (this.centOn) {
      c.fillStyle = '#8fe4ff';
      c.fillText('RALLY: ' + this.rally + ' / ' + ESC_CFG.cent.rallyParaAbrir, 760, 384);
    }
    /* mensaje de NOVA (capa independiente, abajo) */
    if (this._msgT > 0 && this._msg) {
      c.fillStyle = 'rgba(6,12,24,0.72)';
      c.fillRect(60, 470, W - 120, 108);
      c.strokeStyle = 'rgba(120,200,255,0.5)';
      c.lineWidth = 2;
      c.strokeRect(60, 470, W - 120, 108);
      c.fillStyle = '#9fd8ff';
      c.font = '700 24px system-ui, sans-serif';
      c.fillText((this._msgSub || '') + 'NOVA', W / 2, 498);
      c.fillStyle = '#f2f8ff';
      c.font = '600 27px system-ui, sans-serif';
      const palabras = String(this._msg).split(' ');
      let linea = '', y = 538;
      const lineas = [];
      for (const p of palabras) {
        if ((linea + ' ' + p).trim().length > 64) { lineas.push(linea.trim()); linea = p; }
        else linea += ' ' + p;
      }
      if (linea.trim()) lineas.push(linea.trim());
      for (const ln of lineas.slice(0, 2)) { c.fillText(ln, W / 2, y); y += 32; }
    }
    /* banner de preparación / resultado */
    const b = this._banner;
    if (b && this.phase === 'result') {
      c.fillStyle = 'rgba(6,10,20,0.78)';
      c.fillRect(150, 150, W - 300, 220);
      c.strokeStyle = b.col;
      c.lineWidth = 4;
      c.strokeRect(150, 150, W - 300, 220);
      c.fillStyle = b.col;
      c.font = '900 62px system-ui, sans-serif';
      c.fillText(b.title, W / 2, 235);
      c.fillStyle = '#e8f2ff';
      c.font = '700 34px system-ui, sans-serif';
      c.fillText(b.sub || '', W / 2, 308);
    } else if (this.phase === 'prep') {
      c.fillStyle = 'rgba(6,10,20,0.78)';
      c.fillRect(150, 150, W - 300, 220);
      c.strokeStyle = '#ff5a4d';
      c.lineWidth = 4;
      c.strokeRect(150, 150, W - 300, 220);
      c.fillStyle = '#ff5a4d';
      c.font = '900 66px system-ui, sans-serif';
      c.fillText('⚠ ALERTA DE ABORDAJE', W / 2, 228);
      c.fillStyle = '#e8f2ff';
      c.font = '700 32px system-ui, sans-serif';
      c.fillText(tx('Activa el escudo manual: tu pala es la defensa', 'Activate the manual shield: your paddle is the defense'), W / 2, 300);
    }
    this.panTex.needsUpdate = true;
  }
}
