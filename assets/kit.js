// The Bali Buyer's Kit opt-in. Name, email and WhatsApp are required.
// On submit: the row goes to the sheet, the download appears straight away,
// and two optional taps (budget, timing) build a pre-written WhatsApp message
// to Kai. Indonesian numbers get the download only: no WhatsApp handoff.

(function () {
  var DIAL = [
    ["🇦🇺", "61"], ["🇬🇧", "44"], ["🇺🇸", "1"], ["🇩🇪", "49"], ["🇳🇱", "31"], ["🇫🇷", "33"],
    ["🇸🇪", "46"], ["🇳🇴", "47"], ["🇩🇰", "45"], ["🇫🇮", "358"], ["🇧🇪", "32"], ["🇨🇭", "41"],
    ["🇦🇹", "43"], ["🇱🇺", "352"], ["🇮🇪", "353"], ["🇨🇦", "1"], ["🇳🇿", "64"], ["🇸🇬", "65"],
    ["🇮🇩", "62"], ["🇪🇸", "34"], ["🇮🇹", "39"], ["🇵🇹", "351"], ["🇵🇱", "48"], ["🇨🇿", "420"],
    ["🇦🇪", "971"], ["🇸🇦", "966"], ["🇶🇦", "974"], ["🇮🇱", "972"], ["🇿🇦", "27"], ["🇮🇳", "91"],
    ["🇭🇰", "852"], ["🇯🇵", "81"], ["🇰🇷", "82"], ["🇲🇾", "60"], ["🇹🇭", "66"], ["🇵🇭", "63"],
    ["🇻🇳", "84"], ["🇨🇳", "86"], ["🇹🇼", "886"], ["🇧🇷", "55"], ["🇲🇽", "52"], ["🇦🇷", "54"],
    ["🇬🇷", "30"], ["🇷🇴", "40"], ["🇭🇺", "36"], ["🇭🇷", "385"], ["🇪🇪", "372"], ["🇱🇻", "371"],
    ["🇱🇹", "370"], ["🇮🇸", "354"], ["🇲🇹", "356"], ["🇨🇾", "357"], ["🇹🇷", "90"], ["🇷🇺", "7"],
    ["🇺🇦", "380"], ["🇰🇿", "7"], ["🇳🇬", "234"], ["🇰🇪", "254"], ["🇪🇬", "20"]
  ];

  function post(endpoint, data) {
    if (!endpoint) return;
    try {
      // text/plain keeps it a CORS "simple request" Apps Script can accept;
      // keepalive survives WhatsApp taking over the tab on a phone.
      fetch(endpoint, {
        method: "POST", mode: "no-cors", keepalive: true,
        headers: { "Content-Type": "text/plain;charset=utf-8" },
        body: JSON.stringify(data)
      }).catch(function () {});
    } catch (e) {}
  }

  function init(box) {
    var cfg = {};
    try { cfg = JSON.parse(box.getAttribute("data-cfg")); } catch (e) { return; }
    var form = box.querySelector(".kit-f");
    var done = box.querySelector(".kit-done");
    var errEl = box.querySelector(".kit-err");
    var sel = form.elements.dial;
    var loaded = Date.now();
    var dialTouched = false;
    var lead = null;
    var picks = { budget: "", timeline: "" };

    DIAL.forEach(function (c) {
      var o = document.createElement("option");
      o.value = "+" + c[1];
      o.textContent = c[0] + " +" + c[1];
      sel.appendChild(o);
    });
    sel.value = cfg.dial || "+61";
    sel.addEventListener("change", function () { dialTouched = true; });

    function fail(msg, field) {
      errEl.textContent = msg;
      if (field) { try { field.focus(); } catch (e) {} }
      form.classList.add("shake");
      setTimeout(function () { form.classList.remove("shake"); }, 400);
      return false;
    }

    function isIndonesian(digits) {
      if (sel.value === "+62") return true;
      if (/^62\d{8,}$/.test(digits)) return true;
      if (!dialTouched && /^08\d{7,11}$/.test(digits)) return true;
      return false;
    }

    function waHref() {
      var extra = "";
      if (picks.budget) extra += cfg.wa_budget.replace("{budget}", picks.budget);
      if (picks.timeline) extra += cfg.wa_time.replace("{time}", picks.timeline);
      var first = (lead.name.split(/\s+/)[0] || lead.name);
      first = first.charAt(0).toUpperCase() + first.slice(1);
      var text = cfg.wa_msg.replace("{name}", first).replace("{extra}", extra);
      return "https://wa.me/" + cfg.wa + "?text=" + encodeURIComponent(text);
    }

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var name = form.elements.name.value.trim();
      var email = form.elements.email.value.trim();
      var digits = form.elements.phone.value.replace(/[^0-9]/g, "");
      if (name.length < 2) return fail(cfg.e_name, form.elements.name);
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email)) return fail(cfg.e_email, form.elements.email);
      if (digits.length < 6 || digits.length > 15) return fail(cfg.e_phone, form.elements.phone);
      errEl.textContent = "";

      var indo = isIndonesian(digits);
      lead = {
        type: "kit", lang: cfg.lang, where: cfg.where || "", interest: (cfg.guide || "Buyer's Kit").slice(0, 80),
        name: name.slice(0, 80),
        phone: (sel.value + " " + form.elements.phone.value.trim()).slice(0, 40),
        email: email.slice(0, 120),
        budget: "", timeline: "",
        hp: form.elements.company.value,
        ms: Date.now() - loaded,
        ref: document.referrer.slice(0, 200),
        page: location.href.slice(0, 200)
      };
      post(cfg.endpoint, lead);

      form.hidden = true;
      done.hidden = false;
      if (indo) {
        box.querySelector(".kit-q").hidden = true;
        var m = box.querySelector(".kit-mailed"); if (m) m.hidden = true;
        box.querySelector(".kit-id").hidden = false;
      } else {
        box.querySelector(".kit-wa").href = waHref();
      }
      if (window.gtag) {
        gtag("event", "generate_lead", { event_category: "kit", event_label: "kit-" + cfg.lang + "-" + (cfg.where || "") });
      }
      try { done.scrollIntoView({ behavior: "smooth", block: "center" }); } catch (e2) {}
    });

    box.addEventListener("click", function (e) {
      var chip = e.target.closest(".kit-chip");
      if (!chip || !lead) return;
      var k = chip.getAttribute("data-k");
      box.querySelectorAll('.kit-chip[data-k="' + k + '"]').forEach(function (c) { c.classList.remove("sel"); });
      chip.classList.add("sel");
      picks[k] = chip.getAttribute("data-v");
      box.querySelector(".kit-wa").href = waHref();
      if (picks.budget && picks.timeline) {
        var q = {};
        for (var key in lead) q[key] = lead[key];
        q.type = "kit-qualify"; q.budget = picks.budget; q.timeline = picks.timeline;
        q.ms = Date.now() - loaded;
        post(cfg.endpoint, q);
      }
    });

    box.querySelector(".kit-wa").addEventListener("click", function () {
      if (window.gtag) gtag("event", "contact", { event_category: "kit", event_label: "whatsapp-" + cfg.lang });
    });
  }

  document.querySelectorAll(".kit[data-cfg]").forEach(init);
})();
