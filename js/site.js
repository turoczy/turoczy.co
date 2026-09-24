/* turoczy.com — three jobs only:
   1. light/dark toggle, remembered
   2. the hero dot field: dots get connected, slowly, forever
   3. mark the current section in the dot rail
*/

(function () {
  "use strict";

  var NS = "http://www.w3.org/2000/svg";
  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* =======================================================
     1. Theme toggle
     Default is whatever the operating system says. Once you
     press the button, your choice wins and is remembered.
     ======================================================= */

  (function theme() {
    var btn = document.getElementById("theme-toggle");
    var label = document.getElementById("theme-label");
    if (!btn) return;

    var sysDark = window.matchMedia("(prefers-color-scheme: dark)");
    var saved = null;
    try { saved = localStorage.getItem("turoczy-theme"); } catch (e) {}

    function current() {
      var set = document.documentElement.getAttribute("data-theme");
      if (set) return set;
      return sysDark.matches ? "dark" : "light";
    }

    function paint() {
      var now = current();
      // The button offers the other one.
      label.textContent = now === "dark" ? "Light" : "Dark";
      btn.setAttribute("aria-pressed", now === "dark" ? "true" : "false");
      btn.setAttribute(
        "aria-label",
        "Switch to " + (now === "dark" ? "light" : "dark") + " mode"
      );
    }

    if (saved === "dark" || saved === "light") {
      document.documentElement.setAttribute("data-theme", saved);
    }
    paint();

    btn.addEventListener("click", function () {
      var next = current() === "dark" ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", next);
      try { localStorage.setItem("turoczy-theme", next); } catch (e) {}
      paint();
    });

    // If you never pressed the button, follow the system when it changes.
    var onSys = function () { if (!saved) paint(); };
    if (sysDark.addEventListener) sysDark.addEventListener("change", onSys);
    else if (sysDark.addListener) sysDark.addListener(onSys);
  })();

  /* =======================================================
     2. The dot field
     Dots sit still. Connections come and go — one every
     couple of seconds, a few at a time, always well clear
     of the headline.
     ======================================================= */

  (function field() {
    var svg = document.getElementById("field");
    if (!svg) return;

    var W = 1000, H = 700;
    svg.setAttribute("viewBox", "0 0 " + W + " " + H);

    // Seeded, so the arrangement is the same on every visit. This is a
    // diagram of an idea, not a particle toy.
    var seed = 20070801; // Silicon Florist, month one
    function rnd() {
      seed = (seed * 1103515245 + 12345) & 0x7fffffff;
      return seed / 0x7fffffff;
    }

    // --- Where the type is, so nothing gets drawn over it ------------
    // Per line of text, not one box around all of it, so the gaps beside
    // short lines stay open.
    var boxes = [];

    function measure() {
      var ctm = svg.getScreenCTM();
      var bits = document.querySelectorAll(
        ".wordmark, .hero h1, .tagline, .hero .lede, .hero .btn"
      );
      if (!ctm || !bits.length) { boxes = []; return; }

      var inv = ctm.inverse();
      var p = svg.createSVGPoint();
      var pad = 15;
      var next = [];

      Array.prototype.forEach.call(bits, function (el) {
        var rects = el.getClientRects();
        for (var i = 0; i < rects.length; i++) {
          var r = rects[i];
          if (!r.width || !r.height) continue;
          p.x = r.left;  p.y = r.top;    var tl = p.matrixTransform(inv);
          p.x = r.right; p.y = r.bottom; var br = p.matrixTransform(inv);
          next.push({
            x1: Math.min(tl.x, br.x) - pad,
            y1: Math.min(tl.y, br.y) - pad,
            x2: Math.max(tl.x, br.x) + pad,
            y2: Math.max(tl.y, br.y) + pad
          });
        }
      });

      boxes = next;
    }

    function overType(x, y) {
      for (var i = 0; i < boxes.length; i++) {
        var b = boxes[i];
        if (x > b.x1 && x < b.x2 && y > b.y1 && y < b.y2) return true;
      }
      return false;
    }

    // --- Ambient dots: texture, everywhere, never connected ----------
    for (var i = 0; i < 40; i++) {
      var c = document.createElementNS(NS, "circle");
      c.setAttribute("cx", 30 + rnd() * (W - 60));
      c.setAttribute("cy", 24 + rnd() * (H - 48));
      c.setAttribute("r", 1.8 + rnd() * 1.8);
      svg.appendChild(c);
    }

    // --- The matrix --------------------------------------------------
    var MAX_DEGREE = 3;   // airy: no dot becomes a hairball
    var dots = [], nodes = [], pairs = [];
    var degree = {}, used = {}, drawn = 0, target = 0;
    var built = false;

    function build() {
      if (built) return;
      measure();
      if (!boxes.length) return;
      built = true;

      // Place the connectable dots only where there is room for them,
      // spread out, so the matrix reaches the whole field instead of
      // bunching up beside the headline.
      var guard = 0;
      while (dots.length < 38 && guard++ < 4000) {
        var x = 30 + rnd() * (W - 60);
        var y = 24 + rnd() * (H - 48);
        if (overType(x, y)) continue;
        var ok = true;
        for (var k = 0; k < dots.length; k++) {
          if (Math.hypot(dots[k].x - x, dots[k].y - y) < 52) { ok = false; break; }
        }
        if (ok) dots.push({ x: x, y: y });
      }

      // Created, but not yet collected — reveal() brings them in one by one.
      nodes = dots.map(function (d) {
        var n = document.createElementNS(NS, "circle");
        n.setAttribute("cx", d.x);
        n.setAttribute("cy", d.y);
        n.setAttribute("r", 3);
        n.setAttribute("class", "node");
        svg.appendChild(n);
        return n;
      });

      for (var a = 0; a < dots.length; a++) {
        for (var b = a + 1; b < dots.length; b++) {
          var d = Math.hypot(dots[b].x - dots[a].x, dots[b].y - dots[a].y);
          // Long edges would have to cross the type to get anywhere.
          if (d > 52 && d < 215 && !overType((dots[a].x + dots[b].x) / 2,
                                             (dots[a].y + dots[b].y) / 2)) {
            pairs.push([a, b, d]);
          }
        }
      }

      target = Math.min(pairs.length, 54);
    }

    // --- Collect a dot ------------------------------------------------
    var shown = [];   // indexes of dots that have arrived

    function reveal() {
      var left = [];
      for (var i = 0; i < nodes.length; i++) {
        if (shown.indexOf(i) === -1) left.push(i);
      }
      if (!left.length) return false;
      var pick = left[(Math.random() * left.length) | 0];
      nodes[pick].classList.add("shown");
      shown.push(pick);
      return true;
    }

    function connect() {
      if (!built || drawn >= target) return false;

      var pair = null;
      for (var tries = 0; tries < 80 && !pair; tries++) {
        var c = pairs[(Math.random() * pairs.length) | 0];
        var key = c[0] + ":" + c[1];
        if (used[key]) continue;
        // only dots that have been collected can be connected
        if (shown.indexOf(c[0]) === -1 || shown.indexOf(c[1]) === -1) continue;
        if ((degree[c[0]] || 0) >= MAX_DEGREE) continue;
        if ((degree[c[1]] || 0) >= MAX_DEGREE) continue;
        pair = c;
        used[key] = true;
      }
      if (!pair) return false;

      degree[pair[0]] = (degree[pair[0]] || 0) + 1;
      degree[pair[1]] = (degree[pair[1]] || 0) + 1;
      drawn++;

      var p = dots[pair[0]], q = dots[pair[1]];
      var ln = document.createElementNS(NS, "line");
      ln.setAttribute("x1", p.x); ln.setAttribute("y1", p.y);
      ln.setAttribute("x2", q.x); ln.setAttribute("y2", q.y);
      ln.style.setProperty("--len", pair[2]);
      svg.insertBefore(ln, svg.firstChild);

      if (reduced) {
        ln.classList.add("settled");
        nodes[pair[0]].classList.add("linked");
        nodes[pair[1]].classList.add("linked");
        return true;
      }

      nodes[pair[0]].classList.add("active");
      nodes[pair[1]].classList.add("active");

      requestAnimationFrame(function () {
        requestAnimationFrame(function () { ln.classList.add("draw"); });
      });

      // Flare as it lands, then settle back to a resting weight. Nothing
      // is ever removed — the field only accumulates.
      setTimeout(function () {
        ln.classList.remove("draw");
        ln.classList.add("settled");
        [pair[0], pair[1]].forEach(function (n) {
          nodes[n].classList.remove("active");
          nodes[n].classList.add("linked");
        });
      }, 2900);

      return true;
    }

    // Fraunces arrives late and moves everything, so wait for it.
    if (document.fonts && document.fonts.ready) {
      document.fonts.ready.then(start);
      setTimeout(start, 1200); // in case fonts never resolve
    } else {
      start();
    }

    var started = false;

    function start() {
      if (started) return;   // fonts.ready and the fallback both call this
      build();
      if (!built) return;
      started = true;

      if (reduced) {
        while (reveal()) {}
        while (connect()) {}
        return;
      }

      var onScreen = true;
      if ("IntersectionObserver" in window) {
        new IntersectionObserver(function (es) {
          onScreen = es[0].isIntersecting;
        }, { threshold: 0 }).observe(svg.parentNode);
      }

      // Start with a few dots already on the table, nothing joined yet.
      for (var s0 = 0; s0 < 5; s0++) reveal();

      var misses = 0;
      var tick = setInterval(function () {
        if (!onScreen || document.hidden) return;

        // Keep collecting ahead of connecting, so there is always
        // somewhere new for a line to go.
        var moreDots = shown.length < nodes.length;
        var wantDot = moreDots && (shown.length < 8 || Math.random() < 0.45);

        var did = wantDot ? reveal() : connect();
        if (!did) did = wantDot ? connect() : reveal();

        if (did) misses = 0;
        else if (++misses > 6) clearInterval(tick); // nothing left to do
      }, 1500);
    }
  })();

  /* =======================================================
     3. Index filters
     ======================================================= */

  (function filters() {
    var chips = Array.prototype.slice.call(document.querySelectorAll(".chip[data-filter]"));
    var groups = Array.prototype.slice.call(document.querySelectorAll(".ix-group[data-group]"));
    if (!chips.length || !groups.length) return;

    chips.forEach(function (chip) {
      chip.addEventListener("click", function () {
        // a chip may cover more than one group, e.g. "show pod"
        var want = chip.getAttribute("data-filter").split(" ");
        chips.forEach(function (c) {
          c.setAttribute("aria-pressed", c === chip ? "true" : "false");
        });
        groups.forEach(function (g) {
          g.hidden = want[0] !== "all" &&
                     want.indexOf(g.getAttribute("data-group")) === -1;
        });
      });
    });
  })();

  /* =======================================================
     4. Dot rail scrollspy
     ======================================================= */

  (function rail() {
    var sections = Array.prototype.slice.call(document.querySelectorAll(".section[id]"));
    var links = Array.prototype.slice.call(document.querySelectorAll(".rail a, .strip a"));
    if (!sections.length || !links.length) return;

    var queued = false;

    // Whichever section owns the middle of the screen wins. Measured on
    // scroll rather than observed, so it is right on the first paint and
    // stays right after the webfonts reflow the page.
    function paint() {
      queued = false;
      var line = window.innerHeight / 2;
      var current = null;

      for (var k = 0; k < sections.length; k++) {
        var r = sections[k].getBoundingClientRect();
        if (r.top <= line && r.bottom > line) { current = sections[k].id; break; }
      }

      links.forEach(function (a) {
        if (current && a.getAttribute("href") === "#" + current) {
          a.setAttribute("aria-current", "true");
        } else {
          a.removeAttribute("aria-current");
        }
      });
    }

    function schedule() {
      if (queued) return;
      queued = true;
      requestAnimationFrame(paint);
    }

    window.addEventListener("scroll", schedule, { passive: true });
    window.addEventListener("resize", schedule, { passive: true });
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(schedule);
    paint();
  })();
})();
