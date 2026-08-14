// Bali villa ROI calculator. No dependencies.
//
// The point of difference: a leasehold villa is a wasting asset. The premium
// you pay buys a fixed number of years and then returns nothing. Quoting a
// yield without amortising that premium overstates the return, which is how
// most Bali "8-15% yields" are produced. This model shows both numbers.

(function () {
  var form = document.getElementById("calc");
  if (!form) return;

  var USD = function (n) {
    var neg = n < 0;
    n = Math.abs(Math.round(n));
    return (neg ? "−$" : "$") + n.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  };
  var PCT = function (n) { return (n * 100).toFixed(1) + "%"; };
  var num = function (id) {
    var el = document.getElementById(id);
    if (!el) return 0;
    var v = parseFloat(el.value);
    return isNaN(v) ? 0 : v;
  };
  var set = function (id, txt, cls) {
    var el = document.getElementById(id);
    if (!el) return;
    el.textContent = txt;
    if (cls !== undefined) el.className = "calc-v " + cls;
  };

  function structure() {
    var el = form.querySelector('input[name="structure"]:checked');
    return el ? el.value : "lease";
  }

  // Net profit at a given occupancy, holding everything else constant.
  function profitAt(occ, d) {
    var gross = d.adr * 365 * occ;
    var ota = gross * d.ota;
    var pb1 = gross * d.pb1;
    var netRev = gross - ota - pb1;
    var mgmt = netRev * d.mgmt;
    var variable = gross * d.capex;
    var noi = netRev - mgmt - d.opex - variable;
    return noi > 0 ? noi * (1 - d.tax) : noi;
  }

  function run() {
    var isLease = structure() === "lease";

    // Lease-only fields are meaningless on a freehold/HGB purchase.
    document.querySelectorAll(".lease-only").forEach(function (el) {
      el.style.display = isLease ? "" : "none";
    });

    var price = num("price");
    var build = num("build");
    var ffe = num("ffe");
    var txPct = num("tx") / 100;
    var years = Math.max(1, num("years"));

    var invested = price + build + ffe + price * txPct;

    var d = {
      adr: num("adr"),
      ota: num("ota") / 100,
      pb1: num("pb1") / 100,
      mgmt: num("mgmt") / 100,
      capex: num("capex") / 100,
      opex: num("opex") * 12,
      tax: num("tax_rate") / 100
    };

    var occ = num("occ") / 100;
    var gross = d.adr * 365 * occ;
    var ota = gross * d.ota;
    var pb1 = gross * d.pb1;
    var netRev = gross - ota - pb1;
    var mgmt = netRev * d.mgmt;
    var capex = gross * d.capex;
    var noi = netRev - mgmt - d.opex - capex;
    var tax = noi > 0 ? noi * d.tax : 0;
    var net = noi - tax;

    // Headline (what gets advertised) vs net (what lands in your account).
    var grossYield = invested > 0 ? gross / invested : 0;
    var netYield = invested > 0 ? net / invested : 0;

    set("o_invested", USD(invested));
    set("o_gross", USD(gross));
    set("o_netrev", USD(netRev));
    set("o_opex", USD(mgmt + d.opex + capex));
    set("o_noi", USD(noi));
    set("o_tax", USD(tax));
    set("o_net", USD(net));
    set("o_grossyield", PCT(grossYield));
    set("o_netyield", PCT(netYield), netYield >= 0.06 ? "ok" : netYield >= 0.03 ? "mid" : "bad");

    // Payback
    var payback = net > 0 ? invested / net : 0;
    set("o_payback", net > 0 ? payback.toFixed(1) + " years" : "never at this occupancy",
        net > 0 && payback < years ? "ok" : "bad");

    // Lease amortisation — the number agents leave out.
    var amortRow = document.getElementById("row_amort");
    var trueRow = document.getElementById("row_true");
    var expRow = document.getElementById("row_expiry");
    if (isLease) {
      amortRow.style.display = "";
      trueRow.style.display = "";
      expRow.style.display = "";
      var amort = invested / years;
      var economic = net - amort;
      var trueYield = invested > 0 ? economic / invested : 0;
      set("o_amort", USD(amort) + " / year");
      set("o_true", PCT(trueYield) + "  (" + USD(economic) + " / year)",
          trueYield > 0.03 ? "ok" : trueYield > 0 ? "mid" : "bad");
      set("o_expiry", years + " years, then the asset returns to the landowner");
    } else {
      amortRow.style.display = "none";
      trueRow.style.display = "none";
      expRow.style.display = "none";
    }

    // Break-even occupancy — bisection, monotonic in occ.
    var lo = 0, hi = 1, mid = 0;
    if (profitAt(1, d) <= 0) {
      set("o_break", "not achievable at 100% occupancy", "bad");
    } else {
      for (var i = 0; i < 40; i++) {
        mid = (lo + hi) / 2;
        if (profitAt(mid, d) > 0) hi = mid; else lo = mid;
      }
      set("o_break", PCT(hi) + " occupancy to cover costs", hi < occ ? "ok" : "bad");
    }

    // Honest framing of the headline number.
    var warn = document.getElementById("o_warn");
    if (warn) {
      var msgs = [];
      if (isLease) {
        msgs.push("This is a leasehold. You are buying " + years +
          " years of use, not an asset. At expiry the land and everything on it revert to the owner unless the lease contains an enforceable extension clause.");
      }
      if (occ > 0.75) {
        msgs.push("Occupancy above 75% is optimistic for a Bali villa across a full year. Low season is real.");
      }
      if (grossYield - netYield > 0.04) {
        msgs.push("The gap between the advertised gross figure and your net return is " +
          PCT(grossYield - netYield) + " of capital a year. That gap is where most Bali investment pitches live.");
      }
      warn.innerHTML = msgs.length
        ? "<ul><li>" + msgs.join("</li><li>") + "</li></ul>"
        : "";
    }
  }

  form.addEventListener("input", run);
  form.addEventListener("change", run);
  run();
})();
