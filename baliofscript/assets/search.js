// Search + mobile nav. No dependencies, no server.

(function () {
  var btn = document.querySelector(".menu-btn");
  var nav = document.querySelector(".nav");
  if (btn && nav) {
    btn.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      btn.setAttribute("aria-expanded", open);
    });
  }

  var input = document.getElementById("q");
  if (!input) return;

  var results = document.getElementById("results");
  var hits = document.getElementById("hits");
  var data = [];

  fetch("/search-index.json")
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
