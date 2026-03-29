# SKILL: Aurora UI Design

---

## 1. Core Concept

Aurora UI is an emerging design language inspired by the **Northern Lights** — shimmering, shifting gradients of vivid color that bleed and blend across dark, deep backgrounds. It's the evolution of dark-mode design: not just dark, but _cosmically alive_. Unlike glassmorphism (which uses blur/transparency), Aurora UI is defined by **luminous gradient meshes**, glowing halo effects, and iridescent color transitions. The philosophy: _the interface breathes with light_ — every element radiates color onto its surroundings.

---

## 2. Key Visual Elements

### Colors

- **Background**: Deep dark — `#050510`, `#0A0015`, `#020818`
- **Primary aurora**: Electric blue (#00C2FF), violet (#8B00FF), teal (#00FFD1)
- **Secondary**: Hot pink (#FF006E), amber (#FF9500), lime (#00FF85)
- **Text**: Pure white (`#FFFFFF`) and very light muted (`rgba(255,255,255,0.6)`)
- Gradient meshes: colors bleed into each other naturally, not hard stops

### The Aurora Gradient System

```css
/* Background aurora mesh */
.aurora-bg {
  background: #050510;
  position: relative;
  overflow: hidden;
}
/* Aurora glow layers */
.aurora-bg::before {
  content: '';
  position: absolute;
  top: -20%; left: -10%;
  width: 70%; height: 70%;
  background: radial-gradient(ellipse, rgba(0, 194, 255, 0.15), transparent 70%);
  filter: blur(60px);
  animation: auroraShift 12s ease-in-out infinite;
}
.aurora-bg::after {
  content: '';
  position: absolute;
  bottom: -20%; right: -10%;
  width: 60%; height: 60%;
  background: radial-gradient(ellipse, rgba(139, 0, 255, 0.2), transparent 70%);
  filter: blur(80px);
  animation: auroraShift 16s ease-in-out infinite reverse;
}
@keyframes auroraShift {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(40px, -30px) scale(1.1); }
  66% { transform: translate(-20px, 20px) scale(0.9); }
}
```

### Glowing Elements

```css
/* Text glow */
.aurora-glow-text {
  color: #00C2FF;
  text-shadow: 0 0 20px rgba(0, 194, 255, 0.6), 0 0 60px rgba(0, 194, 255, 0.3);
}

/* Button/element glow */
.aurora-glow {
  box-shadow: 
    0 0 20px rgba(0, 194, 255, 0.4),
    0 0 60px rgba(0, 194, 255, 0.2),
    0 4px 20px rgba(0,0,0,0.4);
}
```

### Typography

- Geometric, futuristic: Orbitron, Oxanium, Exo 2, DM Mono
- Or ultra-clean modern: Neue Machina, ClashDisplay
- Light weight for body (300–400), bold for headings
- Gradient text using `background-clip: text`

### Textures

- Very subtle noise grain at 3–4% over backgrounds
- Star field: scattered tiny dots (`rgba(255,255,255,0.3)`)
- Grid lines: `rgba(255,255,255,0.04)` fine mesh

---

## 3. UI Components

### Buttons

```css
.aurora-btn {
  background: linear-gradient(135deg, #00C2FF, #8B00FF);
  border: none;
  border-radius: 50px;
  padding: 14px 32px;
  color: white;
  font-weight: 700;
  font-size: 14px;
  letter-spacing: 0.03em;
  box-shadow: 
    0 0 20px rgba(0, 194, 255, 0.4),
    0 0 60px rgba(139, 0, 255, 0.2),
    0 4px 20px rgba(0,0,0,0.3);
  transition: all 0.3s;
}
.aurora-btn:hover {
  box-shadow:
    0 0 30px rgba(0, 194, 255, 0.6),
    0 0 80px rgba(139, 0, 255, 0.3),
    0 6px 25px rgba(0,0,0,0.4);
  transform: translateY(-2px) scale(1.02);
}
/* Ghost variant */
.aurora-btn-ghost {
  background: transparent;
  border: 1px solid rgba(0, 194, 255, 0.5);
  color: #00C2FF;
  box-shadow: 0 0 10px rgba(0, 194, 255, 0.2), inset 0 0 10px rgba(0, 194, 255, 0.05);
}
```

### Cards

```css
.aurora-card {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 28px;
  position: relative;
  overflow: hidden;
  backdrop-filter: blur(10px);
}
/* Corner glow */
.aurora-card::before {
  content: '';
  position: absolute;
  top: -50%; left: -50%;
  width: 100%; height: 100%;
  background: radial-gradient(circle, rgba(0, 194, 255, 0.06), transparent 60%);
  pointer-events: none;
}
```

### Navbar

```css
.aurora-nav {
  background: rgba(5, 5, 16, 0.8);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255,255,255,0.06);
  padding: 18px 60px;
}
/* Logo: gradient text */
.aurora-logo {
  background: linear-gradient(90deg, #00C2FF, #8B00FF);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-weight: 800;
}
```

### Data Visualization

- Line charts: glowing colored lines with area fill fading to transparent
- Bar charts: gradient fills with glow
- Donut/ring charts: gradient stroke + glow

---

## 4. Best Use Cases

- **AI / ML product landing pages** (most popular)
- **Cybersecurity platforms**
- **Crypto / Web3 / DeFi apps**
- **Game launchers and gaming platforms**
- **Space/astronomy apps and visualizations**
- **Futuristic SaaS dashboards**
- **Music/DJ apps**
- **Developer tool portfolios**

---

## 5. Design Guidelines

### DO

- Always use deep dark backgrounds — aurora glow disappears on light
- Animate the aurora background (8–16 second loops, subtle)
- Use gradient text for headings and brand elements
- Glow effects should match the element's gradient colors
- Layer multiple colored glows at different intensities
- Grain texture at 3–4% for depth

### DON'T

- Use on light/white backgrounds
- Overuse glow (every glowing element = nothing stands out)
- Mix too many aurora colors (max 3 in active use)
- Use warm color palettes (orange/red dominant breaks the aurora feel)
- Make text too glowy — readability suffers above 0.5 opacity glow

### Common Mistakes

- **Static background**: Aurora must animate — static = generic dark gradient
- **Too much glow everywhere**: kills the hierarchy
- **Wrong font**: system fonts break the futuristic mood
- **Ignoring grain**: flat dark backgrounds look cheap — grain adds depth
- **No contrast variation**: all elements same brightness = no depth

---

## 6. Implementation Tips

### Gradient Text

```css
.aurora-gradient-text {
  background: linear-gradient(135deg, #00C2FF 0%, #8B00FF 50%, #FF006E 100%);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-size: 200% auto;
  animation: gradientFlow 4s ease-in-out infinite;
}
@keyframes gradientFlow {
  0%, 100% { background-position: 0% center; }
  50% { background-position: 100% center; }
}
```

### Noise Grain Overlay

```css
.grain::after {
  content: '';
  position: fixed;
  inset: 0;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.04'/%3E%3C/svg%3E");
  pointer-events: none;
  z-index: 9999;
  opacity: 0.4;
}
```

### Star Field

```javascript
const canvas = document.getElementById('stars');
const ctx = canvas.getContext('2d');
for (let i = 0; i < 200; i++) {
  ctx.beginPath();
  ctx.arc(Math.random() * W, Math.random() * H, Math.random() * 1.5, 0, Math.PI * 2);
  ctx.fillStyle = `rgba(255,255,255,${Math.random() * 0.4 + 0.1})`;
  ctx.fill();
}
```

### Tailwind Aurora

```html
<div class="bg-[#050510] min-h-screen relative overflow-hidden">
  <!-- Aurora orbs -->
  <div class="absolute top-0 left-0 w-[600px] h-[600px] 
              bg-[radial-gradient(ellipse,rgba(0,194,255,0.15),transparent_70%)] 
              blur-[80px] animate-pulse"></div>
  <!-- Content -->
  <div class="relative z-10 bg-white/[0.04] border border-white/10 
              rounded-2xl backdrop-blur-xl p-7">
```

---

## 7. Example Layout: AI SaaS Homepage

```
[Deep dark #050510 with animated aurora orbs + grain]
│
├── NAVBAR: Semi-transparent dark, backdrop-blur
│   └── Gradient logo | Links (white, muted) | "Try Free" glowing button
│
├── HERO
│   ├── Badge: "✦ Now in Beta" (border with cyan glow)
│   ├── Headline: 5-word gradient text, 100px
│   ├── Subline: white/60%, 20px, max-width 560px
│   ├── Two buttons: glowing primary + ghost
│   └── Hero visual: Dashboard mockup with glow behind it
│       (drop-shadow matching aurora colors)
│
├── LOGOS: "Trusted by" — white logos at 40% opacity
│
├── FEATURES: 3-col card grid
│   └── Each: subtle border, top corner glow, icon, text
│   └── One featured card: stronger glow border
│
├── CODE BLOCK DEMO: Syntax highlighted, aurora theme
│   └── Animated typing effect
│
└── CTA: Full-width section
    └── Gradient divider lines + big headline + button
    └── Large aurora orb behind the section
```

---

## 8. Advanced Enhancements

### Animated Gradient Border

```css
@keyframes borderRotate {
  from { --angle: 0deg; }
  to { --angle: 360deg; }
}
@property --angle {
  syntax: '<angle>';
  initial-value: 0deg;
  inherits: false;
}
.aurora-border {
  border: 2px solid transparent;
  background: linear-gradient(#050510, #050510) padding-box,
              conic-gradient(from var(--angle), #00C2FF, #8B00FF, #FF006E, #00C2FF) border-box;
  animation: borderRotate 4s linear infinite;
}
```

### Cursor Beam Effect

```javascript
document.addEventListener('mousemove', (e) => {
  beam.style.left = e.clientX + 'px';
  beam.style.top = e.clientY + 'px';
});
```

```css
.cursor-beam {
  position: fixed;
  width: 400px; height: 400px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(0, 194, 255, 0.06), transparent 70%);
  transform: translate(-50%, -50%);
  pointer-events: none;
  mix-blend-mode: screen;
}
```

### Particle Field

- Use `tsparticles` or `particles.js`
- Config: small white dots, slow movement, connect lines on proximity
- Color: match aurora palette