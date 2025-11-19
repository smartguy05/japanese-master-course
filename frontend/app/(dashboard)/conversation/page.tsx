/**
 * Conversation Page
 *
 * AI-powered Japanese conversation practice
 */

'use client';

import { useState, useRef, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { MessageBubble } from '@/components/conversation/MessageBubble';
import { useConversation, useConversations } from '@/hooks/useConversation';
import { Send, Loader2, Plus, MessageSquare } from 'lucide-react';
import type { ConversationScenario } from '@/lib/types';

const scenarios: { value: ConversationScenario; label: string; description: string }[] = [
  {
    value: 'casual_greeting',
    label: 'Casual Greeting',
    description: 'Practice informal greetings with friends',
  },
  {
    value: 'restaurant',
    label: 'Restaurant',
    description: 'Order food and interact with staff',
  },
  {
    value: 'shopping',
    label: 'Shopping',
    description: 'Ask about products and prices',
  },
  {
    value: 'work_meeting',
    label: 'Work Meeting',
    description: 'Professional business communication',
  },
  {
    value: 'job_interview',
    label: 'Job Interview',
    description: 'Practice interview scenarios',
  },
  {
    value: 'free_conversation',
    label: 'Free Conversation',
    description: 'Open-ended conversation practice',
  },
];

export default function ConversationPage() {
  const [selectedConversationId, setSelectedConversationId] = useState<string>();
  const [selectedScenario, setSelectedScenario] = useState<ConversationScenario>();
  const [messageInput, setMessageInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const { conversations } = useConversations();
  const {
    messages,
    sendMessage,
    isSendingMessage,
    endConversation,
  } = useConversation(selectedConversationId);

  // Auto-scroll to latest message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (!messageInput.trim() || isSendingMessage) return;

    const scenario = selectedScenario || 'free_conversation';

    sendMessage(
      {
        scenario,
        user_message: messageInput,
        conversation_id: selectedConversationId,
      },
      {
        onSuccess: (response) => {
          setMessageInput('');
          if (!selectedConversationId) {
            setSelectedConversationId(response.conversation_id);
          }
        },
      }
    );
  };

  const handleNewConversation = () => {
    setSelectedConversationId(undefined);
    setSelectedScenario(undefined);
    setMessageInput('');
  };

  const handleEndConversation = () => {
    if (selectedConversationId) {
      endConversation(selectedConversationId, {
        onSuccess: () => {
          handleNewConversation();
        },
      });
    }
  };

  // Scenario selection view
  if (!selectedConversationId && !selectedScenario) {
    return (
      <div className="space-y-8">
        <div>
          <h1 className="text-3xl font-bold">Conversation Practice</h1>
          <p className="text-muted-foreground mt-2">
            Practice Japanese conversation with AI sensei
          </p>
        </div>

        {/* Recent Conversations */}
        {conversations.length > 0 && (
          <div>
            <h2 className="text-xl font-semibold mb-4">Recent Conversations</h2>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {conversations.slice(0, 6).map((conv) => (
                <Card
                  key={conv.id}
                  className="cursor-pointer hover:shadow-lg transition-shadow"
                  onClick={() => setSelectedConversationId(conv.id)}
                >
                  <CardHeader>
                    <CardTitle className="text-base">
                      {conv.scenario.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase())}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-sm text-muted-foreground">
                      {conv.total_messages} messages
                    </div>
                    <div className="text-xs text-muted-foreground mt-1">
                      {new Date(conv.started_at).toLocaleDateString()}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}

        {/* Scenario Selection */}
        <div>
          <h2 className="text-xl font-semibold mb-4">Start New Conversation</h2>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {scenarios.map((scenario) => (
              <Card
                key={scenario.value}
                className="cursor-pointer hover:shadow-lg transition-shadow"
                onClick={() => setSelectedScenario(scenario.value)}
              >
                <CardHeader>
                  <CardTitle className="text-base">{scenario.label}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">{scenario.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </div>
    );
  }

  // Conversation view
  return (
    <div className="flex flex-col h-[calc(100vh-8rem)]">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">
            {selectedScenario?.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase()) ||
              'Conversation'}
          </h1>
          <p className="text-sm text-muted-foreground">
            {messages.length} messages
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleNewConversation}>
            <Plus className="w-4 h-4 mr-2" />
            New
          </Button>
          {selectedConversationId && (
            <Button variant="outline" onClick={handleEndConversation}>
              End Conversation
            </Button>
          )}
        </div>
      </div>

      {/* Messages */}
      <Card className="flex-1 flex flex-col overflow-hidden">
        <CardContent className="flex-1 overflow-y-auto p-6">
          {messages.length === 0 ? (
            <div className="flex items-center justify-center h-full text-center">
              <div>
                <MessageSquare className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                <p className="text-muted-foreground">
                  Start the conversation in Japanese!
                </p>
                <p className="text-sm text-muted-foreground mt-2">
                  Your AI sensei will respond and provide corrections
                </p>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              {messages.map((message) => (
                <MessageBubble key={message.id} message={message} />
              ))}
              {isSendingMessage && (
                <div className="flex items-start">
                  <div className="bg-muted rounded-2xl rounded-bl-sm px-4 py-3">
                    <Loader2 className="w-5 h-5 animate-spin text-muted-foreground" />
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </CardContent>

        {/* Input */}
        <div className="border-t p-4">
          <form onSubmit={handleSendMessage} className="flex gap-2">
            <Input
              placeholder="Type your message in Japanese..."
              value={messageInput}
              onChange={(e) => setMessageInput(e.target.value)}
              disabled={isSendingMessage}
              className="flex-1"
            />
            <Button
              type="submit"
              disabled={!messageInput.trim() || isSendingMessage}
            >
              <Send className="w-4 h-4" />
            </Button>
          </form>
          <p className="text-xs text-muted-foreground mt-2">
            Press Enter to send • Type in Japanese for best results
          </p>
        </div>
      </Card>
    </div>
  );
}
