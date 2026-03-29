# SKILL: Glassmorphism UI Design

---

## 1. Core Concept

Glassmorphism creates UI surfaces that simulate **frosted glass panels** — translucent, blurred, and layered on top of colorful backgrounds. Introduced by Apple in macOS Big Sur and popularized by Figma UI kits, it creates depth through transparency and blur rather than shadows. The philosophy is: _UI as atmosphere_ — elements feel like they're floating in a luminous, dreamy space. Unlike Liquid Glass (which refracts), Glassmorphism frosted diffuses. The key experience: soft, ethereal, modern.

---

## 2. Key Visual Elements

### Colors

- **Rich gradient backgrounds** (mandatory — glass over flat = invisible)
- Popular: Purple-blue (#7B2FF7 → #2FFFEE), Sunset (orange → pink → purple)
- Aurora: teal/green/purple combinations
- Dark mode: deep backgrounds (#0A0A1A) with vibrant blob colors
- Glass panels themselves: `rgba(255,255,255,0.08–0.20)` light / `rgba(255,255,255,0.05–0.12)` dark

### The Frosted Glass Formula

```css
.glass {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(16px) saturate(1.5);
  -webkit-backdrop-filter: blur(16px) saturate(1.5);
  border: 1px solid rgba(255, 255, 255, 0.25);
  border-radius: 16px;
}
```

### Background (Required for Glass to Work)

```css
.glass-bg {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
  position: relative;
  overflow: hidden;
}
/* Ambient color blobs */
.blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.7;
}
.blob-1 { width: 600px; height: 600px; background: #7B2FF7; top: -200px; left: -200px; }
.blob-2 { width: 400px; height: 400px; background: #2FFFEE; bottom: -100px; right: -100px; }
.blob-3 { width: 300px; height: 300px; background: #FF6B6B; top: 50%; left: 40%; }
```

### Typography

- Light, airy fonts: Inter, Outfit, DM Sans, Manrope
- White or very light text only
- Weight: 300–400 for body, 600–700 for headings
- No dark text — loses contrast on transparent surfaces

### Borders & Depth

- Top-left edge brighter: `border-top: 1px solid rgba(255,255,255,0.4)`
- Bottom-right darker: `border-bottom: 1px solid rgba(255,255,255,0.1)`
- Layered panels at different blur levels create depth

### Shadows

- Soft, diffused: `box-shadow: 0 8px 32px rgba(0,0,0,0.2)`
- Not hard shadows (that's neobrutalism territory)

---

## 3. UI Components

### Cards

```css
.glass-card {
  background: rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(16px) saturate(1.5);
  -webkit-backdrop-filter: blur(16px) saturate(1.5);
  border: 1px solid rgba(255, 255, 255, 0.20);
  border-radius: 20px;
  padding: 28px;
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.3);
}
```

### Buttons

```css
.glass-btn {
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.35);
  border-radius: 50px;
  padding: 12px 28px;
  color: white;
  font-weight: 600;
  transition: all 0.3s;
}
.glass-btn:hover {
  background: rgba(255, 255, 255, 0.30);
  box-shadow: 0 8px 20px rgba(0,0,0,0.2);
  transform: translateY(-2px);
}
/* Solid accent button (for primary CTA) */
.glass-btn-solid {
  background: rgba(255, 255, 255, 0.95);
  color: #6B21A8;
  border: none;
}
```

### Navbar

```css
.glass-nav {
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.12);
  padding: 16px 48px;
  color: white;
}
```

### Dashboard Panels

- Use different blur levels: `blur(10px)` for background panels, `blur(20px)` for foreground
- Nest glass panels: cards inside a glass container
- Data visualizations: white/transparent chart lines on glass

### Forms

```css
.glass-input {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.25);
  border-radius: 12px;
  padding: 14px 18px;
  color: white;
  backdrop-filter: blur(10px);
}
.glass-input::placeholder { color: rgba(255,255,255,0.45); }
.glass-input:focus {
  border-color: rgba(255,255,255,0.6);
  background: rgba(255,255,255,0.14);
  outline: none;
  box-shadow: 0 0 0 3px rgba(255,255,255,0.1);
}
```

### Modal / Sheet

```css
.glass-modal {
  background: rgba(20, 20, 40, 0.6);
  backdrop-filter: blur(30px);
  border: 1px solid rgba(255,255,255,0.15);
  border-radius: 24px;
  padding: 40px;
  box-shadow: 0 24px 80px rgba(0,0,0,0.4);
}
```

---

## 4. Best Use Cases

- **Analytics / SaaS dashboards** (most popular use)
- **Finance / crypto apps**
- **Event / concert landing pages**
- **Gaming portals**
- **Music streaming UI**
- **AI product landing pages**
- **Login / auth screens**
- **Mobile app showcase websites**

---

## 5. Design Guidelines

### DO

- Always have a rich, colorful, gradient or blob background
- Layer multiple glass panels at different depths
- Use blur values between 10–24px (anything less = not frosted)
- Add `saturate()` alongside `blur()` for vibrancy
- Keep glass panels to 8–20% opacity for light mode
- Use white text exclusively on glass surfaces

### DON'T

- Use glassmorphism on white or minimal backgrounds (invisible glass)
- Stack too many glass layers (>4 = performance issue)
- Reduce border-radius below 12px (ruins the soft aesthetic)
- Use dark/opaque text on glass panels
- Forget `-webkit-backdrop-filter` (Safari requirement)
- Use over 25px blur (content becomes unreadable)

### Common Mistakes

- **No background**: the most common error — glass reveals what's behind
- **Too opaque**: >30% opacity = not glass, just translucent box
- **Single glass layer**: depth comes from layering
- **Missing border**: the thin white border defines the glass edge
- **Poor contrast**: white-on-white glass = illegible content

---

## 6. Implementation Tips

### Browser Support Check

```css
@supports (backdrop-filter: blur(1px)) {
  .glass { backdrop-filter: blur(16px); }
}
@supports not (backdrop-filter: blur(1px)) {
  .glass { background: rgba(20, 20, 40, 0.85); } /* Fallback */
}
```

### Tailwind Glassmorphism

```html
<div class="bg-white/10 backdrop-blur-xl border border-white/20 rounded-2xl 
            shadow-[0_8px_32px_rgba(0,0,0,0.2)] p-7">
```

### Animated Background Blobs

```css
.blob { animation: blobFloat 10s ease-in-out infinite; }
@keyframes blobFloat {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(30px, -20px) scale(1.1); }
  66% { transform: translate(-20px, 15px) scale(0.95); }
}
.blob:nth-child(2) { animation-delay: -3s; animation-duration: 14s; }
.blob:nth-child(3) { animation-delay: -7s; animation-duration: 12s; }
```

### Depth Layers System

```css
:root {
  /* Layer 0: Background */
  --glass-l0: blur(0px);    /* The colorful background */
  /* Layer 1: Far panels */
  --glass-l1: blur(8px);    /* Most background cards */
  /* Layer 2: Main content */
  --glass-l2: blur(16px);   /* Primary cards */
  /* Layer 3: Foreground / tooltips */
  --glass-l3: blur(24px);   /* Modals, toasts */
}
```

---

## 7. Example Layout: Analytics Dashboard

```
[Deep purple-blue gradient background with 3 colored blobs]
│
├── NAVBAR: Glass strip, blur-20, border-b-white/10
│   └── Logo (white) | Nav links (white, semi-opaque) | Avatar
│
├── SIDEBAR: Glass panel, blur-16, full height, 240px wide
│   └── Icon + Label navigation (white icons)
│   └── Active item: brighter glass highlight
│
├── MAIN CONTENT AREA
│   ├── STAT CARDS ROW: 4 glass cards
│   │   └── Each: metric title + big number + trend indicator
│   │
│   ├── CHART AREA: Large glass panel
│   │   └── Line/area chart with white/colored lines
│   │   └── Glass tooltip on hover
│   │
│   └── TABLE: Glass card with rows
│       └── Row hover: rgba(255,255,255,0.06) highlight
│
└── RIGHT RAIL: Glass panel
    └── Activity feed, notifications (glass chips)
```

---

## 8. Advanced Enhancements

### Glass Shimmer Effect

```css
@keyframes glassShimmer {
  0% { background-position: -200% center; }
  100% { background-position: 200% center; }
}
.glass-card::after {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: linear-gradient(105deg, 
    transparent 40%, rgba(255,255,255,0.08) 50%, transparent 60%);
  background-size: 200%;
  animation: glassShimmer 3s ease-in-out infinite;
  pointer-events: none;
  border-radius: inherit;
}
```

### Parallax Depth

```javascript
document.addEventListener('mousemove', (e) => {
  const { innerWidth: W, innerHeight: H } = window;
  const x = (e.clientX / W - 0.5) * 20;
  const y = (e.clientY / H - 0.5) * 20;
  
  document.querySelectorAll('.blob').forEach((blob, i) => {
    const depth = (i + 1) * 0.5;
    blob.style.transform = `translate(${x * depth}px, ${y * depth}px)`;
  });
});
```

### Frosted Card on Scroll Reveal

```css
.glass-card {
  opacity: 0;
  transform: translateY(30px);
  transition: opacity 0.6s ease, transform 0.6s ease;
}
.glass-card.visible {
  opacity: 1;
  transform: translateY(0);
}
```

### Tilt Effect on Hover

```javascript
// Use VanillaTilt.js or implement manually
VanillaTilt.init(document.querySelectorAll('.glass-card'), {
  max: 8, speed: 400, glare: true, 'max-glare': 0.15
});
```