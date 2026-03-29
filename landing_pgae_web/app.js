/* ═══════════════════════════════════════
   FUNDTRACE AI — LANDING PAGE ANIMATIONS
   ═══════════════════════════════════════ */

// ── CUSTOM CURSOR ──
const cursor = document.getElementById('luxuryCursor');
const cursorDot = document.getElementById('luxuryCursorDot');
let mouseX = 0, mouseY = 0, curX = 0, curY = 0;

document.addEventListener('mousemove', e => {
  mouseX = e.clientX; mouseY = e.clientY;
  cursorDot.style.left = mouseX + 'px';
  cursorDot.style.top = mouseY + 'px';
});

function animateCursor() {
  curX += (mouseX - curX) * 0.12;
  curY += (mouseY - curY) * 0.12;
  cursor.style.left = curX + 'px';
  cursor.style.top = curY + 'px';
  requestAnimationFrame(animateCursor);
}
animateCursor();

document.querySelectorAll('a, button, [tabindex="0"]').forEach(el => {
  el.addEventListener('mouseenter', () => {
    cursor.style.width = '52px';
    cursor.style.height = '52px';
    cursor.style.background = 'rgba(201,168,76,0.12)';
  });
  el.addEventListener('mouseleave', () => {
    cursor.style.width = '36px';
    cursor.style.height = '36px';
    cursor.style.background = 'transparent';
  });
});

// ── HERO PARTICLE / GRAPH CANVAS ──
const canvas = document.getElementById('heroCanvas');
const ctx = canvas.getContext('2d');
let nodes = [], edges = [], W, H;

function resizeCanvas() {
  W = canvas.width = canvas.offsetWidth;
  H = canvas.height = canvas.offsetHeight;
}
resizeCanvas();
window.addEventListener('resize', () => { resizeCanvas(); initNodes(); });

function initNodes() {
  nodes = [];
  edges = [];
  const count = Math.floor(W / 90);
  for (let i = 0; i < count; i++) {
    nodes.push({
      x: Math.random() * W,
      y: Math.random() * H,
      vx: (Math.random() - 0.5) * 0.4,
      vy: (Math.random() - 0.5) * 0.4,
      r: Math.random() * 2.5 + 1,
      alpha: Math.random() * 0.6 + 0.2,
    });
  }
}
initNodes();

function drawGraph() {
  ctx.clearRect(0, 0, W, H);
  // Draw edges
  for (let i = 0; i < nodes.length; i++) {
    for (let j = i + 1; j < nodes.length; j++) {
      const dx = nodes[i].x - nodes[j].x;
      const dy = nodes[i].y - nodes[j].y;
      const dist = Math.sqrt(dx * dx + dy * dy);
      if (dist < 160) {
        const alpha = (1 - dist / 160) * 0.15;
        ctx.beginPath();
        ctx.moveTo(nodes[i].x, nodes[i].y);
        ctx.lineTo(nodes[j].x, nodes[j].y);
        ctx.strokeStyle = `rgba(201,168,76,${alpha})`;
        ctx.lineWidth = 0.6;
        ctx.stroke();
      }
    }
  }
  // Draw nodes
  nodes.forEach(n => {
    ctx.beginPath();
    ctx.arc(n.x, n.y, n.r, 0, Math.PI * 2);
    ctx.fillStyle = `rgba(201,168,76,${n.alpha})`;
    ctx.fill();
    // Move
    n.x += n.vx; n.y += n.vy;
    if (n.x < 0 || n.x > W) n.vx *= -1;
    if (n.y < 0 || n.y > H) n.vy *= -1;
  });
  requestAnimationFrame(drawGraph);
}
drawGraph();

// ── SCROLL REVEAL ──
const reveals = document.querySelectorAll('.luxury-reveal');
const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry, i) => {
    if (entry.isIntersecting) {
      setTimeout(() => entry.target.classList.add('visible'), i * 80);
      observer.unobserve(entry.target);
    }
  });
}, { threshold: 0.12 });
reveals.forEach(el => observer.observe(el));

// ── HERO ON LOAD REVEAL ──
window.addEventListener('load', () => {
  setTimeout(() => document.getElementById('heroContent').classList.add('visible'), 300);
});

// ── COUNTER ANIMATION ──
function animateCounter(el, target, duration = 1800) {
  let start = null;
  const step = (timestamp) => {
    if (!start) start = timestamp;
    const progress = Math.min((timestamp - start) / duration, 1);
    const ease = 1 - Math.pow(1 - progress, 3);
    el.textContent = Math.floor(ease * target).toLocaleString();
    if (progress < 1) requestAnimationFrame(step);
    else el.textContent = target.toLocaleString();
  };
  requestAnimationFrame(step);
}

const counterObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const el = entry.target;
      const target = parseInt(el.dataset.target);
      animateCounter(el, target);
      counterObserver.unobserve(el);
    }
  });
}, { threshold: 0.5 });
document.querySelectorAll('.stat-num').forEach(el => counterObserver.observe(el));

// ── STICKY NAV SHRINK ──
const nav = document.getElementById('mainNav');
window.addEventListener('scroll', () => {
  if (window.scrollY > 80) {
    nav.style.top = '0';
  } else {
    nav.style.top = '37px';
  }
});

// ── REACT LOOP ANIMATION ──
const reactNodes = document.querySelectorAll('.react-node');
let activeReact = 0;
function cycleReact() {
  reactNodes.forEach(n => n.style.borderColor = 'rgba(201,168,76,0.18)');
  if (reactNodes[activeReact]) {
    reactNodes[activeReact].style.borderColor = 'rgba(201,168,76,0.8)';
    reactNodes[activeReact].style.background = '#221F19';
  }
  activeReact = (activeReact + 1) % reactNodes.length;
}
setInterval(cycleReact, 1400);

// ── WORKFLOW STEP HIGHLIGHT ──
const wfSteps = document.querySelectorAll('.wf-step');
const wfObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.style.opacity = '1';
      entry.target.style.transform = 'translateX(0)';
    }
  });
}, { threshold: 0.3 });
wfSteps.forEach((step, i) => {
  step.style.opacity = '0';
  step.style.transform = 'translateX(-20px)';
  step.style.transition = `opacity 0.6s ${i * 0.15}s ease, transform 0.6s ${i * 0.15}s ease`;
  wfObserver.observe(step);
});

// ── PATTERN CARD TILT ──
document.querySelectorAll('.pattern-card').forEach(card => {
  card.addEventListener('mousemove', (e) => {
    const rect = card.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width - 0.5) * 6;
    const y = ((e.clientY - rect.top) / rect.height - 0.5) * 6;
    card.style.transform = `translateY(-4px) rotateX(${-y}deg) rotateY(${x}deg)`;
    card.style.transition = 'none';
  });
  card.addEventListener('mouseleave', () => {
    card.style.transform = '';
    card.style.transition = 'all 0.4s';
  });
});

// ── GOLD TYPING EFFECT FOR SAMPLE REPORT ──
const reportEl = document.querySelector('.sample-report');
if (reportEl) {
  const rObserver = new IntersectionObserver((entries) => {
    if (entries[0].isIntersecting) {
      const lines = reportEl.querySelectorAll('.sample-line');
      lines.forEach((line, i) => {
        line.style.opacity = '0';
        line.style.transform = 'translateX(-10px)';
        line.style.transition = `opacity 0.5s ${i * 0.18}s ease, transform 0.5s ${i * 0.18}s ease`;
        setTimeout(() => {
          line.style.opacity = '1';
          line.style.transform = 'none';
        }, i * 180 + 200);
      });
      rObserver.disconnect();
    }
  }, { threshold: 0.3 });
  rObserver.observe(reportEl);
}

// ── COMPARE TABLE ROW HOVER ──
document.querySelectorAll('.ct-row').forEach(row => {
  row.addEventListener('mouseenter', () => row.style.background = 'rgba(201,168,76,0.04)');
  row.addEventListener('mouseleave', () => row.style.background = '');
});

// ── SCROLL PROGRESS INDICATOR ──
const progressBar = document.createElement('div');
progressBar.style.cssText = `
  position: fixed; top: 0; left: 0; height: 2px; z-index: 9999;
  background: linear-gradient(90deg, #C9A84C, #F0D080, #C9A84C);
  transition: width 0.1s;
  pointer-events: none;
`;
document.body.appendChild(progressBar);
window.addEventListener('scroll', () => {
  const scrolled = window.scrollY;
  const max = document.documentElement.scrollHeight - window.innerHeight;
  progressBar.style.width = (scrolled / max * 100) + '%';
});

// ── SMOOTH SECTION ENTRANCE FOR PHASE CARDS ──
document.querySelectorAll('.scale-phase').forEach((card, i) => {
  card.style.opacity = '0';
  card.style.transform = 'translateY(20px)';
  card.style.transition = `opacity 0.6s ${i * 0.12}s ease, transform 0.6s ${i * 0.12}s ease`;
  const obs = new IntersectionObserver(entries => {
    if (entries[0].isIntersecting) {
      card.style.opacity = '1';
      card.style.transform = 'none';
      obs.disconnect();
    }
  }, { threshold: 0.2 });
  obs.observe(card);
});

// ── COMPLIANCE BADGE PULSE ──
document.querySelectorAll('.comp-badge').forEach(badge => {
  badge.addEventListener('mouseenter', () => {
    badge.style.background = 'rgba(201,168,76,0.2)';
    badge.style.boxShadow = '0 0 16px rgba(201,168,76,0.3)';
  });
  badge.addEventListener('mouseleave', () => {
    badge.style.background = '';
    badge.style.boxShadow = '';
  });
});

// ── FOOTER MARQUEE: ensure infinite by duplicating text ──
const topText = document.querySelector('.top-bar-text');
if (topText) {
  topText.innerHTML = topText.innerHTML.repeat(4);
}
