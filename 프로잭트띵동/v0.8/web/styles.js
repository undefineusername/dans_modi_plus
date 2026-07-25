// CSS-in-JS 스타일 정의 (채찍지 느낌)
const cssContent = `
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

:root {
    --primary-dark: #0f0f0f;
    --secondary-dark: #1a1a1a;
    --tertiary-dark: #2d2d2d;
    --accent-purple: #8b5cf6;
    --accent-blue: #3b82f6;
    --text-primary: #ffffff;
    --text-secondary: #b0b0b0;
    --border-color: #333333;
    --message-user-bg: #8b5cf6;
    --message-ai-bg: #2d2d2d;
}

html, body {
    height: 100%;
    width: 100%;
    background: var(--primary-dark);
    color: var(--text-primary);
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
    font-size: 14px;
    line-height: 1.5;
    overflow: hidden;
}

/* App Container */
.app-container {
    display: flex;
    height: 100vh;
    width: 100%;
    background: var(--primary-dark);
}

/* Header */
.header {
    position: fixed;
    top: 0;
    left: 300px;
    right: 0;
    height: 80px;
    background: linear-gradient(135deg, var(--secondary-dark) 0%, var(--tertiary-dark) 100%);
    border-bottom: 1px solid var(--border-color);
    padding: 0 32px;
    display: flex;
    align-items: center;
    z-index: 100;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.3);
}

.header-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
    gap: 24px;
}

.logo {
    font-size: 24px;
    font-weight: 700;
    background: linear-gradient(135deg, var(--accent-purple), var(--accent-blue));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.5px;
}

.consultation-info {
    display: flex;
    gap: 24px;
    margin-left: auto;
}

.info-item {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
}

.info-item .label {
    font-size: 12px;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    font-weight: 600;
}

.info-item .value {
    font-size: 16px;
    color: var(--text-primary);
    font-weight: 600;
}

/* Chat Container */
.chat-container {
    position: fixed;
    top: 80px;
    left: 300px;
    right: 0;
    bottom: 0;
    display: flex;
    flex-direction: column;
    background: var(--primary-dark);
}

.messages-wrapper {
    flex: 1;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
}

.messages {
    display: flex;
    flex-direction: column;
    gap: 16px;
    padding: 24px 32px;
    flex: 1;
}

.message-placeholder {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: var(--text-secondary);
}

.placeholder-text {
    font-size: 18px;
    font-weight: 300;
    letter-spacing: 0.5px;
}

/* Messages */
.message {
    display: flex;
    gap: 12px;
    align-items: flex-end;
    animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.message.user {
    justify-content: flex-end;
}

.message.ai {
    justify-content: flex-start;
}

.message-content {
    max-width: 60%;
    padding: 12px 16px;
    border-radius: 12px;
    word-wrap: break-word;
    font-size: 14px;
    line-height: 1.5;
}

.message.user .message-content {
    background: var(--message-user-bg);
    color: var(--text-primary);
    border-bottom-right-radius: 4px;
}

.message.ai .message-content {
    background: var(--message-ai-bg);
    color: var(--text-primary);
    border-bottom-left-radius: 4px;
    border: 1px solid var(--border-color);
}

.message-time {
    font-size: 12px;
    color: var(--text-secondary);
    margin: 0 8px;
}

/* Input Area */
.input-area {
    padding: 24px 32px;
    border-top: 1px solid var(--border-color);
    background: var(--secondary-dark);
}

.input-wrapper {
    display: flex;
    gap: 12px;
    align-items: center;
}

.message-input {
    flex: 1;
    background: var(--tertiary-dark);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 12px 16px;
    color: var(--text-primary);
    font-size: 14px;
    outline: none;
    transition: all 0.2s ease;
}

.message-input:focus {
    border-color: var(--accent-purple);
    box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1);
}

.message-input:disabled {
    background: var(--tertiary-dark);
    color: var(--text-secondary);
    cursor: not-allowed;
    opacity: 0.5;
}

.send-button {
    width: 44px;
    height: 44px;
    background: linear-gradient(135deg, var(--accent-purple), var(--accent-blue));
    border: none;
    border-radius: 8px;
    color: var(--text-primary);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s ease;
    flex-shrink: 0;
}

.send-button:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 8px 16px rgba(139, 92, 246, 0.3);
}

.send-button:active:not(:disabled) {
    transform: translateY(0);
}

.send-button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

/* Sidebar */
.sidebar {
    position: fixed;
    left: 0;
    top: 0;
    width: 300px;
    height: 100vh;
    background: var(--secondary-dark);
    border-right: 1px solid var(--border-color);
    display: flex;
    flex-direction: column;
    z-index: 200;
}

.sidebar-header {
    padding: 24px 16px;
    border-bottom: 1px solid var(--border-color);
}

.sidebar-header h3 {
    font-size: 16px;
    font-weight: 700;
    margin-bottom: 12px;
    color: var(--text-primary);
}

.new-session-btn {
    width: 100%;
    background: var(--accent-purple);
    border: none;
    border-radius: 6px;
    padding: 8px 12px;
    color: var(--text-primary);
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
}

.new-session-btn:hover {
    background: #a78bfa;
    transform: translateY(-1px);
}

/* Sessions List */
.sessions-list {
    flex: 1;
    overflow-y: auto;
    padding: 12px 8px;
}

.session-item {
    padding: 12px;
    margin-bottom: 8px;
    background: var(--tertiary-dark);
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s ease;
    border: 1px solid transparent;
    border-left: 3px solid transparent;
}

.session-item:hover {
    background: var(--tertiary-dark);
    border-color: var(--accent-purple);
}

.session-item.active {
    background: linear-gradient(135deg, rgba(139, 92, 246, 0.2), transparent);
    border-left-color: var(--accent-purple);
}

.session-title {
    font-size: 14px;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 6px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.session-meta {
    display: flex;
    gap: 8px;
    font-size: 12px;
    color: var(--text-secondary);
}

.session-meta span {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.loading-indicator {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px;
    color: var(--text-secondary);
    font-size: 13px;
}

/* Scrollbar */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: transparent;
}

::-webkit-scrollbar-thumb {
    background: var(--border-color);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--tertiary-dark);
}

/* Responsive */
@media (max-width: 768px) {
    .sidebar {
        width: 100%;
        height: auto;
        border-right: none;
        border-bottom: 1px solid var(--border-color);
        flex-direction: row;
        max-height: 200px;
    }

    .header {
        left: 0;
        top: 0;
    }

    .chat-container {
        left: 0;
        top: 80px;
    }

    .message-content {
        max-width: 80%;
    }

    .sidebar-header {
        width: auto;
    }

    .sessions-list {
        display: flex;
        overflow-x: auto;
        padding: 12px;
    }

    .session-item {
        flex-shrink: 0;
        width: 200px;
    }
}
`;

// 스타일 주입
const styleElement = document.createElement('style');
styleElement.textContent = cssContent;
document.head.appendChild(styleElement);
