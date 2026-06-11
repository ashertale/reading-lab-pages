(function () {
  const concepts = Array.isArray(window.CONCEPT_INDEX) ? window.CONCEPT_INDEX : [];

  const elements = {
    totalTopics: document.querySelector("#total-topics"),
    randomTopicButton: document.querySelector("#random-topic-link"),
    searchInput: document.querySelector("#topic-search"),
    sortTopics: document.querySelector("#sort-topics"),
    clearSearch: document.querySelector("#clear-search"),
    searchCount: document.querySelector("#search-count"),
    topicResults: document.querySelector("#topic-results")
  };

  if (!elements.searchInput || !elements.topicResults) return;

  let activeResultIndex = 0;
  let hasActiveResult = false;
  let visibleResults = [];

  function normalizeText(value) {
    return String(value || "").trim().toLowerCase();
  }

  function currentUrlParams() {
    return new URLSearchParams(window.location.search);
  }

  function validSortMode(value) {
    if (!elements.sortTopics) return "";
    return Array.from(elements.sortTopics.options).some((option) => option.value === value)
      ? value
      : "";
  }

  function compareByOrder(a, b) {
    return a.order - b.order
      || a.title.localeCompare(b.title, "zh-Hant");
  }

  function searchableFields(concept) {
    return [
      ["title", concept.title],
      ["subtitle", concept.subtitle],
      ["type", concept.type],
      ["domain", concept.domain],
      ["focus", concept.focus],
      ["thesis", concept.thesis],
      ...(Array.isArray(concept.tags) ? concept.tags.map((tag) => ["tag", tag]) : [])
    ];
  }

  function matchesConcept(concept, query) {
    if (!query) return true;
    return searchableFields(concept).some(([, value]) => normalizeText(value).includes(query));
  }

  function matchedFieldLabel(concept, query) {
    if (!query) return "";
    const match = searchableFields(concept).find(([, value]) => normalizeText(value).includes(query));
    return match ? match[0] : "";
  }

  function matchLabelText(match) {
    if (match === "title") return "符合主題";
    if (match === "subtitle") return "符合英文名稱";
    if (match === "type") return "符合類型";
    if (match === "domain") return "符合領域";
    if (match === "focus") return "符合核心問題";
    if (match === "thesis") return "符合摘要";
    if (match === "tag") return "符合標籤";
    return "";
  }

  function compareConcepts(a, b) {
    const sortMode = elements.sortTopics ? elements.sortTopics.value : "order";

    if (sortMode === "title") {
      return a.title.localeCompare(b.title, "zh-Hant")
        || compareByOrder(a, b);
    }

    if (sortMode === "type") {
      return a.type.localeCompare(b.type, "zh-Hant")
        || compareByOrder(a, b);
    }

    if (sortMode === "domain") {
      return a.domain.localeCompare(b.domain, "zh-Hant")
        || compareByOrder(a, b);
    }

    return compareByOrder(a, b);
  }

  function syncSearchUrl() {
    const url = new URL(window.location.href);
    const query = elements.searchInput.value.trim();
    const sortMode = elements.sortTopics ? elements.sortTopics.value : "order";

    if (query) {
      url.searchParams.set("q", query);
    } else {
      url.searchParams.delete("q");
    }

    if (sortMode && sortMode !== "order") {
      url.searchParams.set("sort", sortMode);
    } else {
      url.searchParams.delete("sort");
    }

    window.history.replaceState(null, "", url.toString());
  }

  function restoreSearchState() {
    const params = currentUrlParams();
    const query = params.get("q") || "";
    const sortMode = validSortMode(params.get("sort") || "");

    if (query) elements.searchInput.value = query;
    if (sortMode && elements.sortTopics) elements.sortTopics.value = sortMode;
  }

  function appendHighlightedText(parent, text, query) {
    const value = String(text || "");
    const lowerValue = value.toLowerCase();
    const index = query ? lowerValue.indexOf(query) : -1;

    if (index < 0) {
      parent.append(document.createTextNode(value));
      return;
    }

    parent.append(document.createTextNode(value.slice(0, index)));

    const mark = document.createElement("mark");
    mark.textContent = value.slice(index, index + query.length);
    parent.append(mark, document.createTextNode(value.slice(index + query.length)));
  }

  function createTag(text) {
    const tag = document.createElement("span");
    tag.className = "result-tag";
    tag.textContent = text;
    return tag;
  }

  function createResultRow(concept, query, index) {
    const row = document.createElement("article");
    row.className = "result-row";
    row.dataset.resultIndex = String(index);
    row.id = `topic-result-${index}`;
    row.setAttribute("role", "option");
    row.setAttribute("aria-selected", "false");
    row.title = `開啟 ${concept.title}`;

    const main = document.createElement("div");
    main.className = "result-main";

    const meta = document.createElement("span");
    meta.className = "result-meta";
    meta.textContent = `Concept ${String(concept.order).padStart(2, "0")} / ${concept.type}`;

    const title = document.createElement("h3");
    appendHighlightedText(title, concept.title, query);

    const subtitle = document.createElement("span");
    subtitle.className = "result-subtitle";
    appendHighlightedText(subtitle, concept.subtitle, query);

    const thesis = document.createElement("p");
    appendHighlightedText(thesis, concept.thesis, query);

    const tagList = document.createElement("div");
    tagList.className = "result-tags";
    tagList.append(
      createTag(concept.domain),
      createTag(concept.focus)
    );

    const match = matchedFieldLabel(concept, query);
    if (match) {
      const matchLabel = document.createElement("span");
      matchLabel.className = "result-match";
      matchLabel.textContent = matchLabelText(match);
      tagList.append(matchLabel);
    }

    main.append(meta, title, subtitle, thesis, tagList);
    row.append(main);
    row.addEventListener("click", (event) => {
      if (event.target.closest("button, input, select, a")) return;
      window.location.href = concept.href;
    });
    return row;
  }

  function updateActiveResult(options = {}) {
    if (!hasActiveResult || !visibleResults.length) {
      elements.searchInput.removeAttribute("aria-activedescendant");
      elements.topicResults.querySelectorAll(".result-row").forEach((row) => {
        row.classList.remove("is-active");
        row.setAttribute("aria-selected", "false");
      });
      return;
    }

    activeResultIndex = Math.max(0, Math.min(activeResultIndex, visibleResults.length - 1));
    elements.topicResults.querySelectorAll(".result-row").forEach((row) => {
      const isActive = Number(row.dataset.resultIndex) === activeResultIndex;
      row.classList.toggle("is-active", isActive);
      row.setAttribute("aria-selected", String(isActive));
      if (isActive) elements.searchInput.setAttribute("aria-activedescendant", row.id);
      if (isActive && options.scroll) row.scrollIntoView({ block: "nearest" });
    });
  }

  function renderSearch() {
    const rawQuery = elements.searchInput.value.trim();
    const query = normalizeText(rawQuery);
    visibleResults = concepts
      .filter((concept) => matchesConcept(concept, query))
      .sort(compareConcepts);

    elements.topicResults.replaceChildren();

    if (!visibleResults.length) {
      hasActiveResult = false;
      activeResultIndex = 0;
      updateActiveResult();

      const empty = document.createElement("div");
      empty.className = "empty-state";
      const emptyTitle = document.createElement("strong");
      emptyTitle.textContent = rawQuery ? `找不到「${rawQuery}」` : "目前沒有可顯示的概念頁";
      const emptyCopy = document.createElement("p");
      emptyCopy.textContent = "可先用模板建立新頁，再把主題加入索引。";
      const backlogLink = document.createElement("a");
      backlogLink.className = "control-link";
      backlogLink.href = "./backlog.html";
      backlogLink.textContent = "查看待生成";
      empty.append(emptyTitle, emptyCopy, backlogLink);
      elements.topicResults.append(empty);
    } else {
      visibleResults.forEach((concept, index) => {
        elements.topicResults.append(createResultRow(concept, query, index));
      });
      hasActiveResult = Boolean(query) || hasActiveResult;
      updateActiveResult();
    }

    if (elements.searchCount) {
      elements.searchCount.textContent = `${visibleResults.length} / ${concepts.length}`;
    }
    if (elements.clearSearch) elements.clearSearch.disabled = !query;
  }

  function renderStats() {
    if (elements.totalTopics) elements.totalTopics.textContent = String(concepts.length);
    if (elements.randomTopicButton) elements.randomTopicButton.disabled = !concepts.length;
  }

  elements.searchInput.addEventListener("input", () => {
    activeResultIndex = 0;
    hasActiveResult = Boolean(normalizeText(elements.searchInput.value));
    syncSearchUrl();
    renderSearch();
  });

  elements.searchInput.addEventListener("keydown", (event) => {
    if (!visibleResults.length) return;

    if (event.key === "Enter") {
      event.preventDefault();
      if (!hasActiveResult && !normalizeText(elements.searchInput.value)) return;
      window.location.href = visibleResults[activeResultIndex].href;
    } else if (event.key === "ArrowDown") {
      event.preventDefault();
      if (!hasActiveResult) {
        hasActiveResult = true;
        activeResultIndex = 0;
        updateActiveResult({ scroll: true });
        return;
      }
      hasActiveResult = true;
      activeResultIndex = (activeResultIndex + 1) % visibleResults.length;
      updateActiveResult({ scroll: true });
    } else if (event.key === "ArrowUp") {
      event.preventDefault();
      if (!hasActiveResult) {
        hasActiveResult = true;
        activeResultIndex = visibleResults.length - 1;
        updateActiveResult({ scroll: true });
        return;
      }
      hasActiveResult = true;
      activeResultIndex = (activeResultIndex - 1 + visibleResults.length) % visibleResults.length;
      updateActiveResult({ scroll: true });
    }
  });

  if (elements.sortTopics) {
    elements.sortTopics.addEventListener("change", () => {
      activeResultIndex = 0;
      hasActiveResult = Boolean(normalizeText(elements.searchInput.value));
      syncSearchUrl();
      renderSearch();
    });
  }

  if (elements.clearSearch) {
    elements.clearSearch.addEventListener("click", () => {
      elements.searchInput.value = "";
      elements.searchInput.focus();
      activeResultIndex = 0;
      hasActiveResult = false;
      syncSearchUrl();
      renderSearch();
    });
  }

  if (elements.randomTopicButton) {
    elements.randomTopicButton.addEventListener("click", () => {
      if (!concepts.length) return;
      const topic = concepts[Math.floor(Math.random() * concepts.length)];
      window.location.href = topic.href;
    });
  }

  restoreSearchState();
  renderStats();
  renderSearch();
})();
