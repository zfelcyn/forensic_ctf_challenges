const state = {
  challenges: [],
  selectedId: null,
  solvedIds: new Set(),
  windowMode: "normal",
};

const STORAGE_KEY = "forensic-ctf-portal-progress-v1";
const difficultyOrder = ["Easy", "Medium", "Hard", "Bonus"];
const challengeTree = document.querySelector("#challengeTree");
const detailPanel = document.querySelector("#detailPanel");
const challengeCount = document.querySelector("#challengeCount");
const solvedCount = document.querySelector("#solvedCount");
const pointsCount = document.querySelector("#pointsCount");

const badgeClassMap = {
  Easy: "easy",
  Medium: "medium",
  Hard: "hard",
  Bonus: "bonus",
  concept: "concept",
  draft: "draft",
  ready: "ready",
  live: "live",
  archived: "archived",
};

async function loadChallenges() {
  const response = await fetch("./data/challenges.json", { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`Failed to load challenge registry: ${response.status}`);
  }

  const payload = await response.json();
  state.challenges = payload.challenges;
  state.solvedIds = readSolvedIds(payload.challenges);
  renderMetrics(payload.challenges);

  const requestedId = getRequestedIdFromHash();
  const defaultId = requestedId ?? getDefaultChallengeId(payload.challenges);
  state.selectedId = defaultId;

  render();
}

function renderMetrics(challenges) {
  const solvedChallenges = challenges.filter((challenge) => state.solvedIds.has(challenge.id));
  const unlockedPoints = solvedChallenges.reduce((total, challenge) => total + challenge.points, 0);

  challengeCount.textContent = String(challenges.length);
  solvedCount.textContent = String(solvedChallenges.length);
  pointsCount.textContent = String(unlockedPoints);
}

function render() {
  if (!state.challenges.some((item) => item.id === state.selectedId)) {
    state.selectedId = null;
    state.windowMode = "normal";
  }

  renderMetrics(state.challenges);
  syncWindowMode();
  renderTree(state.challenges);
  renderDetail(state.challenges);
}

function renderDetail(challenges) {
  const challenge = challenges.find((item) => item.id === state.selectedId);

  if (!challenge) {
    detailPanel.innerHTML = `
      <div class="detail-empty">
        <p>No challenge selected.</p>
      </div>
    `;
    return;
  }

  const isSolved = state.solvedIds.has(challenge.id);
  const artifacts = (challenge.artifacts || [])
    .map((artifact) => `<li><strong>${escapeHtml(artifact.name)}</strong> <span>${escapeHtml(artifact.purpose)}</span></li>`)
    .join("");

  const tools = (challenge.recommendedTools || [])
    .map((tool) => `<span class="meta-chip">${escapeHtml(tool)}</span>`)
    .join("");

  detailPanel.innerHTML = `
    <article class="challenge-window ${state.windowMode === "minimized" ? "minimized" : ""}">
      <div class="window-bar">
        <div class="window-tabs">
          <span class="tab active">Challenge</span>
          <span class="tab">${isSolved ? "Solved" : "Open"}</span>
        </div>
        <div class="window-controls" aria-hidden="true">
          <button type="button" class="window-button red" data-window-action="close" title="Close challenge"></button>
          <button type="button" class="window-button yellow" data-window-action="minimize" title="Minimize challenge"></button>
          <button type="button" class="window-button green ${state.windowMode === "focus" ? "active" : ""}" data-window-action="focus" title="Focus challenge"></button>
        </div>
      </div>

      <div class="window-body">
        <div class="window-heading">
          <p class="challenge-path">./${escapeHtml(challenge.id)}</p>
          <h2>${escapeHtml(challenge.title)}</h2>
          <p class="challenge-points">${challenge.points}</p>
        </div>

        <div class="window-meta">
          <span class="badge ${badgeClassMap[challenge.difficulty]}">${challenge.difficulty}</span>
          <span class="meta-label">${escapeHtml(challenge.category)}</span>
          <span class="meta-label">${isSolved ? "Solved" : "Unsolved"}</span>
        </div>

        <div class="action-row">
          <a class="download-button" href="${escapeHtml(challenge.downloadPath)}">Download Files</a>
          <span class="download-note">Download the files needed for this challenge.</span>
        </div>

        <p class="challenge-scenario">${escapeHtml(challenge.scenario)}</p>

        <section class="window-section">
          <h3>Artifacts</h3>
          <ul class="artifact-list">${artifacts}</ul>
        </section>

        <section class="window-section">
          <h3>Recommended Tools</h3>
          <div class="tool-row">${tools}</div>
        </section>
      </div>

      <form class="flag-form" data-challenge-id="${escapeHtml(challenge.id)}">
        <label class="sr-only" for="flagInput">Flag</label>
        <input
          id="flagInput"
          name="flag"
          type="text"
          placeholder="FLAG{...}"
          autocomplete="off"
          spellcheck="false"
        />
        <button type="submit">${isSolved ? "Solved" : "Submit"}</button>
      </form>

      <div class="submission-meta">
        <span>${escapeHtml(challenge.summary)}</span>
        <span>${challenge.points} pts unlock</span>
      </div>

      <p class="submission-message ${isSolved ? "success" : ""}" id="submissionMessage">
        ${isSolved ? `Flag accepted. ${challenge.points} points unlocked.` : "Enter the exact flag to unlock the challenge points."}
      </p>
    </article>
  `;

  const form = detailPanel.querySelector(".flag-form");
  form?.addEventListener("submit", async (event) => {
    event.preventDefault();

    const formData = new FormData(form);
    const inputValue = String(formData.get("flag") ?? "").trim();
    const message = detailPanel.querySelector("#submissionMessage");
    const input = form.querySelector('input[name="flag"]');

    if (!inputValue) {
      message.textContent = "Enter a flag before submitting.";
      message.className = "submission-message error";
      return;
    }

    const isMatch = await validateFlag(inputValue, challenge.flagValidation.sha256);
    if (!isMatch) {
      message.textContent = "Incorrect flag.";
      message.className = "submission-message error";
      return;
    }

    if (!state.solvedIds.has(challenge.id)) {
      state.solvedIds.add(challenge.id);
      persistSolvedIds();
    }

    message.textContent = `Flag accepted. ${challenge.points} points unlocked.`;
    message.className = "submission-message success";
    if (input instanceof HTMLInputElement) {
      input.value = "";
    }
    render();
  });

  detailPanel.querySelectorAll("[data-window-action]").forEach((button) => {
    button.addEventListener("click", () => {
      const action = button.getAttribute("data-window-action");

      if (action === "close") {
        state.selectedId = null;
        state.windowMode = "normal";
        clearChallengeHash();
        render();
        return;
      }

      if (action === "minimize") {
        state.windowMode = state.windowMode === "minimized" ? "normal" : "minimized";
        render();
        return;
      }

      if (action === "focus") {
        state.windowMode = state.windowMode === "focus" ? "normal" : "focus";
        render();
      }
    });
  });
}

function getRequestedIdFromHash() {
  const match = window.location.hash.match(/^#challenge\/(.+)$/);
  return match ? decodeURIComponent(match[1]) : null;
}

function renderTree(challenges) {
  const groupedChallenges = challenges.reduce((groups, challenge) => {
    const difficulty = challenge.difficulty || "Unknown";
    const existing = groups.get(difficulty) ?? [];
    existing.push(challenge);
    groups.set(difficulty, existing);
    return groups;
  }, new Map());

  const orderedDifficulties = [
    ...difficultyOrder.filter((difficulty) => groupedChallenges.has(difficulty)),
    ...[...groupedChallenges.keys()]
      .filter((difficulty) => !difficultyOrder.includes(difficulty))
      .sort((left, right) => left.localeCompare(right)),
  ];

  const groups = orderedDifficulties.map((difficulty) => ({
    difficulty,
    challenges: groupedChallenges.get(difficulty) ?? [],
  }));

  challengeTree.replaceChildren(
    ...groups.map((group) => {
      const section = document.createElement("section");
      section.className = "tree-group";

      const solvedInGroup = group.challenges.filter((challenge) => state.solvedIds.has(challenge.id)).length;
      const heading = document.createElement("div");
      heading.className = "tree-group-label";
      heading.innerHTML = `
        <span class="tree-toggle">[-]</span>
        <span class="tree-folder">${group.difficulty.toLowerCase()}</span>
        <span class="tree-progress">${solvedInGroup}/${group.challenges.length}</span>
      `;

      const list = document.createElement("ul");
      list.className = "tree-list";

      group.challenges.forEach((challenge, index) => {
        const item = document.createElement("li");
        item.className = "tree-item";

        const button = document.createElement("button");
        button.type = "button";
        button.className = "tree-entry";
        button.classList.toggle("selected", challenge.id === state.selectedId);
        button.classList.toggle("solved", state.solvedIds.has(challenge.id));
        button.innerHTML = `
          <span class="tree-branch">${index === group.challenges.length - 1 ? "└─" : "├─"}</span>
          <span class="tree-title">${escapeHtml(challenge.title)}</span>
          <span class="tree-points">(${challenge.points})</span>
          <span class="badge inline-badge ${badgeClassMap[challenge.difficulty]}">${challenge.difficulty}</span>
        `;

        button.addEventListener("click", () => {
          state.selectedId = challenge.id;
          state.windowMode = "normal";
          window.location.hash = `challenge/${challenge.id}`;
          render();
        });

        item.append(button);
        list.append(item);
      });

      section.append(heading, list);
      return section;
    }),
  );
}

function getDefaultChallengeId(challenges) {
  return challenges.find((challenge) => !state.solvedIds.has(challenge.id))?.id ?? challenges[0]?.id ?? null;
}

function readSolvedIds(challenges) {
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) {
      return new Set();
    }

    const parsed = JSON.parse(raw);
    const validIds = new Set(challenges.map((challenge) => challenge.id));
    return new Set(
      Array.isArray(parsed.solvedIds) ? parsed.solvedIds.filter((id) => validIds.has(id)) : [],
    );
  } catch {
    return new Set();
  }
}

function persistSolvedIds() {
  window.localStorage.setItem(
    STORAGE_KEY,
    JSON.stringify({
      solvedIds: [...state.solvedIds],
    }),
  );
}

function syncWindowMode() {
  const hasSelection = Boolean(state.selectedId);
  detailPanel.classList.toggle("window-focused", hasSelection && state.windowMode === "focus");
  detailPanel.classList.toggle("window-minimized", hasSelection && state.windowMode === "minimized");
  document.body.classList.toggle("challenge-focus-active", hasSelection && state.windowMode === "focus");
}

function clearChallengeHash() {
  const cleanPath = `${window.location.pathname}${window.location.search}`;
  window.history.replaceState(null, "", cleanPath);
}

async function validateFlag(input, expectedDigest) {
  const encoded = new TextEncoder().encode(input);
  const digestBuffer = await window.crypto.subtle.digest("SHA-256", encoded);
  const digestHex = [...new Uint8Array(digestBuffer)]
    .map((byte) => byte.toString(16).padStart(2, "0"))
    .join("");
  return digestHex === expectedDigest;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

window.addEventListener("hashchange", () => {
  const requestedId = getRequestedIdFromHash();
  if (requestedId) {
    state.selectedId = requestedId;
    state.windowMode = "normal";
    render();
    return;
  }

  state.selectedId = null;
  state.windowMode = "normal";
  render();
});

window.addEventListener("keydown", (event) => {
  if (event.key !== "Escape") {
    return;
  }

  if (state.windowMode === "focus") {
    state.windowMode = "normal";
    render();
  }
});

loadChallenges().catch((error) => {
  detailPanel.innerHTML = `
    <div class="detail-empty">
      <h2>Registry Load Failed</h2>
      <p>${escapeHtml(error.message)}</p>
    </div>
  `;
});
