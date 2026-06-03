import React from 'react';
import { Form, Input, Button, Card, message } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import api from '../api';

const LoginPage: React.FC = () => {
  const navigate = useNavigate();

  const onFinish = async (values: any) => {
    try {
      const params = new URLSearchParams();
      params.append('username', values.username);
      params.append('password', values.password);

      const response = await api.post('/auth/login', params);
      const token = response.data.access_token || response.data.token;
      
      if (token) {
        localStorage.setItem('token', token);
        // 保存用户信息和权限
        localStorage.setItem('username', response.data.username || '');
        localStorage.setItem('role_name', response.data.role_name || '');
        localStorage.setItem('permissions', JSON.stringify(response.data.permissions || []));
        message.success('登录成功');
        navigate('/');
      } else {
        message.error('登录失败：未获取到有效Token');
      }
    } catch (error: any) {
      console.error('Login error:', error);
      message.error(error.response?.data?.detail || '登录失败');
    }
  };

  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', background: '#f0f2f5' }}>
      <Card title="代理商软件管理系统" style={{ width: 400 }}>
        <Form name="login" onFinish={onFinish}>
          <Form.Item name="username" rules={[{ required: true, message: '请输入用户名' }]}>
            <Input prefix={<UserOutlined />} placeholder="用户名" size="large" />
          </Form.Item>
          <Form.Item name="password" rules={[{ required: true, message: '请输入密码' }]}>
            <Input.Password prefix={<LockOutlined />} placeholder="密码" size="large" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" style={{ width: '100%' }} size="large">
              登录
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

export default LoginPage;
