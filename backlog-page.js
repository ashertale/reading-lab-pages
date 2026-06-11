(function () {
  const suggestions = Array.isArray(window.CONCEPT_SUGGESTIONS) ? window.CONCEPT_SUGGESTIONS : [];

  const elements = {
    backlogCount: document.querySelector("#backlog-count"),
    suggestedTopics: document.querySelector("#suggested-topics")
  };

  function renderSuggestions() {
    if (elements.backlogCount) elements.backlogCount.textContent = String(suggestions.length);
    if (!elements.suggestedTopics) return;

    elements.suggestedTopics.replaceChildren();

    if (!suggestions.length) {
      const empty = document.createElement("div");
      empty.className = "empty-state";
      const title = document.createElement("strong");
      title.textContent = "目前沒有候選主題";
      const copy = document.createElement("p");
      copy.textContent = "新增候選題時，請更新 data/concept-suggestions.json。";
      empty.append(title, copy);
      elements.suggestedTopics.append(empty);
      return;
    }

    suggestions.forEach((suggestion) => {
      const card = document.createElement("article");
      card.className = "suggestion-card";

      const meta = document.createElement("span");
      meta.className = "result-meta";
      meta.textContent = suggestion.type;

      const title = document.createElement("strong");
      title.textContent = suggestion.title;

      const thesis = document.createElement("p");
      thesis.textContent = suggestion.thesis;

      const relation = document.createElement("em");
      relation.textContent = suggestion.relation;

      card.append(meta, title, thesis, relation);
      elements.suggestedTopics.append(card);
    });
  }

  renderSuggestions();
})();
