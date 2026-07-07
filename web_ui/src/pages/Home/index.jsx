/**
 * Copyright (C) 2025 Xiaomi Corporation
 * This software may be used and distributed according to the terms of the Xiaomi Miloco License Agreement.
 */

import { useTranslation } from 'react-i18next';
import { useAuth, useLayout } from './hooks/index';
import { Layout } from './components';

/**
 * Home Page - Main application layout
 * 首页 - 主应用布局页面
 *
 * @returns {JSX.Element} Home page component
 */
const Home = () => {
  const { t } = useTranslation();
  const { userInfo, logout } = useAuth(t);
  const { selectedMenuKey } = useLayout();

  return (
    <Layout
      selectedMenuKeys={[selectedMenuKey]}
      userInfo={userInfo}
      onLogout={logout}
    />
  );
};

export default Home;
