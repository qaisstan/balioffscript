// Search + mobile nav. No dependencies, no server.

(function () {
  var btn = document.querySelector(".menu-btn");
  var nav = document.querySelector(".nav");
  if (btn && nav) {
    btn.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      btn.setAttribute("aria-expanded", open);
      btn.textContent = open ? "Close" : "Menu";
    });
  }

  // Reveal sections on scroll. Anything not reached stays visible if the
  // observer is unavailable, so content is never hidden by a script failure.
  var targets = document.querySelectorAll(
    ".warn-wrap, .ledger-wrap, .who-wrap, .cards, .chart, .sec-h, .chk"
  );
  if (targets.length && "IntersectionObserver" in window &&
      !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    targets.forEach(function (el) { el.classList.add("reveal"); });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.06 });
    targets.forEach(function (el) { io.observe(el); });
  }

  // Reading progress on article pages. Cheap, and it measurably increases
  // how far people get down a long page.
  var prose = document.querySelector(".article .prose");
  if (prose && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    var bar = document.createElement("div");
    bar.className = "progress";
    document.body.appendChild(bar);
    var tick = function () {
      var r = prose.getBoundingClientRect();
      var total = r.height - window.innerHeight;
      var done = total > 0 ? Math.min(1, Math.max(0, -r.top / total)) : 0;
      bar.style.width = (done * 100).toFixed(1) + "%";
    };
    window.addEventListener("scroll", tick, { passive: true });
    window.addEventListener("resize", tick);
    tick();
  }

  var input = document.getElementById("q");
  if (!input) return;

  var results = document.getElementById("results");
  var hits = document.getElementById("hits");
  var data = [];

  fetch((window.SITE_BASE || "") + "/search-index.json")
    .then(function (r) { return r.json(); })
    .then(function (j) {
      data = j;
      var q = new URLSearchParams(location.search).get("q");
      if (q) { input.value = q; run(q); }
    })
    .catch(function () {
      hits.textContent = "Search index unavailable. Run build.py.";
    });

  function score(item, terms) {
    var t = item.t.toLowerCase(), s = item.s.toLowerCase(), b = item.b.toLowerCase();
    var n = 0;
    for (var i = 0; i < terms.length; i++) {
      var w = terms[i];
      if (!w) continue;
      if (t.indexOf(w) > -1) n += 10;
      else if (s.indexOf(w) > -1) n += 4;
      else if (b.indexOf(w) > -1) n += 1;
      else return 0;
    }
    return n;
  }

  function run(q) {
    var terms = q.toLowerCase().trim().split(/\s+/);
    if (!terms[0]) { results.innerHTML = ""; hits.textContent = ""; return; }

    var out = data
      .map(function (d) { return { d: d, n: score(d, terms) }; })
      .filter(function (x) { return x.n > 0; })
      .sort(function (a, b) { return b.n - a.n; })
      .slice(0, 25);

    hits.textContent = out.length ? out.length + " result" + (out.length === 1 ? "" : "s") : "No results";
    results.innerHTML = out.map(function (x) {
      return '<li class="card"><a href="' + x.d.u + '"><h3>' + x.d.t + "</h3><p>" + x.d.s + "</p></a></li>";
    }).join("");
  }

  var timer;
  input.addEventListener("input", function () {
    clearTimeout(timer);
    timer = setTimeout(function () { run(input.value); }, 120);
  });
})();

// Share row: use the phone's native share sheet where it exists, and fall
// back to copying the link so the button always does something.
(function () {
  document.querySelectorAll(".sh-more").forEach(function (btn) {
    var bar = btn.closest(".sh");
    btn.addEventListener("click", function () {
      var data = { title: bar.dataset.title, url: bar.dataset.url };
      if (navigator.share) { navigator.share(data).catch(function () {}); return; }
      var done = function () {
        var was = btn.getAttribute("aria-label");
        btn.classList.add("ok");
        btn.setAttribute("aria-label", "Link copied");
        setTimeout(function () { btn.classList.remove("ok"); btn.setAttribute("aria-label", was); }, 1600);
      };
      if (navigator.clipboard) { navigator.clipboard.writeText(data.url).then(done, function () {}); }
      else {
        var i = document.createElement("input");
        i.value = data.url; document.body.appendChild(i); i.select();
        try { document.execCommand("copy"); done(); } catch (e) {}
        document.body.removeChild(i);
      }
    });
  });
})();

// Table of contents follows the reader. Reading a rect on a throttled scroll
// is cheaper here than an observer per heading, and it keeps the last section
// highlighted once the reader is past every heading.
(function () {
  var links = Array.prototype.slice.call(
    document.querySelectorAll(".art-rail .toc a")
  );
  if (!links.length) return;

  var heads = links.map(function (a) {
    try {
      return document.getElementById(decodeURIComponent(a.hash.slice(1)));
    } catch (e) { return null; }
  });

  var queued = false;
  function paint() {
    queued = false;
    var cur = 0;
    for (var n = 0; n < heads.length; n++) {
      if (heads[n] && heads[n].getBoundingClientRect().top <= 140) cur = n;
    }
    links.forEach(function (a, n) {
      if (n === cur) { a.classList.add("on"); } else { a.classList.remove("on"); }
    });
  }

  window.addEventListener("scroll", function () {
    if (!queued) { queued = true; requestAnimationFrame(paint); }
  }, { passive: true });
  paint();
})();

// A question in the rail opens its answer rather than dropping the reader at
// a collapsed row they then have to click a second time.
(function () {
  function open(hash) {
    if (!hash || hash.charAt(0) !== "#") return;
    var el;
    try { el = document.getElementById(decodeURIComponent(hash.slice(1))); }
    catch (e) { return; }
    if (!el || el.tagName !== "DETAILS") return;
    el.open = true;
    el.classList.add("hit");
    setTimeout(function () { el.classList.remove("hit"); }, 1600);
  }
  document.addEventListener("click", function (e) {
    var a = e.target.closest ? e.target.closest('.rail-q a') : null;
    if (a) open(a.hash);
  });
  window.addEventListener("hashchange", function () { open(location.hash); });
  open(location.hash);
})();
