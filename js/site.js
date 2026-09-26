/* turoczy.co — three jobs only:
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
        // getClientRects() on a block element gives ONE rect around the
        // whole block, which reserves all the empty space beside short
        // lines. A Range over its contents gives a rect per line
        // fragment instead; merge the fragments that share a line and
        // the gaps beside short lines open up.
        var rects;
        try {
          var rng = document.createRange();
          rng.selectNodeContents(el);
          var frags = rng.getClientRects();
          var rows = [];
          for (var fi = 0; fi < frags.length; fi++) {
            var fr = frags[fi];
            if (!fr.width || !fr.height) continue;
            // Group by line CENTRE, not by overlap: at display sizes a
            // glyph box is taller than the line-height, so consecutive
            // lines overlap and an overlap test collapses them all back
            // into one block — which is the bug this is fixing.
            var hit = null;
            var fc = (fr.top + fr.bottom) / 2;
            for (var ri = 0; ri < rows.length; ri++) {
              var rc = (rows[ri].top + rows[ri].bottom) / 2;
              var tol = Math.max(4, Math.min(fr.bottom - fr.top,
                                             rows[ri].bottom - rows[ri].top) * 0.45);
              if (Math.abs(fc - rc) < tol) { hit = rows[ri]; break; }
            }
            if (hit) {
              hit.left = Math.min(hit.left, fr.left);
              hit.right = Math.max(hit.right, fr.right);
              hit.top = Math.min(hit.top, fr.top);
              hit.bottom = Math.max(hit.bottom, fr.bottom);
            } else {
              rows.push({ left: fr.left, right: fr.right,
                          top: fr.top, bottom: fr.bottom });
            }
          }
          rects = rows.length ? rows : el.getClientRects();
        } catch (err) {
          rects = el.getClientRects();
        }

        for (var i = 0; i < rects.length; i++) {
          var r = rects[i];
          var rw = r.width !== undefined ? r.width : r.right - r.left;
          var rh = r.height !== undefined ? r.height : r.bottom - r.top;
          if (!rw || !rh) continue;
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
      return boxIndexAt(x, y) !== -1;
    }

    // Which line of type a point falls in, or -1. A punctuation dot is
    // allowed to thread out through its own line — that is where it
    // lives — but never across any other.
    function boxIndexAt(x, y) {
      for (var i = 0; i < boxes.length; i++) {
        var b = boxes[i];
        if (x > b.x1 && x < b.x2 && y > b.y1 && y < b.y2) return i;
      }
      return -1;
    }

    function overTypeExcept(x, y, skip) {
      var i = boxIndexAt(x, y);
      return i !== -1 && i !== skip;
    }

    // --- The matrix --------------------------------------------------
    var MAX_DEGREE = 5;   // woven: every dot ends up joined several ways
    var dots = [], nodes = [], pairs = [];
    var degree = {}, used = {}, drawn = 0, target = 0;
    var hub = null, hubPairs = [], hubUsed = {}, hubDrawn = 0, hubTarget = 0;
    var hubLinked = {};   // dots Rick has reached; these interconnect first
    var built = false;
    var ellShown = {};   // the three ellipsis dots, by index
    var ellDots2 = {};   // same set, visible to connectHub()
    var ellBox = {};     // the line of type each punctuation dot sits in
    var ellDots = {};    // punctuation dots, by index

    function build() {
      if (built) return;
      measure();
      if (!boxes.length) return;
      built = true;

      // The ellipsis after "innovation" is three real dots. Put them in
      // first, at the glyph's own position, so the sentence trails off
      // straight into the network.
      ellDots = {};
      var glyphs = document.querySelectorAll(".hero .ell");
      var ctm0 = svg.getScreenCTM();
      if (glyphs.length && ctm0) {
        var inv0 = ctm0.inverse();
        var ep = svg.createSVGPoint();
        Array.prototype.forEach.call(glyphs, function (g) {
          var er = g.getBoundingClientRect();
          if (!er.width) return;
          var n = parseInt(g.getAttribute("data-dots"), 10) || 1;
          for (var ei = 0; ei < n; ei++) {
            ep.x = er.left + er.width * (ei + 0.5) / n;
            ep.y = er.top + er.height * 0.78;   // sits on the baseline
            var ec = ep.matrixTransform(inv0);
            ellDots[dots.length] = true;
            ellBox[dots.length] = boxIndexAt(ec.x, ec.y);
            ellShown[dots.length] = true;
            ellDots2[dots.length] = true;
            dots.push({ x: ec.x, y: ec.y });
          }
        });
      }

      // Place the rest only where there is room for them, spread out, so
      // the matrix reaches the whole field instead of bunching up beside
      // the headline.
      var guard = 0;
      while (dots.length < 120 && guard++ < 30000) {
        var x = 30 + rnd() * (W - 60);
        var y = 24 + rnd() * (H - 48);
        if (overType(x, y)) continue;
        var ok = true;
        for (var k = 0; k < dots.length; k++) {
          if (Math.hypot(dots[k].x - x, dots[k].y - y) < 28) { ok = false; break; }
        }
        if (ok) dots.push({ x: x, y: y });
      }

      // Created, but not yet collected — reveal() brings them in one by one.
      nodes = dots.map(function (d, di) {
        var n = document.createElementNS(NS, "circle");
        n.setAttribute("cx", d.x);
        n.setAttribute("cy", d.y);
        n.setAttribute("r", 3);
        // The ellipsis dots are drawn by the typeface, not by us.
        n.setAttribute("class", ellDots[di] ? "node ellnode" : "node");
        svg.appendChild(n);
        return n;
      });

      for (var a = 0; a < dots.length; a++) {
        for (var b = a + 1; b < dots.length; b++) {
          var d = Math.hypot(dots[b].x - dots[a].x, dots[b].y - dots[a].y);
          // Long edges would have to cross the type to get anywhere.
          // A punctuation dot may thread out through the line it sits
          // in — it belongs to that line — but not across any other.
          var mx = (dots[a].x + dots[b].x) / 2;
          var my = (dots[a].y + dots[b].y) / 2;
          var skip = -1;
          if (ellDots[a] && !ellDots[b]) skip = ellBox[a];
          else if (ellDots[b] && !ellDots[a]) skip = ellBox[b];
          else if (ellDots[a] && ellDots[b]) skip = ellBox[a];
          var ok2 = skip === -1 ? !overType(mx, my)
                                : !overTypeExcept(mx, my, skip);
          if (d > 28 && d < 190 && ok2) {
            pairs.push([a, b, d]);
          }
        }
      }

      target = pairs.length;   // draw every edge the field allows

      // --- The hub: Rick, in the middle of it -------------------------
      // The avatar's centre, in the field's own coordinates. Lines leave
      // from under the disc, so its float never shows a seam.
      var av = document.querySelector(".hero-avatar");
      var ctm2 = svg.getScreenCTM();
      if (av && ctm2) {
        var ar = av.getBoundingClientRect();
        if (ar.width) {
          var inv2 = ctm2.inverse();
          var hp = svg.createSVGPoint();
          hp.x = ar.left + ar.width / 2;
          hp.y = ar.top + ar.height / 2;
          var hc = hp.matrixTransform(inv2);
          hub = { x: hc.x, y: hc.y };
          for (var hi = 0; hi < dots.length; hi++) {
            var hd = Math.hypot(dots[hi].x - hub.x, dots[hi].y - hub.y);
            // The ellipsis always gets a thread to Rick — the sentence
            // trails off and lands on him.
            if (ellDots[hi]) { hubPairs.push([hi, hd]); continue; }
            if (hd > 60 && hd < 430 &&
                !overType((dots[hi].x + hub.x) / 2, (dots[hi].y + hub.y) / 2)) {
              hubPairs.push([hi, hd]);
            }
          }
          hubPairs.sort(function (m, n) {
            var me = ellDots[m[0]] ? 0 : 1, ne = ellDots[n[0]] ? 0 : 1;
            return me - ne || m[1] - n[1];
          });
          hubTarget = Math.min(hubPairs.length, 16);
        }
      }
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

    // A line from Rick to a dot he has collected.
    function connectHub() {
      if (!hub || hubDrawn >= hubTarget) return false;
      var pick = null;
      // The ellipsis threads go first, in order; after that it is the
      // usual scatter of whoever Rick happens to reach next.
      for (var e = 0; e < hubPairs.length && !pick; e++) {
        var ec = hubPairs[e];
        if (!ellDots2[ec[0]] || hubUsed[ec[0]]) continue;
        if ((degree[ec[0]] || 0) >= MAX_DEGREE) continue;
        pick = ec;
      }
      for (var t = 0; t < 60 && !pick; t++) {
        var cand = hubPairs[(Math.random() * hubPairs.length) | 0];
        if (!cand || hubUsed[cand[0]]) continue;
        if (shown.indexOf(cand[0]) === -1) continue;
        if ((degree[cand[0]] || 0) >= MAX_DEGREE) continue;
        pick = cand;
      }
      if (!pick) return false;

      hubUsed[pick[0]] = true;
      hubLinked[pick[0]] = true;
      degree[pick[0]] = (degree[pick[0]] || 0) + 1;
      hubDrawn++;

      var q = dots[pick[0]];
      var ln = document.createElementNS(NS, "line");
      ln.setAttribute("x1", hub.x); ln.setAttribute("y1", hub.y);
      ln.setAttribute("x2", q.x);   ln.setAttribute("y2", q.y);
      ln.style.setProperty("--len", pick[1]);
      ln.setAttribute("class", "hubline");
      svg.insertBefore(ln, svg.firstChild);

      if (reduced) {
        ln.classList.add("settled");
        nodes[pick[0]].classList.add("linked");
        return true;
      }
      nodes[pick[0]].classList.add("active");
      requestAnimationFrame(function () {
        requestAnimationFrame(function () { ln.classList.add("draw"); });
      });
      setTimeout(function () {
        ln.classList.remove("draw");
        ln.classList.add("settled");
        nodes[pick[0]].classList.remove("active");
        nodes[pick[0]].classList.add("linked");
      }, 1200);
      return true;
    }

    // Draw an edge between two dots, whatever the bookkeeping said.
    function drawEdge(a, b, d) {
      used[a + ":" + b] = true;
      used[b + ":" + a] = true;
      degree[a] = (degree[a] || 0) + 1;
      degree[b] = (degree[b] || 0) + 1;

      var p = dots[a], q = dots[b];
      var ln = document.createElementNS(NS, "line");
      ln.setAttribute("x1", p.x); ln.setAttribute("y1", p.y);
      ln.setAttribute("x2", q.x); ln.setAttribute("y2", q.y);
      ln.style.setProperty("--len", d);
      svg.insertBefore(ln, svg.firstChild);

      if (reduced) {
        ln.classList.add("settled");
        nodes[a].classList.add("linked");
        nodes[b].classList.add("linked");
        return;
      }
      nodes[a].classList.add("active");
      nodes[b].classList.add("active");
      requestAnimationFrame(function () {
        requestAnimationFrame(function () { ln.classList.add("draw"); });
      });
      setTimeout(function () {
        ln.classList.remove("draw");
        ln.classList.add("settled");
        [a, b].forEach(function (n) {
          nodes[n].classList.remove("active");
          nodes[n].classList.add("linked");
        });
      }, 1200);
    }

    // The punctuation dots connect to the field, full stop. No type
    // test, no distance test, no waiting for the random draw to notice
    // them: each one is wired to its nearest neighbours up front.
    var GLYPH_LINKS = 4;
    var glyphQueue = null;
    function glyphSeed() {
      if (!built) return false;
      if (glyphQueue === null) {
        glyphQueue = [];
        Object.keys(ellDots).forEach(function (k) {
          var i = +k;
          var near = [];
          for (var j = 0; j < dots.length; j++) {
            if (j === i || ellDots[j]) continue;
            near.push([j, Math.hypot(dots[j].x - dots[i].x, dots[j].y - dots[i].y)]);
          }
          near.sort(function (m, n) { return m[1] - n[1]; });
          for (var g = 0; g < GLYPH_LINKS && g < near.length; g++) {
            glyphQueue.push([i, near[g][0], near[g][1]]);
          }
        });
      }
      while (glyphQueue.length) {
        var e = glyphQueue.shift();
        if (used[e[0] + ":" + e[1]]) continue;
        if (shown.indexOf(e[1]) === -1) { nodes[e[1]].classList.add("shown"); shown.push(e[1]); }
        drawEdge(e[0], e[1], e[2]);
        return true;
      }
      return false;
    }

    // Nobody left behind: any dot still short of two connections gets
    // joined to its nearest reachable neighbour, degree caps ignored.
    // This is the whole point of the picture, so it is not left to luck.
    var MIN_DEGREE = 2;
    function rescue() {
      if (!built) return false;
      for (var i = 0; i < dots.length; i++) {
        if ((degree[i] || 0) >= MIN_DEGREE) continue;
        var best = -1, bestD = Infinity;
        for (var j = 0; j < dots.length; j++) {
          if (j === i || used[i + ":" + j]) continue;
          var d = Math.hypot(dots[j].x - dots[i].x, dots[j].y - dots[i].y);
          if (d < 28 || d >= bestD) continue;
          var mx = (dots[i].x + dots[j].x) / 2, my = (dots[i].y + dots[j].y) / 2;
          var skip = ellDots[i] ? ellBox[i] : (ellDots[j] ? ellBox[j] : -1);
          var blocked = skip === -1 ? overType(mx, my)
                                    : overTypeExcept(mx, my, skip);
          if (blocked) continue;
          best = j; bestD = d;
        }
        if (best === -1) continue;
        if (shown.indexOf(i) === -1) { nodes[i].classList.add("shown"); shown.push(i); }
        if (shown.indexOf(best) === -1) { nodes[best].classList.add("shown"); shown.push(best); }
        drawEdge(i, best, bestD);
        return true;
      }
      return false;
    }

    function connect() {
      if (!built || drawn >= target) return false;

      // The point of the whole thing: once Rick has reached two people,
      // they start finding each other. Those pairs go first; everything
      // else fills in behind them.
      var pair = null;
      function eligible(c) {
        if (!c || used[c[0] + ":" + c[1]]) return false;
        if (shown.indexOf(c[0]) === -1 || shown.indexOf(c[1]) === -1) return false;
        if ((degree[c[0]] || 0) >= MAX_DEGREE) return false;
        if ((degree[c[1]] || 0) >= MAX_DEGREE) return false;
        return true;
      }

      for (var hp = 0; hp < 120 && !pair; hp++) {
        var hc = pairs[(Math.random() * pairs.length) | 0];
        if (eligible(hc) && hubLinked[hc[0]] && hubLinked[hc[1]]) pair = hc;
      }
      for (var tries = 0; tries < 120 && !pair; tries++) {
        var c = pairs[(Math.random() * pairs.length) | 0];
        if (eligible(c)) pair = c;
      }
      // Nothing at random: sweep for anything still legal, poorest dots
      // first, so no dot is left hanging just because it got unlucky.
      if (!pair) {
        var best = null, bestDeg = 99;
        for (var z = 0; z < pairs.length; z++) {
          var cz = pairs[z];
          if (!eligible(cz)) continue;
          var dg = Math.min(degree[cz[0]] || 0, degree[cz[1]] || 0);
          if (dg < bestDeg) { bestDeg = dg; best = cz; if (!dg) break; }
        }
        pair = best;
      }
      if (!pair) return false;
      used[pair[0] + ":" + pair[1]] = true;

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
      }, 1200);

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
        while (connectHub()) {}
        while (glyphSeed()) {}
        while (connect()) {}
        while (rescue()) {}
        return;
      }

      var onScreen = true;
      if ("IntersectionObserver" in window) {
        new IntersectionObserver(function (es) {
          onScreen = es[0].isIntersecting;
        }, { threshold: 0 }).observe(svg.parentNode);
      }

      // Start with a few dots already on the table, nothing joined yet.
      // The ellipsis is already part of the sentence, so it is already
      // on the table.
      for (var e0 = 0; e0 < dots.length; e0++) {
        if (ellShown[e0]) { nodes[e0].classList.add("shown"); shown.push(e0); }
      }
      for (var s0 = 0; s0 < 22; s0++) reveal();

      var misses = 0;
      var tick = setInterval(function () {
        if (!onScreen || document.hidden) return;

        // Keep collecting ahead of connecting, so there is always
        // somewhere new for a line to go.
        var moreDots = shown.length < nodes.length;
        var wantDot = moreDots && Math.random() < 0.5;

        // Rick reaches out first; after that his lines are an
        // occasional thread through the ordinary dot-to-dot work.
        var wantHub = hub && hubDrawn < hubTarget &&
                      (hubDrawn < 3 ? shown.length >= 3 : Math.random() < 0.25);

        var did = wantHub ? connectHub() : glyphSeed();
        if (!did) did = wantDot ? reveal() : connect();
        if (!did) did = wantDot ? connect() : reveal();
        if (!did) did = connectHub();
        if (!did) did = rescue();   // finish the job for any stragglers

        if (did) misses = 0;
        else if (++misses > 6) clearInterval(tick); // nothing left to do
      }, 240);
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

/* ---------- Footer copyright year ---------- */
(function () {
  var el = document.getElementById("copyright-year");
  if (el) el.textContent = new Date().getFullYear();
})();
