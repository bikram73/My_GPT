import { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { Send, User, Bot, Plus, MessageSquare, Paperclip, Globe, BookOpen, Image, Mic, HelpCircle, ChevronDown, LogOut, Trash2 } from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function App() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [chatStarted, setChatStarted] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [authMode, setAuthMode] = useState('login');
  const [conversations, setConversations] = useState([]);
  const [currentConversationId, setCurrentConversationId] = useState(null);
  const [showRegisterPrompt, setShowRegisterPrompt] = useState(false);
  const [selectedModel, setSelectedModel] = useState('auto');
  const [showModelSelector, setShowModelSelector] = useState(false);
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  // Available models
  const models = [
    { id: 'auto', name: 'Auto Select', description: 'Automatically chooses best model' },
    { id: 'mistral-7b', name: 'Mistral 7B', description: '⚡ Fast general chat' },
    { id: 'llama-3.2-3b', name: 'Llama 3.2 3B', description: '💬 Efficient assistant' },
    { id: 'qwen-coder-7b', name: 'Qwen Coder 7B', description: '💻 Coding specialist' },
    { id: 'deepseek-coder', name: 'DeepSeek Coder', description: '🔧 Code expert' },
    { id: 'qwen-math', name: 'Qwen Math 7B', description: '🧮 Math & reasoning' },
    { id: 'deepseek-r1', name: 'DeepSeek R1', description: '🤔 Deep reasoning' },
    { id: 'llama-8b', name: 'Llama 3.1 8B', description: '✍️ Creative writing' },
    { id: 'qwen-multilingual', name: 'Qwen 7B', description: '🌍 Multilingual' },
    { id: 'gpt2', name: 'GPT-2', description: '🔄 Fallback model' }
  ];

  // Auth form state
  const [authForm, setAuthForm] = useState({
    email: '',
    password: '',
    name: ''
  });

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Check for existing token on mount
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      fetchCurrentUser();
      fetchConversations();
    }
  }, []);

  const fetchCurrentUser = async () => {
    try {
      const response = await axios.get(`${API_URL}/auth/me`);
      setUser(response.data);
      setIsAuthenticated(true);
    } catch (error) {
      localStorage.removeItem('token');
      delete axios.defaults.headers.common['Authorization'];
    }
  };

  const fetchConversations = async () => {
    try {
      const response = await axios.get(`${API_URL}/conversations`);
      setConversations(response.data);
    } catch (error) {
      console.error('Error fetching conversations:', error);
    }
  };

  const handleAuth = async (e) => {
    e.preventDefault();
    try {
      const endpoint = authMode === 'login' ? '/auth/login' : '/auth/register';
      const response = await axios.post(`${API_URL}${endpoint}`, authForm);
      
      localStorage.setItem('token', response.data.token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${response.data.token}`;
      
      setUser(response.data.user);
      setIsAuthenticated(true);
      setShowAuthModal(false);
      setAuthForm({ email: '', password: '', name: '' });
      fetchConversations();
    } catch (error) {
      alert(error.response?.data?.detail || 'Authentication failed');
    }
  };

  const handleNewChat = () => {
    setMessages([]);
    setChatStarted(false);
    setCurrentConversationId(null);
    setInput("");
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    delete axios.defaults.headers.common['Authorization'];
    setIsAuthenticated(false);
    setUser(null);
    setMessages([]);
    setConversations([]);
    setChatStarted(false);
    setCurrentConversationId(null);
  };

  const loadConversation = async (convId) => {
    try {
      const response = await axios.get(`${API_URL}/conversations/${convId}`);
      setMessages(response.data.messages);
      setCurrentConversationId(convId);
      setChatStarted(true);
    } catch (error) {
      console.error('Error loading conversation:', error);
    }
  };

  const deleteConversation = async (convId, e) => {
    e.stopPropagation();
    if (!confirm('Delete this conversation?')) return;
    
    try {
      await axios.delete(`${API_URL}/conversations/${convId}`);
      setConversations(conversations.filter(c => c.id !== convId));
      if (currentConversationId === convId) {
        handleNewChat();
      }
    } catch (error) {
      console.error('Error deleting conversation:', error);
    }
  };

  const handleSend = async () => {
    if (!input.trim()) return;

    if (!chatStarted) setChatStarted(true);

    const userMessage = { role: 'user', content: input, timestamp: new Date().toISOString() };
    setMessages(prev => [...prev, userMessage]);
    setInput("");
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
    setIsLoading(true);

    try {
      const response = await axios.post(`${API_URL}/chat`, {
        message: userMessage.content,
        conversation_id: currentConversationId,
        model_preference: selectedModel === 'auto' ? null : selectedModel
      });
      
      const botMessage = { 
        role: 'assistant', 
        content: response.data.response,
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, botMessage]);
      
      if (!currentConversationId) {
        setCurrentConversationId(response.data.conversation_id);
        if (isAuthenticated) {
          fetchConversations();
        }
      }
      
      // Show prompt to register if guest user after 3 messages
      if (!isAuthenticated && messages.length >= 5 && !showRegisterPrompt) {
        setShowRegisterPrompt(true);
      }
    } catch (error) {
      console.error("Error:", error);
      const errorMsg = "Error: Could not connect to the model backend.";
      setMessages(prev => [...prev, { role: 'assistant', content: errorMsg, timestamp: new Date().toISOString() }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div style={{ fontFamily: "'Söhne', ui-sans-serif, system-ui, -apple-system, sans-serif" }} className="flex h-screen text-white bg-[#212121]">

      {/* Sidebar */}
      <div className="w-[260px] bg-[#171717] hidden md:flex flex-col p-3 flex-shrink-0">
        {/* Logo + model selector */}
        <div className="mb-2">
          <div 
            onClick={() => setShowModelSelector(!showModelSelector)}
            className="flex items-center justify-between px-2 py-2 hover:bg-[#2A2A2A] rounded-lg cursor-pointer transition-colors"
          >
            <div className="flex items-center gap-2">
              <svg width="28" height="28" viewBox="0 0 41 41" fill="white" xmlns="http://www.w3.org/2000/svg">
                <path d="M37.532 16.87a9.963 9.963 0 0 0-.856-8.184 10.078 10.078 0 0 0-10.855-4.835 9.964 9.964 0 0 0-6.13-3.386 10.079 10.079 0 0 0-11.483 4.964 9.964 9.964 0 0 0-6.664 4.834 10.079 10.079 0 0 0 1.24 11.817 9.965 9.965 0 0 0 .856 8.185 10.079 10.079 0 0 0 10.855 4.835 9.965 9.965 0 0 0 6.129 3.386 10.079 10.079 0 0 0 11.484-4.963 9.964 9.964 0 0 0 6.663-4.834 10.079 10.079 0 0 0-1.239-11.818ZM22.498 37.886a7.474 7.474 0 0 1-4.799-1.735c.061-.033.168-.091.237-.134l7.964-4.6a1.294 1.294 0 0 0 .655-1.134V19.054l3.366 1.944a.12.12 0 0 1 .066.092v9.299a7.505 7.505 0 0 1-7.49 7.496ZM6.392 31.006a7.471 7.471 0 0 1-.894-5.023c.06.036.162.099.237.141l7.964 4.6a1.297 1.297 0 0 0 1.308 0l9.724-5.614v3.888a.12.12 0 0 1-.048.103l-8.051 4.649a7.504 7.504 0 0 1-10.24-2.744ZM4.297 13.62A7.469 7.469 0 0 1 8.2 10.333c0 .068-.004.19-.004.274v9.201a1.294 1.294 0 0 0 .654 1.132l9.723 5.614-3.366 1.944a.12.12 0 0 1-.114.012L7.044 23.86a7.504 7.504 0 0 1-2.747-10.24Zm27.658 6.437-9.724-5.615 3.367-1.943a.121.121 0 0 1 .114-.012l8.048 4.648a7.498 7.498 0 0 1-1.158 13.528v-9.476a1.293 1.293 0 0 0-.647-1.13Zm3.35-5.043c-.059-.037-.162-.099-.236-.141l-7.965-4.6a1.298 1.298 0 0 0-1.308 0l-9.723 5.614v-3.888a.12.12 0 0 1 .048-.103l8.05-4.645a7.497 7.497 0 0 1 11.135 7.763Zm-21.063 6.929-3.367-1.944a.12.12 0 0 1-.065-.092v-9.299a7.497 7.497 0 0 1 12.293-5.756 6.94 6.94 0 0 0-.236.134l-7.965 4.6a1.294 1.294 0 0 0-.654 1.132l-.006 11.225Zm1.829-3.943 4.33-2.501 4.332 2.5v4.999l-4.331 2.5-4.331-2.5V18Z"/>
              </svg>
              <span className="font-semibold text-white text-[15px]">MyGPT</span>
              <ChevronDown size={14} className={`text-gray-400 transition-transform ${showModelSelector ? 'rotate-180' : ''}`} />
            </div>
          </div>
          
          {/* Model Selector Dropdown */}
          {showModelSelector && (
            <div className="mt-2 bg-[#2A2A2A] rounded-lg p-2 max-h-[400px] overflow-y-auto">
              <div className="text-xs text-gray-400 px-2 py-1 mb-1">Select Model</div>
              {models.map((model) => (
                <div
                  key={model.id}
                  onClick={() => {
                    setSelectedModel(model.id);
                    setShowModelSelector(false);
                  }}
                  className={`px-3 py-2 rounded-lg cursor-pointer transition-colors ${
                    selectedModel === model.id ? 'bg-[#19c37d]/20 text-[#19c37d]' : 'hover:bg-[#3A3A3A] text-gray-300'
                  }`}
                >
                  <div className="text-sm font-medium">{model.name}</div>
                  <div className="text-xs text-gray-500">{model.description}</div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* New Chat */}
        <button
          onClick={handleNewChat}
          className="flex items-center gap-3 rounded-lg px-3 py-2 hover:bg-[#2A2A2A] transition-colors text-sm text-white mb-1 w-full text-left"
        >
          <Plus size={16} />
          New chat
        </button>

        {/* History */}
        <div className="flex-1 overflow-y-auto mt-2">
          {isAuthenticated ? (
            conversations.length > 0 ? (
              <>
                <div className="text-xs text-gray-500 font-medium mb-1 px-3 py-1">Recent</div>
                {conversations.map((conv) => (
                  <div
                    key={conv.id}
                    onClick={() => loadConversation(conv.id)}
                    className={`group flex items-center gap-3 w-full px-3 py-2 rounded-lg hover:bg-[#2A2A2A] transition-colors text-sm cursor-pointer ${
                      currentConversationId === conv.id ? 'bg-[#2A2A2A]' : ''
                    }`}
                  >
                    <MessageSquare size={14} className="text-gray-400 flex-shrink-0" />
                    <span className="truncate text-gray-300 flex-1">{conv.title}</span>
                    <button
                      onClick={(e) => deleteConversation(conv.id, e)}
                      className="opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-[#3A3A3A] rounded"
                    >
                      <Trash2 size={14} className="text-gray-400" />
                    </button>
                  </div>
                ))}
              </>
            ) : null
          ) : (
            <div className="px-3 py-4 text-center">
              <p className="text-xs text-gray-500 mb-3">Sign up to save your conversations</p>
              <button
                onClick={() => { setAuthMode('register'); setShowAuthModal(true); }}
                className="w-full px-3 py-2 bg-[#19c37d] text-white text-sm rounded-lg hover:bg-[#17b370] transition-colors font-medium"
              >
                Create account
              </button>
            </div>
          )}
        </div>

        {/* Bottom user area */}
        <div className="border-t border-white/10 pt-2">
          {isAuthenticated ? (
            <div className="group relative">
              <div className="flex items-center gap-3 p-2 hover:bg-[#2A2A2A] rounded-lg cursor-pointer transition-colors">
                <div className="w-8 h-8 bg-[#19c37d] rounded-full flex items-center justify-center text-xs font-bold">
                  {user?.name?.charAt(0).toUpperCase() || 'U'}
                </div>
                <div className="text-sm font-medium truncate flex-1">{user?.name || user?.email}</div>
                <button
                  onClick={handleLogout}
                  className="opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-[#3A3A3A] rounded"
                  title="Logout"
                >
                  <LogOut size={14} className="text-gray-400" />
                </button>
              </div>
            </div>
          ) : (
            <button
              onClick={() => setShowAuthModal(true)}
              className="w-full flex items-center gap-3 p-2 hover:bg-[#2A2A2A] rounded-lg cursor-pointer transition-colors"
            >
              <div className="w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center text-xs font-bold">?</div>
              <div className="text-sm font-medium">Log in</div>
            </button>
          )}
        </div>
      </div>

      {/* Main Area */}
      <div className="flex-1 flex flex-col bg-[#212121] relative overflow-hidden">

        {/* Top Nav (shown when chat not started) */}
        {!chatStarted && (
          <div className="absolute top-0 left-0 right-0 flex items-center justify-end px-6 py-4 z-10">
            <div className="flex items-center gap-2">
              {!isAuthenticated ? (
                <>
                  <button
                    onClick={() => { setAuthMode('login'); setShowAuthModal(true); }}
                    className="px-4 py-1.5 rounded-full border border-white/20 text-sm text-white hover:bg-white/10 transition-colors font-medium"
                  >
                    Log in
                  </button>
                  <button
                    onClick={() => { setAuthMode('register'); setShowAuthModal(true); }}
                    className="px-4 py-1.5 rounded-full bg-white text-black text-sm hover:bg-gray-200 transition-colors font-medium"
                  >
                    Sign up for free
                  </button>
                </>
              ) : (
                <div className="flex items-center gap-3 px-3 py-1.5 rounded-full bg-[#2A2A2A]">
                  <div className="w-6 h-6 bg-[#19c37d] rounded-full flex items-center justify-center text-xs font-bold">
                    {user?.name?.charAt(0).toUpperCase() || 'U'}
                  </div>
                  <span className="text-sm">{user?.name || user?.email}</span>
                  <button onClick={handleLogout} className="ml-2 p-1 hover:bg-[#3A3A3A] rounded">
                    <LogOut size={14} />
                  </button>
                </div>
              )}
              <button className="ml-2 w-8 h-8 rounded-full border border-white/20 flex items-center justify-center hover:bg-white/10 transition-colors">
                <HelpCircle size={16} className="text-white" />
              </button>
            </div>
          </div>
        )}

        {/* Guest User Register Prompt */}
        {!isAuthenticated && showRegisterPrompt && chatStarted && (
          <div className="absolute top-4 left-1/2 transform -translate-x-1/2 z-20 max-w-md">
            <div className="bg-[#2A2A2A] border border-[#19c37d]/30 rounded-xl p-4 shadow-lg flex items-center gap-3">
              <div className="flex-1">
                <p className="text-sm text-white font-medium mb-1">Save your conversations</p>
                <p className="text-xs text-gray-400">Sign up to access your chat history from any device</p>
              </div>
              <button
                onClick={() => { setAuthMode('register'); setShowAuthModal(true); }}
                className="px-4 py-2 bg-[#19c37d] text-white text-sm rounded-lg hover:bg-[#17b370] transition-colors font-medium whitespace-nowrap"
              >
                Sign up
              </button>
              <button
                onClick={() => setShowRegisterPrompt(false)}
                className="text-gray-400 hover:text-white transition-colors"
              >
                ✕
              </button>
            </div>
          </div>
        )}

        {/* Landing / Chat Messages */}
        {!chatStarted ? (
          /* Landing Page */
          <div className="flex-1 flex flex-col items-center justify-center px-4">
            <h1 className="text-3xl font-semibold text-white mb-8 tracking-tight">What can I help with?</h1>
            <p className="text-sm text-gray-500 mb-4">Powered by {models.find(m => m.id === selectedModel)?.name || 'Multiple AI Models'}</p>

            {/* Input Box */}
            <div className="w-full max-w-[680px]">
              <div className="bg-[#2F2F2F] rounded-2xl px-4 pt-4 pb-3 shadow-lg">
                <textarea
                  ref={textareaRef}
                  value={input}
                  onChange={(e) => {
                    setInput(e.target.value);
                    e.target.style.height = 'auto';
                    e.target.style.height = `${e.target.scrollHeight}px`;
                  }}
                  onKeyDown={handleKeyDown}
                  placeholder="Ask anything"
                  className="w-full bg-transparent text-white placeholder-gray-500 focus:outline-none resize-none max-h-[200px] overflow-y-auto min-h-[24px] text-[15px] leading-6 mb-3"
                  rows={1}
                />
                <div className="flex items-center justify-between">
                  {/* Action Pills */}
                  <div className="flex items-center gap-2 flex-wrap">
                    <button className="flex items-center gap-1.5 px-3 py-1.5 rounded-full border border-white/15 text-gray-400 hover:border-white/30 hover:text-white transition-colors text-xs font-medium">
                      <Paperclip size={13} />
                      Attach
                    </button>
                    <button className="flex items-center gap-1.5 px-3 py-1.5 rounded-full border border-white/15 text-gray-400 hover:border-white/30 hover:text-white transition-colors text-xs font-medium">
                      <Globe size={13} />
                      Search
                    </button>
                    <button className="flex items-center gap-1.5 px-3 py-1.5 rounded-full border border-white/15 text-gray-400 hover:border-white/30 hover:text-white transition-colors text-xs font-medium">
                      <BookOpen size={13} />
                      Study
                    </button>
                    <button className="flex items-center gap-1.5 px-3 py-1.5 rounded-full border border-white/15 text-gray-400 hover:border-white/30 hover:text-white transition-colors text-xs font-medium">
                      <Image size={13} />
                      Create image
                    </button>
                  </div>
                  {/* Right side: Voice or Send */}
                  <div className="flex items-center gap-2">
                    {input.trim() ? (
                      <button
                        onClick={handleSend}
                        className="w-8 h-8 rounded-full bg-white flex items-center justify-center hover:bg-gray-200 transition-colors"
                      >
                        <Send size={14} className="text-black" />
                      </button>
                    ) : (
                      <button className="flex items-center gap-1.5 px-3 py-1.5 rounded-full border border-white/15 text-gray-400 hover:border-white/30 hover:text-white transition-colors text-xs font-medium">
                        <Mic size={13} />
                        Voice
                      </button>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        ) : (
          /* Chat View */
          <>
            <div className="flex-1 overflow-y-auto w-full pb-40 scroll-smooth">
              {messages.map((msg, index) => (
                <div
                  key={index}
                  className={`w-full ${msg.role === 'assistant' ? '' : ''}`}
                >
                  <div className="max-w-3xl mx-auto flex gap-4 px-6 py-5">
                    {msg.role === 'assistant' ? (
                      <>
                        <div className="w-7 h-7 min-w-[1.75rem] rounded-full bg-white flex items-center justify-center flex-shrink-0 mt-0.5">
                          <svg width="14" height="14" viewBox="0 0 41 41" fill="black" xmlns="http://www.w3.org/2000/svg">
                            <path d="M37.532 16.87a9.963 9.963 0 0 0-.856-8.184 10.078 10.078 0 0 0-10.855-4.835 9.964 9.964 0 0 0-6.13-3.386 10.079 10.079 0 0 0-11.483 4.964 9.964 9.964 0 0 0-6.664 4.834 10.079 10.079 0 0 0 1.24 11.817 9.965 9.965 0 0 0 .856 8.185 10.079 10.079 0 0 0 10.855 4.835 9.965 9.965 0 0 0 6.129 3.386 10.079 10.079 0 0 0 11.484-4.963 9.964 9.964 0 0 0 6.663-4.834 10.079 10.079 0 0 0-1.239-11.818ZM22.498 37.886a7.474 7.474 0 0 1-4.799-1.735c.061-.033.168-.091.237-.134l7.964-4.6a1.294 1.294 0 0 0 .655-1.134V19.054l3.366 1.944a.12.12 0 0 1 .066.092v9.299a7.505 7.505 0 0 1-7.49 7.496ZM6.392 31.006a7.471 7.471 0 0 1-.894-5.023c.06.036.162.099.237.141l7.964 4.6a1.297 1.297 0 0 0 1.308 0l9.724-5.614v3.888a.12.12 0 0 1-.048.103l-8.051 4.649a7.504 7.504 0 0 1-10.24-2.744ZM4.297 13.62A7.469 7.469 0 0 1 8.2 10.333c0 .068-.004.19-.004.274v9.201a1.294 1.294 0 0 0 .654 1.132l9.723 5.614-3.366 1.944a.12.12 0 0 1-.114.012L7.044 23.86a7.504 7.504 0 0 1-2.747-10.24Zm27.658 6.437-9.724-5.615 3.367-1.943a.121.121 0 0 1 .114-.012l8.048 4.648a7.498 7.498 0 0 1-1.158 13.528v-9.476a1.293 1.293 0 0 0-.647-1.13Zm3.35-5.043c-.059-.037-.162-.099-.236-.141l-7.965-4.6a1.298 1.298 0 0 0-1.308 0l-9.723 5.614v-3.888a.12.12 0 0 1 .048-.103l8.05-4.645a7.497 7.497 0 0 1 11.135 7.763Zm-21.063 6.929-3.367-1.944a.12.12 0 0 1-.065-.092v-9.299a7.497 7.497 0 0 1 12.293-5.756 6.94 6.94 0 0 0-.236.134l-7.965 4.6a1.294 1.294 0 0 0-.654 1.132l-.006 11.225Zm1.829-3.943 4.33-2.501 4.332 2.5v4.999l-4.331 2.5-4.331-2.5V18Z"/>
                          </svg>
                        </div>
                        <div className="leading-7 text-[15px] text-gray-100 whitespace-pre-wrap">{msg.content}</div>
                      </>
                    ) : (
                      <div className="ml-auto max-w-[85%] bg-[#2F2F2F] rounded-2xl px-4 py-3 text-[15px] leading-6 text-white whitespace-pre-wrap">
                        {msg.content}
                      </div>
                    )}
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="max-w-3xl mx-auto flex gap-4 px-6 py-5">
                  <div className="w-7 h-7 min-w-[1.75rem] rounded-full bg-white flex items-center justify-center flex-shrink-0">
                    <Bot size={14} className="text-black" />
                  </div>
                  <div className="flex items-center gap-1 pt-2">
                    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay:'0ms'}}></span>
                    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay:'150ms'}}></span>
                    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay:'300ms'}}></span>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Chat Input */}
            <div className="absolute bottom-0 left-0 w-full bg-gradient-to-t from-[#212121] via-[#212121] to-transparent pt-8 pb-6 px-4">
              <div className="max-w-3xl mx-auto">
                <div className="bg-[#2F2F2F] rounded-2xl px-4 pt-4 pb-3 shadow-lg">
                  <textarea
                    ref={textareaRef}
                    value={input}
                    onChange={(e) => {
                      setInput(e.target.value);
                      e.target.style.height = 'auto';
                      e.target.style.height = `${e.target.scrollHeight}px`;
                    }}
                    onKeyDown={handleKeyDown}
                    placeholder="Ask anything"
                    className="w-full bg-transparent text-white placeholder-gray-500 focus:outline-none resize-none max-h-[200px] overflow-y-auto min-h-[24px] text-[15px] leading-6 mb-3"
                    rows={1}
                  />
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <button className="flex items-center gap-1.5 px-3 py-1.5 rounded-full border border-white/15 text-gray-400 hover:border-white/30 hover:text-white transition-colors text-xs font-medium">
                        <Paperclip size={13} />
                        Attach
                      </button>
                      <button className="flex items-center gap-1.5 px-3 py-1.5 rounded-full border border-white/15 text-gray-400 hover:border-white/30 hover:text-white transition-colors text-xs font-medium">
                        <Globe size={13} />
                        Search
                      </button>
                    </div>
                    <div className="flex items-center gap-2">
                      {input.trim() ? (
                        <button
                          onClick={handleSend}
                          disabled={isLoading}
                          className="w-8 h-8 rounded-full bg-white flex items-center justify-center hover:bg-gray-200 transition-colors disabled:opacity-40"
                        >
                          <Send size={14} className="text-black" />
                        </button>
                      ) : (
                        <button className="w-8 h-8 rounded-full border border-white/15 flex items-center justify-center text-gray-400 hover:border-white/30 hover:text-white transition-colors">
                          <Mic size={14} />
                        </button>
                      )}
                    </div>
                  </div>
                </div>
                <p className="text-xs text-center text-gray-600 mt-3">
                  MyGPT can make mistakes. Consider checking important information.
                </p>
              </div>
            </div>
          </>
        )}
      </div>

      {/* Auth Modal */}
      {showAuthModal && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
          <div className="bg-[#2A2A2A] rounded-2xl p-8 max-w-md w-full shadow-2xl">
            <h2 className="text-2xl font-semibold text-white mb-6 text-center">
              {authMode === 'login' ? 'Welcome back' : 'Create your account'}
            </h2>
            <form onSubmit={handleAuth} className="space-y-4">
              {authMode === 'register' && (
                <div>
                  <label className="block text-sm text-gray-300 mb-2">Name</label>
                  <input
                    type="text"
                    value={authForm.name}
                    onChange={(e) => setAuthForm({ ...authForm, name: e.target.value })}
                    className="w-full px-4 py-3 bg-[#3A3A3A] text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-[#19c37d]"
                    required={authMode === 'register'}
                  />
                </div>
              )}
              <div>
                <label className="block text-sm text-gray-300 mb-2">Email</label>
                <input
                  type="email"
                  value={authForm.email}
                  onChange={(e) => setAuthForm({ ...authForm, email: e.target.value })}
                  className="w-full px-4 py-3 bg-[#3A3A3A] text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-[#19c37d]"
                  required
                />
              </div>
              <div>
                <label className="block text-sm text-gray-300 mb-2">Password</label>
                <input
                  type="password"
                  value={authForm.password}
                  onChange={(e) => setAuthForm({ ...authForm, password: e.target.value })}
                  className="w-full px-4 py-3 bg-[#3A3A3A] text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-[#19c37d]"
                  required
                />
              </div>
              <button
                type="submit"
                className="w-full py-3 bg-[#19c37d] text-white rounded-lg font-medium hover:bg-[#17b370] transition-colors"
              >
                {authMode === 'login' ? 'Log in' : 'Sign up'}
              </button>
            </form>
            <div className="mt-6 text-center">
              <button
                onClick={() => setAuthMode(authMode === 'login' ? 'register' : 'login')}
                className="text-sm text-gray-400 hover:text-white transition-colors"
              >
                {authMode === 'login' ? "Don't have an account? Sign up" : 'Already have an account? Log in'}
              </button>
            </div>
            <button
              onClick={() => setShowAuthModal(false)}
              className="absolute top-4 right-4 text-gray-400 hover:text-white transition-colors"
            >
              ✕
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;