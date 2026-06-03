import React, { useState, useEffect } from 'react';
import { Table, Button, Modal, Form, Input, Select, message } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import api from '../api';

const { Option } = Select;

interface User {
  id: number;
  username: string;
  full_name: string;
  role_id: number;
  role_name: string;
  is_active: boolean;
}

interface Role {
  id: number;
  name: string;
}

const UserList: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [roles, setRoles] = useState<Role[]>([]);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [form] = Form.useForm();

  useEffect(() => {
    fetchUsers();
    fetchRoles();
  }, []);

  const fetchUsers = async () => {
    try {
      const response = await api.get('/users');
      setUsers(response.data);
    } catch (error) {
      message.error('获取用户列表失败');
    }
  };

  const fetchRoles = async () => {
    try {
      const response = await api.get('/roles');
      setRoles(response.data);
    } catch (error) {
      message.error('获取角色列表失败');
    }
  };

  const showModal = (user?: User) => {
    if (user) {
      setEditingUser(user);
      form.setFieldsValue({
        username: user.username,
        full_name: user.full_name,
        role_id: user.role_id,
        is_active: user.is_active,
      });
    } else {
      setEditingUser(null);
      form.resetFields();
    }
    setIsModalVisible(true);
  };

  const handleOk = async () => {
    try {
      const values = await form.validateFields();
      if (editingUser) {
        await api.put(`/users/${editingUser.id}`, values);
        message.success('用户更新成功');
      } else {
        await api.post('/users', values);
        message.success('用户创建成功');
      }
      setIsModalVisible(false);
      fetchUsers();
    } catch (error) {
      message.error('操作失败');
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await api.delete(`/users/${id}`);
      message.success('用户删除成功');
      fetchUsers();
    } catch (error) {
      message.error('删除失败');
    }
  };

  const columns = [
    {
      title: '用户名',
      dataIndex: 'username',
      key: 'username',
    },
    {
      title: '姓名',
      dataIndex: 'full_name',
      key: 'full_name',
    },
    {
      title: '角色',
      dataIndex: 'role_name',
      key: 'role_name',
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (is_active: boolean) => (is_active ? '启用' : '禁用'),
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <span>
          <Button icon={<EditOutlined />} onClick={() => showModal(record)} style={{ marginRight: 8 }}>
            编辑
          </Button>
          <Button icon={<DeleteOutlined />} onClick={() => handleDelete(record.id)} danger>
            删除
          </Button>
        </span>
      ),
    },
  ];

  return (
    <div>
      <Button type="primary" icon={<PlusOutlined />} onClick={() => showModal()} style={{ marginBottom: 16 }}>
        添加用户
      </Button>
      <Table dataSource={users} columns={columns} rowKey="id" />

      <Modal
        title={editingUser ? '编辑用户' : '添加用户'}
        open={isModalVisible}
        onOk={handleOk}
        onCancel={() => setIsModalVisible(false)}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="username"
            label="用户名"
            rules={[{ required: true, message: '请输入用户名' }]}
          >
            <Input disabled={!!editingUser} />
          </Form.Item>
          <Form.Item
            name="password"
            label={editingUser ? '新密码（不填则不修改）' : '密码'}
          >
            <Input.Password />
          </Form.Item>
          <Form.Item
            name="full_name"
            label="姓名"
            rules={[{ required: true, message: '请输入姓名' }]}
          >
            <Input />
          </Form.Item>
          <Form.Item
            name="role_id"
            label="角色"
            rules={[{ required: true, message: '请选择角色' }]}
          >
            <Select>
              {roles.map((role) => (
                <Option key={role.id} value={role.id}>
                  {role.name}
                </Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item name="is_active" label="状态">
            <Select>
              <Option value={true}>启用</Option>
              <Option value={false}>禁用</Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default UserList;
