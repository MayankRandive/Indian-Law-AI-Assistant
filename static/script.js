const chat = document.getElementById("chat")
const chatArea = document.getElementById("chatArea")
const input = document.getElementById("input")

// ---------------- SEND MESSAGE ---------------- //
async function send(){

const text = input.value.trim()
if(!text) return

addMessage(text,"user")

input.value=""

// 🔄 Show loading message
const loadingId = addMessage("Thinking...", "bot", true)

try{
    const res = await fetch("/ask",{
        method:"POST",
        headers:{
            "Content-Type":"application/json"
        },
        body: JSON.stringify({question:text})
    })

    const data = await res.json()

    // Replace loading with actual response
    updateMessage(loadingId, data.answer)

}catch(err){
    updateMessage(loadingId, "⚠️ Error connecting to server.")
}

setTimeout(()=>{
chatArea.scrollTop=chatArea.scrollHeight
},50)

}

// ---------------- ADD MESSAGE ---------------- //
function addMessage(content, type, isTemp=false){

const spacer = document.querySelector(".chat-spacer")

const div = document.createElement("div")
div.className = "message"

const id = "msg-" + Date.now()

div.innerHTML =
type==="user"
? `<div class="user">${content}</div>`
: `<div class="bot" id="${id}">${content}</div>`

chat.insertBefore(div, spacer)

return isTemp ? id : null
}

// ---------------- UPDATE MESSAGE ---------------- //
function updateMessage(id, newContent){
const el = document.getElementById(id)
if(el){
    el.innerHTML = newContent
}
}

// ---------------- EXAMPLE CLICK ---------------- //
function askExample(el){
input.value = el.innerText
send()
}

// ---------------- HOME RESET ---------------- //
function goHome(){

chat.innerHTML=`

<div class="landing">

<div class="landing-icon">⚖️</div>

<h2>Know Your Rights</h2>

<p class="subtitle">
Ask about Indian law.
</p>

<div class="suggestions">

<div class="card" onclick="askExample(this)">
Section 420 IPC
</div>

<div class="card" onclick="askExample(this)">
Attempt to murder punishment
</div>

<div class="card" onclick="askExample(this)">
Cyber crime complaint
</div>

<div class="card" onclick="askExample(this)">
Arrest rights
</div>

</div>

</div>

<div class="chat-spacer"></div>
`
}

// ---------------- ENTER KEY ---------------- //
input.addEventListener("keypress", e=>{
if(e.key==="Enter") send()
})