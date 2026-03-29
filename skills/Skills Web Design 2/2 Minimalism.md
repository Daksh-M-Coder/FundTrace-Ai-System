# SKILL: Minimalism UI Design

---

## 1. Core Concept

Minimalism is the philosophy that **every pixel must earn its place**. It's not emptiness — it's _intentional restraint_ that forces hierarchy, clarity, and purpose. The visual identity is defined by what's removed, not what's added. Inspired by Swiss International Style and Japanese Zen aesthetics, minimalist design communicates sophistication through negative space, strict typographic systems, and monochromatic or near-monochromatic palettes. The guiding principle: _if removing it doesn't break the design, remove it_.

---

## 2. Key Visual Elements

### Colors

- **Palette: 2–3 colors maximum**
- Primary: Off-white (#FAFAFA, #F5F5F0) — never pure white
- Text: Near-black (#111, #1A1A1A) — never pure black
- Accent: One strong color only (deep blue #0047FF, warm orange #FF4D00, or classic red #FF0000)
- Alternative: All black & white with one yellow or green pop

### Typography (THE HERO in minimalism)

- **One display font, one body font — max**
- Display: Editorial New, Playfair Display, Neue Haas Grotesk, GT Alpina
- Body: IBM Plex Mono, Söhne, Freight Text
- **Use size contrast dramatically**: 96px headline vs 14px body
- Letter-spacing: `0.02em` for body, `-0.02em` tight for large headings
- Line-height: 1.1–1.2 for headings, 1.6–1.8 for body

### Spacing

- **Generous margins**: minimum 80px sides on desktop
- Section padding: 120–160px vertical
- Component gaps: 8pt grid system strictly
- **White space IS the design** — don't fear emptiness

### Shadows & Depth

- Mostly flat — avoid shadows
- If used: `box-shadow: 0 1px 3px rgba(0,0,0,0.08)` only
- Borders preferred over shadows: `1px solid #E5E5E5`
- Hover states: color fill or underline, not shadow

### Textures

- None, or very subtle paper grain at 3–5% opacity
- No gradients (or very subtle: same hue 5% variation)
- Flat photography with consistent treatment (B&W or desaturated)

---

## 3. UI Components

### Buttons

```css
/* Primary — Fill */
.min-btn-primary {
  background: #111;
  color: #fff;
  border: none;
  border-radius: 0; /* or 4px max */
  padding: 14px 32px;
  font-size: 13px;
  font-weight: 500;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  transition: background 0.2s;
}
.min-btn-primary:hover { background: #333; }

/* Secondary — Ghost */
.min-btn-ghost {
  background: transparent;
  color: #111;
  border: 1px solid #111;
  padding: 13px 31px;
}
.min-btn-ghost:hover { background: #111; color: #fff; }
```

### Cards

- **No rounded corners** (or max 4px)
- No shadows — use thin border or nothing
- Content-first: image edge-to-edge, then text below
- Hover: subtle opacity change or underline on title

### Navbar

```css
nav {
  position: fixed;
  top: 0; width: 100%;
  padding: 24px 80px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(250,250,248,0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid #E5E5E5;
}
/* Links: no decoration, hover = underline only */
nav a { text-decoration: none; font-size: 13px; letter-spacing: 0.05em; }
nav a:hover { text-decoration: underline; }
```

### Forms

- Full-width inputs with bottom border only
- No box, no rounded corners on the input field

```css
.min-input {
  border: none;
  border-bottom: 1px solid #ccc;
  border-radius: 0;
  background: transparent;
  padding: 12px 0;
  width: 100%;
  font-size: 16px;
  outline: none;
}
.min-input:focus { border-bottom-color: #111; }
```

### Modals

- Full-screen takeover or slide-in panel
- White background, prominent close X
- Content centered with large typography

---

## 4. Best Use Cases

- **Architecture, interior design studios**
- **Luxury fashion brands** (Celine, Bottega Veneta type)
- **Photography portfolios**
- **Writing/editorial platforms**
- **High-end product landing pages**
- **Law firms, financial advisors** (trust-building)
- **Personal brand websites** for thought leaders

---

## 5. Design Guidelines

### DO

- Let typography do the heavy lifting
- Use high-quality, consistent photography
- Maintain strict 8pt spacing grid
- One accent color used sparingly and with purpose
- Horizontal rules (`<hr>`) as dividers instead of boxes
- Use ALL CAPS for labels/captions (with generous tracking)

### DON'T

- Add decorative elements "just to fill space"
- Use more than 2 fonts
- Add gradients or shadows unless absolutely necessary
- Use bright multi-color palettes
- Round corners more than 4–6px
- Animate things that don't need animating

### Common Mistakes

- **Boring minimalism**: removing decoration without adding hierarchy = bland
- **Wrong font choices**: using Inter/Roboto = generic, not minimal
- **Too tight spacing**: minimalism needs air — small margins kill it
- **No focal point**: everything equal = nothing important
- **Weak typography scale**: poor contrast between headline and body

---

## 6. Implementation Tips

### CSS Variables

```css
:root {
  --c-bg: #FAFAFA;
  --c-text: #111111;
  --c-muted: #888888;
  --c-border: #E0E0E0;
  --c-accent: #0047FF;
  --space-xs: 8px;
  --space-sm: 16px;
  --space-md: 32px;
  --space-lg: 64px;
  --space-xl: 120px;
  --font-display: 'Editorial New', serif;
  --font-body: 'IBM Plex Mono', monospace;
  --radius: 0px;
}
```

### Typography Scale

```css
.display { font-size: clamp(64px, 8vw, 120px); line-height: 1.0; letter-spacing: -0.02em; }
.heading { font-size: clamp(32px, 4vw, 56px); line-height: 1.1; }
.subhead { font-size: 18px; line-height: 1.6; color: var(--c-muted); }
.label { font-size: 11px; letter-spacing: 0.12em; text-transform: uppercase; }
.body { font-size: 16px; line-height: 1.75; }
```

### Tailwind Classes

```html
<!-- Card -->
<div class="border border-neutral-200 p-8 group cursor-pointer">
  <img class="w-full aspect-video object-cover mb-6 grayscale group-hover:grayscale-0 transition-all duration-500">
  <p class="text-xs uppercase tracking-widest text-neutral-400 mb-2">Category</p>
  <h3 class="text-2xl font-light tracking-tight group-hover:underline">Title</h3>
</div>
```

### Hover Animations

```css
/* Underline draw effect */
.min-link {
  position: relative;
  text-decoration: none;
}
.min-link::after {
  content: '';
  position: absolute;
  bottom: -2px; left: 0;
  width: 0; height: 1px;
  background: currentColor;
  transition: width 0.3s ease;
}
.min-link:hover::after { width: 100%; }
```

---

## 7. Example Layout: Architecture Studio Homepage

```
[Off-white background, #FAFAFA]
│
├── NAVBAR: Left logo (wordmark), right: About Work Contact
│   └── Thin 1px bottom border
│
├── HERO: Full-viewport
│   ├── Massive serif headline: "We Build"
│   │   "What Matters." (3 lines, 120px, tight tracking)
│   ├── Bottom-left: small body text (2 lines)
│   └── Bottom-right: scroll indicator (01 ↓)
│
├── FEATURED WORK: 2-column asymmetric grid
│   ├── Left: Large image (takes 60%) with project name below
│   └── Right: Two stacked smaller images (each 50% height)
│
├── ABOUT STRIP: Full-width, centered
│   └── Single sentence in 40px light serif + thin HR lines
│
├── SERVICES: 4-column, just text
│   └── Number + Title + Short description (no icons, no cards)
│
└── FOOTER: Two columns
    ├── Left: Address + Email
    └── Right: Social links (text only, no icons)
```

---

## 8. Advanced Enhancements

### Word-by-Word Headline Reveal

```javascript
const words = headline.textContent.split(' ');
headline.innerHTML = words.map((word, i) => 
  `<span style="display:inline-block; opacity:0; transform:translateY(20px); 
   transition: all 0.6s ${i * 0.1}s ease">${word}&nbsp;</span>`
).join('');
// On scroll into view, set opacity:1 translateY(0)
```

### Image Hover Zoom

```css
.project-img { overflow: hidden; }
.project-img img {
  transition: transform 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}
.project-img:hover img { transform: scale(1.05); }
```

### Cursor Customization

```css
* { cursor: none; }
.custom-cursor {
  position: fixed;
  width: 8px; height: 8px;
  background: #111;
  border-radius: 50%;
  pointer-events: none;
  transition: transform 0.1s;
}
/* On hover over links: expand to 40px, outline only */
```

### Page Transitions

- Fade + slight vertical translate: `opacity 0→1, translateY 20px→0`
- Duration: 400ms ease
- Trigger on route change or anchor click