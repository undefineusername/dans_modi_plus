// Initialize Firebase
const firebaseConfig = {
  apiKey: "AIzaSyANsHaVMwpuOR_TiIAC9vA0p3lfo62OSKs",
  authDomain: "chat-49c18.firebaseapp.com",
  projectId: "chat-49c18",
  storageBucket: "chat-49c18.firebasestorage.app",
  messagingSenderId: "125873381410",
  appId: "1:125873381410:web:3ad3d76f3c094ae84caa7b",
  measurementId: "G-RQMQQXLB1Q"
};
// Initialize Firebase App & Firestore
if (!firebase.apps.length) {
  firebase.initializeApp(firebaseConfig);
}
const db = firebase.firestore();

// Application State
let currentSessionId = null;
let currentMode = "기본 상담";
let currentEmotion = "중립";

// DOM Elements
const messagesContainer = document.getElementById('messagesContainer');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');
const sessionsList = document.getElementById('sessionsList');
const newSessionBtn = document.getElementById('newSessionBtn');
const modeDisplay = document.getElementById('modeDisplay');
const emotionDisplay = document.getElementById('emotionDisplay');

// Initialize Event Listeners
document.addEventListener('DOMContentLoaded', () => {
  initEventListeners();
  loadSessions();
});

function initEventListeners() {
  newSessionBtn.addEventListener('click', createNewSession);

  sendButton.addEventListener('click', handleSendMessage);

  messageInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  });
}

// Render Sessions List
function loadSessions() {
  db.collection('sessions')
    .orderBy('updatedAt', 'desc')
    .onSnapshot((snapshot) => {
      sessionsList.innerHTML = '';

      if (snapshot.empty) {
        sessionsList.innerHTML = '<div class="loading-indicator">상담 내역이 없습니다.</div>';
        return;
      }

      snapshot.forEach((doc) => {
        const session = doc.data();
        const sessionEl = createSessionItemElement(doc.id, session);
        sessionsList.appendChild(sessionEl);
      });
    }, (error) => {
      console.error("Error loading sessions:", error);
      sessionsList.innerHTML = '<div class="loading-indicator">세션을 불러올 수 없습니다.</div>';
    });
}

function createSessionItemElement(id, session) {
  const div = document.createElement('div');
  div.className = `session-item ${id === currentSessionId ? 'active' : ''}`;
  div.dataset.id = id;

  const date = session.updatedAt ? new Date(session.updatedAt.toDate()).toLocaleDateString() : '';

  div.innerHTML = `
    <div class="session-title">${escapeHTML(session.title || '새로운 상담')}</div>
    <div class="session-meta">
      <span>${escapeHTML(session.mode || '일반')}</span>
      <span>•</span>
      <span>${date}</span>
    </div>
  `;

  div.addEventListener('click', () => selectSession(id, session));
  return div;
}

// Create a New Session
async function createNewSession() {
  try {
    const newSession = {
      title: '새 상담 세션',
      mode: '일반 상담',
      emotion: '중립',
      createdAt: firebase.firestore.FieldValue.serverTimestamp(),
      updatedAt: firebase.firestore.FieldValue.serverTimestamp()
    };

    const docRef = await db.collection('sessions').add(newSession);
    selectSession(docRef.id, newSession);
  } catch (error) {
    console.error("Error creating session:", error);
    alert("새 세션을 생성하는데 실패했습니다.");
  }
}

// Select Active Session
function selectSession(sessionId, sessionData) {
  currentSessionId = sessionId;
  currentMode = sessionData.mode || '일반 상담';
  currentEmotion = sessionData.emotion || '중립';

  // Update Header UI
  modeDisplay.textContent = currentMode;
  emotionDisplay.textContent = currentEmotion;

  // Enable Inputs
  messageInput.disabled = false;
  sendButton.disabled = false;
  messageInput.focus();

  // Highlight active sidebar item
  document.querySelectorAll('.session-item').forEach(el => {
    el.classList.toggle('active', el.dataset.id === sessionId);
  });

  // Load Messages for the Selected Session
  loadMessages(sessionId);
}

// Load Chat Messages
function loadMessages(sessionId) {
  db.collection('sessions').doc(sessionId).collection('messages')
    .orderBy('timestamp', 'asc')
    .onSnapshot((snapshot) => {
      messagesContainer.innerHTML = '';

      if (snapshot.empty) {
        messagesContainer.innerHTML = `
          <div class="message-placeholder">
            <div class="placeholder-text">안녕하세요! 무엇을 도와드릴까요?</div>
          </div>`;
        return;
      }

      snapshot.forEach((doc) => {
        const msg = doc.data();
        appendMessageUI(msg.text, msg.sender, msg.timestamp);
      });

      scrollToBottom();
    });
}

// Append Message to UI
function appendMessageUI(text, sender, timestamp) {
  const msgDiv = document.createElement('div');
  msgDiv.className = `message ${sender}`;

  const timeStr = timestamp
    ? new Date(timestamp.toDate ? timestamp.toDate() : timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    : new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  msgDiv.innerHTML = `
    ${sender === 'user' ? `<span class="message-time">${timeStr}</span>` : ''}
    <div class="message-content">${escapeHTML(text)}</div>
    ${sender === 'ai' ? `<span class="message-time">${timeStr}</span>` : ''}
  `;

  messagesContainer.appendChild(msgDiv);
  scrollToBottom();
}

// Handle Send Action
async function handleSendMessage() {
  const text = messageInput.value.trim();
  if (!text || !currentSessionId) return;

  messageInput.value = '';

  try {
    // 1. Save user message to Firestore
    await db.collection('sessions').doc(currentSessionId).collection('messages').add({
      text: text,
      sender: 'user',
      timestamp: firebase.firestore.FieldValue.serverTimestamp()
    });

    // Update Session Title if it's the first user message
    db.collection('sessions').doc(currentSessionId).update({
      title: text.substring(0, 20) + (text.length > 20 ? '...' : ''),
      updatedAt: firebase.firestore.FieldValue.serverTimestamp()
    });

    // 2. Trigger Mock AI Response (Replace with your actual API endpoint)
    simulateAIResponse(text);

  } catch (error) {
    console.error("Error sending message:", error);
  }
}

// Simulated AI Backend Call
async function simulateAIResponse(userText) {
  // Simulate delay
  setTimeout(async () => {
    const aiReply = `말씀하신 "${userText}"에 대해 이해했습니다. 어떻게 도와드릴까요?`;

    await db.collection('sessions').doc(currentSessionId).collection('messages').add({
      text: aiReply,
      sender: 'ai',
      timestamp: firebase.firestore.FieldValue.serverTimestamp()
    });
  }, 1000);
}

// Auto-scroll chat area
function scrollToBottom() {
  const wrapper = document.querySelector('.messages-wrapper');
  if (wrapper) {
    wrapper.scrollTop = wrapper.scrollHeight;
  }
}

// Helper: Sanitize Text
function escapeHTML(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}