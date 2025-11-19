/**
 * MessageBubble Component
 *
 * Displays a conversation message with optional correction
 */

'use client';

import { motion } from 'framer-motion';
import type { Message } from '@/lib/types';
import { cn } from '@/lib/utils';
import { CorrectionDisplay } from './CorrectionDisplay';

interface MessageBubbleProps {
  message: Message;
  className?: string;
}

export function MessageBubble({ message, className }: MessageBubbleProps) {
  const isUser = message.role === 'user';

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={cn(
        'flex flex-col gap-2 mb-4',
        isUser ? 'items-end' : 'items-start',
        className
      )}
    >
      <div
        className={cn(
          'max-w-[80%] rounded-2xl px-4 py-3',
          isUser
            ? 'bg-primary text-primary-foreground rounded-br-sm'
            : 'bg-muted text-foreground rounded-bl-sm'
        )}
      >
        <p className="text-base whitespace-pre-wrap">{message.content}</p>
        <p className="text-xs opacity-70 mt-1">
          {new Date(message.timestamp).toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
          })}
        </p>
      </div>

      {message.correction && (
        <div className="max-w-[80%]">
          <CorrectionDisplay correction={message.correction} />
        </div>
      )}

      {message.encouragement && (
        <div className="max-w-[80%] text-sm text-muted-foreground italic">
          {message.encouragement}
        </div>
      )}
    </motion.div>
  );
}
