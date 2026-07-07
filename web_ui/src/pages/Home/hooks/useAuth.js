/**
 * Copyright (C) 2025 Xiaomi Corporation
 * This software may be used and distributed according to the terms of the Xiaomi Miloco License Agreement.
 */

import { useState, useEffect } from 'react';
import { setLanguage } from '@/api';
import { useSettingStore } from '@/stores/settingStore';

/**
 * Auth hook — authentication is disabled, always returns a static user.
 * @returns {Object} User info and no-op auth methods
 */
export const useAuth = (t) => {
  const { getLanguage } = useSettingStore();

  const [userInfo] = useState({ nick_name: 'Robot Dog' });

  /** Sync language setting to server on mount */
  useEffect(() => {
    const syncLanguage = async () => {
      try {
        const storedLanguage = getLanguage();
        if (storedLanguage) {
          await setLanguage({ language: storedLanguage });
        }
      } catch (e) {
        console.warn('Failed to sync language setting to server:', e);
      }
    };
    syncLanguage();
  }, []);

  return {
    userInfo,
    loading: false,
    needRetryAuth: false,
    showConsentModal: false,
    retryAuth: () => {},
    logout: () => {},
    handleConsentAgree: () => {},
    handleConsentExit: () => {},
    loginUrl: '',
  };
};
