/**
 * Copyright (C) 2025 Xiaomi Corporation
 * This software may be used and distributed according to the terms of the Xiaomi Miloco License Agreement.
 */

import './App.css'
import { Routes, Route, Navigate } from 'react-router-dom'
import { ThemeProvider } from './contexts/ThemeContext'
import GlobalSocketProvider from './contexts/GlobalSocketProvider'
import { LogViewerModal } from './components'
import Home from './pages/Home'
import McpService from './pages/McpService'
import Instant from './pages/Instant'
import Error500 from './pages/Error/Error500';
import Setting from './pages/Setting'
import ModelManage from './pages/ModelManage'

function App() {
  return (
    <ThemeProvider>
      <GlobalSocketProvider>
        <Routes>
          <Route path="/" element={<Navigate to="/home/instant" replace />} />
          <Route path="/500" element={<Error500 />} />
          <Route path="/home" element={<Home />} >
            <Route index element={<Navigate to="instant" replace />} />
            <Route path="instant" element={<Instant />} />
            <Route path="mcpService" element={<McpService />} />
            <Route path="modelManage" element={<ModelManage />} />
            <Route path="setting" element={<Setting />} />
          </Route>
        </Routes>
        <LogViewerModal />
      </GlobalSocketProvider>
    </ThemeProvider>
  )
}

export default App
