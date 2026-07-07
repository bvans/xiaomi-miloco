/**
 * Copyright (C) 2025 Xiaomi Corporation
 * This software may be used and distributed according to the terms of the Xiaomi Miloco License Agreement.
 */

import { getApi, postApi, putApi, deleteApi } from "@/utils/http";

// auth API
export const getJudgeLogin = () => getApi('/api/auth/register-status');
export const getUserLoginOut = () => getApi('/api/auth/logout');
export const setInitPinCode = (data) => postApi('/api/auth/register', data);
export const getPinLogin = (data) => postApi('/api/auth/login', data);
export const setLanguage = (data) => postApi('/api/auth/language', data);
export const getLanguage = () => getApi('/api/auth/language');

// model API
export const getAllModels = () => getApi('/api/model');
export const createModel = (data) => postApi('/api/model', data);
export const getModelDetail = (modelId) => getApi(`/api/model/${modelId}`);
export const updateModel = (modelId, data) => putApi(`/api/model/${modelId}`, data);
export const deleteModel = (modelId) => deleteApi(`/api/model/${modelId}`);
export const getVendorModels = (data) => postApi('/api/model/get_vendor_models', data);
export const setCurrentModel = (modelId, purpose = '') => getApi(`/api/model/set_current_model?${purpose ? `purpose=${purpose}` : ''}${modelId ? `&model_id=${modelId}` : ''}`);
export const getModelPurposes = () => getApi('/api/model/model_purposes');

// mcp
export const getMCPService = () => getApi('/api/mcp');
export const setMCPService = (data) => postApi('/api/mcp', data);
export const updateMCPService = (id, data) => putApi(`/api/mcp/${id}`, data);
export const deleteMCPService = (id) => deleteApi(`/api/mcp/${id}`);
export const getMCPStatus = () => getApi('/api/mcp/clients/status');
export const reconnectMCPService = (id) => postApi(`/api/mcp/reconnect/${id}`);

// history API
export const getHistoryList = () => getApi('/api/chat/historys');
export const getHistoryDetail = (id) => getApi(`/api/chat/history/${id}`);
export const deleteChatHistory = (id) => deleteApi(`/api/chat/history/${id}`);
