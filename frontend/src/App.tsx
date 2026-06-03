import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import MainLayout from './components/MainLayout';
import LoginPage from './pages/LoginPage';
import InventoryList from './pages/InventoryList';
import PurchaseList from './pages/PurchaseList';
import InstallList from './pages/InstallList';
import TransferList from './pages/TransferList';
import StockLogs from './pages/StockLogs';
import UserList from './pages/UserList';
import RoleList from './pages/RoleList';
import DictionaryList from './pages/DictionaryList';

const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const token = localStorage.getItem('token');
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
};

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <MainLayout />
            </ProtectedRoute>
          }
        >
          <Route index element={<InventoryList />} />
          <Route path="purchase" element={<PurchaseList />} />
          <Route path="install" element={<InstallList />} />
          <Route path="transfer" element={<TransferList />} />
          <Route path="logs" element={<StockLogs />} />
          <Route path="users" element={<UserList />} />
          <Route path="roles" element={<RoleList />} />
          <Route path="dictionary" element={<DictionaryList />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
