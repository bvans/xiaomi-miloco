/**
 * Copyright (C) 2025 Xiaomi Corporation
 * This software may be used and distributed according to the terms of the Xiaomi Miloco License Agreement.
 */

import React, { useState, useEffect, useRef } from 'react';
import { Button, Tag, Collapse } from 'antd';
import { useTranslation } from 'react-i18next';
import { useGlobalSocket } from '@/hooks/useGlobalSocket';
import { useChatStore } from '@/stores/chatStore';
import { MESSAGE_CONFIRMATION_NAME, MESSAGE_NAMESPACE, MESSAGE_TYPES } from '@/constants/messageTypes';

const { Panel } = Collapse;

/**
 * ActionConfirmMessage – renders an interactive confirmation card for HITL tool-call approvals.
 *
 * Props:
 *   data      – parsed payload from Confirmation.ActionConfirmRequest
 *   mode      – 'queryEdit' (interactive) | 'readonly' (already answered)
 */
const ActionConfirmMessage = React.memo(({ data, mode = 'queryEdit' }) => {
  const { t } = useTranslation();
  const socketActions = useGlobalSocket();
  const { sessionId, currentRequestId } = useChatStore();

  const {
    confirm_id,
    risk_level = 'low',
    tool_name = '',
    tool_params = {},
    description = '',
    timeout_seconds = 30,
    // readonly fields (injected when mode === 'readonly')
    confirmed: alreadyConfirmed,
  } = data;

  // countdown timer
  const [remaining, setRemaining] = useState(timeout_seconds);
  const [answered, setAnswered] = useState(mode === 'readonly');
  const [confirmedState, setConfirmedState] = useState(
    alreadyConfirmed !== undefined ? alreadyConfirmed : null
  );
  const [loading, setLoading] = useState(false);
  const timerRef = useRef(null);

  useEffect(() => {
    if (answered || mode === 'readonly') return;

    timerRef.current = setInterval(() => {
      setRemaining(prev => {
        if (prev <= 1) {
          clearInterval(timerRef.current);
          // Auto-deny on timeout
          handleDecision(false);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timerRef.current);
  }, [answered, mode]); // eslint-disable-line react-hooks/exhaustive-deps

  const sendResult = (confirmed) => {
    if (!socketActions?.sendMessageDirect) return;

    const msg = {
      header: {
        type: MESSAGE_TYPES.EVENT,
        namespace: MESSAGE_NAMESPACE.CONFIRMATION,
        name: MESSAGE_CONFIRMATION_NAME.ACTION_CONFIRM_RESULT,
        timestamp: Math.floor(Date.now() / 1000),
        request_id: currentRequestId,
        session_id: sessionId,
      },
      payload: JSON.stringify({
        confirm_id,
        confirmed,
        modified_params: null,
      }),
    };

    socketActions.sendMessageDirect(msg);
  };

  const handleDecision = async (confirmed) => {
    if (answered) return;
    clearInterval(timerRef.current);
    setLoading(true);

    try {
      sendResult(confirmed);
    } finally {
      setAnswered(true);
      setConfirmedState(confirmed);
      setLoading(false);
    }
  };

  // ---- style helpers ----
  const riskColor = {
    high: { border: '#ff4d4f', bg: '#fff2f0', tag: 'error' },
    medium: { border: '#faad14', bg: '#fffbe6', tag: 'warning' },
    low: { border: 'var(--border-color)', bg: 'var(--bg-color-card)', tag: 'default' },
  }[risk_level] || { border: 'var(--border-color)', bg: 'var(--bg-color-card)', tag: 'default' };

  const getRiskLabel = () => {
    if (risk_level === 'high') return t('instant.chat.hitlRiskHigh');
    if (risk_level === 'medium') return t('instant.chat.hitlRiskMedium');
    return t('instant.chat.hitlRiskLow');
  };

  // ---- readonly (already answered) ----
  if (answered || mode === 'readonly') {
    const wasConfirmed = confirmedState;
    return (
      <div style={{
        border: wasConfirmed ? '1px solid #b7eb8f' : '1px solid #ffccc7',
        borderRadius: '8px',
        padding: '12px 16px',
        backgroundColor: wasConfirmed ? '#f6ffed' : '#fff2f0',
        maxWidth: '460px',
        fontSize: '13px',
        color: 'var(--text-color-65)',
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
      }}>
        <span style={{ fontSize: '16px' }}>{wasConfirmed ? '✅' : '❌'}</span>
        <span>
          <strong style={{ color: 'var(--text-color-85)' }}>{tool_name}</strong>
          {' — '}
          {wasConfirmed ? t('instant.chat.hitlConfirmed') : t('instant.chat.hitlCanceled')}
        </span>
      </div>
    );
  }

  // ---- interactive card ----
  return (
    <div style={{
      border: `1px solid ${riskColor.border}`,
      borderRadius: '8px',
      padding: '16px',
      backgroundColor: riskColor.bg,
      maxWidth: '460px',
      boxSizing: 'border-box',
    }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '10px' }}>
        <Tag color={riskColor.tag} style={{ margin: 0 }}>{getRiskLabel()}</Tag>
        <span style={{ fontSize: '13px', color: 'var(--text-color-65)' }}>
          {t('instant.chat.hitlTitle')}
        </span>
      </div>

      {/* Tool description */}
      <div style={{
        fontWeight: 600,
        fontSize: '14px',
        color: 'var(--text-color-85)',
        marginBottom: '10px',
        wordBreak: 'break-all',
      }}>
        {description}
      </div>

      {/* Collapsible params */}
      {Object.keys(tool_params).length > 0 && (
        <Collapse ghost size="small" style={{ marginBottom: '12px' }}>
          <Panel
            header={
              <span style={{ fontSize: '12px', color: 'var(--text-color-45)' }}>
                {t('instant.chat.hitlParams')}
              </span>
            }
            key="1"
          >
            <pre style={{
              fontSize: '12px',
              backgroundColor: 'var(--bg-color)',
              borderRadius: '4px',
              padding: '8px',
              margin: 0,
              overflowX: 'auto',
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-all',
              color: 'var(--text-color-65)',
            }}>
              {JSON.stringify(tool_params, null, 2)}
            </pre>
          </Panel>
        </Collapse>
      )}

      {/* Timeout hint */}
      <div style={{ fontSize: '12px', color: 'var(--text-color-45)', marginBottom: '14px' }}>
        ⏱ {remaining} {t('instant.chat.hitlTimeout')}
      </div>

      {/* Action buttons */}
      <div style={{ display: 'flex', gap: '10px' }}>
        <Button
          type="primary"
          size="small"
          loading={loading}
          onClick={() => handleDecision(true)}
          style={{ flex: 1 }}
        >
          {t('instant.chat.hitlConfirm')}
        </Button>
        <Button
          size="small"
          danger
          loading={loading}
          onClick={() => handleDecision(false)}
          style={{ flex: 1 }}
        >
          {t('instant.chat.hitlCancel')}
        </Button>
      </div>
    </div>
  );
});

export default ActionConfirmMessage;
