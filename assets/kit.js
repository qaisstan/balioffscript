// The Bali Buyer's Kit opt-in. Name, email and WhatsApp are required.
// On submit: the row goes to the sheet, the download appears straight away,
// and two optional taps (budget, timing) build a pre-written WhatsApp message
// to Kai. Indonesian numbers get the download only: no WhatsApp handoff.

(function () {
  // Default country code from the visitor's own time zone, so nobody gets labelled Australian by
  // accident. Indonesian time zones keep the page default: most visitors in Bali are travellers.
  function guessDial(fallback) {
    var TZ = {"Pacific/Auckland":"+64","Europe/London":"+44","Europe/Dublin":"+353","Europe/Lisbon":"+351","Europe/Madrid":"+34","Europe/Paris":"+33","Europe/Berlin":"+49","Europe/Amsterdam":"+31","Europe/Brussels":"+32","Europe/Zurich":"+41","Europe/Vienna":"+43","Europe/Stockholm":"+46","Europe/Oslo":"+47","Europe/Copenhagen":"+45","Europe/Helsinki":"+358","Europe/Rome":"+39","Europe/Warsaw":"+48","Europe/Prague":"+420","Europe/Moscow":"+7","Europe/Kiev":"+380","Europe/Kyiv":"+380","Europe/Istanbul":"+90","Europe/Athens":"+30","Europe/Bucharest":"+40","Europe/Budapest":"+36","Europe/Zagreb":"+385","Europe/Tallinn":"+372","Europe/Riga":"+371","Europe/Vilnius":"+370","Europe/Luxembourg":"+352","Europe/Malta":"+356","Atlantic/Reykjavik":"+354","Asia/Nicosia":"+357","Asia/Dubai":"+971","Asia/Riyadh":"+966","Asia/Qatar":"+974","Asia/Jerusalem":"+972","Africa/Johannesburg":"+27","Asia/Kolkata":"+91","Asia/Calcutta":"+91","Asia/Shanghai":"+86","Asia/Hong_Kong":"+852","Asia/Taipei":"+886","Asia/Tokyo":"+81","Asia/Seoul":"+82","Asia/Kuala_Lumpur":"+60","Asia/Singapore":"+65","Asia/Bangkok":"+66","Asia/Manila":"+63","Asia/Ho_Chi_Minh":"+84","Africa/Cairo":"+20","Africa/Lagos":"+234","Africa/Nairobi":"+254","America/Sao_Paulo":"+55","America/Mexico_City":"+52","America/Argentina/Buenos_Aires":"+54","America/Santiago":"+56","America/Bogota":"+57"};
    try {
      var tz = Intl.DateTimeFormat().resolvedOptions().timeZone || "";
      if (TZ[tz]) return TZ[tz];
      if (tz.indexOf("Australia/") === 0) return "+61";
      if (tz.indexOf("America/") === 0) return "+1";
    } catch (e) {}
    return fallback;
  }

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
    sel.value = guessDial(cfg.dial || "+61");
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
