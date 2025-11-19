/**
 * useConversation Hook
 *
 * Handles AI conversation sessions
 */

'use client';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { conversationAPI } from '@/services/api';
import type { Conversation, ConversationRequest, ConversationScenario } from '@/lib/types';
import toast from 'react-hot-toast';

export function useConversations() {
  const {
    data: conversations,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['conversations'],
    queryFn: conversationAPI.getAll,
  });

  return {
    conversations: conversations || [],
    isLoading,
    error,
  };
}

export function useConversation(conversationId?: string) {
  const queryClient = useQueryClient();

  // Fetch conversation details
  const {
    data: conversation,
    isLoading: isConversationLoading,
  } = useQuery({
    queryKey: ['conversations', conversationId],
    queryFn: () => conversationAPI.getById(conversationId!),
    enabled: !!conversationId,
  });

  // Send message mutation
  const sendMessageMutation = useMutation({
    mutationFn: (request: ConversationRequest) => conversationAPI.sendMessage(request),
    onSuccess: (response) => {
      // Update conversation cache with new message
      if (conversationId) {
        queryClient.setQueryData<Conversation>(
          ['conversations', conversationId],
          (old) => {
            if (!old) return old;
            return {
              ...old,
              messages: [...old.messages, response.message],
              total_messages: old.total_messages + 1,
            };
          }
        );
      }

      queryClient.invalidateQueries({ queryKey: ['conversations'] });
      queryClient.invalidateQueries({ queryKey: ['progress'] });
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to send message');
    },
  });

  // End conversation mutation
  const endConversationMutation = useMutation({
    mutationFn: (id: string) => conversationAPI.endConversation(id),
    onSuccess: () => {
      toast.success('Conversation ended. Great practice!');
      queryClient.invalidateQueries({ queryKey: ['conversations'] });
      queryClient.invalidateQueries({ queryKey: ['progress'] });
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to end conversation');
    },
  });

  return {
    conversation,
    isConversationLoading,
    messages: conversation?.messages || [],
    sendMessage: sendMessageMutation.mutate,
    isSendingMessage: sendMessageMutation.isPending,
    endConversation: endConversationMutation.mutate,
    isEndingConversation: endConversationMutation.isPending,
  };
}
