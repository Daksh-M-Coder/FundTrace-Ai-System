# SKILL: Skeuomorphism UI Design

---

## 1. Core Concept

Skeuomorphism designs digital interfaces to **mimic physical, real-world objects**. A notes app looks like a legal pad. A calendar looks like a desk calendar. Buttons look like actual physical buttons you can press. This design language was dominant in iOS 6 and earlier (Steve Jobs era). It's now experiencing a **sophisticated renaissance** — not as literal mimicry, but as _tactile realism_: interfaces with physical depth, realistic materials (wood, leather, metal, glass), and interactions that feel like touching real objects. Modern skeuomorphism is refined, not kitsch.

---

## 2. Key Visual Elements

### Materials & Textures (The Core of Skeuomorphism)

- **Metal**: Brushed aluminum, chrome, polished steel
- **Leather**: Stitching, grain texture, warm browns
- **Wood**: Grain patterns, warm tones
- **Paper**: Subtle cream tones, slight fiber texture
- **Fabric**: Linen, felt, velvet

### Colors

- **Warm neutrals**: #8B7355 (leather), #C4A882 (wood), #E8E8E8 (brushed metal)
- **Deep, rich backgrounds**: #1C1C1E, #2C2C2E, #1A1008
- **Highlight colors**: Metallic golds, silvers
- **Interface accent**: Deep blue (#003D7A) or forest green (#1B5E20) for "professional" tools

### Shadows & Depth (Multi-Layer Reality)

```css
/* Realistic button depth */
.skeu-btn {
  box-shadow:
    /* Top highlight */
    0 1px 0 rgba(255,255,255,0.6),
    /* Main shadow */
    0 4px 8px rgba(0,0,0,0.4),
    /* Bottom inner shadow (pressed look) */
    inset 0 -2px 4px rgba(0,0,0,0.3),
    /* Top inner highlight */
    inset 0 1px 2px rgba(255,255,255,0.4);
}
```

### Typography

- Older style but refined: Georgia, Palatino, Optima
- Or modern humanist: Lato, Source Sans Pro (neutral carriers)
- Small text with tight tracking for labels
- Embossed/debossed text effects using `text-shadow`

### Textures via CSS

```css
/* Brushed metal */
.metal-surface {
  background: linear-gradient(
    90deg,
    #d4d4d4 0%, #e8e8e8 25%, #c8c8c8 50%, 
    #e0e0e0 75%, #d4d4d4 100%
  );
  background-size: 4px 100%;
}

/* Leather */
.leather-surface {
  background-color: #6B4226;
  background-image: 
    url("data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' width='4' height='4'><rect fill='%235A3621' x='0' y='0' width='2' height='2'/><rect fill='%23794B2E' x='2' y='2' width='2' height='2'/></svg>");
}

/* Linen fabric */
.linen-surface {
  background: #f0ece4;
  background-image: 
    repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,0,0,0.03) 2px, rgba(0,0,0,0.03) 4px),
    repeating-linear-gradient(90deg, transparent, transparent 2px, rgba(0,0,0,0.03) 2px, rgba(0,0,0,0.03) 4px);
}
```

---

## 3. UI Components

### Buttons (Physical Press Effect)

```css
.skeu-btn {
  background: linear-gradient(180deg, #5A9FD4 0%, #2A75B8 45%, #1F5F99 100%);
  border: 1px solid #1A5080;
  border-radius: 8px;
  padding: 12px 28px;
  color: white;
  font-size: 14px;
  font-weight: 600;
  text-shadow: 0 -1px 1px rgba(0,0,0,0.3);
  box-shadow:
    0 1px 0 rgba(255,255,255,0.25) inset,
    0 -1px 0 rgba(0,0,0,0.2) inset,
    0 4px 8px rgba(0,0,0,0.3),
    0 1px 2px rgba(0,0,0,0.2);
  transition: all 0.08s;
}
.skeu-btn:hover {
  background: linear-gradient(180deg, #6BAADE 0%, #3585C8 45%, #2570A9 100%);
}
.skeu-btn:active {
  background: linear-gradient(180deg, #1F5F99 0%, #2A75B8 100%);
  box-shadow:
    0 1px 0 rgba(255,255,255,0.1) inset,
    0 2px 4px rgba(0,0,0,0.3) inset,
    0 1px 2px rgba(0,0,0,0.15);
  transform: translateY(1px);
}
```

### Toggle Switch (iOS-style)

```css
.skeu-toggle {
  width: 52px; height: 30px;
  background: linear-gradient(180deg, #c8c8c8, #e8e8e8);
  border-radius: 15px;
  border: 1px solid #aaa;
  box-shadow: inset 0 2px 5px rgba(0,0,0,0.25), 0 1px 0 rgba(255,255,255,0.8);
  position: relative;
  cursor: pointer;
}
.skeu-toggle.on {
  background: linear-gradient(180deg, #39b54a, #4dc35e);
  border-color: #2d9a3d;
}
.skeu-toggle-knob {
  width: 26px; height: 26px;
  background: radial-gradient(circle at 35% 35%, #fff, #d8d8d8);
  border-radius: 50%;
  box-shadow: 0 2px 5px rgba(0,0,0,0.35), 0 0 0 0.5px rgba(0,0,0,0.15);
  position: absolute;
  top: 2px; left: 2px;
  transition: left 0.2s ease;
}
.on .skeu-toggle-knob { left: 24px; }
```

### Knob / Dial Control

```css
.skeu-knob {
  width: 80px; height: 80px;
  border-radius: 50%;
  background: radial-gradient(circle at 35% 30%, #606060, #1a1a1a);
  box-shadow:
    0 4px 12px rgba(0,0,0,0.6),
    0 1px 0 rgba(255,255,255,0.15),
    inset 0 1px 2px rgba(255,255,255,0.1),
    inset 0 -2px 4px rgba(0,0,0,0.5);
  cursor: pointer;
}
```

### Cards (Notebook / App Panel)

```css
.skeu-card {
  background: #FFFEF7; /* paper white */
  border-radius: 4px;
  box-shadow:
    0 1px 3px rgba(0,0,0,0.12),
    0 8px 24px rgba(0,0,0,0.08),
    /* Bottom edge */
    0 1px 0 #ccc inset;
  border: 1px solid #D5D0C0;
  /* Ruled lines */
  background-image: repeating-linear-gradient(
    transparent, transparent 31px, #E8E4D8 31px, #E8E4D8 32px
  );
  background-attachment: local;
  padding: 16px 20px;
}
```

### Slider

```css
.skeu-slider {
  -webkit-appearance: none;
  height: 8px;
  background: linear-gradient(180deg, #a0a0a0, #d0d0d0);
  border-radius: 4px;
  border: 1px solid #888;
  box-shadow: inset 0 1px 3px rgba(0,0,0,0.4);
}
.skeu-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 24px; height: 24px;
  border-radius: 50%;
  background: radial-gradient(circle at 35% 30%, #e8e8e8, #a8a8a8);
  box-shadow: 0 2px 6px rgba(0,0,0,0.4);
  cursor: pointer;
}
```

---

## 4. Best Use Cases

- **Audio/music production tools** (DAWs, EQs)
- **Smart home control panels**
- **Luxury brand websites** (watches, hi-fi audio)
- **Calculator / clock apps** replicating physical devices
- **Financial dashboards** (Bloomberg-style gravitas)
- **Photography tools** (camera-inspired UI)
- **Gaming UIs** (inventory, equipment panels)
- **Premium hardware product pages**

---

## 5. Design Guidelines

### DO

- Research the physical object you're mimicking — accuracy matters
- Use multi-layer shadows (minimum 4 layers for believability)
- Add inset shadows for recessed elements
- Include subtle texture — metal grain, paper fiber
- Highlight must catch light from one consistent direction (top-left)
- Use `:active` states that physically press the element down

### DON'T

- Go so literal it becomes comedic (stitched leather everywhere)
- Mix flat and skeuomorphic elements inconsistently
- Forget the light source direction (inconsistent highlights = wrong)
- Make the texture so strong it becomes noise
- Use it for mobile-first interfaces with small targets
- Apply to fast-moving consumer interfaces (too slow to process)

### Common Mistakes

- **Inconsistent light source**: all highlights must come from same direction
- **No inset shadows**: depth without recession = not convincing
- **Single-layer shadow**: flat shadows kill the 3D illusion
- **Texture overdone**: texture should support, not dominate
- **Wrong scale**: physical metaphors break when too small

---

## 6. Implementation Tips

### Consistent Light Source System

```css
:root {
  /* All highlights come from top-left (10:30 position) */
  --light-highlight: rgba(255, 255, 255, 0.6);
  --light-shadow: rgba(0, 0, 0, 0.35);
  --ambient-shadow: rgba(0, 0, 0, 0.15);
  
  /* Raised element formula */
  --raised-shadow: 
    inset 0 1px 0 var(--light-highlight),
    inset -1px 0 0 rgba(255,255,255,0.2),
    0 2px 4px var(--ambient-shadow),
    0 4px 12px var(--light-shadow);
    
  /* Pressed/recessed formula */
  --pressed-shadow:
    inset 0 2px 6px var(--light-shadow),
    inset 0 1px 3px rgba(0,0,0,0.4),
    0 1px 0 var(--light-highlight);
}
```

### Metal Gradient Generator

```css
/* Brushed horizontal */
.brushed-h { background: repeating-linear-gradient(
  90deg, #d0d0d0 0px, #e4e4e4 1px, #d8d8d8 2px, #e0e0e0 4px); }

/* Polished radial */
.polished { background: radial-gradient(
  ellipse at 30% 30%, #f0f0f0, #c0c0c0 40%, #909090 100%); }
```

### Embossed Text

```css
.embossed-text {
  color: transparent;
  background-clip: text;
  -webkit-background-clip: text;
  background-image: linear-gradient(180deg, #888, #444);
  text-shadow: 0 1px 0 rgba(255,255,255,0.5), 0 -1px 0 rgba(0,0,0,0.3);
}
.debossed-text {
  color: rgba(0,0,0,0.5);
  text-shadow: 0 1px 0 rgba(255,255,255,0.6);
}
```

---

## 7. Example Layout: Audio Production Dashboard

```
[Deep dark background: #1A1A1A with subtle metal texture]
│
├── TOP BAR: Brushed aluminum strip, chrome lettering
│   └── Transport controls (▶ ⏹ ⏺) as physical buttons
│
├── MAIN PANEL
│   ├── Left sidebar: Leather-textured channel strip
│   │   └── Round knobs (volume, pan, EQ) — CSS radial gradients
│   │
│   ├── Center: Piano-roll / timeline area
│   │   └── Dark felt/velvet background texture
│   │   └── Tracks as raised metal strips
│   │
│   └── Right: Effects rack panel
│       └── Individual rack units with screws (visual detail)
│       └── LED meters (CSS gradient + animation)
│
└── BOTTOM: Transport strip
    └── Brushed aluminum, physical slider for timeline position
    └── BPM display (7-segment LED font: "Digital-7")
```

---

## 8. Advanced Enhancements

### Realistic Knob Rotation (JS)

```javascript
let isDragging = false, startY, startAngle;
knob.addEventListener('mousedown', (e) => {
  isDragging = true;
  startY = e.clientY;
  startAngle = currentAngle;
});
document.addEventListener('mousemove', (e) => {
  if (!isDragging) return;
  const delta = startY - e.clientY;
  currentAngle = Math.max(-135, Math.min(135, startAngle + delta));
  knob.style.transform = `rotate(${currentAngle}deg)`;
});
```

### LED/VU Meter Animation

```css
.vu-bar {
  background: linear-gradient(to top, 
    #00cc00 0%, #00cc00 70%, 
    #ffcc00 70%, #ffcc00 85%, 
    #ff3300 85%, #ff3300 100%);
  height: var(--level, 50%);
  transition: height 0.05s;
}
```

### Click Sound Feedback

```javascript
// Subtle click sound on button press (Web Audio API)
const ctx = new AudioContext();
function playClick() {
  const osc = ctx.createOscillator();
  const gain = ctx.createGain();
  osc.connect(gain); gain.connect(ctx.destination);
  osc.frequency.value = 800;
  gain.gain.setValueAtTime(0.1, ctx.currentTime);
  gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.05);
  osc.start(); osc.stop(ctx.currentTime + 0.05);
}
```