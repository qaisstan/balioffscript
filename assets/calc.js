// Bali property return model. No dependencies, charts drawn as inline SVG.
//
// Universal across tenure (leasehold / HGB / freehold-equivalent), asset type
// (villa, apartment, guesthouse) and revenue model (nightly or long-term).
//
// The number the market leaves out: a time-limited right is a wasting asset.
// Whatever the premium buys, it buys for a fixed number of years, and what is
// left at the end is the residual — zero on a plain lease. Amortising that
// against income is the only way to compare a lease to a freehold honestly.

(function () {
  var form = document.getElementById("calc");
  if (!form) return;

  // ---------------------------------------------------------------- helpers

  var money = function (n) {
    var neg = n < 0;
    n = Math.abs(n);
    var s = n >= 1000000 ? (n / 1000000).toFixed(2) + "M"
          : n >= 1000 ? Math.round(n / 1000) + "k"
          : Math.round(n).toString();
    return (neg ? "−$" : "$") + s;
  };
  var full = function (n) {
    var neg = n < 0;
    n = Math.abs(Math.round(n));
    return (neg ? "−$" : "$") + n.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  };
  var pct = function (n) { return (n * 100).toFixed(1) + "%"; };
  var num = function (id) {
    var el = document.getElementById(id);
    if (!el) return 0;
    var v = parseFloat(el.value);
    return isNaN(v) ? 0 : v;
  };
  var setv = function (id, v) { var e = document.getElementById(id); if (e) e.value = v; };
  var set = function (id, txt, cls) {
    var el = document.getElementById(id);
    if (!el) return;
    el.textContent = txt;
    el.className = "calc-v" + (cls ? " " + cls : "");
  };
  var show = function (sel, on) {
    document.querySelectorAll(sel).forEach(function (el) { el.style.display = on ? "" : "none"; });
  };
  var radio = function (name) {
    var el = form.querySelector('input[name="' + name + '"]:checked');
    return el ? el.value : "";
  };

  // ---------------------------------------------------------------- presets

  // Starting points only — deliberately mid-range, not promotional.
  var PRESETS = {
    villa:     { adr: 180, occ: 65, opex: 1200, mgmt: 20, price: 300000, ffe: 35000, rent: 2200 },
    apartment: { adr: 95,  occ: 70, opex: 450,  mgmt: 18, price: 150000, ffe: 15000, rent: 1100 },
    guesthouse:{ adr: 120, occ: 62, opex: 2600, mgmt: 22, price: 550000, ffe: 70000, rent: 4000 }
  };
  // Residual: what the asset is worth to you when the term ends.
  var RESIDUAL = { lease: 0, hgb: 60, freehold: 100 };

  var touched = {};
  form.addEventListener("input", function (e) {
    if (e.target.id) touched[e.target.id] = true;
  });

  function applyPreset() {
    var p = PRESETS[radio("asset")];
    if (!p) return;
    ["adr", "occ", "opex", "mgmt", "price", "ffe", "rent"].forEach(function (k) {
      if (!touched[k]) setv(k, p[k]);
    });
  }

  // ---------------------------------------------------------------- model

  function model() {
    var tenure = radio("tenure");
    var nightly = radio("revmode") === "nightly";
    var years = Math.max(1, Math.round(num("years")));
    if (tenure === "freehold") years = Math.max(years, 1);

    var price = num("price"), build = num("build"), ffe = num("ffe");
    var invested = price + build + ffe + price * (num("tx") / 100);

    var gross = nightly
      ? num("adr") * 365 * (num("occ") / 100)
      : num("rent") * 12 * (1 - num("vacancy") / 100);

    var otaR = nightly ? num("ota") / 100 : 0;
    var d = {
      otaR: otaR, pb1R: num("pb1") / 100, mgmtR: num("mgmt") / 100,
      opex: num("opex") * 12, capexR: num("capex") / 100, taxR: num("tax_rate") / 100
    };

    function yearNet(g) {
      var ota = g * d.otaR, pb1 = g * d.pb1R;
      var netRev = g - ota - pb1;
      var mgmt = netRev * d.mgmtR;
      var capex = g * d.capexR;
      var noi = netRev - mgmt - d.opex - capex;
      var tax = noi > 0 ? noi * d.taxR : 0;
      return { ota: ota, pb1: pb1, netRev: netRev, mgmt: mgmt, capex: capex,
               opexAnnual: d.opex, noi: noi, tax: tax, net: noi - tax };
    }

    var y1 = yearNet(gross);
    var residualR = num("residual") / 100;
    var residual = invested * residualR;
    var amort = (invested - residual) / years;
    var growth = num("growth") / 100;

    // Year-by-year series for the charts.
    var series = [], cum = -invested, g = gross, payback = 0;
    for (var i = 1; i <= years; i++) {
      var yr = yearNet(g);
      cum += yr.net;
      if (payback === 0 && cum >= 0) payback = i;
      series.push({ year: i, net: yr.net, cum: cum, value: invested - amort * i });
      g = g * (1 + growth);
    }
    var cumWithResidual = cum + residual;

    return {
      tenure: tenure, nightly: nightly, years: years, invested: invested,
      gross: gross, y1: y1, residual: residual, amort: amort,
      series: series, payback: payback, cumWithResidual: cumWithResidual,
      grossYield: invested > 0 ? gross / invested : 0,
      netYield: invested > 0 ? y1.net / invested : 0,
      realYield: invested > 0 ? (y1.net - amort) / invested : 0,
      breakEven: breakEven(d, gross)
    };
  }

  // Occupancy (or rent) fraction at which net profit reaches zero.
  function breakEven(d, gross) {
    function at(f) {
      var g = gross * f;
      var netRev = g - g * d.otaR - g * d.pb1R;
      return netRev - netRev * d.mgmtR - d.opex - g * d.capexR;
    }
    if (at(1 / Math.max(0.0001, 1)) <= 0 && at(3) <= 0) return null;
    var lo = 0, hi = 3, mid;
    if (at(hi) <= 0) return null;
    for (var i = 0; i < 50; i++) { mid = (lo + hi) / 2; if (at(mid) > 0) hi = mid; else lo = mid; }
    return hi;
  }

  // ---------------------------------------------------------------- charts

  var DEFS =
    '<defs>' +
    '<linearGradient id="gInk" x1="0" y1="0" x2="0" y2="1">' +
    '<stop offset="0%" stop-color="#14181f" stop-opacity="0.20"/>' +
    '<stop offset="100%" stop-color="#14181f" stop-opacity="0.02"/></linearGradient>' +
    '<linearGradient id="gSeal" x1="0" y1="0" x2="0" y2="1">' +
    '<stop offset="0%" stop-color="#9e2b20" stop-opacity="0.22"/>' +
    '<stop offset="100%" stop-color="#9e2b20" stop-opacity="0.02"/></linearGradient>' +
    "</defs>";

  function svg(w, h, inner, cls) {
    return '<svg viewBox="0 0 ' + w + ' ' + h + '" class="cx ' + (cls || "") +
           '" role="img" preserveAspectRatio="xMidYMid meet">' + DEFS + inner + "</svg>";
  }

  // Horizontal gridlines with value labels down the left gutter.
  function grid(L, W, R, T, ph, min, max, y) {
    var out = "", steps = 4;
    for (var i = 0; i <= steps; i++) {
      var v = min + ((max - min) * i) / steps;
      var yy = y(v).toFixed(1);
      out += '<line x1="' + L + '" y1="' + yy + '" x2="' + (W - R) + '" y2="' + yy + '" class="cx-grid"/>';
      out += '<text x="' + (L - 6) + '" y="' + (parseFloat(yy) + 3).toFixed(1) + '" class="cx-t cx-end">' + money(v) + "</text>";
    }
    return out;
  }

  // Cumulative position: capital returned over the term.
  function chartCum(m) {
    var W = 560, H = 220, L = 62, R = 12, T = 14, B = 28;
    var pw = W - L - R, ph = H - T - B;
    var vals = m.series.map(function (s) { return s.cum; }).concat([-m.invested, m.cumWithResidual]);
    var min = Math.min.apply(null, vals), max = Math.max.apply(null, vals);
    if (max === min) max = min + 1;
    var pad = (max - min) * 0.08; min -= pad; max += pad;
    var x = function (i) { return L + (pw * i) / Math.max(1, m.years); };
    var y = function (v) { return T + ph - ((v - min) / (max - min)) * ph; };

    var pts = [[x(0), y(-m.invested)]].concat(m.series.map(function (s) { return [x(s.year), y(s.cum)]; }));
    var line = pts.map(function (p, i) { return (i ? "L" : "M") + p[0].toFixed(1) + " " + p[1].toFixed(1); }).join(" ");
    var area = line + " L" + x(m.years).toFixed(1) + " " + y(Math.max(min, 0)).toFixed(1) +
               " L" + x(0).toFixed(1) + " " + y(Math.max(min, 0)).toFixed(1) + " Z";

    var g = grid(L, W, R, T, ph, min, max, y);
    g += '<path d="' + area + '" class="cx-area"/><path d="' + line + '" class="cx-line"/>';
    if (min < 0 && max > 0) {
      g += '<line x1="' + L + '" y1="' + y(0).toFixed(1) + '" x2="' + (W - R) + '" y2="' + y(0).toFixed(1) + '" class="cx-zero"/>';
    }
    // Residual step at expiry — the cliff on a wasting asset.
    if (m.residual > 0) {
      g += '<line x1="' + x(m.years).toFixed(1) + '" y1="' + y(m.series[m.years - 1].cum).toFixed(1) +
           '" x2="' + x(m.years).toFixed(1) + '" y2="' + y(m.cumWithResidual).toFixed(1) + '" class="cx-res"/>';
    }
    var endY = y(m.cumWithResidual);
    g += '<circle cx="' + x(m.years).toFixed(1) + '" cy="' + endY.toFixed(1) + '" r="3.5" class="' +
         (m.cumWithResidual >= 0 ? "cx-dot-ok" : "cx-dot-bad") + '"/>';
    // End-position badge
    var bw = 62, bx = Math.min(W - R - bw, x(m.years) - bw / 2), by = Math.max(T, endY - 22);
    g += '<rect x="' + bx.toFixed(1) + '" y="' + by.toFixed(1) + '" width="' + bw + '" height="14" rx="2" class="cx-badge"/>' +
         '<text x="' + (bx + bw / 2).toFixed(1) + '" y="' + (by + 10).toFixed(1) + '" class="cx-badge-t cx-mid">' +
         money(m.cumWithResidual) + "</text>";
    if (m.payback) {
      g += '<line x1="' + x(m.payback).toFixed(1) + '" y1="' + T + '" x2="' + x(m.payback).toFixed(1) +
           '" y2="' + (T + ph) + '" class="cx-mark"/>' +
           '<text x="' + (x(m.payback) + 4).toFixed(1) + '" y="' + (T + 10) + '" class="cx-t">even, yr ' + m.payback + "</text>";
    }
    g += '<text x="' + L + '" y="' + (H - 8) + '" class="cx-t">year 1</text>';
    g += '<text x="' + (W - R) + '" y="' + (H - 8) + '" class="cx-t cx-end">year ' + m.years + "</text>";
    return svg(W, H, g);
  }

  // Where a year of revenue actually goes: one bar, split by claimant.
  function chartSplit(m) {
    var W = 560, T = 26, BAR = 30;
    var y1 = m.y1;
    if (m.gross <= 0) return svg(W, 60, '<text x="0" y="34" class="cx-t">No revenue at these inputs</text>');

    var segs = [
      ["Platform", y1.ota, "s1"],
      ["PB1", y1.pb1, "s2"],
      ["Management", y1.mgmt, "s3"],
      ["Running costs", m.y1.opexAnnual, "s4"],
      ["Refurb reserve", y1.capex, "s5"],
      ["Tax", y1.tax, "s6"],
      ["Yours", Math.max(0, y1.net), "s7"]
    ].filter(function (s) { return s[1] > 0; });

    var total = segs.reduce(function (a, s) { return a + s[1]; }, 0) || 1;
    var x = 0, bars = "", legend = "", rows = 0;
    segs.forEach(function (s) {
      var w = (s[1] / total) * W;
      bars += '<rect x="' + x.toFixed(1) + '" y="' + T + '" width="' + Math.max(0.5, w).toFixed(1) +
              '" height="' + BAR + '" class="cx-seg ' + s[2] + '"><title>' + s[0] + ": " + full(s[1]) +
              " (" + ((s[1] / total) * 100).toFixed(1) + "%)</title></rect>";
      // Label inside the segment when it is wide enough to read.
      if (w > 54) {
        bars += '<text x="' + (x + w / 2).toFixed(1) + '" y="' + (T + 19) +
                '" class="cx-badge-t cx-mid">' + Math.round((s[1] / total) * 100) + "%</text>";
      }
      x += w;
    });
    segs.forEach(function (s, i) {
      var col = i % 3, row = Math.floor(i / 3);
      rows = Math.max(rows, row + 1);
      legend += '<rect x="' + (col * 186) + '" y="' + (T + BAR + 14 + row * 17) + '" width="9" height="9" class="cx-seg ' + s[2] + '"/>' +
                '<text x="' + (col * 186 + 14) + '" y="' + (T + BAR + 22 + row * 17) + '" class="cx-t">' +
                s[0] + " " + money(s[1]) + "</text>";
    });
    var head = '<text x="0" y="14" class="cx-t-b">' + full(m.gross) + " gross</text>" +
               '<text x="' + W + '" y="14" class="cx-t-b cx-end">' + full(Math.max(0, y1.net)) + " to you</text>";
    return svg(W, T + BAR + 20 + rows * 17, head + bars + legend);
  }

  // The depreciation curve — what the right itself is worth as the term runs down.
  function chartValue(m) {
    var W = 560, H = 190, L = 62, R = 12, T = 14, B = 28;
    var pw = W - L - R, ph = H - T - B;
    var max = m.invested || 1;
    var x = function (i) { return L + (pw * i) / Math.max(1, m.years); };
    var y = function (v) { return T + ph - (v / max) * ph; };
    var pts = [[x(0), y(m.invested)]].concat(m.series.map(function (s) { return [x(s.year), y(Math.max(0, s.value))]; }));
    var line = pts.map(function (p, i) { return (i ? "L" : "M") + p[0].toFixed(1) + " " + p[1].toFixed(1); }).join(" ");
    var g = grid(L, W, R, T, ph, 0, max, y);
    g += '<path d="' + line + " L" + x(m.years).toFixed(1) + " " + y(0).toFixed(1) +
         " L" + x(0).toFixed(1) + " " + y(0).toFixed(1) + ' Z" class="cx-area cx-area-warn"/>' +
         '<path d="' + line + '" class="cx-line cx-line-warn"/>';
    g += '<circle cx="' + x(m.years).toFixed(1) + '" cy="' + y(m.residual).toFixed(1) +
         '" r="3.5" class="' + (m.residual > 0 ? "cx-dot-ok" : "cx-dot-bad") + '"/>';
    g += '<text x="' + L + '" y="' + (H - 8) + '" class="cx-t">today</text>';
    g += '<text x="' + (W - R) + '" y="' + (H - 8) + '" class="cx-t cx-end">year ' + m.years + "</text>";
    g += '<text x="' + (L + 8) + '" y="' + (T + 14) + '" class="cx-t-b">−' + full(m.amort) + " a year</text>";
    return svg(W, H, g);
  }

  // ---------------------------------------------------------------- render

  function run() {
    applyPreset();
    var tenure = radio("tenure");
    var nightly = radio("revmode") === "nightly";

    show(".term-only", tenure !== "freehold");
    show(".nightly-only", nightly);
    show(".monthly-only", !nightly);

    if (!touched.residual) setv("residual", RESIDUAL[tenure]);

    var m = model();

    set("o_invested", full(m.invested));
    set("o_gross", full(m.gross));
    set("o_netrev", full(m.y1.netRev));
    set("o_noi", full(m.y1.noi));
    set("o_tax", full(m.y1.tax));
    set("o_net", full(m.y1.net), m.y1.net > 0 ? "ok" : "bad");
    set("o_grossyield", pct(m.grossYield));
    set("o_netyield", pct(m.netYield), m.netYield >= 0.06 ? "ok" : m.netYield >= 0.03 ? "mid" : "bad");

    show("#row_amort", tenure !== "freehold");
    show("#row_real", tenure !== "freehold");
    if (tenure !== "freehold") {
      set("o_amort", full(m.amort) + " / yr");
      set("o_real", pct(m.realYield), m.realYield > 0.03 ? "ok" : m.realYield > 0 ? "mid" : "bad");
    }
    set("o_payback", m.payback ? m.payback + " years" : "not within the term",
        m.payback ? "ok" : "bad");
    set("o_break", m.breakEven === null ? "never covers costs"
        : nightly ? pct(m.breakEven * (num("occ") / 100)) + " occupancy"
                  : pct(m.breakEven) + " of current rent",
        m.breakEven !== null && m.breakEven < 1 ? "ok" : "bad");
    set("o_endpos", full(m.cumWithResidual), m.cumWithResidual > 0 ? "ok" : "bad");

    document.getElementById("chart_cum").innerHTML = chartCum(m);
    document.getElementById("chart_split").innerHTML = chartSplit(m);
    var vw = document.getElementById("chart_value_wrap");
    if (tenure === "freehold") {
      vw.style.display = "none";
    } else {
      vw.style.display = "";
      document.getElementById("chart_value").innerHTML = chartValue(m);
    }

    var notes = [];
    if (tenure === "lease") {
      notes.push("A lease is a wasting asset. After " + m.years +
        " years it returns nothing unless the agreement contains an enforceable, priced extension clause. Check that the clause binds the owner's heirs and successors.");
    }
    if (tenure === "hgb") {
      notes.push("HGB is time-limited, not freehold. The 30 + 20 + 30 framework is available, not automatic: each step needs approval and cost. The residual above assumes renewal succeeds.");
    }
    if (nightly && num("occ") > 75) {
      notes.push("Occupancy above 75% across a full year is optimistic in Bali. Low season is real.");
    }
    if (m.grossYield - m.netYield > 0.04) {
      notes.push("The gap between the advertised gross figure and what you keep is " +
        pct(m.grossYield - m.netYield) + " of your capital every year.");
    }
    if (m.cumWithResidual < 0) {
      notes.push("Over the full term this deal returns less than you put in.");
    }
    var w = document.getElementById("o_warn");
    if (w) w.innerHTML = notes.length ? "<ul><li>" + notes.join("</li><li>") + "</li></ul>" : "";
  }

  // Info toggles
  document.addEventListener("click", function (e) {
    var b = e.target.closest ? e.target.closest(".info") : null;
    if (!b) return;
    e.preventDefault();
    var box = b.closest(".f").querySelector(".f-h");
    if (!box) return;
    var open = box.hasAttribute("hidden");
    if (open) box.removeAttribute("hidden"); else box.setAttribute("hidden", "");
    b.setAttribute("aria-expanded", open ? "true" : "false");
  });

  form.addEventListener("input", run);
  form.addEventListener("change", run);
  run();
})();
