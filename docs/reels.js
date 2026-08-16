// Instagram reel strip. Each embed is created only when its card scrolls
// into view, and the Instagram script is fetched once, on first need.
// Twelve embeds loaded eagerly would add several seconds to page load.

(function () {
  var strip = document.getElementById("reels");
  if (!strip) return;

  var slots = strip.querySelectorAll(".rs-slot");
  if (!slots.length) return;

  var scriptLoaded = false;
  function loadScript(cb) {
    if (scriptLoaded) { cb(); return; }
    scriptLoaded = true;
    var s = document.createElement("script");
    s.async = true;
    s.src = "https://www.instagram.com/embed.js";
    s.onload = cb;
    document.body.appendChild(s);
  }

  function mount(slot) {
    if (slot.dataset.done) return;
    slot.dataset.done = "1";
    var code = slot.dataset.reel;
    slot.innerHTML =
      '<blockquote class="instagram-media" data-instgrm-captioned ' +
      'data-instgrm-permalink="https://www.instagram.com/reel/' + code + '/" ' +
      'data-instgrm-version="14"></blockquote>';
    loadScript(function () {
      if (window.instgrm && window.instgrm.Embeds) window.instgrm.Embeds.process();
    });
  }

  if (!("IntersectionObserver" in window)) {
    slots.forEach(mount);
    return;
  }
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (e.isIntersecting) { mount(e.target); io.unobserve(e.target); }
    });
  }, { root: strip.querySelector(".rs-track"), rootMargin: "300px" });
  slots.forEach(function (s) { io.observe(s); });
})();
