/* AI Advisor page logic: chat-style Q&A with the finance advisor. */

function appendMessage(text, sender) {
  const chatWindow = document.getElementById("chatWindow");
  const div = document.createElement("div");
  div.className = "chat-message " + (sender === "user" ? "chat-user" : "chat-bot");
  div.textContent = text;
  chatWindow.appendChild(div);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

async function askAdvisor(question) {
  appendMessage(question, "user");
  const typingId = "typing-" + Date.now();
  appendMessage("Thinking...", "bot");
  const chatWindow = document.getElementById("chatWindow");
  const lastBubble = chatWindow.lastElementChild;

  try {
    const data = await apiRequest("/api/advisor", {
      method: "POST",
      body: JSON.stringify({ question }),
    });
    lastBubble.textContent = data.answer;
  } catch (err) {
    lastBubble.textContent = "Sorry, I couldn't process that question. " + err.message;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("advisorForm").addEventListener("submit", (e) => {
    e.preventDefault();
    const input = document.getElementById("advisorQuestion");
    const question = input.value.trim();
    if (!question) return;
    input.value = "";
    askAdvisor(question);
  });

  document.querySelectorAll(".suggested-q").forEach((btn) => {
    btn.addEventListener("click", () => askAdvisor(btn.textContent));
  });
});
