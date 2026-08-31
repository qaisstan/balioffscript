// Multi-step lead form. One question per screen, no dependencies.
//
// The endpoint is a Google Apps Script web app that only ever appends a row.
// It returns nothing readable, so the public URL in this file cannot be used
// to read anyone's submission. See apps-script/README.md.

(function () {
  var form = document.getElementById("lead");
  if (!form) return;

  var ENDPOINT = form.dataset.endpoint || "";
  var WA = form.dataset.wa || "";
  var steps = Array.prototype.slice.call(form.querySelectorAll(".ld-step"));
  var bar = document.getElementById("ld-bar");
  var count = document.getElementById("ld-count");
  var live = document.getElementById("ld-live");
  var loaded = Date.now();
  var i = 0;

  // Flag, dial code, name. Kai's buyers cluster in the first few markets, so
  // those lead; the name is kept for the accessible label and for search-by-typing.
  var DIAL = [
    ["🇦🇺", "61", "Australia"], ["🇺🇸", "1", "United States"],
    ["🇬🇧", "44", "United Kingdom"], ["🇸🇬", "65", "Singapore"],
    ["🇮🇩", "62", "Indonesia"], ["🇳🇱", "31", "Netherlands"],
    ["🇩🇪", "49", "Germany"], ["🇫🇷", "33", "France"],
    ["🇨🇦", "1", "Canada"], ["🇳🇿", "64", "New Zealand"],
    ["🇮🇪", "353", "Ireland"], ["🇨🇭", "41", "Switzerland"],
    ["🇸🇪", "46", "Sweden"], ["🇳🇴", "47", "Norway"],
    ["🇩🇰", "45", "Denmark"], ["🇫🇮", "358", "Finland"],
    ["🇧🇪", "32", "Belgium"], ["🇦🇹", "43", "Austria"],
    ["🇪🇸", "34", "Spain"], ["🇮🇹", "39", "Italy"],
    ["🇵🇹", "351", "Portugal"], ["🇵🇱", "48", "Poland"],
    ["🇨🇿", "420", "Czechia"], ["🇷🇺", "7", "Russia"],
    ["🇺🇦", "380", "Ukraine"], ["🇹🇷", "90", "Turkey"],
    ["🇦🇪", "971", "UAE"], ["🇸🇦", "966", "Saudi Arabia"],
    ["🇶🇦", "974", "Qatar"], ["🇮🇱", "972", "Israel"],
    ["🇿🇦", "27", "South Africa"], ["🇮🇳", "91", "India"],
    ["🇨🇳", "86", "China"], ["🇭🇰", "852", "Hong Kong"],
    ["🇹🇼", "886", "Taiwan"], ["🇯🇵", "81", "Japan"],
    ["🇰🇷", "82", "South Korea"], ["🇲🇾", "60", "Malaysia"],
    ["🇹🇭", "66", "Thailand"], ["🇵🇭", "63", "Philippines"],
    ["🇻🇳", "84", "Vietnam"], ["🇧🇷", "55", "Brazil"],
    ["🇲🇽", "52", "Mexico"], ["🇦🇷", "54", "Argentina"],
    ["🇨🇱", "56", "Chile"], ["🇨🇴", "57", "Colombia"],
    ["🇬🇷", "30", "Greece"], ["🇷🇴", "40", "Romania"],
    ["🇭🇺", "36", "Hungary"], ["🇭🇷", "385", "Croatia"],
    ["🇪🇪", "372", "Estonia"], ["🇱🇻", "371", "Latvia"],
    ["🇱🇹", "370", "Lithuania"], ["🇱🇺", "352", "Luxembourg"],
    ["🇮🇸", "354", "Iceland"], ["🇲🇹", "356", "Malta"],
    ["🇨🇾", "357", "Cyprus"], ["🇰🇿", "7", "Kazakhstan"],
    ["🇳🇬", "234", "Nigeria"], ["🇰🇪", "254", "Kenya"],
    ["🇪🇬", "20", "Egypt"]
  ];

  var sel = document.getElementById("ld-dial");
  if (sel) {
    DIAL.forEach(function (c) {
      var o = document.createElement("option");
      o.value = "+" + c[1];
      o.textContent = c[0] + "  +" + c[1];
      o.setAttribute("aria-label", c[2] + " +" + c[1]);
      sel.appendChild(o);
    });
    sel.value = "+61";
  }

  function show(n) {
    steps[i].classList.remove("on");
    i = n;
    steps[i].classList.add("on");

    // Neither the intro nor the thank-you screen counts as a question.
    var total = steps.length - 2;
    var pct = Math.min(i / total, 1) * 100;
    if (bar) bar.style.width = pct.toFixed(0) + "%";
    if (count) count.textContent = i > 0 && i <= total ? i + " of " + total : "";

    var field = steps[i].querySelector("input:not([type=hidden]), select, button");
    // Autofocus is deliberate on desktop only; on mobile it yanks the keyboard
    // up before the question is readable.
    if (field && window.matchMedia("(min-width: 40rem)").matches) {
      setTimeout(function () { try { field.focus(); } catch (e) {} }, 220);
    }
    var h = steps[i].querySelector("h2");
    if (live && h) live.textContent = h.textContent;
  }

  function err(step, msg) {
    var e = step.querySelector(".ld-err");
    if (e) e.textContent = msg || "";
    if (msg) {
      step.classList.add("shake");
      setTimeout(function () { step.classList.remove("shake"); }, 400);
    }
  }

  function valid(step) {
    var name = step.dataset.field;
    if (name === "name") {
      var v = form.elements.name.value.trim();
      if (v.length < 2) { err(step, "Please enter your name."); return false; }
      if (v.length > 80) { err(step, "That name is too long."); return false; }
    }
    if (name === "phone") {
      var digits = form.elements.phone.value.replace(/[^0-9]/g, "");
      if (digits.length < 6) { err(step, "Please enter a valid number."); return false; }
      if (digits.length > 15) { err(step, "That number is too long."); return false; }
      // Email is optional, but a typo in one that was filled in is worth catching.
      var mail = form.elements.email.value.trim();
      if (mail && !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(mail)) {
        err(step, "That email doesn't look right."); return false;
      }
    }
    err(step, "");
    return true;
  }

  // Next / back buttons
  form.addEventListener("click", function (e) {
    var next = e.target.closest("[data-next]");
    if (next) {
      e.preventDefault();
      if (!valid(steps[i])) return;
      if (i === steps.length - 2) { submit(); } else { show(i + 1); }
      return;
    }
    var back = e.target.closest("[data-back]");
    if (back) { e.preventDefault(); if (i > 0) show(i - 1); return; }

    // Choice buttons advance on their own, which is what makes it feel quick.
    var pick = e.target.closest("[data-value]");
    if (pick) {
      e.preventDefault();
      var step = pick.closest(".ld-step");
      step.querySelectorAll("[data-value]").forEach(function (b) {
        b.classList.remove("sel");
        b.setAttribute("aria-pressed", "false");
      });
      pick.classList.add("sel");
      pick.setAttribute("aria-pressed", "true");
      form.elements[step.dataset.field].value = pick.dataset.value;
      setTimeout(function () {
        if (i === steps.length - 2) { submit(); } else { show(i + 1); }
      }, 180);
    }
  });

  // Enter advances a text step rather than submitting the whole form.
  form.addEventListener("keydown", function (e) {
    if (e.key !== "Enter") return;
    e.preventDefault();
    var step = steps[i];
    if (step.querySelector("input:not([type=hidden])")) {
      if (!valid(step)) return;
      if (i === steps.length - 2) { submit(); } else { show(i + 1); }
    }
  });

  form.addEventListener("submit", function (e) { e.preventDefault(); });

  function payload() {
    var dial = sel ? sel.value : "";
    return {
      name: form.elements.name.value.trim().slice(0, 80),
      phone: (dial + " " + form.elements.phone.value.trim()).slice(0, 40),
      email: form.elements.email.value.trim().slice(0, 120),
      budget: form.elements.budget.value,
      timeline: form.elements.timeline.value,
      // Bot checks. A real person leaves the honeypot empty and takes more
      // than a couple of seconds to read four questions.
      hp: form.elements.company.value,
      ms: Date.now() - loaded,
      ref: document.referrer.slice(0, 200),
      page: location.href.slice(0, 200)
    };
  }

  function done() {
    // Clear the submitting state first, or the thank-you screen inherits the
    // dimmed, non-interactive look meant for the moment the request is in flight.
    steps.forEach(function (s) { s.classList.remove("busy"); });
    show(steps.length - 1);
    if (bar) bar.style.width = "100%";
    if (count) count.textContent = "";
    if (window.gtag) {
      gtag("event", "generate_lead", { event_category: "lead", event_label: "opportunities" });
    }
  }

  function fallback(d) {
    // Never lose a lead to a failed request. Hand them to WhatsApp with the
    // answers already written out.
    var box = document.getElementById("ld-fallback");
    if (!box || !WA) { done(); return; }
    var text = "Hi Kai, I filled in the form on your site.\n\n"
      + "Name: " + d.name + "\nPhone: " + d.phone
      + (d.email ? "\nEmail: " + d.email : "")
      + "\nBudget: " + d.budget + "\nTimeline: " + d.timeline;
    box.querySelector("a").href = "https://wa.me/" + WA + "?text=" + encodeURIComponent(text);
    box.hidden = false;
    done();
  }

  function submit() {
    var d = payload();
    var btn = form.querySelector("[data-next].primary:not([hidden])");
    steps.forEach(function (s) { s.classList.add("busy"); });

    if (!ENDPOINT) { fallback(d); return; }

    // text/plain keeps this a CORS "simple request", so the browser skips the
    // preflight that Apps Script cannot answer.
    fetch(ENDPOINT, {
      method: "POST",
      mode: "no-cors",
      headers: { "Content-Type": "text/plain;charset=utf-8" },
      body: JSON.stringify(d)
    }).then(function () {
      done();
    }).catch(function () {
      fallback(d);
    });
  }

  show(0);
})();
