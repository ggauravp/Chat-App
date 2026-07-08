const chatData = document.getElementById("chat-data");

const conversationId = chatData.dataset.conversationId;
const userId = chatData.dataset.userId;
const userName = chatData.dataset.username;

// Message container
const messagesContainer = document.getElementById("messages");

// Create WebSocket connection
const socket = new WebSocket(
    "ws://" + window.location.host + "/ws/chat/" + conversationId + "/"
);
// Handle incoming events
socket.onmessage = function(event){
    console.log("Received:", event.data);
    const data = JSON.parse(event.data);
    if(data.type === "chat"){
        appendMessage(
            data.sender_id,
            data.sender_username,
            data.message,
            data.timestamp || getTime()
        );
    }
    else if(data.type === "incoming_audio_call"){
        alert(data.caller + " is calling you 📞");
    }
    else if(data.type === "incoming_video_call"){
        alert(data.caller + " is video calling you 🎥");
    }
};

// Send chat message
function sendMessage(){

    const input = document.getElementById("messageInput");

    if(!input.value.trim()) return;

    socket.send(JSON.stringify({

        type:"chat",
        message:input.value

    }));

    input.value="";
}

// Audio call
function startAudioCall(){

    socket.send(JSON.stringify({

        type:"audio_call"

    }));

}

// Video call
function startVideoCall(){

    socket.send(JSON.stringify({

        type:"video_call"

    }));

}

socket.onclose=()=>console.log("WebSocket closed");

// Load old messages
const oldMessages = JSON.parse(
    document.getElementById("messages-data").textContent
);
oldMessages.forEach(msg=>{

    appendMessage(

        msg.sender_id,
        msg.sender_username,
        msg.message,
        msg.timestamp

    );

});

// Add message bubble
function appendMessage(senderId,senderName,message,time){

    const div=document.createElement("div");

    const isMe=parseInt(senderId)===parseInt(userId);

    div.classList.add("msg");
    div.classList.add(isMe?"sent":"received");

    div.innerHTML=`
        <div class="msg-meta">
            <span>${isMe?"You":senderName}</span>
            <span>${time}</span>
        </div>

        <div>${message}</div>
    `;

    messagesContainer.appendChild(div);

    messagesContainer.scrollTop=messagesContainer.scrollHeight;

}

// Current time
function getTime(){

    const now=new Date();

    return now.getHours()+":"+
    String(now.getMinutes()).padStart(2,"0");

}