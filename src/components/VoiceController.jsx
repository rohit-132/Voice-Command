import React, { useState, useEffect, useRef } from 'react';
import { Mic, MicOff, Loader2 } from 'lucide-react';
import { useShopping } from '../context/ShoppingContext';
import { processTranscript } from '../services/nlpService';

const languageOptions = [
  { value: 'en-US', label: 'English' },
  { value: 'es-ES', label: 'Español' },
  { value: 'fr-FR', label: 'Français' },
  { value: 'de-DE', label: 'Deutsch' },
  { value: 'it-IT', label: 'Italiano' },
  { value: 'pt-BR', label: 'Português' },
  { value: 'nl-NL', label: 'Nederlands' },
  { value: 'ar-SA', label: 'العربية' },
  { value: 'hi-IN', label: 'हिन्दी' },
  { value: 'ja-JP', label: '日本語' },
  { value: 'ko-KR', label: '한국어' },
  { value: 'zh-CN', label: '中文' }
];

const VoiceController = () => {
  const [isListening, setIsListening] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [transcript, setTranscript] = useState('');
  const { language, addItem, removeItem, performSearch, showStatus, setLanguage } = useShopping();
  
  const recognitionRef = useRef(null);

  useEffect(() => {
    // Initialize Web Speech API
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = true;
      recognition.lang = language;

      recognition.onstart = () => {
        setIsListening(true);
      };

      recognition.onresult = (event) => {
        let interimTranscript = '';
        let finalTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; ++i) {
          if (event.results[i].isFinal) {
            finalTranscript += event.results[i][0].transcript;
          } else {
            interimTranscript += event.results[i][0].transcript;
          }
        }

        if (finalTranscript) {
          setTranscript(finalTranscript);
          handleFinalCommand(finalTranscript);
        } else {
          setTranscript(interimTranscript);
        }
      };

      recognition.onerror = (event) => {
        console.error('Speech recognition error', event.error);
        setIsListening(false);
        if (event.error !== 'no-speech') {
          showStatus(`Microphone error: ${event.error}`, 'error');
        }
      };

      recognition.onend = () => {
        setIsListening(false);
      };

      recognitionRef.current = recognition;
    } else {
      showStatus("Voice recognition not supported in this browser.", "error");
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.abort();
      }
    };
  }, [language]); // Re-initialize if language changes

  const handleFinalCommand = async (text) => {
    setIsProcessing(true);
    showStatus("AI is thinking...", "success");
    
    const { intent, item, quantity, category, maxPrice, message } = await processTranscript(text, language);
    
    setIsProcessing(false);
    setTimeout(() => setTranscript(''), 2000);

    if (intent === 'ADD' && item) {
      addItem(item, quantity, category);
    } else if (intent === 'REMOVE' && item) {
      removeItem(item);
    } else if (intent === 'SEARCH' && item) {
      performSearch(item, maxPrice);
    } else {
      showStatus(message || "Didn't understand that.", 'error');
    }
  };

  const toggleListening = () => {
    if (isListening) {
      recognitionRef.current?.stop();
    } else {
      setTranscript('');
      recognitionRef.current?.start();
    }
  };

  return (
    <div className="glass-panel voice-controller">
      <select 
        className="lang-selector"
        value={language}
        onChange={(e) => setLanguage(e.target.value)}
        disabled={isProcessing}
      >
        {languageOptions.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>

      <button 
        className={`mic-button ${isListening ? 'listening' : ''}`}
        onClick={toggleListening}
        disabled={isProcessing}
        aria-label="Toggle Voice Recording"
      >
        {isProcessing ? <Loader2 size={32} className="animate-spin" /> : (isListening ? <Mic size={32} /> : <MicOff size={32} />)}
      </button>

      <div className="transcript-area">
        {transcript ? (
          <p className="transcript-text">"{transcript}"</p>
        ) : (
          <p className="transcript-placeholder">
            {isProcessing ? "Analyzing command..." : (isListening ? "Listening..." : "Tap to speak (e.g., 'Add 2 apples')")}
          </p>
        )}
      </div>
    </div>
  );
};

export default VoiceController;
