let chatHistory = [];

document.addEventListener('DOMContentLoaded', function() {
  
  const chatForm = document.getElementById('chat-form');
  chatForm.addEventListener('submit', function(event) {
    event.preventDefault();
    sendMessage();
  });

  const inputElement = document.getElementById('user-input');
  inputElement.addEventListener('keypress', function(event) {
    // 13 is the key code for the Enter key
    if (event.keyCode === 13) {
      // Prevent the default Enter key action
      event.preventDefault();
      // Call the sendMessage function
      sendMessage();
    }
  });
});

function showTypingIndicator() {
  addToMessageList('Bot', 'Finding the answer...');
}

/**
* sendMessage() handles the logic for displaying and sending a user's message
*/
function sendMessage() {
  const inputElement = document.getElementById('user-input');
  const message = inputElement.value;
  inputElement.value = '';
  inputElement.focus();
  if (!message.trim()) return;
  addToMessageList('You', message);

  showTypingIndicator(); // Show the typing indicator
  fetch('/respond', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({ message: message, chat_history: chatHistory })
  })
  .then(response => response.json())
  .then(data => {
    removeTypingIndicator(); // Remove the typing indicator
    addToMessageList('Bot', data.bot_message);
    chatHistory.push({
        'user': message,
        'bot': data.bot_message
    });
  })
  .catch(error => {
    console.error('Error:', error);
    removeTypingIndicator(); // Also remove the typing indicator in case of an error
  });
}
// Add a function that clears the typing message from the chat UI
function removeTypingIndicator() {
  const messagelistElement = document.getElementById('message-list');
  const typingIndicator = document.querySelector('.typing-indicator');
  if (typingIndicator) {
    messagelistElement.removeChild(typingIndicator);
  }
}

/**
* addToMessageList handles the UI logic for displaying a sent messsage
*/
function addToMessageList(sender, message) {

  const messagelistElement = document.getElementById('message-list');

  const messageDiv = document.createElement('div');
  messageDiv.classList.add('message');
  if (sender === 'You') {
      messageDiv.classList.add('usermessage');
  } else if (sender === 'Bot') {
    if (message === 'Finding the answer...') {
      messageDiv.classList.add('typing-indicator'); // Use a special class for the typing indicator
    } else {
      messageDiv.classList.add('apimessage');
    }
  }

  const messageContent = document.createElement('div');
  messageContent.classList.add('message-content');
  messageContent.textContent = message;
  // Add the text content to messageDiv
  messageDiv.appendChild(messageContent);
  messagelistElement.appendChild(messageDiv);
  messagelistElement.scrollTop = messagelistElement.scrollHeight; // Scroll to the new message
}

