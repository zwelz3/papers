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
