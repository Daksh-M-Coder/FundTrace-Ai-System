# SKILL: Dark Luxury UI Design

---

## 1. Core Concept

Dark Luxury UI is the digital equivalent of a Rolls Royce interior or a high-end fashion house. It's **opulence through restraint** — deep, rich dark backgrounds with gold/platinum accents, impeccable typography, and a sense of exclusivity. Not garish gold everywhere, but _considered_ application of premium materials. The philosophy: _whisper, don't shout_ — the luxury is felt through texture, proportion, and detail, not decoration. Think Dior.com, Cartier, or private banking interfaces.

---

## 2. Key Visual Elements

### Colors (The Gold Standard)

- **Background**: Near-black, warm: `#0D0B08`, `#111008`, `#1A1610`
- **Card surfaces**: `#1C1914`, `#221F19`, `#2A2620`
- **Gold accent**: `#C9A84C`, `#D4B483`, `#B8960A` — NEVER neon yellow
- **Platinum**: `#C5C5C5`, `#A8A8A8`
- **Text primary**: `#F5EDD8` (warm off-white), never pure white
- **Text muted**: `#7D7468`

### Gold Gradient (The Signature)

```css
.gold-gradient {
  background: linear-gradient(
    135deg, 
    #C9A84C 0%, 
    #F0D080 25%, 
    #C9A84C 50%, 
    #A87C28 75%, 
    #D4B060 100%
  );
}
.gold-text {
  background: linear-gradient(135deg, #C9A84C, #F0D080, #C9A84C);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
```

### Typography (THE HERO)

- **Display**: Cormorant Garamond, Bodoni Moda, Didot, Freight Display
- **Body**: Cormorant (light), Optima, Garamond
- **Captions/Labels**: Futura PT, Raleway (all-caps, widely tracked)
- **Size Drama**: 80–120px headlines vs. 12px UPPERCASE labels
- `letter-spacing: 0.15em` for all-caps labels
- Line-height: 1.05–1.15 for display, 1.7 for body

### Textures

- Very subtle fabric/grain texture overlay
- Gold foil SVG/CSS for special elements
- Dark leather texture for backgrounds (`background-image: url()`)
- Linen or paper for light panels

### Borders & Lines

- Thin gold hairlines: `border: 1px solid rgba(201, 168, 76, 0.3)`
- Decorative horizontal rules with gold fade
- Monogram/logo mark rendered in gold SVG

---

## 3. UI Components

### Buttons

```css
/* Primary: Gold fill */
.luxury-btn {
  background: linear-gradient(135deg, #C9A84C, #D4B060, #A87C28);
  color: #0D0B08;
  border: none;
  padding: 14px 40px;
  font-family: 'Raleway', sans-serif;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  border-radius: 0; /* sharp or very slight: 2px */
  box-shadow: 0 4px 20px rgba(201, 168, 76, 0.3);
  transition: all 0.3s;
}
.luxury-btn:hover {
  box-shadow: 0 6px 30px rgba(201, 168, 76, 0.5);
  transform: translateY(-1px);
}

/* Ghost: Gold border */
.luxury-btn-ghost {
  background: transparent;
  border: 1px solid rgba(201, 168, 76, 0.6);
  color: #C9A84C;
  padding: 13px 39px;
}
.luxury-btn-ghost:hover {
  border-color: #C9A84C;
  background: rgba(201, 168, 76, 0.05);
}
```

### Cards

```css
.luxury-card {
  background: #1C1914;
  border: 1px solid rgba(201, 168, 76, 0.15);
  border-radius: 2px;
  padding: 40px;
  position: relative;
}
/* Corner accent */
.luxury-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0;
  width: 40px; height: 1px;
  background: linear-gradient(90deg, #C9A84C, transparent);
}
.luxury-card::after {
  content: '';
  position: absolute;
  top: 0; left: 0;
  width: 1px; height: 40px;
  background: linear-gradient(180deg, #C9A84C, transparent);
}
```

### Navigation

```css
.luxury-nav {
  background: rgba(13, 11, 8, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(201, 168, 76, 0.12);
  padding: 24px 80px;
}
.luxury-nav a {
  font-family: 'Raleway', sans-serif;
  font-size: 10px;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: rgba(245, 237, 216, 0.7);
  text-decoration: none;
  transition: color 0.3s;
}
.luxury-nav a:hover { color: #C9A84C; }
```

### Dividers (Decorative)

```css
.luxury-divider {
  display: flex;
  align-items: center;
  gap: 20px;
  margin: 40px 0;
}
.luxury-divider::before,
.luxury-divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(201, 168, 76, 0.4), transparent);
}
/* Center ornament: ◆ or custom SVG monogram */
```

---

## 4. Best Use Cases

- **Luxury fashion brands** (jewelry, couture, watches)
- **Private banking / wealth management**
- **High-end real estate**
- **Luxury hotel & hospitality**
- **Fine dining / Michelin restaurants**
- **Premium membership / exclusive clubs**
- **Luxury automotive** (Rolls, Bentley type)
- **High-end beauty / fragrance**

---

## 5. Design Guidelines

### DO

- Typography IS the luxury — invest in beautiful typefaces
- Use gold sparingly: 10–15% of visible elements
- Every section needs generous whitespace (breathe)
- Photography: only editorial-quality, dark/moody
- All-caps with wide tracking for labels/CTAs
- Hairline borders (1px gold) as structural elements

### DON'T

- Use bright or neon colors (destroys luxury feel)
- Use rounded corners > 4px (rounds = casual)
- Add decorative elements without purpose
- Use stock photography (fatal to luxury perception)
- Make CTAs urgent or pushy ("BUY NOW!", "LIMITED!!!")
- Use sans-serif as the primary display typeface

### Common Mistakes

- **Wrong gold**: Neon yellow or bronze ≠ luxury gold
- **Too much gold**: saturation kills exclusivity
- **Wrong typeface**: Helvetica/Inter = corporate, not luxury
- **Pure black/white**: slightly warm dark + warm off-white = luxury
- **No texture**: flat dark surfaces look cheap — subtle grain is essential

---

## 6. Implementation Tips

### CSS Variables

```css
:root {
  --luxury-bg: #0D0B08;
  --luxury-surface: #1C1914;
  --luxury-surface-2: #221F19;
  --luxury-gold: #C9A84C;
  --luxury-gold-light: #D4B483;
  --luxury-gold-dark: #8B6B1F;
  --luxury-gold-glow: rgba(201, 168, 76, 0.3);
  --luxury-text: #F5EDD8;
  --luxury-text-muted: #7D7468;
  --luxury-border: rgba(201, 168, 76, 0.2);
  --font-display: 'Cormorant Garamond', serif;
  --font-label: 'Raleway', sans-serif;
  --font-body: 'Cormorant', serif;
}
```

### Shimmer Effect (Gold Sheen)

```css
@keyframes goldShimmer {
  0% { background-position: -200% center; }
  100% { background-position: 200% center; }
}
.gold-shimmer {
  background: linear-gradient(
    90deg, 
    #C9A84C 0%, #F0D080 30%, #C9A84C 50%, #A87C28 70%, #C9A84C 100%
  );
  background-size: 300% auto;
  animation: goldShimmer 4s ease-in-out infinite;
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
```

### Page Load Luxury Transition

```css
.luxury-reveal {
  opacity: 0;
  transform: translateY(16px);
  transition: opacity 1.2s ease, transform 1.2s ease;
}
.luxury-reveal.visible {
  opacity: 1;
  transform: none;
}
/* Stagger: delay 0s, 0.2s, 0.4s, 0.6s for sequential elements */
```

---

## 7. Example Layout: Luxury Watch Brand Homepage

```
[#0D0B08 background, subtle linen grain overlay]
│
├── TOP BAR: 1px gold border bottom
│   └── "Established 1884" RALLYE 10px text | Social icons (gold)
│
├── NAVBAR: Centered logo (gold wordmark SVG)
│   └── Left: Collection About Craft
│   └── Right: Boutique Reserve
│   └── All: uppercase, 10px, 0.18em tracking
│
├── HERO: Full-viewport, 60/40 split
│   ├── Left: 
│   │   ├── "2025" (10px, tracking, gold)
│   │   ├── Headline: "TIME IS" / "MASTERCRAFT" (80px Cormorant Garamond Italic)
│   │   ├── Thin gold rule (120px wide)
│   │   ├── Body: 2 lines, 16px, warm off-white, 60% opacity
│   │   └── Two buttons: gold fill + ghost
│   └── Right: Watch photography on dark surface, slight glow
│
├── MARQUEE: "◆ NEW COLLECTION ◆ FALL 2025 ◆ HANDCRAFTED ◆"
│   └── Gold text on #0D0B08, 1px gold borders top/bottom
│
├── COLLECTION GRID: 3-col, edge-to-edge images
│   └── Hover: gold overlay with text
│
└── PHILOSOPHY: Dark panel, centered, editorial
    └── Single pull quote, 48px italic serif, gold
```

---

## 8. Advanced Enhancements

### Parallax Image Depth

```javascript
window.addEventListener('scroll', () => {
  const scrolled = window.pageYOffset;
  heroImage.style.transform = `translateY(${scrolled * 0.3}px)`;
});
```

### Cursor: Custom Gold Ring

```css
* { cursor: none; }
.luxury-cursor {
  width: 32px; height: 32px;
  border: 1px solid rgba(201, 168, 76, 0.7);
  border-radius: 50%;
  position: fixed;
  pointer-events: none;
  transition: transform 0.1s, width 0.3s, height 0.3s;
  z-index: 99999;
}
/* On hover over links: fills with gold, shrinks to 12px */
```

### Collection Image Hover

```css
.collection-item { overflow: hidden; position: relative; }
.collection-item img {
  transition: transform 1.2s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}
.collection-item:hover img { transform: scale(1.08); }
.collection-item-overlay {
  position: absolute; inset: 0;
  background: rgba(13, 11, 8, 0.7);
  opacity: 0;
  transition: opacity 0.5s;
  display: flex; align-items: center; justify-content: center;
}
.collection-item:hover .collection-item-overlay { opacity: 1; }
```