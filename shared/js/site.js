// Client-side search + tag filtering for the library landing page.
(function () {
  var data = window.__PAPERS__ || [];
  var byslug = {};
  data.forEach(function (p) { byslug[p.slug] = p; });

  var search = document.getElementById("search");
  var tagFilter = document.getElementById("tag-filter");
  var filterCount = document.getElementById("filter-count");
  var activeTagBox = document.getElementById("active-tags");
  var tagClear = document.getElementById("tag-clear");
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

  function boxes() {
    return tagFilter ? Array.prototype.slice.call(
      tagFilter.querySelectorAll('.tag-opt input[type="checkbox"]')) : [];
  }

  function syncChrome() {
    var n = activeTags.size;
    if (filterCount) {
      filterCount.textContent = String(n);
      filterCount.hidden = n === 0;
    }
    if (!activeTagBox) return;
    activeTagBox.textContent = "";
    Array.from(activeTags).forEach(function (tag) {
      var chip = document.createElement("span");
      chip.className = "active-tag";
      var label = document.createElement("span");
      label.textContent = tag;
      var x = document.createElement("button");
      x.type = "button";
      x.setAttribute("aria-label", "Remove filter: " + tag);
      x.textContent = "\u00d7";
      x.addEventListener("click", function () {
        activeTags.delete(tag);
        boxes().forEach(function (b) { if (b.value === tag) b.checked = false; });
        syncChrome();
        apply();
      });
      chip.appendChild(label);
      chip.appendChild(x);
      activeTagBox.appendChild(chip);
    });
  }

  if (tagFilter) {
    tagFilter.addEventListener("change", function (e) {
      var box = e.target;
      if (!box || box.type !== "checkbox") return;
      if (box.checked) activeTags.add(box.value);
      else activeTags.delete(box.value);
      syncChrome();
      apply();
    });
    // clicking outside closes the panel
    document.addEventListener("click", function (e) {
      if (tagFilter.open && !tagFilter.contains(e.target)) tagFilter.open = false;
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && tagFilter.open) tagFilter.open = false;
    });
  }

  if (tagClear) {
    tagClear.addEventListener("click", function () {
      activeTags.clear();
      boxes().forEach(function (b) { b.checked = false; });
      syncChrome();
      apply();
    });
  }

  syncChrome();

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
