import React, { useState } from 'react';
import { Layout, Menu, Button, theme } from 'antd';
import {
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  DashboardOutlined,
  DatabaseOutlined,
  HistoryOutlined,
  LogoutOutlined,
  ShoppingOutlined,
  DesktopOutlined,
  SwapOutlined,
  UserOutlined,
  LockOutlined,
} from '@ant-design/icons';
import { useNavigate, Outlet, useLocation } from 'react-router-dom';

const { Header, Sider, Content } = Layout;

const MainLayout: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken();

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  const menuItems = [
    {
      key: '/',
      icon: <DashboardOutlined />,
      label: '库存列表',
    },
    {
      key: '/purchase',
      icon: <ShoppingOutlined />,
      label: '采购记录',
    },
    {
      key: '/install',
      icon: <DesktopOutlined />,
      label: '安装记录',
    },
    {
      key: '/transfer',
      icon: <SwapOutlined />,
      label: '划拨记录',
    },
    {
      key: '/logs',
      icon: <HistoryOutlined />,
      label: '库存变动记录',
    },
    {
      type: 'divider' as const,
    },
    {
      key: '/users',
      icon: <UserOutlined />,
      label: '用户管理',
    },
    {
      key: '/roles',
      icon: <LockOutlined />,
      label: '角色管理',
    },
  ];

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider trigger={null} collapsible collapsed={collapsed}>
        <div style={{ height: 32, margin: 16, background: 'rgba(255, 255, 255, 0.2)', color: 'white', textAlign: 'center', lineHeight: '32px', fontWeight: 'bold' }}>
          {collapsed ? 'AMS' : '软件管理系统'}
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={({ key }) => {
            if (key !== location.pathname) {
              navigate(key);
            }
          }}
        />
      </Sider>
      <Layout>
        <Header style={{ padding: 0, background: colorBgContainer, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Button
            type="text"
            icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
            onClick={() => setCollapsed(!collapsed)}
            style={{ fontSize: '16px', width: 64, height: 64 }}
          />
          <Button
            type="text"
            icon={<LogoutOutlined />}
            onClick={handleLogout}
            style={{ marginRight: 16 }}
          >
            退出登录
          </Button>
        </Header>
        <Content
          style={{
            margin: '24px 16px',
            padding: 24,
            minHeight: 280,
            background: colorBgContainer,
            borderRadius: borderRadiusLG,
            overflow: 'auto'
          }}
        >
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
};

export default MainLayout;
