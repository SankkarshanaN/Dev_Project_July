// Setup CodeMirror
const editor = CodeMirror.fromTextArea(document.getElementById("code"), {
    lineNumbers: true,
    mode: "python",
    theme: "dracula",
    matchBrackets: true,
    autoCloseBrackets: true,
    indentUnit: 4,
    tabSize: 4,
    indentWithTabs: true,
});

// force bigger size
editor.setSize("100%", "500px");



// Change mode when language changes
document.getElementById('language').addEventListener('change', function () {
    const lang = this.value;
    if (lang === 'python') {
        editor.setOption('mode', 'python');
    } else if (lang === 'java') {
        editor.setOption('mode', 'text/x-java');
    } else if (lang === 'cpp' || lang === 'c') {
        editor.setOption('mode', 'text/x-c++src');
    }
});

// Custom Input/Output Run Handler
document.getElementById("run-custom-btn").addEventListener("click", async () => {
    const code = editor.getValue();
    const lang = document.getElementById("language").value;
    const input = document.getElementById("custom-input").value;

    try {
        const response = await fetch(runCustomUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken
            },
            body: JSON.stringify({
                language: lang,
                code: code,
                input: input
            })
        });

        const result = await response.json();
        document.getElementById("custom-output").textContent =
            result.output || "⚠️ Error running code.";
    } catch (err) {
        document.getElementById("custom-output").textContent =
            "❌ Failed to connect to server.";
    }
});
