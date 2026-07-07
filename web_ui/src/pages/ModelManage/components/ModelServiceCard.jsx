/**
 * Copyright (C) 2025 Xiaomi Corporation
 * This software may be used and distributed according to the terms of the Xiaomi Miloco License Agreement.
 */

import React from 'react';
import { Button, Typography, Empty } from 'antd';
import { useTranslation } from 'react-i18next';
import { Card, Icon } from '@/components';
import { ModelItem } from './index';
import styles from '../index.module.less';

const { Title } = Typography;

/**
 * ModelServiceCard Component - Model service card component
 * 模型服务卡片组件
 *
 * @returns {JSX.Element} ModelServiceCard component
 */
const ModelServiceCard = ({
  models,
  onAddModel,
  onEditModel,
  onDeleteModel,
}) => {
  const { t } = useTranslation();
  return (
    <div
      className={styles.modelServiceCard}
    >
      <div className={styles.modelList}>
        <Card className={styles.modelCategory} contentClassName={styles.modelCategoryContent}>
          <div className={styles.modelCategoryTitle}>
            <Title style={{ marginBottom: 0 }} level={5}>{t('modelModal.cloudModels')}</Title>
            <Button
              type="primary"
              icon={<Icon name="add" size={14} style={{ color: 'white' }} />}
              onClick={() => { onAddModel() }}
            >
              {t('modelModal.addModel')}
            </Button>
          </div>
          <div className={styles.contentWrap}>


            {(() => {
              const cloudModels = models;
              return cloudModels.length > 0 ? (
                cloudModels.map(model => (
                  <ModelItem
                    key={model.id}
                    model={model}
                    onEdit={onEditModel}
                    onDelete={onDeleteModel}
                  />
                ))
              ) : (
                <Empty description={t('modelModal.noCloudModels')} />
              );
            })()}
          </div>

        </Card>
      </div>
    </div>
  );
};

export default ModelServiceCard;
