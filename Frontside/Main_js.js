async function SendChatBot() {
 var inputQuestion = document.getElementById("inputQuestion").value;
 let Final_text = ""
 let BufferThink = ""

    // Send the question to the backend
    var response = await fetch("http://localhost:5000/API/Streamer", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ message: inputQuestion })
    });

    document.getElementById("inputQuestion").value = ""; // Clear the input field after sending
    
    document.getElementById("ChatContainer").innerHTML += "<br>" + "--------------------------" + "<br>"
    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    while (true) {
        const { done, value } = await reader.read()
        if (done) break
    
            const chunk = decoder.decode(value)
            //BufferThink += chunk
            //if BufferThink == "<think/>":
            
            Final_text += chunk
            console.log(Final_text)
            document.getElementById("ChatContainer").innerHTML = Final_text

    }
    



}