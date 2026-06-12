import React, { useState, useMemo, useEffect } from 'react';
import { Layout, Menu, Button, theme, Drawer } from 'antd';
import {
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  DashboardOutlined,
  HistoryOutlined,
  LogoutOutlined,
  ShoppingOutlined,
  DesktopOutlined,
  SwapOutlined,
  UserOutlined,
  LockOutlined,
  MenuOutlined,
  FileOutlined,
  RobotOutlined,
} from '@ant-design/icons';
import { useNavigate, Outlet, useLocation } from 'react-router-dom';

const { Header, Sider, Content } = Layout;

const MainLayout: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken();

  // 检测是否为移动端
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
      if (window.innerWidth < 768) {
        setCollapsed(true);
      }
    };
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

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
      label: '代理商库存管理',
      permission: 'inventory.view',
    },
    {
      key: '/purchase',
      icon: <ShoppingOutlined />,
      label: '代理商采购记录',
      permission: 'purchase.view',
    },
    {
      key: '/install',
      icon: <DesktopOutlined />,
      label: '代理商安装记录',
      permission: 'installation.view',
    },
    {
      key: '/transfer',
      icon: <SwapOutlined />,
      label: '代理商划拨记录',
      permission: 'transfer.view',
    },
    {
      key: '/logs',
      icon: <HistoryOutlined />,
      label: '代理商库存记录',
      permission: 'logs.view',
    },
    {
      type: 'divider' as const,
    },
    {
      key: '/dictionary',
      icon: <FileOutlined />,
      label: '数据字典',
      permission: 'dictionary.view',
    },
    {
      key: '/mcp',
      icon: <RobotOutlined />,
      label: 'AI 助手设置',
      permission: 'mcp.settings',
    },
    {
      key: '/users',
      icon: <UserOutlined />,
      label: '用户管理',
      permission: 'user.view',
    },
    {
      key: '/roles',
      icon: <LockOutlined />,
      label: '角色管理',
      permission: 'role.view',
    },
  ];

  // 根据权限过滤菜单
  const filteredMenuItems = useMemo(() => {
    return allMenuItems.filter(item => {
      if (item.type === 'divider') return true; // 保留分隔符
      return hasPermission(item.permission || '');
    });
  }, [userPermissions]);

  const handleMenuClick = (key: string) => {
    if (key !== location.pathname) {
      navigate(key);
    }
    if (isMobile) {
      setMobileMenuOpen(false);
    }
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      {!isMobile && (
        <Sider trigger={null} collapsible collapsed={collapsed} style={{ minWidth: collapsed ? 80 : 200 }}>
          <div style={{ height: 32, margin: 16, background: 'rgba(255, 255, 255, 0.2)', color: 'white', textAlign: 'center', lineHeight: '32px', fontWeight: 'bold', fontSize: collapsed ? 14 : 16 }}>
            {collapsed ? 'AMS' : '软件管理系统'}
          </div>
          <Menu
            theme="dark"
            mode="inline"
            selectedKeys={[location.pathname]}
            items={filteredMenuItems}
            onClick={({ key }) => handleMenuClick(key)}
          />
        </Sider>
      )}
      <Layout>
        <Header style={{ padding: 0, background: colorBgContainer, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          {!isMobile ? (
            <Button
              type="text"
              icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
              onClick={() => setCollapsed(!collapsed)}
              style={{ fontSize: '16px', width: 64, height: 64 }}
            />
          ) : (
            <Button
              type="text"
              icon={<MenuOutlined />}
              onClick={() => setMobileMenuOpen(true)}
              style={{ fontSize: '16px', width: 64, height: 64 }}
            />
          )}
          <div style={{ display: 'flex', alignItems: 'center', gap: 16, marginRight: isMobile ? 12 : 16 }}>
            <span style={{ display: !isMobile ? 'block' : 'none', fontSize: 14 }}>
              {localStorage.getItem('full_name') || localStorage.getItem('username')}
            </span>
            <Button
              type="text"
              icon={<LogoutOutlined />}
              onClick={handleLogout}
              style={{ padding: isMobile ? 4 : undefined }}
            >
              {isMobile ? null : '退出'}
            </Button>
          </div>
        </Header>
        <Content
          style={{
            margin: isMobile ? '12px 8px' : '24px 16px',
            padding: isMobile ? 12 : 24,
            minHeight: 280,
            background: colorBgContainer,
            borderRadius: borderRadiusLG,
            overflow: 'auto',
            fontSize: isMobile ? 14 : 16,
          }}
        >
          <Outlet />
        </Content>
      </Layout>

      {/* 移动端菜单抽屉 */}
      <Drawer
        title="软件管理系统"
        placement="left"
        onClose={() => setMobileMenuOpen(false)}
        open={mobileMenuOpen}
        width={260}
        bodyStyle={{ padding: 0 }}
      >
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={filteredMenuItems}
          onClick={({ key }) => handleMenuClick(key)}
          style={{ height: '100%', borderRight: 0 }}
        />
      </Drawer>
    </Layout>
  );
};

export default MainLayout;
