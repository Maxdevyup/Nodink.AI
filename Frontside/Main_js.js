async function SendChatBot() {
    var inputQuestion = document.getElementById("inputQuestion").value;
    let Final_text = ""
    let BufferThink = ""
    let Thinking = true

    var response = await fetch("http://localhost:5000/API/Streamer", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ message: inputQuestion })
    });

    document.getElementById("inputQuestion").value = "";

    const reader = response.body.getReader()
    const decoder = new TextDecoder()

    while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value)
        BufferThink += chunk

        if (BufferThink.includes("<think>")) {
            Thinking = true
        }
        if (BufferThink.includes("</think>")) {
            Thinking = false
        }

        if (Thinking === false) {
            Final_text += chunk
            document.getElementById("ChatContainer").innerHTML = Final_text.replace("<|im_end|>", "")
        }
    }
}