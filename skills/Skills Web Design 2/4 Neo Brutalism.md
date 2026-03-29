# SKILL: Neo Brutalism UI Design

---

## 1. Core Concept

Neo Brutalism (or "Neobrutalism") is a contemporary reaction to the over-polished, glassmorphic internet. It takes raw architectural brutalism — exposed structure, unapologetic heaviness — and injects it with **loud color, bold typography, and visible construction**. The hallmarks are thick black borders, hard offset box shadows (no blur), flat color fills, and massive type. The philosophy is _anti-beautiful on purpose_: deliberately raw, intentionally unconventional, and rebelliously distinct. It says "I don't need to be pretty to be powerful."

---

## 2. Key Visual Elements

### Colors

- **Electric primary**: Neon yellow (#FFE600), hot green (#00FF85), electric blue (#0066FF), vivid coral (#FF3C00)
- **Strict black** (#000000) for all borders and shadows — no softening
- **White** (#FFFFFF) as default background
- **Contrasting fills**: solid colors, NO gradients
- Typical combos: Yellow + Black | Green + Black | Purple + Yellow | Orange + Black

### The Signature Shadow

```css
/* THE defining neo-brutalism technique */
.neo-shadow {
  box-shadow: 4px 4px 0px #000000; /* or 6px, 8px — always hard, never blurred */
  border: 2px solid #000000;
}
/* On hover: shift the element to "press" into the shadow */
.neo-shadow:hover {
  box-shadow: 2px 2px 0px #000000;
  transform: translate(2px, 2px);
}
.neo-shadow:active {
  box-shadow: 0px 0px 0px #000000;
  transform: translate(4px, 4px);
}
```

### Typography

- **Heavy weights**: Black (900), Extra-Bold (800) — always
- Display fonts: Space Grotesk Bold, DM Sans Black, Syne ExtraBold, Bricolage Grotesque
- Mono fonts for code/labels: JetBrains Mono, Space Mono
- ALL CAPS for buttons and labels
- Oversized headlines: 80–140px
- Tight letter-spacing: `-0.03em` to `-0.05em`
- Mixed sizes for drama: giant numbers, small labels

### Borders

- Always `2px solid #000` minimum
- Use `outline: 2px solid #000` for layered border effects
- Decorative: `border: 3px dashed #000` for tags/badges

### Textures

- Subtle dot grid or line pattern backgrounds
- Paper texture at 4–6% opacity
- Grid lines as page structure
- NO gradients, NO blurs

---

## 3. UI Components

### Buttons (The Pressable Block)

```css
.neo-btn {
  background: #FFE600;
  color: #000;
  border: 2px solid #000;
  border-radius: 0; /* HARD corners — no radius */
  padding: 14px 28px;
  font-weight: 900;
  font-size: 14px;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  box-shadow: 4px 4px 0px #000;
  cursor: pointer;
  transition: all 0.1s ease;
  position: relative;
}
.neo-btn:hover {
  transform: translate(2px, 2px);
  box-shadow: 2px 2px 0px #000;
}
.neo-btn:active {
  transform: translate(4px, 4px);
  box-shadow: 0px 0px 0px #000;
}
```

### Cards

```css
.neo-card {
  background: #fff;
  border: 2px solid #000;
  border-radius: 0;
  padding: 28px;
  box-shadow: 6px 6px 0 #000;
  position: relative;
}
/* Accent top-bar variant */
.neo-card-accent::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0; height: 6px;
  background: #FFE600;
}
```

### Navbar

```css
nav {
  background: #FFE600;
  border-bottom: 3px solid #000;
  padding: 0 48px;
  height: 72px;
  display: flex; align-items: center;
  justify-content: space-between;
}
/* Nav links: bold, uppercase, hover = underline with offset */
nav a {
  font-weight: 800;
  text-transform: uppercase;
  font-size: 13px;
  text-decoration: none;
  color: #000;
  position: relative;
}
nav a::after {
  content: '';
  position: absolute;
  bottom: -4px; left: 0; right: 0; height: 3px;
  background: #000;
  transform: scaleX(0);
  transition: transform 0.15s;
}
nav a:hover::after { transform: scaleX(1); }
```

### Forms / Inputs

```css
.neo-input {
  border: 2px solid #000;
  border-radius: 0;
  padding: 12px 16px;
  font-size: 15px;
  font-weight: 600;
  background: #fff;
  box-shadow: 3px 3px 0 #000;
  outline: none;
  transition: all 0.1s;
}
.neo-input:focus {
  box-shadow: 5px 5px 0 #000;
  transform: translate(-1px, -1px);
}
```

### Tags / Badges

```css
.neo-tag {
  display: inline-block;
  background: #00FF85;
  border: 2px solid #000;
  padding: 4px 12px;
  font-weight: 800;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}
```

---

## 4. Best Use Cases

- **Startup landing pages** (especially tech, SaaS)
- **Creative agency portfolios**
- **Fashion / streetwear brands**
- **Music / entertainment platforms**
- **News / media sites** (editorial brutalism)
- **Developer tools** (code editors, CLI tools)
- **Gaming / esports platforms**
- **NFT / Web3** projects

---

## 5. Design Guidelines

### DO

- Use `box-shadow: Xpx Xpx 0 #000` — the hard shadow is THE signature
- Keep border-radius at 0 or maximum 4px
- Go LOUD with color — timid color kills neobrutalism
- Make typography as large as possible in the hero
- Include visible structure: grids, lines, borders as design elements
- Use the "press" interaction (translate on :active)

### DON'T

- Add blur or gradient to shadows (turns into regular design)
- Use soft/rounded corners (breaks the brutalist identity)
- Use pastel or muted colors as primary fills
- Use thin fonts (300, 400 weight) for headings
- Over-polish: imperfection is intentional
- Use more than 2–3 colors (will become chaotic)

### Common Mistakes

- **Shadow without border**: the border is what frames the offset shadow
- **Wrong shadow direction**: should be consistent (bottom-right typically)
- **Too much color variation**: pick 1–2 accent colors max
- **Normal hover states**: hover should physically shift the element
- **Round corners**: even 8px border-radius = not neobrutalist

---

## 6. Implementation Tips

### CSS Custom Properties

```css
:root {
  --neo-border: 2px solid #000000;
  --neo-border-thick: 3px solid #000000;
  --neo-shadow-sm: 3px 3px 0 #000000;
  --neo-shadow-md: 5px 5px 0 #000000;
  --neo-shadow-lg: 8px 8px 0 #000000;
  --neo-yellow: #FFE600;
  --neo-green: #00FF85;
  --neo-blue: #0066FF;
  --neo-coral: #FF3C00;
  --font-display: 'Syne', sans-serif;
  --font-body: 'Space Grotesk', sans-serif;
  --font-mono: 'Space Mono', monospace;
}
```

### Tailwind Neobrutalism Classes

```html
<!-- Button -->
<button class="bg-yellow-300 border-2 border-black px-6 py-3 font-black uppercase
               shadow-[4px_4px_0px_#000] hover:shadow-[2px_2px_0px_#000] 
               hover:translate-x-[2px] hover:translate-y-[2px]
               active:shadow-none active:translate-x-[4px] active:translate-y-[4px]
               transition-all duration-100">
  Get Started
</button>

<!-- Card -->
<div class="bg-white border-2 border-black p-7 shadow-[6px_6px_0_#000]">
```

### Dot Grid Background

```css
.neo-bg {
  background-color: #fff;
  background-image: radial-gradient(circle, #000 1px, transparent 1px);
  background-size: 24px 24px;
}
```

### Marquee Text Banner

```css
.neo-marquee {
  background: #FFE600;
  border-top: 2px solid #000;
  border-bottom: 2px solid #000;
  padding: 12px 0;
  overflow: hidden;
  white-space: nowrap;
}
.neo-marquee-inner {
  display: inline-block;
  animation: marquee 20s linear infinite;
  font-weight: 900;
  font-size: 18px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
@keyframes marquee {
  from { transform: translateX(0); }
  to { transform: translateX(-50%); }
}
```

---

## 7. Example Layout: SaaS Startup Homepage

```
[White background with subtle dot-grid texture]
│
├── TOP BANNER: Yellow marquee strip — "★ NEW LAUNCH ★ FREE TRIAL ★ BUILD FASTER ★"
│
├── NAVBAR: Yellow bg, 3px bottom border
│   └── Bold wordmark | Links (uppercase bold) | "Sign Up Free" (black button)
│
├── HERO SECTION
│   ├── Giant badge: [■ LAUNCH DAY] (green bg, border)
│   ├── Headline: "BUILD STUFF"
│   │   "THAT WORKS." (120px, black, tight tracking)
│   ├── Subtext: 18px regular, max-width 480px
│   ├── Two buttons: Yellow primary + Ghost secondary
│   └── Right: Browser mockup with neo-brutal border + shadow
│
├── LOGOS STRIP: "Used by teams at —" + text logos (no image logos)
│
├── FEATURES: 3-column card grid
│   └── Number (#01, #02, #03) + bold title + text
│   Each card: border, hard shadow, accent top stripe in different colors
│
├── PRICING: 3 pricing cards
│   └── Middle card: Yellow background (standout), border, big shadow
│
└── FOOTER: Yellow background, 3px top border
    └── Big wordmark + nav links + social (text only)
```

---

## 8. Advanced Enhancements

### Text Scramble Effect

```javascript
const chars = "!<>-_\\/[]{}—=+*^?#";
// On hover, randomize letters then resolve to correct text
```

### Elastic Hover Effect

```css
.neo-elastic {
  transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1),
              box-shadow 0.1s linear;
}
```

### Glitch Effect for Hero Text

```css
@keyframes glitch {
  0%, 100% { text-shadow: none; }
  20% { text-shadow: -3px 0 #FF3C00, 3px 0 #0066FF; }
  40% { text-shadow: 3px 0 #FF3C00, -3px 0 #0066FF; }
  60% { text-shadow: none; }
}
```

### Counter Animations

- Large animated number counters (0 → 10,000 users)
- Monospace font, runs on scroll into view
- Pairs well with neo-brutal stat cards