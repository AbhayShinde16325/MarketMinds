async function sendQuestion() {
    const input = document.getElementById("question");
    const chat = document.getElementById("chat");

    const question = input.value.trim();
    if (!question) return;

    addMessage(question, "user");
    input.value = "";

    try {
        const response = await fetch("/ask", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ question })
        });

        if (!response.ok) {
            addMessage(`Error: ${response.status}`, "bot");
            return;
        }

        const data = await response.json();
        addMessage(data.answer, "bot");

    } catch (err) {
        addMessage("Failed to reach backend.", "bot");
        console.error(err);
    }
}

/* Register Enter key ONCE */
document.getElementById("question").addEventListener("keydown", function (e) {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendQuestion();
    }
});

function addMessage(text, role) {
    const chat = document.getElementById("chat");
    const div = document.createElement("div");
    div.className = `message ${role}`;
    div.innerHTML = text.replace(/\n/g, "<br>");
    chat.appendChild(div);

    //️// Auto-scroll to bottom
    chat.scrollTop = chat.scrollHeight;
}
