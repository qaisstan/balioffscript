// Land budget explorer. No dependencies.
//
// Drag a budget and see how much land it leases in each area. The point is
// not precision — prices move street by street — it is the shape of the
// trade-off, which is very hard to feel from a table of numbers.

(function () {
  var root = document.getElementById("land");
  if (!root) return;

  // USD per are (100 m²), leasehold, per the term. Ranges as published on
  // the areas pages — treat as a starting point, not a valuation.
  var AREAS = [
    { n: "Berawa",            lo: 75000, hi: 90000,  r: "Badung", note: "Deepest liquidity, most saturated" },
    { n: "Pererenan / Cemagi", lo: 55000, hi: 75000, r: "Badung", note: "Where Canggu money moved" },
    { n: "Uluwatu clifftop",  lo: 40000, hi: 60000,  r: "Badung", note: "Highest rates, hardest setbacks" },
    { n: "Uluwatu inland",    lo: 25000, hi: 40000,  r: "Badung", note: "The Bukit without the cliff premium" },
    { n: "Sanur",             lo: 30000, hi: 45000,  r: "Denpasar", note: "Fastest permits on the island" },
    { n: "Ubud",              lo: 25000, hi: 40000,  r: "Gianyar", note: "Longer stays, lower rates" },
    { n: "Tabanan coast",     lo: 18000, hi: 30000,  r: "Tabanan", note: "Toll road catalyst, hardest licensing" }
  ];

  var fmtUSD = function (n) {
    return "$" + Math.round(n).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  };

  var slider = root.querySelector("#land-budget");
  var out = root.querySelector("#land-rows");
  var readout = root.querySelector("#land-read");

  function render() {
    var budget = parseInt(slider.value, 10);
    readout.textContent = fmtUSD(budget);

    // Scale bars against the largest plot any area yields at this budget.
    var maxAre = 0;
    AREAS.forEach(function (a) {
      maxAre = Math.max(maxAre, budget / a.lo);
    });

    out.innerHTML = AREAS.map(function (a) {
      var areLo = budget / a.hi;          // fewer are at the top of the range
      var areHi = budget / a.lo;          // more are at the bottom
      var m2Lo = areLo * 100, m2Hi = areHi * 100;
      var w = Math.max(1.5, (areHi / maxAre) * 100);
      var wLo = Math.max(1, (areLo / maxAre) * 100);
      // A 500 m² plot is roughly the minimum for a two-bedroom villa with a pool.
      var viable = m2Lo >= 300;
      return '<div class="lx-row">' +
        '<div class="lx-head"><span class="lx-n">' + a.n + '</span>' +
        '<span class="lx-r">' + a.r + '</span></div>' +
        '<div class="lx-track">' +
          '<div class="lx-bar' + (viable ? "" : " lx-bar-thin") + '" style="width:' + w + '%">' +
            '<div class="lx-bar-in" style="width:' + (wLo / w * 100) + '%"></div>' +
          '</div>' +
        '</div>' +
        '<div class="lx-foot"><span class="lx-m2">' +
          Math.round(m2Lo).toLocaleString() + "–" + Math.round(m2Hi).toLocaleString() +
          ' m²</span><span class="lx-note">' + a.note + "</span></div>" +
      "</div>";
    }).join("");

    var best = AREAS.map(function (a) { return { n: a.n, m2: (budget / a.hi) * 100 }; })
                    .sort(function (x, y) { return y.m2 - x.m2; })[0];
    var tight = AREAS.filter(function (a) { return (budget / a.hi) * 100 < 300; });
    var msg = "At " + fmtUSD(budget) + ", " + best.n + " gives you the most ground — about " +
              Math.round(best.m2).toLocaleString() + " m² at the top of its range.";
    if (tight.length) {
      msg += " " + tight.length + " of these areas would not reach 300 m², which is tight for a villa with a pool once setbacks come off.";
    }
    root.querySelector("#land-msg").textContent = msg;
  }

  slider.addEventListener("input", render);
  render();
})();
