# SKILL: Claymorphism UI Design

---

## 1. Core Concept

Claymorphism takes 3D illustration aesthetics and applies them as a full UI design language. UI elements look like **soft, rounded, puffy clay objects** — inflated, tactile, toy-like, and friendly. Think Notions 3D illustration pack turned into a full interface. The philosophy is _physical playfulness_: every element should look like you could pinch it. Inspired by 3D characters from Pixar/Disney and the "inflated" icon trend, Claymorphism makes digital interfaces feel warm, approachable, and joyful.

---

## 2. Key Visual Elements

### Colors

- **Soft, muted pastels** as backgrounds: #F0EBE3, #E8F4FD, #F5F0FF
- **Rich, saturated clay colors** for elements: teal (#00B4A0), coral (#FF6B6B), warm yellow (#FFD166), violet (#9C6FDE)
- Each element has its own "clay color" — avoid using the same tint everywhere
- White highlights on raised surfaces
- Slightly darker shadows underneath

### 3D Clay Effect (CSS-only method)

```css
/* The "inflated" clay look */
.clay-card {
  background: linear-gradient(145deg, #ffffff22, transparent);
  box-shadow:
    /* Outer depth */
    0 10px 30px rgba(0, 0, 0, 0.12),
    0 4px 8px rgba(0, 0, 0, 0.08),
    /* Inner highlight (top-left) */
    inset 0 2px 6px rgba(255, 255, 255, 0.7),
    /* Inner shadow (bottom-right) */
    inset 0 -3px 8px rgba(0, 0, 0, 0.1);
  border-radius: 28px;
}
```

### Typography

- **Rounded fonts only**: Nunito, Fredoka One, Poppins, Baloo 2, Quicksand
- Bold weights (600–800) for headings
- Semi-bold (500–600) for body
- No serif, no condensed, no sharp fonts
- Large scale: 48–72px for hero text

### Spacing

- Generous padding: 28–40px inside cards
- Large border-radius: 24–36px for cards, 50px for buttons (pills)
- Content feels "padded" and breathing

### Textures

- Subtle noise grain overlay (2–3%) for organic clay feel
- Soft gradient on each element surface
- No hard edges anywhere

---

## 3. UI Components

### Buttons (Puffy Pills)

```css
.clay-btn {
  background: linear-gradient(145deg, #FF8A80, #FF5252);
  border: none;
  border-radius: 50px;
  padding: 16px 36px;
  font-family: 'Nunito', sans-serif;
  font-weight: 800;
  font-size: 15px;
  color: white;
  box-shadow:
    0 8px 20px rgba(255, 82, 82, 0.35),
    0 2px 4px rgba(0,0,0,0.1),
    inset 0 2px 4px rgba(255,255,255,0.4),
    inset 0 -2px 4px rgba(0,0,0,0.1);
  transition: transform 0.15s, box-shadow 0.15s;
}
.clay-btn:hover {
  transform: translateY(-2px) scale(1.02);
  box-shadow:
    0 12px 28px rgba(255, 82, 82, 0.4),
    0 4px 8px rgba(0,0,0,0.12),
    inset 0 2px 4px rgba(255,255,255,0.4),
    inset 0 -2px 4px rgba(0,0,0,0.1);
}
.clay-btn:active {
  transform: translateY(1px) scale(0.98);
  box-shadow: 0 4px 10px rgba(255, 82, 82, 0.3);
}
```

### Cards

```css
.clay-card {
  background: #ffffff;
  border-radius: 28px;
  padding: 32px;
  box-shadow:
    0 20px 50px rgba(0,0,0,0.08),
    0 6px 12px rgba(0,0,0,0.06),
    inset 0 2px 0 rgba(255,255,255,0.9);
  position: relative;
  overflow: hidden;
}
/* Subtle gradient top highlight */
.clay-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0; height: 60%;
  background: linear-gradient(180deg, rgba(255,255,255,0.4), transparent);
  border-radius: 28px 28px 0 0;
  pointer-events: none;
}
```

### Navbar

- Floating, centered, pill-shaped
- White background with clay shadow
- Active link: colored pill highlight

### 3D Clay Icons/Illustrations

- Embed Spline 3D scenes or use Rive animations
- CSS-only inflated icons:

```css
.clay-icon {
  width: 72px; height: 72px;
  border-radius: 22px;
  background: linear-gradient(135deg, #A8EDEA, #FED6E3);
  box-shadow:
    0 8px 20px rgba(0,0,0,0.15),
    inset 0 2px 4px rgba(255,255,255,0.6),
    inset 0 -2px 4px rgba(0,0,0,0.08);
  display: flex; align-items: center; justify-content: center;
}
```

---

## 4. Best Use Cases

- **Children's apps or kid-friendly platforms**
- **Health & wellness apps** (meditation, fitness)
- **Productivity tools** wanting friendly vibes (Notion alternatives)
- **Food delivery / ordering apps**
- **Education platforms** (e-learning, coding for kids)
- **Pet care / lifestyle apps**
- **SaaS landing pages** wanting to stand out with playfulness

---

## 5. Design Guidelines

### DO

- Use proper inset shadows for the "inflated" 3D effect
- Combine with 3D illustrations (Spline, Rive, LottieFiles)
- Each component has its own clay color
- Use bold rounded fonts exclusively
- Add subtle bounce animations to interactions
- Include 3D character/mascot illustrations

### DON'T

- Mix clay with flat/minimalist elements
- Use sharp corners — everything must be rounded
- Use serif or condensed fonts
- Create overly complex layouts — clay works with simple grids
- Overuse the 3D effect (it loses impact)

### Common Mistakes

- **No inset shadow** = flat card, not clay
- **Wrong shadow color**: use colored shadows matching the element hue, not just black
- **Too many clay colors** = chaotic, not playful
- **Forgetting hover states** — clay should squish and bounce
- **Sharp shadows**: clay shadows should be soft and spread out

---

## 6. Implementation Tips

### Color-Matched Shadows

```css
/* Shadow color = element color at 30-40% opacity */
.clay-teal { 
  background: #00B4A0;
  box-shadow: 0 12px 30px rgba(0, 180, 160, 0.4), 
              inset 0 2px 4px rgba(255,255,255,0.5);
}
.clay-coral { 
  background: #FF6B6B;
  box-shadow: 0 12px 30px rgba(255, 107, 107, 0.4),
              inset 0 2px 4px rgba(255,255,255,0.5);
}
```

### Tailwind Clay Card

```html
<div class="bg-white rounded-[28px] p-8 
            shadow-[0_20px_50px_rgba(0,0,0,0.08),0_6px_12px_rgba(0,0,0,0.06),inset_0_2px_0_rgba(255,255,255,0.9)]
            relative overflow-hidden">
```

### Bounce Animation

```css
@keyframes clayBounce {
  0% { transform: scale(1); }
  40% { transform: scale(1.06) translateY(-4px); }
  60% { transform: scale(0.97) translateY(1px); }
  80% { transform: scale(1.02) translateY(-1px); }
  100% { transform: scale(1); }
}
.clay-btn:active { animation: clayBounce 0.4s ease; }
```

### Spline 3D Integration

```html
<script type="module" src="https://unpkg.com/@splinetool/viewer@0.9.490/build/spline-viewer.js"></script>
<spline-viewer url="https://prod.spline.design/your-scene/scene.splinecode"></spline-viewer>
```

---

## 7. Example Layout: Wellness App Homepage

```
[Soft cream background #FFF8F0]
│
├── NAVBAR: Floating pill, white clay background
│   └── Logo (rounded, clay icon) | Links | "Start Free" coral button
│
├── HERO: Split layout
│   ├── Left: 
│   │   ├── Badge pill: "✦ New — Clay UI App"
│   │   ├── Headline: "Feel Better,"
│   │   │   "Every Day." (72px Fredoka Bold)
│   │   ├── Subtext (18px, muted)
│   │   └── Two buttons: primary coral + ghost
│   └── Right: Spline 3D character (meditating figure)
│       + floating clay stat cards (bouncing)
│
├── FEATURES: 3 clay cards in row
│   └── Teal, Violet, Yellow — each with 3D icon + text
│
├── SOCIAL PROOF: Horizontally scrolling pill tags
│   └── User avatars + rating (clay style avatars)
│
└── CTA: Large clay card, full-width rounded
    └── Centered headline + button + floating 3D elements
```

---

## 8. Advanced Enhancements

### Inflate on Hover (3D Press Effect)

```css
.clay-pressable {
  transition: all 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.clay-pressable:hover {
  transform: translateY(-4px) scale(1.03);
}
.clay-pressable:active {
  transform: translateY(2px) scale(0.97);
  box-shadow: 0 4px 10px rgba(0,0,0,0.1);
}
```

### Floating Card Animation

```css
@keyframes clayFloat {
  0%, 100% { transform: translateY(0px) rotate(0deg); }
  33% { transform: translateY(-8px) rotate(1deg); }
  66% { transform: translateY(-4px) rotate(-0.5deg); }
}
.clay-float { animation: clayFloat 4s ease-in-out infinite; }
```

### Staggered Float (for multiple cards)

```css
.clay-float:nth-child(2) { animation-delay: -1.3s; }
.clay-float:nth-child(3) { animation-delay: -2.7s; }
```

### Confetti on CTA Click

- Use `canvas-confetti` library
- Configure with rounded shapes and clay-matching colors