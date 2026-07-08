const chatData = document.getElementById("chat-data");

const conversationId = chatData.dataset.conversationId;
const userId = chatData.dataset.userId;
const userName = chatData.dataset.username;

const callModal=document.getElementById("callModal");

const callTitle=document.getElementById("callTitle");

const callText=document.getElementById("callText");

const acceptBtn=document.getElementById("acceptBtn");

const declineBtn=document.getElementById("declineBtn");

const cancelBtn=document.getElementById("cancelBtn");

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
       if(parseInt(data.caller_id)!==parseInt(userId)){

            callTitle.innerText="Incoming Audio Call";

            callText.innerText=data.caller+" is calling you";

            acceptBtn.classList.remove("hidden");

            declineBtn.classList.remove("hidden");

            cancelBtn.classList.add("hidden");

            callModal.classList.remove("hidden");

        }              
    }
    else if(data.type === "incoming_video_call"){
        if(parseInt(data.caller_id)!==parseInt(userId)){
        
            callTitle.innerText="Incoming Video Call";
        
            callText.innerText=data.caller+" is video calling you";
        
            acceptBtn.classList.remove("hidden");
        
            declineBtn.classList.remove("hidden");
        
            cancelBtn.classList.add("hidden");
        
            callModal.classList.remove("hidden");
        
        }
    }
    else if (data.type === "call_accepted") {

        console.log(data.username + " accepted the call.");

    }

    else if (data.type === "call_declined") {

        console.log(data.username + " declined the call.");

        callModal.classList.add("hidden");

    }

    else if (data.type === "call_cancelled") {

        console.log(data.username + " cancelled the call.");

        callModal.classList.add("hidden");

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

    callTitle.innerText="Calling...";

    callText.innerText="Calling user...";

    acceptBtn.classList.add("hidden");

    declineBtn.classList.add("hidden");

    cancelBtn.classList.remove("hidden");

    callModal.classList.remove("hidden");

    socket.send(JSON.stringify({

        type:"audio_call"

    }));

}

// Video call
function startVideoCall(){

    callTitle.innerText="Video Calling...";

    callText.innerText="Connecting...";

    acceptBtn.classList.add("hidden");

    declineBtn.classList.add("hidden");

    cancelBtn.classList.remove("hidden");

    callModal.classList.remove("hidden");

    socket.send(JSON.stringify({

        type:"video_call"

    }));

}

acceptBtn.onclick = function () {

    socket.send(JSON.stringify({
        type: "call_accepted"
    }));

    callModal.classList.add("hidden");

};
declineBtn.onclick = function () {

    socket.send(JSON.stringify({
        type: "call_declined"
    }));

    callModal.classList.add("hidden");

};
cancelBtn.onclick = function () {

    socket.send(JSON.stringify({
        type: "call_cancelled"
    }));

    callModal.classList.add("hidden");

};

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