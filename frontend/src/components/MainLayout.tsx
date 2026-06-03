import React, { useState, useMemo } from 'react';
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
    localStorage.removeItem('username');
    localStorage.removeItem('role_name');
    localStorage.removeItem('permissions');
    navigate('/login');
  };

  // 获取用户权限
  const userPermissions = useMemo(() => {
    try {
      const permissionsStr = localStorage.getItem('permissions');
      return permissionsStr ? JSON.parse(permissionsStr) : [];
    } catch {
      return [];
    }
  }, []);

  // 检查是否有指定权限
  const hasPermission = (permission: string) => {
    if (!permission) return true; // 不需要权限的菜单项
    if (userPermissions.includes('*')) return true; // 拥有全部权限
    return userPermissions.includes(permission);
  };

  // 定义菜单项及其所需权限
  const allMenuItems = [
    {
      key: '/',
      icon: <DashboardOutlined />,
      label: '库存列表',
      permission: 'inventory.view',
    },
    {
      key: '/purchase',
      icon: <ShoppingOutlined />,
      label: '采购记录',
      permission: 'purchase.view',
    },
    {
      key: '/install',
      icon: <DesktopOutlined />,
      label: '安装记录',
      permission: 'installation.view',
    },
    {
      key: '/transfer',
      icon: <SwapOutlined />,
      label: '划拨记录',
      permission: 'transfer.view',
    },
    {
      key: '/logs',
      icon: <HistoryOutlined />,
      label: '库存变动记录',
      permission: 'inventory.view',
    },
    {
      type: 'divider' as const,
    },
    {
      key: '/users',
      icon: <UserOutlined />,
      label: '用户管理',
      permission: 'user.manage',
    },
    {
      key: '/roles',
      icon: <LockOutlined />,
      label: '角色管理',
      permission: 'role.manage',
    },
  ];

  // 根据权限过滤菜单
  const filteredMenuItems = useMemo(() => {
    return allMenuItems.filter(item => {
      if (item.type === 'divider') return true; // 保留分隔符
      return hasPermission(item.permission || '');
    });
  }, [userPermissions]);

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
          items={filteredMenuItems}
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
