document.addEventListener("DOMContentLoaded", () => {
  const root = document.querySelector("[data-practice-app]");
  if (!root) return;

  const csrfToken = document.querySelector("meta[name='csrf-token']").content;
  const questionList = document.getElementById("questionList");
  const selectedQuestion = document.getElementById("selectedQuestion");
  const selectedMeta = document.getElementById("selectedMeta");
  const answerInput = document.getElementById("answerInput");
  const feedbackForm = document.getElementById("feedbackForm");
  const submitButton = document.getElementById("submitButton");
  const clearButton = document.getElementById("clearButton");
  const readinessBar = document.getElementById("readinessBar");
  const readinessLabel = document.getElementById("readinessLabel");
  const wordCount = document.getElementById("wordCount");

  const state = {
    category: root.dataset.category,
    difficulty: root.dataset.difficulty,
    question: root.dataset.firstQuestion,
  };

  bindFilterButtons();
  bindQuestionButtons();
  updateReadiness();

  answerInput.addEventListener("input", updateReadiness);
  clearButton.addEventListener("click", () => {
    answerInput.value = "";
    updateReadiness();
    answerInput.focus();
  });

  feedbackForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    await submitFeedback();
  });

  function bindFilterButtons() {
    document.querySelectorAll("#categoryButtons [data-category]").forEach((button) => {
      button.addEventListener("click", async () => {
        state.category = button.dataset.category;
        setActive("[data-category]", button);
        await loadQuestions();
      });
    });

    document.querySelectorAll("#difficultyButtons [data-difficulty]").forEach((button) => {
      button.addEventListener("click", async () => {
        state.difficulty = button.dataset.difficulty;
        setActive("[data-difficulty]", button);
        await loadQuestions();
      });
    });
  }

  function bindQuestionButtons() {
    questionList.querySelectorAll("[data-question]").forEach((button) => {
      button.addEventListener("click", () => chooseQuestion(button));
    });
  }

  function chooseQuestion(button) {
    state.question = button.dataset.question;
    setActive("[data-question]", button);
    selectedQuestion.textContent = state.question;
    selectedMeta.textContent = `${state.category} / ${state.difficulty}`;
  }

  async function loadQuestions() {
    selectedMeta.textContent = `${state.category} / ${state.difficulty}`;
    questionList.classList.add("is-loading");

    const params = new URLSearchParams({
      category: state.category,
      difficulty: state.difficulty,
    });

    try {
      const response = await fetch(`/api/questions?${params.toString()}`);
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Unable to load questions.");

      renderQuestions(data.questions);
      hideFeedback();
    } catch (error) {
      showToast(error.message);
    } finally {
      questionList.classList.remove("is-loading");
    }
  }

  function renderQuestions(questions) {
    questionList.replaceChildren();
    questions.forEach((question, index) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = `question-card ${index === 0 ? "is-active" : ""}`;
      button.dataset.question = question;

      const number = document.createElement("span");
      number.className = "question-number";
      number.textContent = String(index + 1);

      const text = document.createElement("span");
      text.textContent = question;

      button.append(number, text);
      questionList.append(button);
    });

    state.question = questions[0] || "";
    selectedQuestion.textContent = state.question || "No questions available";
    bindQuestionButtons();
  }

  async function submitFeedback() {
    const answer = answerInput.value.trim();
    if (!answer) {
      showToast("Please write an answer before requesting feedback.");
      answerInput.focus();
      return;
    }

    submitButton.disabled = true;
    submitButton.textContent = "Analyzing...";

    try {
      const response = await fetch("/api/feedback", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify({
          category: state.category,
          difficulty: state.difficulty,
          question: state.question,
          answer,
        }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Feedback failed.");

      renderFeedback(data.feedback);
      updateStats(data.stats);
    } catch (error) {
      showToast(error.message);
    } finally {
      submitButton.disabled = false;
      submitButton.textContent = "Analyze answer";
    }
  }

  function updateReadiness() {
    const words = countWords(answerInput.value);
    const starHits = ["situation", "task", "action", "result", "impact"].filter((term) =>
      answerInput.value.toLowerCase().includes(term)
    ).length;
    const numberBonus = /\d+|percent|users|days|hours|marks/i.test(answerInput.value) ? 15 : 0;
    const lengthScore = Math.min(70, Math.round((words / 90) * 70));
    const readiness = Math.min(100, lengthScore + starHits * 5 + numberBonus);

    readinessBar.style.width = `${readiness}%`;
    readinessLabel.textContent = `${readiness}%`;
    wordCount.textContent = `${words} ${words === 1 ? "word" : "words"}`;
  }

  function renderFeedback(feedback) {
    document.getElementById("feedbackPanel").classList.remove("is-hidden");
    document.getElementById("feedbackGrade").textContent = feedback.grade;
    document.getElementById("feedbackScore").textContent = feedback.score;
    document.getElementById("feedbackSummary").textContent = feedback.summary;

    const criteriaGrid = document.getElementById("criteriaGrid");
    criteriaGrid.replaceChildren();
    ["relevance", "structure", "specificity", "communication"].forEach((key) => {
      const item = document.createElement("div");
      item.className = "criterion";

      const top = document.createElement("div");
      const label = document.createElement("span");
      label.textContent = titleCase(key);
      const score = document.createElement("strong");
      score.textContent = feedback.criteria[key];
      top.append(label, score);

      const track = document.createElement("div");
      track.className = "meter-track";
      const fill = document.createElement("span");
      fill.className = "meter-fill";
      fill.style.width = `${feedback.criteria[key]}%`;
      track.append(fill);

      item.append(top, track);
      criteriaGrid.append(item);
    });

    fillList("strengthList", feedback.strengths);
    fillList("improvementList", feedback.improvements);
  }

  function fillList(id, items) {
    const list = document.getElementById(id);
    list.replaceChildren();
    items.forEach((item) => {
      const li = document.createElement("li");
      li.textContent = item;
      list.append(li);
    });
  }

  function updateStats(stats) {
    document.getElementById("totalAttempts").textContent = stats.total_attempts;
    document.getElementById("averageScore").textContent = stats.average_score;
    document.getElementById("bestScore").textContent = stats.best_score;
  }

  function hideFeedback() {
    document.getElementById("feedbackPanel").classList.add("is-hidden");
  }

  function setActive(selector, activeButton) {
    root.querySelectorAll(selector).forEach((button) => button.classList.remove("is-active"));
    activeButton.classList.add("is-active");
  }

  function countWords(text) {
    return (text.trim().match(/\b[\w']+\b/g) || []).length;
  }

  function titleCase(text) {
    return text.charAt(0).toUpperCase() + text.slice(1);
  }

  function showToast(message) {
    const toast = document.createElement("div");
    toast.className = "toast";
    toast.textContent = message;
    document.body.append(toast);
    setTimeout(() => toast.remove(), 3500);
  }
});
