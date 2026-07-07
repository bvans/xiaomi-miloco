/**
 * Copyright (C) 2025 Xiaomi Corporation
 * This software may be used and distributed according to the terms of the Xiaomi Miloco License Agreement.
 */

import React, { useEffect } from 'react';
import {Select, message, Segmented} from 'antd';
import { useTranslation } from 'react-i18next';
import { GlobalOutlined, BulbOutlined } from '@ant-design/icons';
import { getLanguage, setLanguage } from '@/api';
import { useTheme } from '@/contexts/ThemeContext';
import { useSettingStore } from '@/stores/settingStore';
import { Card, Header } from '@/components';
import styles from './index.module.less';

const { Option } = Select;

/**
 * Setting Page - Application settings page for language, theme, and authorization configuration
 * 设置页面 - 用于语言、主题和授权配置的应用设置页面
 *
 * @returns {JSX.Element} Settings page component
 */
const Setting = () => {
  const { i18n, t } = useTranslation();
  const { themeMode, changeTheme } = useTheme();
  const {
    language: storeLanguage,
    themeMode: storeThemeMode,
    setLanguage: setStoreLanguage,
    setThemeMode: setStoreThemeMode
  } = useSettingStore();


  // language options
  const languageOptions = [
    { key: 'zh', label: '简体中文' },
    { key: 'en', label: 'English' },
  ];

  // theme mode options
  const themeOptions = [
    { key: 'light', label: t('setting.lightMode'), icon: '☀️' },
    { key: 'dark', label: t('setting.darkMode'), icon: '🌙' },
    { key: 'system', label: t('setting.systemMode'), icon: '🔄' },
  ];


  useEffect(() => {
    const fetchServerLanguage = async () => {
      try {
        const res = await getLanguage();
        if (res && res?.code === 0) {
          const serverLanguage = res?.data?.language;
          if (serverLanguage && serverLanguage !== i18n.language) {
            setStoreLanguage(serverLanguage);
            i18n.changeLanguage(serverLanguage);
          }
        }
      } catch (error) {
        console.warn('Failed to get server language setting:', error);
        if (storeLanguage && storeLanguage !== i18n.language) {
          i18n.changeLanguage(storeLanguage);
        }
      }
    };
    fetchServerLanguage();
  }, []); 

  useEffect(() => {
    if (storeLanguage && storeLanguage !== i18n.language) {
      i18n.changeLanguage(storeLanguage);
    }
  }, [storeLanguage, i18n]);

  // handle language change
  const handleLanguageChange = async (value) => {
    try {
      setStoreLanguage(value);
      i18n.changeLanguage(value);

      const res = await setLanguage({ language: value });
      if (res && res?.code === 0) {
        const languageName = languageOptions.find(opt => opt.key === value)?.label;
        message.success(`${t('setting.languageChanged')} ${languageName}`);
      } else {
        message.error(res?.message || t('setting.languageChangeFailed'));
      }
    } catch (error) {
      console.error('Failed to change language:', error);
      message.error(t('setting.languageChangeFailed'));
    }
  };

  // handle theme mode change
  const handleThemeChange = (value) => {
    setStoreThemeMode(value);
    changeTheme(value);
    message.success(`${t('setting.themeChanged')} ${themeOptions.find(opt => opt.key === value)?.label} ${t('setting.mode')}`);
  };

  return (
    <div className={styles.settingContainer}>
      <div className={styles.settingContent}>
        <Header title={t('home.menu.setting')} />

        {/* regular setting */}
        <Card className={styles.settingCard} contentClassName={styles.settingCardContent}>
          <div className={styles.settingCardTitle}>{t('setting.regularSetting')}</div>
          <div className={styles.settingCardItemList}>
          <div className={styles.settingItem}>
            <div className={styles.settingLabel}>
              <GlobalOutlined /> {t('setting.language')}
            </div>
            <Select
              value={storeLanguage || i18n.language}
              onChange={handleLanguageChange}
              style={{ width: 382 }}
              placeholder={t('setting.pleaseSelectLanguage')}
            >
              {languageOptions.map(option => (
                <Option key={option.key} value={option.key}>
                  {option.label}
                </Option>
              ))}
            </Select>
          </div>

          <div className={styles.settingItem}>
            <div className={styles.settingLabel}>
              <BulbOutlined /> {t('setting.themeMode')}
            </div>
            <Segmented
              value={storeThemeMode || themeMode}
              onChange={handleThemeChange}
              options={themeOptions.map(option => ({
                label: (
                  <div className={styles.segmentedOption}>
                    {/* <span className={styles.segmentedIcon}>{option.icon}</span> */}
                    <span>{option.label}</span>
                  </div>
                ),
                value: option.key
              }))}
              className={styles.themeSegmented}
            />
          </div>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default Setting;
