// Collapsible nav pane + scroll-spy for paper pages.
(function () {
  var toggle = document.querySelector(".nav-toggle");
  var pane = document.getElementById("nav-pane");
  var body = document.body;
  if (!toggle || !pane) return;

  // Restore last state on desktop; default closed on narrow screens.
  var wide = window.matchMedia("(min-width: 1100px)");
  function setOpen(open) {
    body.classList.toggle("nav-open", open);
    toggle.setAttribute("aria-expanded", String(open));
    try { localStorage.setItem("navOpen", open ? "1" : "0"); } catch (e) {}
  }
  var stored = null;
  try { stored = localStorage.getItem("navOpen"); } catch (e) {}
  setOpen(stored !== null ? stored === "1" : wide.matches);

  toggle.addEventListener("click", function () {
    setOpen(!body.classList.contains("nav-open"));
  });

  // Close when a link is tapped on narrow screens.
  pane.addEventListener("click", function (e) {
    if (e.target.tagName === "A" && !wide.matches) setOpen(false);
  });

  // Scroll-spy: highlight the section currently in view.
  var links = Array.prototype.slice.call(pane.querySelectorAll("a[href^='#']"));
  var map = {};
  var targets = [];
  links.forEach(function (a) {
    var id = a.getAttribute("href").slice(1);
    var el = document.getElementById(id);
    if (el) { map[id] = a; targets.push(el); }
  });

  if ("IntersectionObserver" in window && targets.length) {
    var visible = new Set();
    var obs = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) visible.add(en.target.id);
        else visible.delete(en.target.id);
      });
      // pick the topmost visible heading
      var best = null, bestTop = Infinity;
      targets.forEach(function (t) {
        if (visible.has(t.id)) {
          var top = t.getBoundingClientRect().top;
          if (top < bestTop) { bestTop = top; best = t.id; }
        }
      });
      links.forEach(function (a) { a.classList.remove("active"); });
      if (best && map[best]) map[best].classList.add("active");
    }, { rootMargin: "-72px 0px -70% 0px", threshold: 0 });
    targets.forEach(function (t) { obs.observe(t); });
  }
})();
