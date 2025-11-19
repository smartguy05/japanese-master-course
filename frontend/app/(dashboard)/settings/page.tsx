/**
 * Settings Page
 *
 * User profile and preferences management
 */

'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useAuth } from '@/hooks/useAuth';
import { useSettings } from '@/hooks/useSettings';
import { Save, User, Bell, Palette, Shield } from 'lucide-react';
import { useForm } from 'react-hook-form';
import type { UserSettings } from '@/lib/types';

export default function SettingsPage() {
  const { user } = useAuth();
  const { settings, updateSettings } = useSettings();
  const [activeTab, setActiveTab] = useState<'profile' | 'preferences' | 'notifications' | 'security'>('profile');

  const { register, handleSubmit } = useForm({
    defaultValues: {
      full_name: user?.full_name || '',
      email: user?.email || '',
      native_language: user?.native_language || '',
    },
  });

  const onSubmitProfile = (data: { full_name?: string; email?: string; native_language?: string }) => {
    // Update profile logic
    console.log('Update profile:', data);
  };

  const handleUpdateSettings = (updates: Partial<UserSettings>) => {
    updateSettings(updates);
  };

  const tabs = [
    { id: 'profile' as const, label: 'Profile', icon: User },
    { id: 'preferences' as const, label: 'Preferences', icon: Palette },
    { id: 'notifications' as const, label: 'Notifications', icon: Bell },
    { id: 'security' as const, label: 'Security', icon: Shield },
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">Settings</h1>
        <p className="text-muted-foreground mt-2">
          Manage your account and preferences
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-4">
        {/* Sidebar */}
        <div className="space-y-1">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors ${
                  activeTab === tab.id
                    ? 'bg-primary text-primary-foreground'
                    : 'hover:bg-accent'
                }`}
              >
                <Icon className="w-4 h-4" />
                {tab.label}
              </button>
            );
          })}
        </div>

        {/* Content */}
        <div className="md:col-span-3">
          {/* Profile Tab */}
          {activeTab === 'profile' && (
            <Card>
              <CardHeader>
                <CardTitle>Profile Information</CardTitle>
                <CardDescription>
                  Update your personal information
                </CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSubmit(onSubmitProfile)} className="space-y-4">
                  <div className="space-y-2">
                    <label htmlFor="full_name" className="text-sm font-medium">
                      Full Name
                    </label>
                    <Input
                      id="full_name"
                      {...register('full_name')}
                    />
                  </div>

                  <div className="space-y-2">
                    <label htmlFor="email" className="text-sm font-medium">
                      Email
                    </label>
                    <Input
                      id="email"
                      type="email"
                      {...register('email')}
                      disabled
                    />
                    <p className="text-xs text-muted-foreground">
                      Email cannot be changed
                    </p>
                  </div>

                  <div className="space-y-2">
                    <label htmlFor="native_language" className="text-sm font-medium">
                      Native Language
                    </label>
                    <Input
                      id="native_language"
                      {...register('native_language')}
                    />
                  </div>

                  <Button type="submit">
                    <Save className="w-4 h-4 mr-2" />
                    Save Changes
                  </Button>
                </form>
              </CardContent>
            </Card>
          )}

          {/* Preferences Tab */}
          {activeTab === 'preferences' && (
            <Card>
              <CardHeader>
                <CardTitle>Learning Preferences</CardTitle>
                <CardDescription>
                  Customize your learning experience
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Target JLPT Level</label>
                  <select className="w-full p-2 border rounded-lg">
                    <option value="N5">N5 - Beginner</option>
                    <option value="N4">N4 - Elementary</option>
                    <option value="N3">N3 - Intermediate</option>
                    <option value="N2">N2 - Upper Intermediate</option>
                    <option value="N1">N1 - Advanced</option>
                  </select>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">
                    Daily Study Goal (minutes)
                  </label>
                  <Input type="number" defaultValue={30} min={10} max={240} />
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium">Auto-play Pronunciation</p>
                    <p className="text-xs text-muted-foreground">
                      Automatically play audio for Japanese text
                    </p>
                  </div>
                  <input
                    type="checkbox"
                    defaultChecked={settings?.auto_play_pronunciation}
                    onChange={(e) =>
                      handleUpdateSettings({ auto_play_pronunciation: e.target.checked })
                    }
                    className="w-4 h-4"
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium">Audio Enabled</p>
                    <p className="text-xs text-muted-foreground">
                      Enable sound effects and audio
                    </p>
                  </div>
                  <input
                    type="checkbox"
                    defaultChecked={settings?.audio_enabled}
                    onChange={(e) =>
                      handleUpdateSettings({ audio_enabled: e.target.checked })
                    }
                    className="w-4 h-4"
                  />
                </div>

                <Button>
                  <Save className="w-4 h-4 mr-2" />
                  Save Preferences
                </Button>
              </CardContent>
            </Card>
          )}

          {/* Notifications Tab */}
          {activeTab === 'notifications' && (
            <Card>
              <CardHeader>
                <CardTitle>Notification Settings</CardTitle>
                <CardDescription>
                  Manage how you receive notifications
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium">Study Reminders</p>
                    <p className="text-xs text-muted-foreground">
                      Get reminded to practice daily
                    </p>
                  </div>
                  <input
                    type="checkbox"
                    defaultChecked={settings?.study_reminders}
                    onChange={(e) =>
                      handleUpdateSettings({ study_reminders: e.target.checked })
                    }
                    className="w-4 h-4"
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium">Email Updates</p>
                    <p className="text-xs text-muted-foreground">
                      Receive progress updates via email
                    </p>
                  </div>
                  <input
                    type="checkbox"
                    defaultChecked={settings?.email_updates}
                    onChange={(e) =>
                      handleUpdateSettings({ email_updates: e.target.checked })
                    }
                    className="w-4 h-4"
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">Daily Reminder Time</label>
                  <Input
                    type="time"
                    defaultValue={settings?.daily_reminder_time || '19:00'}
                  />
                </div>

                <Button>
                  <Save className="w-4 h-4 mr-2" />
                  Save Notifications
                </Button>
              </CardContent>
            </Card>
          )}

          {/* Security Tab */}
          {activeTab === 'security' && (
            <Card>
              <CardHeader>
                <CardTitle>Security Settings</CardTitle>
                <CardDescription>
                  Manage your account security
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-4">
                  <h3 className="text-sm font-semibold">Change Password</h3>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Current Password</label>
                    <Input type="password" />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">New Password</label>
                    <Input type="password" />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Confirm New Password</label>
                    <Input type="password" />
                  </div>
                  <Button>Update Password</Button>
                </div>

                <div className="border-t pt-6">
                  <h3 className="text-sm font-semibold text-destructive mb-4">
                    Danger Zone
                  </h3>
                  <Button variant="destructive">
                    Delete Account
                  </Button>
                  <p className="text-xs text-muted-foreground mt-2">
                    This action cannot be undone. All your data will be permanently deleted.
                  </p>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
