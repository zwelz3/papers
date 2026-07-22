// Client-side search + tag filtering for the library landing page.
(function () {
  var data = window.__PAPERS__ || [];
  var byslug = {};
  data.forEach(function (p) { byslug[p.slug] = p; });

  var search = document.getElementById("search");
  var tagFilters = document.getElementById("tag-filters");
  var list = document.getElementById("paper-list");
  var empty = document.getElementById("empty-state");
  var count = document.getElementById("result-count");
  var cards = Array.prototype.slice.call(list.querySelectorAll(".paper-card"));

  var activeTags = new Set();
  var query = "";

  function matches(slug) {
    var p = byslug[slug];
    if (!p) return true;
    if (query && p.text.indexOf(query) === -1) return false;
    if (activeTags.size) {
      for (var t of activeTags) {
        if (p.tags.indexOf(t) === -1) return false; // AND semantics
      }
    }
    return true;
  }

  function apply() {
    var shown = 0;
    cards.forEach(function (card) {
      var ok = matches(card.getAttribute("data-slug"));
      card.hidden = !ok;
      if (ok) shown++;
    });
    empty.hidden = shown !== 0;
    var total = cards.length;
    if (query || activeTags.size) {
      count.textContent = shown + " of " + total +
        (total === 1 ? " paper" : " papers");
    } else {
      count.textContent = total + (total === 1 ? " paper" : " papers");
    }
  }

  if (search) {
    search.addEventListener("input", function () {
      query = search.value.trim().toLowerCase();
      apply();
    });
    // "/" focuses search
    document.addEventListener("keydown", function (e) {
      if (e.key === "/" && document.activeElement !== search) {
        e.preventDefault();
        search.focus();
      }
    });
  }

  var sortSel = document.getElementById("sort");

  function applySort() {
    if (!sortSel) return;
    var mode = sortSel.value;
    var sorted = cards.slice().sort(function (a, b) {
      var pa = byslug[a.getAttribute("data-slug")] || {};
      var pb = byslug[b.getAttribute("data-slug")] || {};
      switch (mode) {
        case "date-asc":   return (pa.date || "").localeCompare(pb.date || "");
        case "title-asc":  return (pa.title || "").localeCompare(pb.title || "");
        case "title-desc": return (pb.title || "").localeCompare(pa.title || "");
        default:           return (pb.date || "").localeCompare(pa.date || "");
      }
    });
    sorted.forEach(function (c) { list.appendChild(c); });
    try { localStorage.setItem("sort", mode); } catch (e) {}
  }

  if (sortSel) {
    var savedSort = null;
    try { savedSort = localStorage.getItem("sort"); } catch (e) {}
    if (savedSort) sortSel.value = savedSort;
    sortSel.addEventListener("change", applySort);
    applySort();
  }

  if (tagFilters) {
    tagFilters.addEventListener("click", function (e) {
      var btn = e.target.closest(".tag-btn");
      if (!btn) return;
      var tag = btn.getAttribute("data-tag");
      if (activeTags.has(tag)) { activeTags.delete(tag); btn.classList.remove("on"); }
      else { activeTags.add(tag); btn.classList.add("on"); }
      apply();
    });
  }

  apply();
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
