# SKILL: Retro Pixel / 8-bit UI Design

---

## 1. Core Concept

Retro Pixel UI harnesses the nostalgia and cultural identity of 8-bit and 16-bit video games — pixelated fonts, chunky dithering patterns, NES/SNES color palettes, and CRT screen effects. It's not just "add pixel art" — it's a complete design language with its own grid system (pixel grid), interaction vocabulary (press = scanline flash), and aesthetic rules. The philosophy: _embrace the constraint as the art form_ — the limitation of pixels IS the aesthetic. Think indie game launcher, retro music site, or developer portfolio with character.

---

## 2. Key Visual Elements

### Colors (8-bit Palettes)

- **NES Palette**: `#0D0D0D` bg, `#FF0000` red, `#0000FF` blue, `#00FF00` green
- **Game Boy**: `#0F380F`, `#306230`, `#8BAC0F`, `#9BBC0F` (4-shade green)
- **SNES**: richer 16-bit with 32768 possible colors
- **Modern Pixel**: `#1A1A2E` (deep navy), `#E94560` (hot pixel red), `#0F3460`, `#16213E`
- Background: Always dark (CRT phosphor glow effect works on dark)

### Typography (Pixel Fonts)

- **Primary**: Press Start 2P, VT323, Silkscreen, Pixelify Sans (Google Fonts)
- **Monospace pixel**: Courier-style bitmap rendering
- `image-rendering: pixelated` on small text images
- No anti-aliasing on pixel fonts (sharp edges = correct)
- Size: use multiples of 8px (8, 16, 24, 32, 48, 64)

### The Pixel Grid System

```css
/* Everything aligns to 8px or 4px grid */
:root {
  --px: 4px; /* base pixel unit */
}
/* All measurements: calc(var(--px) * N) */
.pixel-card { padding: calc(var(--px) * 6); } /* 24px */
```

### Pixel/Chunky Borders (No Border-Radius)

```css
/* Pixel-perfect box border */
.pixel-box {
  image-rendering: pixelated;
  border: 4px solid #E94560;
  border-radius: 0;
  box-shadow: 4px 4px 0 #000; /* Always 4px multiples */
}
```

### CRT Effects

```css
/* Scanlines overlay */
.crt::after {
  content: '';
  position: fixed;
  inset: 0;
  background: repeating-linear-gradient(
    0deg,
    transparent,
    transparent 2px,
    rgba(0, 0, 0, 0.15) 2px,
    rgba(0, 0, 0, 0.15) 4px
  );
  pointer-events: none;
  z-index: 9999;
}

/* CRT screen curvature + vignette */
.crt-screen {
  box-shadow: 
    inset 0 0 60px rgba(0,0,0,0.5),
    inset 0 0 20px rgba(0,255,0,0.05);
  border-radius: 8px; /* slight CRT curve */
}
```

### Dithering Pattern

```css
/* Classic checkerboard dither */
.dither-pattern {
  background-image: 
    radial-gradient(circle, #E94560 1px, transparent 1px);
  background-size: 4px 4px;
}
/* Or dashed pattern fill */
.dither-fill {
  background: repeating-linear-gradient(
    45deg, 
    #E94560 0, #E94560 2px, 
    transparent 2px, transparent 6px
  );
}
```

---

## 3. UI Components

### Buttons (Pixel Press)

```css
.pixel-btn {
  background: #E94560;
  color: #fff;
  border: none;
  border-radius: 0;
  padding: 12px 24px;
  font-family: 'Press Start 2P', monospace;
  font-size: 12px;
  line-height: 1.8;
  image-rendering: pixelated;
  box-shadow: 4px 4px 0 #000, inset 2px 2px 0 rgba(255,255,255,0.2);
  cursor: pointer;
  transition: all 0.05s;
  text-transform: uppercase;
}
.pixel-btn:hover { background: #FF6B80; }
.pixel-btn:active {
  box-shadow: 0 0 0 #000, inset 2px 2px 0 rgba(0,0,0,0.3);
  transform: translate(4px, 4px);
}
```

### Cards (Pixel Panels)

```css
.pixel-panel {
  background: #1A1A2E;
  border: 4px solid #E94560;
  border-radius: 0;
  padding: 24px;
  /* Pixel corner decoration */
  box-shadow: 
    4px 4px 0 #000,
    -4px -4px 0 rgba(255,255,255,0.1);
}
/* Corner pixel dots */
.pixel-panel::before {
  content: '';
  position: absolute;
  width: 8px; height: 8px;
  background: #E94560;
  top: -4px; left: -4px;
}
```

### Health/Progress Bar (Game HUD)

```css
.pixel-hp-bar {
  background: #000;
  border: 4px solid #fff;
  height: 20px;
  image-rendering: pixelated;
}
.pixel-hp-fill {
  height: 100%;
  background: linear-gradient(90deg, #00FF00 0%, #FFFF00 60%, #FF0000 100%);
  background-size: 200% 100%;
  /* Position based on value: 100%hp=green, 50%=yellow, 25%=red */
  background-position: calc((1 - var(--hp, 1)) * 100%) 0;
  transition: width 0.5s ease;
  image-rendering: pixelated;
}
```

### Navbar (Game Menu)

```css
.pixel-menu {
  background: #0F3460;
  border-bottom: 4px solid #E94560;
  padding: 16px 32px;
  display: flex;
  gap: 32px;
}
.pixel-menu-item {
  font-family: 'Press Start 2P', monospace;
  font-size: 10px;
  color: #fff;
  text-decoration: none;
  padding: 8px 12px;
  image-rendering: pixelated;
}
/* Active: white bg, dark text (game selection cursor) */
.pixel-menu-item.active {
  background: #fff;
  color: #0F3460;
}
/* Selection cursor: ► */
.pixel-menu-item.active::before { content: '► '; color: #E94560; }
```

### Dialog Box (RPG Style)

```css
.pixel-dialog {
  background: #000;
  border: 4px solid #fff;
  padding: 20px 24px;
  font-family: 'VT323', monospace;
  font-size: 22px;
  line-height: 1.6;
  color: #fff;
  position: relative;
}
/* Blinking cursor at end */
.pixel-cursor {
  display: inline-block;
  width: 10px; height: 20px;
  background: #fff;
  animation: blink 0.8s step-end infinite;
}
@keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }
```

---

## 4. Best Use Cases

- **Indie game studios** / game landing pages
- **Developer portfolios** with personality
- **Retro gaming platforms** / ROM sites
- **Chiptune / 8-bit music** artists
- **Pixel art marketplaces**
- **Tech conference** websites (nerdy, fun)
- **Hackathon** landing pages
- **Developer tools** wanting personality

---

## 5. Design Guidelines

### DO

- Use `image-rendering: pixelated` on all pixel art
- Stick to multiples of 4px or 8px for all sizing
- Zero border-radius on everything (or 4px absolute maximum)
- Use pixel/bitmap fonts throughout — no smooth sans-serif
- Add CRT scanlines as overlay (subtle, 10–20% opacity)
- Include sound effects on interactions (optional but authentic)

### DON'T

- Mix pixel fonts with modern sans-serif in the same context
- Use drop-shadow blur (pixel art = hard shadows only)
- Use gradients liberally (dithering patterns instead)
- Anti-alias pixel art or fonts
- Use smooth/eased animations (step() functions instead)
- Use border-radius above 4px

### Common Mistakes

- **Smooth fonts**: modern fonts destroy the aesthetic
- **Blurred shadows**: pixel shadows = 4px hard offset, never blurred
- **Smooth animations**: use `steps()` timing function for pixel-accurate movement
- **Too small text**: Press Start 2P at 10px is minimum — pixels need room
- **Missing scanlines**: flat modern dark bg + pixel art = incomplete

---

## 6. Implementation Tips

### Load Pixel Fonts (Google Fonts)

```html
<link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&family=VT323:wght@400&display=swap" rel="stylesheet">
```

### Step Animations (NOT smooth)

```css
/* Pixel movement: steps, not ease */
.pixel-walk { animation: walk 0.4s steps(4) infinite; }
@keyframes walk {
  from { background-position: 0; }
  to { background-position: -128px; } /* sprite sheet */
}

/* Step cursor blink */
.cursor { animation: blink 1s steps(1) infinite; }

/* Step transition (no smoothing) */
.pixel-transition { transition: transform 0.1s steps(3); }
```

### CSS Pixel Art (No Images)

```css
/* Render pixel art using box-shadow on a 1px element */
.pixel-sprite {
  width: 1px; height: 1px;
  box-shadow: 
    1px 1px #E94560, 2px 1px #E94560, 3px 1px #0D0D0D,
    1px 2px #0D0D0D, 2px 2px #E94560, 3px 2px #E94560;
  transform: scale(8); /* scale up, stays crisp */
  image-rendering: pixelated;
}
```

### Tailwind Pixel Classes

```html
<button class="font-['Press_Start_2P'] text-[12px] bg-red-500 text-white 
               px-6 py-3 rounded-none border-0
               shadow-[4px_4px_0_#000] 
               active:shadow-none active:translate-x-1 active:translate-y-1
               transition-none cursor-pointer uppercase">
  START GAME
</button>
```

---

## 7. Example Layout: Indie Game Studio Homepage

```
[Dark #1A1A2E background with scanline overlay]
│
├── TOP BAR: Pixel marquee "★ NEW GAME ★ OUT NOW ★ PLAY FREE ★"
│   └── Scrolling pixel text (steps animation, no smooth)
│
├── NAVBAR: #0F3460 bg, 4px red border-bottom
│   └── Logo (pixel art logo) | GAMES ABOUT PRESS CONTACT
│   └── All uppercase, Press Start 2P
│
├── HERO: 2/3 + 1/3 split
│   ├── Left:
│   │   ├── "GAME STUDIO" (12px label, spaced)
│   │   ├── "PIXEL" / "CRAFT" (48px Press Start 2P)
│   │   ├── Blinking pixel cursor after
│   │   ├── Body text: VT323 24px, 1.6 line-height
│   │   └── Buttons: PLAY NOW + HIGH SCORES
│   └── Right: Pixel art character animation (CSS sprite sheet)
│
├── TICKER TAPE: Yellow on black, score-style
│   └── "P1: 00045200   HI: 00098000   STAGE 01"
│
├── GAMES GRID: 3 games, pixel art thumbnails
│   └── Each: 4px border, hard shadow, VT323 title
│
└── FOOTER: Dark, simple
    └── Copyright + "INSERT COIN TO CONTINUE"
```

---

## 8. Advanced Enhancements

### Typewriter Effect (Step-based)

```javascript
const text = "LOADING ADVENTURE...";
let i = 0;
const interval = setInterval(() => {
  el.textContent += text[i++];
  if (i >= text.length) clearInterval(interval);
}, 80); // Consistent speed, not random
```

### Screen Power-on Effect

```css
@keyframes crtPowerOn {
  0% { transform: scaleY(0.01); opacity: 0.5; filter: brightness(3); }
  30% { transform: scaleY(0.01); opacity: 1; filter: brightness(3); }
  60% { transform: scaleY(1); filter: brightness(2); }
  100% { transform: scaleY(1); filter: brightness(1); }
}
.crt-poweron { animation: crtPowerOn 0.5s ease-out; }
```

### Chiptune Background Music

```javascript
// Web Audio API 8-bit sounds
const AudioContext = window.AudioContext;
function playChip(freq, duration) {
  const osc = ctx.createOscillator();
  osc.type = 'square'; // NES-style square wave
  osc.frequency.value = freq;
  // Connect and play
}
```

### Score Counter

```javascript
// Animate score counting up
function animateScore(from, to, duration) {
  const steps = 60;
  const step = (to - from) / steps;
  let current = from;
  const interval = setInterval(() => {
    current += step;
    display.textContent = Math.floor(current).toString().padStart(8, '0');
    if (current >= to) clearInterval(interval);
  }, duration / steps);
}
```