let audio1 = new Audio(
  "https://s3-us-west-2.amazonaws.com/s.cdpn.io/242518/clickUp.mp3"
);
function chatOpen() {
  document.getElementById("chat-open").style.display = "none";
  document.getElementById("chat-close").style.display = "block";
  document.getElementById("chat-window1").style.display = "block";

  audio1.load();
  audio1.play();
}
function chatClose() {
  document.getElementById("chat-open").style.display = "block";
  document.getElementById("chat-close").style.display = "none";
  document.getElementById("chat-window1").style.display = "none";
  document.getElementById("chat-window2").style.display = "none";

  audio1.load();
  audio1.play();
}
function openConversation() {
  document.getElementById("chat-window2").style.display = "block";
  document.getElementById("chat-window1").style.display = "none";

  audio1.load();
  audio1.play();

  socket.emit("start_conversation");
}

//Gets the text from the input box(user)
function userResponse() {
  const userText = document.getElementById("textInput").value;
  const audio3 = new Audio(
    "https://prodigits.co.uk/content/ringtones/tone/2020/alert/preview/4331e9c25345461.mp3"
  );

  if (userText == "") {
    alert("Please type something!");
  } else {
    const objDiv = document.getElementById("messageBox");

    objDiv.innerHTML += `<div class="first-chat">
      <p>${userText}</p>
      <div class="arrow"></div>
      </div>`;
    audio3.load();
    audio3.play();

    document.getElementById("textInput").value = "";
    objDiv.innerHTML += `<div class="second-chat">
        <div class="circle" id="circle-mar"></div>
        <p class="bot_mssg_box"></p>
        <div class="arrow"></div> 
      </div>`;
    objDiv.scrollTop = objDiv.scrollHeight;
    socket.emit("user_message", { "message": userText });
    console.log(document.getElementById("textInput").value);
  }
}
socket.on("first_message", function (response) {
  const msg = response["message"];
  const options = response["options"] ? response["options"] : null;
  console.log(msg, options);
  const nodes = document.querySelectorAll(".bot_mssg_box")
  const objDiv = document.getElementById("messageBox");
  const last = nodes[nodes.length - 1];
  const html = convertToHTML(msg);
  last.append(`${html}`);

  const buttons2 = document.createElement("div");
  for (let key in options) {
    const option = options[key];
    console.log(key);
    const button = document.createElement("button");
    button.innerHTML = key;
    button.style.margin = "5px";
    button.style.padding = "5px";
      button.style.border = "none";
      button.style.borderRadius = "5px";
      button.classList.add("greive-btn");
      button.style.backgroundColor = "#7f8ac5";
      button.style.color = "white";
      button.style.fontFamily="Montserrat";
      button.addEventListener('mouseover', () => {
        button.style.backgroundColor = '#4c5aa1';
      });
      button.addEventListener('mouseout', () => {
        button.style.backgroundColor = '#7f8ac5';
      });


    objDiv.scrollTop = objDiv.scrollHeight;
    button.onclick = function () {
      socket.emit("user_message", { "message": option });
      const objDiv = document.getElementById("messageBox");
      objDiv.innerHTML += `<div class="first-chat
      ">
      <p>${key}</p>
      <div class="arrow"></div>
      </div>`;
      objDiv.innerHTML += `<div class="second-chat">
      <div class="circle" id="circle-mar"></div>
      <p class="bot_mssg_box"></p>
      <div class="arrow"></div>
    </div>`;
      objDiv.scrollTop = objDiv.scrollHeight;
    }
    buttons2.appendChild(button);
  }
  buttons2.classList.add("button-container");
  document.getElementById("messageBox").appendChild(buttons2);

  const audio3 = new Audio(
    "https://downloadwap.com/content2/mp3-ringtones/tone/2020/alert/preview/56de9c2d5169679.mp3"
  );
  audio3.load();
  audio3.play();
  objDiv.scrollTop = objDiv.scrollHeight;
});

// bot's Respononse to user's message
socket.on("user_response", function (response) {
  const msg = response["message"];
  const options = response["options"] ? response["options"] : null;
  console.log(msg, options);
  const nodes = document.querySelectorAll(".bot_mssg_box")
  const last = nodes[nodes.length - 1];
  last.append(` ${msg} `);

  const buttons = document.createElement("div");
  if (options) {
    for (let key in options) {
      const option = options[key];
      console.log(key);

      const button = document.createElement("button");
      
      button.innerHTML = key;
      button.style.margin = "5px";
      button.style.padding = "5px";
      button.style.border = "none";
      button.style.borderRadius = "5px";
      button.style.backgroundColor = "#7f8ac5";
      button.style.color = "white";
      button.style.fontFamily="Montserrat";
      button.addEventListener('mouseover', () => {
        button.style.backgroundColor = '#4c5aa1';
      });
      button.addEventListener('mouseout', () => {
        button.style.backgroundColor = '#7f8ac5';
      });
      button.onclick = function () {
        socket.emit("user_message", { "message": option });
        const objDiv = document.getElementById("messageBox");
        objDiv.innerHTML += `<div class="first-chat
        ">
        <p>${key}</p>
        <div class="arrow"></div>
        </div>`;
        objDiv.innerHTML += `<div class="second-chat">
        <div class="circle" id="circle-mar"></div>
        <p class="bot_mssg_box"></p>
        <div class="arrow"></div>
      </div>`;
        objDiv.scrollTop = objDiv.scrollHeight;
      }
      buttons.appendChild(button);
    }
    buttons.classList.add("button-container");
    document.getElementById("messageBox").appendChild(buttons);
  }
  // const audio3 = new Audio(
  //   "https://downloadwap.com/content2/mp3-ringtones/tone/2020/alert/preview/56de9c2d5169679.mp3"
  // );
  // audio3.load();
  // audio3.play();
  const objDiv = document.getElementById("messageBox");
  objDiv.scrollTop = objDiv.scrollHeight;
});

//press enter on keyboard and send message
addEventListener("keypress", (e) => {
  if (e.keyCode === 13) {

    const e = document.getElementById("textInput");
    if (e === document.activeElement) {
      userResponse();
    }
  }
});

function convertToHTML(text) {
  // Regular expression to match each step
  // const regex = /\d+\s*\.\s*(.*)/g;
  
  // Replace each match with HTML list item
  // const html = text.replace(regex, '<li>$1</li>');

  // Wrap the list items in an ordered list
  // const finalHTML = `<li>${html}</li>`;
  console.log(text);
  return text;
}
