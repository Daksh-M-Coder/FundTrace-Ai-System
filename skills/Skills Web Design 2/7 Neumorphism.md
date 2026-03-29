# SKILL: Neumorphism (Soft UI) Design

---

## 1. Core Concept

Neumorphism (New + Skeuomorphism) creates interfaces that look like they're **extruded from the background material itself** — as if elements are soft, smooth lumps pushed out of or pressed into a single continuous surface. It's neither flat nor traditionally 3D; it's _emerging from the same material_. Using dual shadows (light from top-left, dark from bottom-right), elements float above or sink into the surface. The philosophy: _the interface is sculpted from one continuous material_.

---

## 2. Key Visual Elements

### Colors (The Most Critical Choice)

- **Background and elements MUST be the same color** — this is the defining rule
- Common: Light grey (#E0E5EC), warm beige (#E8E0D5), off-white (#F0F0F3)
- Dark mode: #1E2235, #2A2D3E, #1A1A2E
- **Accent color** (used sparingly): single brand color for active states

### The Dual Shadow Formula

```css
/* This IS neumorphism */
.neu {
  background: #E0E5EC;
  /* Light shadow: top-left (light source) */
  /* Dark shadow: bottom-right (shadow) */
  box-shadow: 
    6px 6px 12px rgba(163, 177, 198, 0.6),
    -6px -6px 12px rgba(255, 255, 255, 0.8);
  border-radius: 16px;
}

/* Pressed/inset state */
.neu-pressed {
  box-shadow: 
    inset 4px 4px 8px rgba(163, 177, 198, 0.6),
    inset -4px -4px 8px rgba(255, 255, 255, 0.8);
}

/* Concave (sunken surface) */
.neu-concave {
  background: linear-gradient(145deg, #D1D9E6, #F9FBFF);
  box-shadow: 
    6px 6px 12px rgba(163, 177, 198, 0.6),
    -6px -6px 12px rgba(255, 255, 255, 0.8);
}
```

### Dark Neumorphism

```css
.neu-dark {
  background: #1E2235;
  box-shadow:
    6px 6px 12px rgba(10, 12, 22, 0.6),
    -6px -6px 12px rgba(40, 46, 68, 0.8);
}
```

### Typography

- Clean, modern sans: Poppins, Nunito, Mulish, Rubik
- Muted text colors (never pure black): `#6B7280` on light, `rgba(255,255,255,0.7)` on dark
- Headers: slightly darker than background (`#4A5568` on light mode)
- NO bold typography — neumorphism is serene, not loud

### Spacing

- Generous — minimum 24px padding inside components
- Rounded corners: 16–24px for cards, 50px for toggles
- Breathe — tight elements break the illusion

---

## 3. UI Components

### Buttons

```css
.neu-btn {
  background: #E0E5EC;
  border: none;
  border-radius: 12px;
  padding: 14px 28px;
  font-size: 15px;
  font-weight: 600;
  color: #6B7280;
  cursor: pointer;
  box-shadow: 
    5px 5px 10px rgba(163, 177, 198, 0.6),
    -5px -5px 10px rgba(255, 255, 255, 0.8);
  transition: all 0.15s ease;
}
.neu-btn:hover {
  box-shadow: 
    7px 7px 14px rgba(163, 177, 198, 0.7),
    -7px -7px 14px rgba(255, 255, 255, 0.9);
}
.neu-btn:active {
  box-shadow: 
    inset 4px 4px 8px rgba(163, 177, 198, 0.6),
    inset -4px -4px 8px rgba(255, 255, 255, 0.8);
  color: #4A90E2; /* Accent color on press */
}
```

### Cards

```css
.neu-card {
  background: #E0E5EC;
  border-radius: 20px;
  padding: 28px;
  box-shadow: 
    8px 8px 16px rgba(163, 177, 198, 0.6),
    -8px -8px 16px rgba(255, 255, 255, 0.8);
}
```

### Toggle

```css
.neu-toggle-track {
  width: 60px; height: 32px;
  background: #E0E5EC;
  border-radius: 16px;
  box-shadow: 
    inset 3px 3px 6px rgba(163, 177, 198, 0.6),
    inset -3px -3px 6px rgba(255, 255, 255, 0.8);
}
.neu-toggle-thumb {
  width: 24px; height: 24px;
  border-radius: 50%;
  background: #E0E5EC;
  box-shadow: 
    3px 3px 6px rgba(163, 177, 198, 0.7),
    -3px -3px 6px rgba(255, 255, 255, 0.9);
}
.neu-toggle.on .neu-toggle-thumb {
  background: #4A90E2;
  box-shadow: 0 2px 6px rgba(74, 144, 226, 0.5);
}
```

### Icon Buttons

```css
.neu-icon-btn {
  width: 56px; height: 56px;
  border-radius: 50%;
  background: #E0E5EC;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 
    5px 5px 10px rgba(163, 177, 198, 0.6),
    -5px -5px 10px rgba(255, 255, 255, 0.8);
  cursor: pointer;
  border: none;
}
```

### Input Fields

```css
.neu-input {
  background: #E0E5EC;
  border: none;
  border-radius: 12px;
  padding: 14px 18px;
  color: #4A5568;
  font-size: 15px;
  box-shadow: 
    inset 4px 4px 8px rgba(163, 177, 198, 0.5),
    inset -4px -4px 8px rgba(255, 255, 255, 0.7);
  outline: none;
}
.neu-input:focus {
  box-shadow: 
    inset 4px 4px 8px rgba(163, 177, 198, 0.6),
    inset -4px -4px 8px rgba(255, 255, 255, 0.8),
    0 0 0 2px #4A90E2;
}
```

### Progress Bar

```css
.neu-progress-track {
  height: 12px;
  border-radius: 6px;
  background: #E0E5EC;
  box-shadow: inset 3px 3px 6px rgba(163,177,198,0.5), inset -3px -3px 6px rgba(255,255,255,0.7);
}
.neu-progress-fill {
  height: 100%;
  border-radius: 6px;
  background: linear-gradient(90deg, #4A90E2, #6CB3F5);
  box-shadow: 2px 0 8px rgba(74,144,226,0.5);
}
```

---

## 4. Best Use Cases

- **Health & fitness dashboards** (calm, focused)
- **Music players** (controls feel physical)
- **Smart home control panels**
- **Finance / budgeting apps**
- **Meditation / wellness apps**
- **Clock / timer interfaces**
- **Settings / preferences panels**
- **Calculator apps**

---

## 5. Design Guidelines

### DO

- Background and component color = same value (non-negotiable)
- Use dual shadow (light + dark) — both required
- Keep shadow offset small: 4–10px (not 20px+)
- Use one accent color for active/on states
- Maintain consistent light direction (top-left always)
- Keep designs simple — neumorphism can't handle complex layouts

### DON'T

- Use different background and element colors
- Use single shadows (looks like glassmorphism or flat design)
- Make shadow colors too strong (looks muddy)
- Add many different colors (destroys the monochrome magic)
- Use on complex data-heavy interfaces (readability suffers)
- Mix with other design styles (glassmorphism + neumorphism = confusion)

### Common Mistakes

- **Wrong shadow colors**: don't use pure black/white — derive from background hue
- **Too large offsets**: 20px shadows = looks broken
- **No pressed state**: neumorphism without inset states = incomplete
- **Low contrast text**: the muted aesthetic can reduce accessibility
- **Too many elements**: neumorphism shines in focused, minimal layouts

---

## 6. Implementation Tips

### Shadow Color Calculator

```
Light shadow = background color lightened 15-20% = rgba(255,255,255,0.8)
Dark shadow = background color darkened 15-20% = background-specific rgba

For #E0E5EC:
  Light: rgba(255, 255, 255, 0.8)
  Dark: rgba(163, 177, 198, 0.6)

For #1E2235:
  Light: rgba(40, 46, 68, 0.8)
  Dark: rgba(10, 12, 22, 0.6)
```

### CSS Variables Template

```css
:root {
  --bg: #E0E5EC;
  --shadow-dark: rgba(163, 177, 198, 0.6);
  --shadow-light: rgba(255, 255, 255, 0.8);
  --text-primary: #4A5568;
  --text-muted: #9AA5B4;
  --accent: #4A90E2;
  
  --raised: 6px 6px 12px var(--shadow-dark), -6px -6px 12px var(--shadow-light);
  --pressed: inset 4px 4px 8px var(--shadow-dark), inset -4px -4px 8px var(--shadow-light);
  --concave: var(--raised); /* + gradient background */
}
```

### Tailwind Neumorphism

```html
<!-- Raised card -->
<div class="bg-[#E0E5EC] rounded-2xl p-7
            shadow-[6px_6px_12px_rgba(163,177,198,0.6),_-6px_-6px_12px_rgba(255,255,255,0.8)]">

<!-- Pressed input -->
<input class="bg-[#E0E5EC] rounded-xl px-4 py-3 border-0 outline-none
              shadow-[inset_4px_4px_8px_rgba(163,177,198,0.5),_inset_-4px_-4px_8px_rgba(255,255,255,0.7)]">
```

---

## 7. Example Layout: Fitness Dashboard

```
[Uniform #E0E5EC background — wall-to-wall]
│
├── SIDEBAR: Raised neumorphic panel
│   └── Round icon buttons (each neumorphic circle)
│   └── Active: pressed inset style + accent color icon
│
├── MAIN: "Today's Activity"
│   ├── STAT CARDS: 3 raised cards in row
│   │   └── Each: neumorphic card, icon, number, label
│   │
│   ├── RING CHART: SVG circular progress
│   │   └── Track: neumorphic inset ring
│   │   └── Fill: accent color gradient
│   │
│   ├── WORKOUT LIST: Neumorphic list items
│   │   └── Each: raised pill, icon, name, duration
│   │
│   └── MUSIC PLAYER: Compact neumorphic widget
│       └── Album (raised square) + controls (circle buttons)
│       └── Slider: neumorphic track with accent fill
│
└── RIGHT PANEL: Calendar widget (neumorphic grid)
```

---

## 8. Advanced Enhancements

### Smooth State Transitions

```css
.neu-interactive {
  transition: box-shadow 0.2s ease, transform 0.2s ease;
}
/* Hover: lift slightly */
.neu-interactive:hover {
  box-shadow: 
    10px 10px 20px rgba(163, 177, 198, 0.7),
    -10px -10px 20px rgba(255, 255, 255, 0.9);
  transform: translateY(-1px);
}
```

### Pulsing Active Indicator

```css
@keyframes neuPulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(74,144,226,0.4); }
  50% { box-shadow: 0 0 0 8px rgba(74,144,226,0); }
}
.neu-active-dot {
  width: 8px; height: 8px;
  border-radius: 50%;
  background: #4A90E2;
  animation: neuPulse 2s ease-in-out infinite;
}
```

### Circular Progress Ring

```javascript
// SVG stroke-dashoffset technique
const circumference = 2 * Math.PI * radius;
circle.style.strokeDasharray = circumference;
circle.style.strokeDashoffset = circumference - (percent / 100) * circumference;
```