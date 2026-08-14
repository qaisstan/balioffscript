// Area map interaction. No dependencies.
//
// Hover on a pointer device, tap on touch, and keyboard-reachable either way.
// The card is the point of the thing: price is the least interesting field,
// the constraint is the one that decides whether a deal exists.

(function () {
  var root = document.getElementById("map");
  if (!root || !window.MAP_DATA) return;

  var card = document.getElementById("mp-card");
  var pins = root.querySelectorAll(".mp-pin");
  var base = window.SITE_BASE || "";
  var pinned = null;

  function draw(id) {
    var d = window.MAP_DATA[id];
    if (!d) return;
    card.innerHTML =
      '<p class="mp-c-r">' + d.r + " regency</p>" +
      '<h3 class="mp-c-h">' + d.n + "</h3>" +
      '<dl class="mp-c-dl">' +
        "<dt>Land</dt><dd>" + d.price + "</dd>" +
        "<dt>PBG</dt><dd>" + d.pbg + "</dd>" +
      "</dl>" +
      '<p class="mp-c-w"><span>Watch</span>' + d.watch + "</p>" +
      '<a class="mp-c-a" href="' + base + d.url + '">Read the ' + d.n + " page &rarr;</a>";
    pins.forEach(function (p) {
      p.classList.toggle("on", p.dataset.id === id);
    });
  }

  function clear() {
    if (pinned) return;
    card.innerHTML = '<p class="mp-empty">Pick an area.</p>';
    pins.forEach(function (p) { p.classList.remove("on"); });
  }

  pins.forEach(function (p) {
    var id = p.dataset.id;
    p.addEventListener("mouseenter", function () { if (!pinned) draw(id); });
    p.addEventListener("mouseleave", clear);
    p.addEventListener("focus", function () { draw(id); });
    p.addEventListener("blur", clear);
    // Tap pins the card open so it survives the finger lifting off.
    p.addEventListener("click", function (e) {
      e.preventDefault();
      pinned = pinned === id ? null : id;
      if (pinned) draw(id); else clear();
    });
    p.addEventListener("keydown", function (e) {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        pinned = pinned === id ? null : id;
        if (pinned) draw(id); else clear();
      }
    });
  });

  // Clicking away releases a pinned card.
  document.addEventListener("click", function (e) {
    if (!root.contains(e.target)) { pinned = null; clear(); }
  });
})();
