/**
 * Nouveaux skins de balles pour Swing & Snap.
 * Même format que ballSkins du jeu : draw:c=>{...} centré en (0,0), rayon ~10,
 * dessiné dans un contexte tournant (le jeu fait rotate(Date.now()/250)).
 * Palettes libres (Lospec-style) accordées au néon du jeu.
 *
 * À copier dans this.ballSkins (+ i18n + shop) à la phase d'intégration.
 */
const NEW_BALL_SKINS = {
  // Sunset Neon — orbe chaud rose/orange/or avec halo
  'sunset_neon': { price: 1600, name: 'Néon Crépuscule', color: '#FF5E7E', draw: c => {
    const g = c.createRadialGradient(-3, -3, 0, 0, 0, 12);
    g.addColorStop(0, '#FFD56B'); g.addColorStop(.4, '#FF9F45'); g.addColorStop(.75, '#FF5E7E'); g.addColorStop(1, '#6A2C8F');
    c.fillStyle = g; c.shadowBlur = 12; c.shadowColor = '#FF5E7E';
    c.beginPath(); c.arc(0, 0, 10, 0, 6.28); c.fill(); c.shadowBlur = 0;
    c.strokeStyle = 'rgba(255,213,107,.7)'; c.lineWidth = 1.4; c.beginPath(); c.arc(0, 0, 10, 0, 6.28); c.stroke();
    c.fillStyle = 'rgba(255,255,255,.55)'; c.beginPath(); c.arc(-3, -3, 3, 0, 6.28); c.fill();
  }},

  // Cyber Aqua — orbe sombre, circuits néon turquoise
  'cyber_aqua': { price: 2900, name: 'Cyber Aqua', color: '#00E5C0', draw: c => {
    c.fillStyle = '#0B1A2E'; c.beginPath(); c.arc(0, 0, 10, 0, 6.28); c.fill();
    c.save(); c.beginPath(); c.arc(0, 0, 10, 0, 6.28); c.clip();
    c.shadowBlur = 8; c.shadowColor = '#00E5C0'; c.strokeStyle = '#00E5C0'; c.lineWidth = 1;
    c.beginPath(); c.moveTo(-10, -3); c.lineTo(-3, -3); c.lineTo(-3, -9); c.moveTo(10, 3); c.lineTo(3, 3); c.lineTo(3, 9); c.stroke();
    c.strokeStyle = '#1AA7EC'; c.beginPath(); c.arc(0, 0, 5, 0, 6.28); c.stroke();
    c.fillStyle = '#00E5C0'; c.beginPath(); c.arc(0, 0, 2, 0, 6.28); c.fill();
    c.fillStyle = '#1AA7EC'; [[-3, -3], [3, 3]].forEach(([x, y]) => { c.beginPath(); c.arc(x, y, 1.2, 0, 6.28); c.fill(); });
    c.restore(); c.shadowBlur = 0;
  }},

  // Toxic Glow — orbe radioactif vert avec bulles
  'toxic': { price: 1900, name: 'Toxique', color: '#39FF14', draw: c => {
    const g = c.createRadialGradient(-2, -2, 0, 0, 0, 12);
    g.addColorStop(0, '#EAFFD0'); g.addColorStop(.3, '#B6FF3C'); g.addColorStop(.7, '#39FF14'); g.addColorStop(1, '#1f8a2d');
    c.fillStyle = g; c.shadowBlur = 12; c.shadowColor = '#39FF14';
    c.beginPath(); c.arc(0, 0, 10, 0, 6.28); c.fill(); c.shadowBlur = 0;
    c.fillStyle = 'rgba(20,60,10,.45)';
    [[3, -2, 2], [-3, 3, 1.6], [2, 4, 1.3], [-4, -3, 1.4]].forEach(([x, y, r]) => { c.beginPath(); c.arc(x, y, r, 0, 6.28); c.fill(); });
    c.fillStyle = 'rgba(255,255,255,.5)'; c.beginPath(); c.arc(-3, -3, 2.4, 0, 6.28); c.fill();
  }},

  // Royal Amethyst — gemme taillée violette à liseré or
  'amethyst': { price: 3400, name: 'Améthyste', color: '#9D4EDD', draw: c => {
    const g = c.createLinearGradient(0, -11, 0, 11);
    g.addColorStop(0, '#E9D5FF'); g.addColorStop(.4, '#C77DFF'); g.addColorStop(.8, '#9D4EDD'); g.addColorStop(1, '#5A189A');
    c.fillStyle = g; c.beginPath();
    c.moveTo(0, -11); c.lineTo(7, -3); c.lineTo(9, 4); c.lineTo(0, 11); c.lineTo(-9, 4); c.lineTo(-7, -3); c.closePath(); c.fill();
    c.shadowBlur = 6; c.shadowColor = 'rgba(255,215,0,.6)'; c.strokeStyle = '#FFD700'; c.lineWidth = 1.2; c.stroke(); c.shadowBlur = 0;
    c.fillStyle = 'rgba(255,255,255,.45)';
    c.beginPath(); c.moveTo(0, -9); c.lineTo(3, -3); c.lineTo(0, 2); c.lineTo(-3, -3); c.closePath(); c.fill();
  }},

  // Molten Chrome — métal liquide miroir bleu/argent
  'chrome': { price: 2600, name: 'Chrome Liquide', color: '#90A4D4', draw: c => {
    const g = c.createLinearGradient(-8, -8, 8, 8);
    g.addColorStop(0, '#FFFFFF'); g.addColorStop(.25, '#AEB8D6'); g.addColorStop(.5, '#5C6B99');
    g.addColorStop(.7, '#AEB8D6'); g.addColorStop(.85, '#2E3A5E'); g.addColorStop(1, '#8A97C0');
    c.fillStyle = g; c.beginPath(); c.arc(0, 0, 10, 0, 6.28); c.fill();
    c.strokeStyle = 'rgba(230,235,255,.5)'; c.lineWidth = 1; c.beginPath(); c.arc(0, 0, 10, 0, 6.28); c.stroke();
    c.fillStyle = 'rgba(255,255,255,.85)'; c.beginPath(); c.ellipse(-3, -4, 3, 1.6, -.5, 0, 6.28); c.fill();
    c.fillStyle = 'rgba(20,30,60,.5)'; c.beginPath(); c.ellipse(3, 5, 3.5, 1.6, -.4, 0, 6.28); c.fill();
  }}
};

if (typeof module !== 'undefined' && module.exports) module.exports = { NEW_BALL_SKINS };
if (typeof window !== 'undefined') window.NEW_BALL_SKINS = NEW_BALL_SKINS;
