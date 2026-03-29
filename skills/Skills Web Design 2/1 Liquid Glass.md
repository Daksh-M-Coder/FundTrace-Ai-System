# SKILL: Liquid Glass UI Design

---

## 1. Core Concept

Liquid Glass is Apple's newest design language introduced in iOS 26 / macOS Tahoe (2025). It extends glassmorphism by adding **fluid, refractive, lens-like properties** to UI surfaces — as if the interface is made of actual curved glass that bends and distorts the world behind it. Unlike flat glassmorphism (which is just frosted), Liquid Glass surfaces **refract light, distort backgrounds, and feel physically thick and dimensional**. The philosophy is: _the UI should feel like touching water frozen in time_.

---

## 2. Key Visual Elements

### Colors

- **No solid backgrounds** — all panels are translucent with refraction
- Tints derived from underlying content (dynamic color extraction)
- White/light chrome edges on glass surfaces
- Subtle iridescence: thin-film rainbow shimmer at edges
- Dark mode: deep navy/obsidian base with liquid highlights

### Textures & Effects

- **Backdrop blur**: 20–40px, but with additional `backdrop-brightness` and `backdrop-saturate`
- **Refraction distortion**: SVG feTurbulence + feDisplacementMap, or canvas-based lens warp
- **Specular highlight**: a bright curved streak across the top of each panel
- **Edge glow**: 0.5–1px inner border with `rgba(255,255,255,0.6)`
- **Caustic light patterns**: animated light ripples on hover

### Shadows & Depth

- `box-shadow: 0 8px 32px rgba(0,0,0,0.12), 0 2px 8px rgba(0,0,0,0.08), inset 0 1px 0 rgba(255,255,255,0.5)`
- Multi-layer shadows for "thickness" illusion
- Drop shadows that interact with the background

### Typography

- SF Pro / system-ui (Apple-native), or Geist, Neue Haas
- Light weights (300–400) for body, Medium for labels
- White text on glass, with `text-shadow: 0 1px 2px rgba(0,0,0,0.15)`
- **NO dark text on glass** — breaks the illusion

### Spacing

- Generous padding (24–32px inside cards)
- Rounded corners: 20–28px radius (pill-like for small elements)
- Breathing room — never pack elements tightly

---

## 3. UI Components

### Buttons

```css
.liquid-btn {
  background: rgba(255, 255, 255, 0.18);
  backdrop-filter: blur(20px) saturate(1.8) brightness(1.1);
  border: 1px solid rgba(255, 255, 255, 0.55);
  border-radius: 50px;
  box-shadow: 
    0 4px 16px rgba(0,0,0,0.12),
    inset 0 1px 0 rgba(255,255,255,0.6),
    inset 0 -1px 0 rgba(255,255,255,0.1);
  color: white;
  font-weight: 500;
  padding: 12px 28px;
  position: relative;
  overflow: hidden;
}
/* Specular streak */
.liquid-btn::before {
  content: '';
  position: absolute;
  top: 0; left: 10%; right: 10%;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.8), transparent);
}
```

### Cards

- Frosted glass + refraction filter overlay
- Top specular line (1–2px curved highlight)
- Content inside should have its own text hierarchy
- On hover: subtle scale(1.02) + increased blur intensity

### Navbar

- Floating pill-shaped bar, NOT full-width
- Heavy blur, thin white border, slight shadow
- Active items get a brighter, more opaque indicator

### Modals

- Sheet-style (slides up from bottom on mobile)
- Strong background blur (40px+) + dim overlay
- Thick glass look: multiple inset shadows

### Forms / Inputs

```css
.liquid-input {
  background: rgba(255,255,255,0.1);
  border: 1px solid rgba(255,255,255,0.3);
  backdrop-filter: blur(10px);
  border-radius: 14px;
  color: white;
  padding: 14px 18px;
}
.liquid-input:focus {
  border-color: rgba(255,255,255,0.7);
  box-shadow: 0 0 0 3px rgba(255,255,255,0.15);
}
```

---

## 4. Best Use Cases

- **Music / media players** (Apple Music-style)
- **iOS/macOS-like web apps**
- **Weather, clock, ambient dashboards**
- **Luxury SaaS products** (premium, high-end feel)
- **Personal portfolios** for designers/creatives
- **AR/VR interfaces** (spatial computing UIs)
- **Financial apps** wanting a premium feel

---

## 5. Design Guidelines

### DO

- Always have a rich, colorful, moving background — glass needs something to refract
- Use CSS `backdrop-filter` as base, enhance with canvas/SVG for refraction
- Add specular highlights (that bright curved streak on glass)
- Keep text white or very light
- Use generous border-radius (20px+)
- Animate backgrounds slowly (3–8 second loops)

### DON'T

- Use on white/flat backgrounds — glass over nothing = invisible
- Make glass panels too opaque (>50% kills the effect)
- Use heavy dark text on glass (destroys illusion)
- Apply to tiny UI elements (icons, tags) — waste at small scale
- Skimp on the background — it's 50% of the design

### Common Mistakes

- Forgetting `backdrop-filter` browser support (use `@supports`)
- No specular highlight = flat fake glass
- Blur without saturation boost = muddy, grey look
- Same blur value everywhere = boring depth
- Ignoring performance: `backdrop-filter` is GPU-expensive, limit layers

---

## 6. Implementation Tips

### CSS Foundation

```css
:root {
  --glass-bg: rgba(255, 255, 255, 0.12);
  --glass-border: rgba(255, 255, 255, 0.45);
  --glass-blur: blur(24px) saturate(1.8) brightness(1.05);
  --glass-shadow: 0 8px 32px rgba(0,0,0,0.15), inset 0 1px 0 rgba(255,255,255,0.5);
  --glass-radius: 24px;
}

.glass-surface {
  background: var(--glass-bg);
  backdrop-filter: var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
  border: 1px solid var(--glass-border);
  border-radius: var(--glass-radius);
  box-shadow: var(--glass-shadow);
}
```

### Animated Background (Required)

```css
.liquid-bg {
  background: linear-gradient(135deg, #667eea, #764ba2, #f093fb, #0093E9);
  background-size: 400% 400%;
  animation: liquidShift 8s ease infinite;
}
@keyframes liquidShift {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}
```

### Refraction Effect (SVG Filter)

```html
<svg style="position:absolute;width:0;height:0">
  <defs>
    <filter id="liquid-refract">
      <feTurbulence type="fractalNoise" baseFrequency="0.015" numOctaves="3" result="noise"/>
      <feDisplacementMap in="SourceGraphic" in2="noise" scale="8" xChannelSelector="R" yChannelSelector="G"/>
    </filter>
  </defs>
</svg>
```

### Tailwind Equivalent

```html
<div class="bg-white/10 backdrop-blur-2xl backdrop-saturate-200 
            border border-white/40 rounded-3xl 
            shadow-[0_8px_32px_rgba(0,0,0,0.15),inset_0_1px_0_rgba(255,255,255,0.5)]">
```

### Performance Tip

- Limit `backdrop-filter` elements to 3–5 visible at once
- Use `will-change: transform` on animated glass panels
- Consider `filter: blur()` on a cloned background instead for older browsers

---

## 7. Example Layout: Music Player Homepage

```
[Animated gradient blob background — blues, purples, pinks]
│
├── NAVBAR: Floating glass pill, centered, 60% width
│   └── Logo | Links | CTA Button (glass pill)
│
├── HERO SECTION
│   ├── Left: Glass card — "Now Playing" widget
│   │   ├── Album art (rounded square, casts color glow)
│   │   ├── Track info (white text)
│   │   ├── Progress bar (glass track, white fill)
│   │   └── Controls (glass circular buttons)
│   └── Right: 3 stacked glass feature cards (offset/layered)
│
├── FEATURES: 3-column glass cards grid
│   └── Icon + Heading + Description each
│
└── CTA SECTION
    └── Large glass panel, gradient text headline, two glass buttons
```

---

## 8. Advanced Enhancements

### Hover Ripple Effect

```javascript
element.addEventListener('mousemove', (e) => {
  const rect = element.getBoundingClientRect();
  const x = ((e.clientX - rect.left) / rect.width) * 100;
  const y = ((e.clientY - rect.top) / rect.height) * 100;
  element.style.background = 
    `radial-gradient(circle at ${x}% ${y}%, rgba(255,255,255,0.2), rgba(255,255,255,0.08))`;
});
```

### Liquid Morph Animation

```css
@keyframes liquidMorph {
  0% { border-radius: 24px; }
  50% { border-radius: 40px 20px 35px 15px; }
  100% { border-radius: 24px; }
}
```

### Parallax Glass Layers

- Layer multiple glass panels at different depths
- Move each at different speeds on scroll (`translateY` at 0.1x, 0.3x, 0.5x)
- Creates immersive 3D depth effect

### Cursor Glow

```javascript
document.addEventListener('mousemove', (e) => {
  const glow = document.querySelector('.cursor-glow');
  glow.style.left = e.clientX - 150 + 'px';
  glow.style.top = e.clientY - 150 + 'px';
});
```

```css
.cursor-glow {
  position: fixed;
  width: 300px; height: 300px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(255,255,255,0.08), transparent 70%);
  pointer-events: none;
  mix-blend-mode: screen;
}
```