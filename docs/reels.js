// Reel marquee. Scrolls continuously, pauses on hover or focus, and opens the
// real reel in a lightbox on click. The track is duplicated in the markup, so
// resetting at the halfway point makes the loop seamless.

(function () {
  var root = document.getElementById("reels");
  if (!root) return;

  var lb = document.getElementById("rl-lb");
  var frame = document.getElementById("rl-frame");
  var closeBtn = document.getElementById("rl-close");

  // Motion is a CSS animation, not requestAnimationFrame. rAF gets throttled
  // to nothing when the tab is backgrounded, and CSS keeps the loop smooth on
  // the compositor. Pausing on hover is handled in the stylesheet too.

  // ---- lightbox ----------------------------------------------------------
  function open(code) {
    frame.innerHTML =
      '<iframe src="https://www.instagram.com/reel/' + code + '/embed/" ' +
      'frameborder="0" scrolling="no" allowtransparency="true" ' +
      'allow="autoplay; encrypted-media" title="Instagram reel"></iframe>';
    lb.hidden = false;
    document.body.style.overflow = "hidden";
    closeBtn.focus();
  }
  function close() {
    lb.hidden = true;
    frame.innerHTML = "";
    document.body.style.overflow = "";
  }

  root.addEventListener("click", function (e) {
    var card = e.target.closest(".rl-card");
    if (card) { open(card.dataset.reel); return; }
    if (e.target === lb || e.target === closeBtn) close();
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && !lb.hidden) close();
  });
})();
