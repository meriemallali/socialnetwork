// I wrote this code.
const id = JSON.parse(document.getElementById("user-id").textContent);
const message_owner = JSON.parse(
  document.getElementById("user-username").textContent
);
const friend = JSON.parse(
  document.getElementById("username-friend").textContent
);
// console.log(friend)

wsURL = `ws://${window.location.host}/ws/${id}`;
// console.log(wsURL)

const websocket = new WebSocket(wsURL);

websocket.onopen = (event) => {
  console.log("Accepted Connection", event);
};

websocket.onclose = (event) => {
  console.log("Lost Connection", event);
};

websocket.onerror = (event) => {
  console.log("Error Occured while connecting:", event);
};

var timeSince = function (date) {
  if (typeof date !== "object") {
    date = new Date(date);
  }

  var seconds = Math.floor((new Date() - date) / 1000);
  var intervalType;

  let intervalTime = Math.floor(seconds / 60);
  if (intervalTime >= 1) {
    intervalType = "minute";
  } else {
    intervalTime = seconds;
  }
  if (intervalTime === 0) {
    return "just now";
  }

  return intervalTime + " " + intervalType;
};

// parse the message and change its appearance depending on the message owner and current logged in user.
websocket.onmessage = function (event) {
  const message_data = JSON.parse(event.data);
  console.log(message_data);
  //   console.log(message_data);
  // if the message owner is the current logged in user => display in right side, if not display in left side.
  if (message_data.username == message_owner) {
    document.querySelector("#message").innerHTML += ` 
    <div class="d-flex flex-row justify-content-end mb-4 pt-1">
    <div>
      <p class="small p-2 me-3 mb-1 text-white rounded-3 " style="background-color:#507E9F" >${
        message_data.message
      }</p>
      <p class="small me-3 mb-3 rounded-3 text-muted d-flex justify-content-end">${timeSince(
        new Date(Date.now())
      )}</p>
    </div>
  </div>
 `;
  } else {
    document.querySelector("#message").innerHTML += `    
  <div class="d-flex flex-row justify-content-start">
  <div>
    <p class="small p-2 ms-3 mb-1 rounded-3" style="background-color: #f5f6f7;">${message_data.message}</p>
    <p class="small ms-3 mb-3 rounded-3 text-muted">${message.sent_date}</p>
  </div>                  
</div>
  `;
  }
};

document.querySelector("#message-submit").onclick = function (event) {
  const input = document.querySelector("#input");
  const message = input.value;

  websocket.send(
    JSON.stringify({
      message: message,
      username: message_owner,
      friend: friend,
    })
  );
  //clear input field after submitting to an empty string.
  event.preventDefault();
  input.value = "";
};

// End of code I wrote.
