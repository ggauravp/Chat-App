const chatData = document.getElementById("chat-data");

const conversationId = chatData.dataset.conversationId;
const userId = chatData.dataset.userId;
const userName = chatData.dataset.username;
let currentCallType = null;
const callModal=document.getElementById("callModal");

const callTitle=document.getElementById("callTitle");

const callText=document.getElementById("callText");

const acceptBtn=document.getElementById("acceptBtn");

const declineBtn=document.getElementById("declineBtn");


// Message container
const messagesContainer = document.getElementById("messages");

// Call screen
const callScreen =
document.getElementById("callScreen");

// Local camera
const localVideo =
document.getElementById("localVideo");

// Remote camera
const remoteVideo =
document.getElementById("remoteVideo");

// Local media stream
let localStream = null;

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
       currentCallType = "audio";
       if(parseInt(data.caller_id)!==parseInt(userId)){

            callTitle.innerText="Incoming Audio Call";

            callText.innerText=data.caller+" is calling you";

            acceptBtn.classList.remove("hidden");

            declineBtn.classList.remove("hidden");

            callModal.classList.remove("hidden");

        }              
    }
    else if(data.type === "incoming_video_call"){
        currentCallType = "video";
        if(parseInt(data.caller_id)!==parseInt(userId)){
        
            callTitle.innerText="Incoming Video Call";
        
            callText.innerText=data.caller+" is video calling you";
        
            acceptBtn.classList.remove("hidden");
        
            declineBtn.classList.remove("hidden");
        
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

        callModal.classList.add("hidden");
        callScreen.classList.add("hidden");

        if (localStream) {
            localStream.getTracks().forEach(track => track.stop());
            localStream = null;
        }

        localVideo.srcObject = null;
        remoteVideo.srcObject = null;
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
async function startAudioCall(){

    await openLocalMedia(false); // Open local microphone only, no video
    socket.send(JSON.stringify({

        type:"audio_call"

    }));

}

// Video call
async function startVideoCall(){

    await openLocalMedia(true); // Open local camera and microphone 
    socket.send(JSON.stringify({

        type:"video_call"

    }));

}

acceptBtn.onclick = async function () {
    console.log("Call accepted by user");

    // Open receiver camera & microphone
    if (currentCallType === "video") {
        await openLocalMedia(true); // Open local camera and microphone

    } else if (currentCallType === "audio") {
        await openLocalMedia(false); // Open local microphone only, no video
    }
    
    console.log("Local media stream opened");

    // Hide incoming call popup
    callModal.classList.add("hidden");

    // Notify caller
    socket.send(JSON.stringify({
        type: "call_accepted"
    }));

};
declineBtn.onclick = function () {

    socket.send(JSON.stringify({
        type: "call_declined"
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

async function openLocalMedia( video=true ){

    try{
        // Request access to camera and microphone and add video and audio tracks to the local stream
        localStream =
        await navigator.mediaDevices.getUserMedia({ 

            video:video,

            audio:true

        });

        localVideo.srcObject = localStream; // adds the local stream to the local video element

        callScreen.classList.remove("hidden"); // makes the call screen visible

        if(video){
            localVideo.style.display = "block"; // shows the local video element if video is enabled
        } else {
            localVideo.style.display = "none"; // hides the local video element if video is disabled
        }

    }

    catch(err){

        alert("Unable to access camera or microphone. Please check your device settings and permissions.");

        console.error(err);

    }

}

function endCall(){   
    console.log("Ending call...");
    if(socket.readyState === WebSocket.OPEN){
        console.log("Sending call_cancelled");
        socket.send(JSON.stringify({
            type: "call_cancelled"
        }));
    }
    if(localStream){
        localStream
        .getTracks()
        .forEach(track=>track.stop());
        localStream = null;
    }
    localVideo.srcObject=null;
    remoteVideo.srcObject=null;
    callScreen.classList.add("hidden");
}
