// Country code picker: type the country name ("port", "germ", "+49") instead of scrolling a list of
// flags. It sits on top of the forms' own <select>, which stays the real value, so kit.js and lead.js
// work unchanged (picking a country fires "change" on the select, like a manual pick).
(function () {
  var C = [
    ["🇦🇺", "61", "Australia"], ["🇺🇸", "1", "United States"], ["🇬🇧", "44", "United Kingdom"],
    ["🇸🇬", "65", "Singapore"], ["🇮🇩", "62", "Indonesia"], ["🇳🇱", "31", "Netherlands"],
    ["🇩🇪", "49", "Germany"], ["🇫🇷", "33", "France"], ["🇨🇦", "1", "Canada"], ["🇳🇿", "64", "New Zealand"],
    ["🇮🇪", "353", "Ireland"], ["🇨🇭", "41", "Switzerland"], ["🇸🇪", "46", "Sweden"], ["🇳🇴", "47", "Norway"],
    ["🇩🇰", "45", "Denmark"], ["🇫🇮", "358", "Finland"], ["🇧🇪", "32", "Belgium"], ["🇦🇹", "43", "Austria"],
    ["🇪🇸", "34", "Spain"], ["🇮🇹", "39", "Italy"], ["🇵🇹", "351", "Portugal"], ["🇵🇱", "48", "Poland"],
    ["🇨🇿", "420", "Czechia"], ["🇸🇰", "421", "Slovakia"], ["🇷🇺", "7", "Russia"], ["🇺🇦", "380", "Ukraine"],
    ["🇹🇷", "90", "Turkey"], ["🇦🇪", "971", "United Arab Emirates"], ["🇸🇦", "966", "Saudi Arabia"],
    ["🇶🇦", "974", "Qatar"], ["🇰🇼", "965", "Kuwait"], ["🇧🇭", "973", "Bahrain"], ["🇴🇲", "968", "Oman"],
    ["🇮🇱", "972", "Israel"], ["🇿🇦", "27", "South Africa"], ["🇮🇳", "91", "India"], ["🇨🇳", "86", "China"],
    ["🇭🇰", "852", "Hong Kong"], ["🇹🇼", "886", "Taiwan"], ["🇯🇵", "81", "Japan"], ["🇰🇷", "82", "South Korea"],
    ["🇲🇾", "60", "Malaysia"], ["🇹🇭", "66", "Thailand"], ["🇵🇭", "63", "Philippines"], ["🇻🇳", "84", "Vietnam"],
    ["🇰🇭", "855", "Cambodia"], ["🇧🇷", "55", "Brazil"], ["🇲🇽", "52", "Mexico"], ["🇦🇷", "54", "Argentina"],
    ["🇨🇱", "56", "Chile"], ["🇨🇴", "57", "Colombia"], ["🇵🇪", "51", "Peru"], ["🇬🇷", "30", "Greece"],
    ["🇷🇴", "40", "Romania"], ["🇧🇬", "359", "Bulgaria"], ["🇭🇺", "36", "Hungary"], ["🇭🇷", "385", "Croatia"],
    ["🇸🇮", "386", "Slovenia"], ["🇷🇸", "381", "Serbia"], ["🇪🇪", "372", "Estonia"], ["🇱🇻", "371", "Latvia"],
    ["🇱🇹", "370", "Lithuania"], ["🇱🇺", "352", "Luxembourg"], ["🇮🇸", "354", "Iceland"], ["🇲🇹", "356", "Malta"],
    ["🇨🇾", "357", "Cyprus"], ["🇲🇨", "377", "Monaco"], ["🇰🇿", "7", "Kazakhstan"], ["🇳🇬", "234", "Nigeria"],
    ["🇰🇪", "254", "Kenya"], ["🇪🇬", "20", "Egypt"], ["🇲🇦", "212", "Morocco"], ["🇹🇳", "216", "Tunisia"],
    ["🇵🇰", "92", "Pakistan"], ["🇧🇩", "880", "Bangladesh"], ["🇱🇰", "94", "Sri Lanka"], ["🇳🇵", "977", "Nepal"],
    ["🇧🇳", "673", "Brunei"]
  ];

  function norm(s) { return String(s || "").toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, ""); }

  function enhance(sel) {
    if (!sel || sel.dataset.dp) return;
    sel.dataset.dp = "1";
    var wrap = document.createElement("div");
    wrap.className = "dp";
    sel.parentNode.insertBefore(wrap, sel);
    wrap.appendChild(sel);
    sel.classList.add("dp-native");
    sel.tabIndex = -1;
    sel.setAttribute("aria-hidden", "true");

    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "dp-btn";
    btn.setAttribute("aria-haspopup", "listbox");
    wrap.appendChild(btn);

    var pop = document.createElement("div");
    pop.className = "dp-pop";
    pop.hidden = true;
    pop.innerHTML = '<input type="search" class="dp-q" placeholder="Type your country" aria-label="Search country" autocomplete="off"><ul class="dp-list" role="listbox"></ul>';
    wrap.appendChild(pop);
    var q = pop.querySelector(".dp-q"), list = pop.querySelector(".dp-list");
    var current = null;

    function label() {
      var v = sel.value, hit = current && ("+" + current[1]) === v ? current : null;
      if (!hit) { for (var i = 0; i < C.length; i++) if ("+" + C[i][1] === v) { hit = C[i]; break; } }
      btn.textContent = hit ? hit[0] + " " + v : (v || "Code");
      btn.setAttribute("aria-label", "Country code " + (hit ? hit[2] + " " : "") + v);
    }
    function draw() {
      var t = norm(q.value).replace(/^\+/, "");
      var rows = C.filter(function (c) { return !t || norm(c[2]).indexOf(t) === 0 || norm(c[2]).indexOf(" " + t) > -1 || c[1].indexOf(t) === 0; });
      list.innerHTML = rows.slice(0, 60).map(function (c, i) {
        return '<li role="option" data-i="' + C.indexOf(c) + '"' + (i === 0 ? ' class="on"' : "") + '><span>' + c[0] + "</span><b>" + c[2] + "</b><i>+" + c[1] + "</i></li>";
      }).join("") || '<li class="dp-none">No match</li>';
    }
    function pick(c) {
      var v = "+" + c[1];
      if (![].some.call(sel.options, function (o) { return o.value === v; })) {
        var o = document.createElement("option"); o.value = v; o.textContent = c[0] + " " + v; sel.appendChild(o);
      }
      current = c;
      sel.value = v;
      sel.dispatchEvent(new Event("change", { bubbles: true }));
      label(); close();
      var tel = wrap.parentNode.querySelector('input[type="tel"]'); if (tel) tel.focus();
    }
    function open() { pop.hidden = false; q.value = ""; draw(); setTimeout(function () { q.focus(); }, 0); }
    function close() { pop.hidden = true; }

    btn.addEventListener("click", function () { pop.hidden ? open() : close(); });
    q.addEventListener("input", draw);
    q.addEventListener("keydown", function (e) {
      if (e.key === "Enter") { e.preventDefault(); var f = list.querySelector("li[data-i]"); if (f) pick(C[+f.dataset.i]); }
      if (e.key === "Escape") { close(); btn.focus(); }
    });
    list.addEventListener("click", function (e) { var li = e.target.closest("li[data-i]"); if (li) pick(C[+li.dataset.i]); });
    document.addEventListener("click", function (e) { if (!wrap.contains(e.target)) close(); });
    sel.addEventListener("change", label);
    label();
  }

  function run() { [].forEach.call(document.querySelectorAll('select[name="dial"], #ld-dial'), enhance); }
  // After the forms' own scripts have filled the list and chosen the default (they are deferred too).
  if (document.readyState === "complete") run(); else document.addEventListener("DOMContentLoaded", run);
  window.addEventListener("load", run);
  window.DialPicker = { enhance: enhance };
})();
