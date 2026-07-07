/**
 * Copyright (C) 2025 Xiaomi Corporation
 * This software may be used and distributed according to the terms of the Xiaomi Miloco License Agreement.
 */

import { memo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import defaultAvatar from '@/assets/images/avatar.png';
import styles from './UserAvatar.module.less';

/**
 * UserAvatar Component - User avatar component
 * 用户头像组件 - 显示用户头像和昵称
 *
 * @param {Object} props - Component props
 * @param {Object} [props.userInfo={}] - User information object
 * @param {string} [props.userInfo.icon] - User avatar URL
 * @param {string} [props.userInfo.nickname] - User nickname
 * @param {boolean} [props.collapsed=false] - Whether component is in collapsed state
 * @param {boolean} [props.isDragging=false] - Whether component is being dragged
 * @returns {JSX.Element} User avatar component
 */
const UserAvatar = memo(({
  userInfo = {},
  collapsed = false,
  isDragging = false,
}) => {
  const { icon, nickname } = userInfo;
  const navigate = useNavigate();
  const { t } = useTranslation();

  return (
    <div
      className={`${styles.userAvatar} ${collapsed ? styles.collapsed : ''} ${isDragging ? styles.dragging : ''}`}
      onClick={() => {
        navigate('/home/setting');
      }}
    >
      <img
        src={icon || defaultAvatar}
        alt="User Avatar"
        className={styles.avatar}
        onError={(e) => {
          e.target.src = defaultAvatar;
        }}
      />
      {!collapsed && (
        <div className={styles.userInfo}>
          <div className={styles.nickname} title={nickname}>
            {nickname || t('home.userPopover.notLoggedIn')}
          </div>
        </div>
      )}
    </div>
  );
});

export default UserAvatar;
