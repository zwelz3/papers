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
// Light/dark toggle. The theme is set on <html data-theme> before first paint
// by an inline snippet in the page head; this only handles the button.
(function () {
  function apply(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    try { localStorage.setItem("theme", theme); } catch (e) {}
  }
  document.addEventListener("click", function (e) {
    var btn = e.target.closest && e.target.closest(".theme-toggle");
    if (!btn) return;
    var now = document.documentElement.getAttribute("data-theme");
    apply(now === "dark" ? "light" : "dark");
  });
  // follow the OS only while the reader has not chosen for themselves
  var mq = window.matchMedia("(prefers-color-scheme: dark)");
  var listener = function (ev) {
    var stored = null;
    try { stored = localStorage.getItem("theme"); } catch (e) {}
    if (!stored) document.documentElement.setAttribute("data-theme", ev.matches ? "dark" : "light");
  };
  if (mq.addEventListener) mq.addEventListener("change", listener);
})();

/* copy buttons on code blocks */
(function () {
  var COPY = '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><rect x="5.5" y="5.5" width="8" height="9" rx="1.5"/><path d="M10.5 3.5v-1a1 1 0 0 0-1-1h-6a1 1 0 0 0-1 1v8a1 1 0 0 0 1 1h1"/></svg>';
  var OK = '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M3 8.5 6.5 12 13 4.5"/></svg>';
  document.querySelectorAll(".code-block").forEach(function (block) {
    var code = block.querySelector("td.code pre") || block.querySelector("pre");
    if (!code) return;
    var btn = document.createElement("button");
    btn.className = "code-copy";
    btn.type = "button";
    btn.innerHTML = COPY + "<span>Copy</span>";
    btn.setAttribute("aria-label", "Copy code to clipboard");
    btn.addEventListener("click", function () {
      var text = code.textContent.replace(/\n$/, "");
      var done = function () {
        btn.innerHTML = OK + "<span>Copied</span>";
        setTimeout(function () { btn.innerHTML = COPY + "<span>Copy</span>"; }, 1600);
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(done);
      } else {
        var ta = document.createElement("textarea");
        ta.value = text; ta.style.position = "fixed"; ta.style.opacity = "0";
        document.body.appendChild(ta); ta.select();
        try { document.execCommand("copy"); done(); } finally { ta.remove(); }
      }
    });
    block.appendChild(btn);
  });
})();
