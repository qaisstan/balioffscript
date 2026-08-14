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
