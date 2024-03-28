import React, { useState, useEffect, useRef  } from 'react';
import { TypeAnimation } from 'react-type-animation';
import './ChatbotUi.css';

export default function ChatbotUi(){

    const [messages, setMessages] = useState([]);
    const [userInput, setUserInput] = useState('');
    const [isLoading, setIsLoading] = useState(false); // New loading state

    const ExampleComponent = ({fetchMessage}) => {
      return (
        <TypeAnimation
          sequence={[
            // Same substring at the start will only be typed out once, initially
            fetchMessage,
            1000
          ]}
          wrapper="span"
          speed={50}
          style={{ fontSize: '1em', display: 'inline-block' }}
          repeat={1}
        />
      );
    };
  
    const handleUserInput = (e) => {
      setUserInput(e.target.value);
    };

    const handleSubmit = (e) => {
      e.preventDefault();
      if (userInput.trim() === "") {
          return;
      }
      setIsLoading(true); // Start loading
      const userMessage = { id: Date.now(), text: userInput, sender: 'user', type: 'text' };
      setMessages(prevMessages => [...prevMessages, userMessage]);
  
      // Send user input to backend and wait for the response
      fetch('http://localhost:5000/submit-user-input', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json',
          },
          body: JSON.stringify({ text: userInput })
      })
      .then(response => response.json())
      .then(data => {
          // After receiving the response from submit, fetch the message
          fetchMessage();
      })
      .catch(error => console.error('There was an error!', error))
      .finally(() => setIsLoading(false));
  
      setUserInput('');
  };
  
  const fetchMessage = () => {
      fetch('http://localhost:5000/get-message')
          .then(response => response.json())
          .then(data => {
              const botMessage = { id: Date.now(), text: data.message, sender: 'bot', type: 'text' };
              setMessages(prevMessages => [...prevMessages, botMessage]);
          })
          .catch(error => console.error('There was an error fetching the message!', error));
  };
  
  const initializeChat = () => {
    fetch('http://localhost:5000/init-conversation', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({})
    })
    .then(response => response.json())
    .then(data => {
        console.log("Chat initialized:", data);
        // Optionally update the UI with a welcome message or other initial state
    })
    .catch(error => {
        console.error('Error initializing chat:', error);
    });
};

  // Initialize chat on component mount
    useEffect(() => {
        initializeChat();
    }, []);
  
    const chatWindowRef = useRef(null);
    useEffect(() => {
      const chatWindow = chatWindowRef.current;
      chatWindow.scrollTop = chatWindow.scrollHeight;
    }, [messages]);

    return(
        <div>
            <div className="chat-window" ref={chatWindowRef}>
              {messages.map((msg) => (
                <div key={msg.id} className={`message ${msg.sender}`}>
                  {msg.type === 'text' ? msg.text : React.createElement(msg.component)}
                </div>
              ))}
              {isLoading && <div className="loading-message">Generating response...</div>} {/* Loading indicator */}
            </div>
            <form className="chat-bot-form" onSubmit={handleSubmit}>
                <input
                type="text"
                value={userInput}
                onChange={handleUserInput}
                placeholder="Say something..."
                />
                <button type="submit">Send</button>
            </form>
          </div>
    );
}
