/**
 * CorrectionDisplay Component
 *
 * Shows grammar/vocabulary corrections with explanation
 */

'use client';

import { Card } from '@/components/ui/card';
import type { Correction } from '@/lib/types';
import { cn } from '@/lib/utils';
import { AlertCircle, Info, AlertTriangle } from 'lucide-react';

interface CorrectionDisplayProps {
  correction: Correction;
}

export function CorrectionDisplay({ correction }: CorrectionDisplayProps) {
  const severityConfig = {
    minor: { icon: Info, color: 'text-blue-500', bg: 'bg-blue-50 dark:bg-blue-950' },
    moderate: { icon: AlertCircle, color: 'text-yellow-500', bg: 'bg-yellow-50 dark:bg-yellow-950' },
    major: { icon: AlertTriangle, color: 'text-red-500', bg: 'bg-red-50 dark:bg-red-950' },
  };

  const config = severityConfig[correction.severity];
  const Icon = config.icon;

  return (
    <Card className={cn('p-3', config.bg)}>
      <div className="flex gap-2">
        <Icon className={cn('w-5 h-5 flex-shrink-0 mt-0.5', config.color)} />
        <div className="flex-1 space-y-1">
          <div className="text-sm font-medium">
            {correction.type.charAt(0).toUpperCase() + correction.type.slice(1)} Correction
          </div>
          <div className="text-sm space-y-1">
            <div>
              <span className="text-muted-foreground">Original:</span>{' '}
              <span className="line-through">{correction.original}</span>
            </div>
            <div>
              <span className="text-muted-foreground">Corrected:</span>{' '}
              <span className="font-medium text-green-600 dark:text-green-400">
                {correction.corrected}
              </span>
            </div>
          </div>
          <p className="text-xs text-muted-foreground mt-2">{correction.explanation}</p>
        </div>
      </div>
    </Card>
  );
}
