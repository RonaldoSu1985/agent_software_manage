import React, { useState, useEffect, useMemo } from 'react';
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
  department: string;
  department_name: string;
}

interface Role {
  id: number;
  name: string;
}

interface Department {
  item_key: string;
  item_value: string;
}

const UserList: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [roles, setRoles] = useState<Role[]>([]);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [form] = Form.useForm();
  const [searchForm] = Form.useForm();

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
    if (!permission) return true;
    if (userPermissions.includes('*')) return true;
    return userPermissions.includes(permission);
  };

  useEffect(() => {
    fetchUsers();
    fetchRoles();
    fetchDepartments();
  }, []);

  const fetchUsers = async (params: any = {}) => {
    try {
      // 添加时间戳参数防止缓存
      const response = await api.get('/users', { 
        params: { ...params, _t: Date.now() } 
      });
      console.log('API Response:', response.data);
      
      // 确保数据正确，不被其他代码修改
      const safeUsers = response.data.map((user: any) => ({
        ...user,
        username: user.username, // 强制使用 username 字段
      }));
      
      console.log('Safe Users:', safeUsers);
      setUsers(safeUsers);
    } catch (error) {
      message.error('获取用户列表失败');
    }
  };

  const handleSearch = () => {
    const values = searchForm.getFieldsValue();
    fetchUsers(values);
  };

  const handleReset = () => {
    searchForm.resetFields();
    fetchUsers();
  };

  const fetchRoles = async () => {
    try {
      const response = await api.get('/roles');
      setRoles(response.data);
    } catch (error) {
      message.error('获取角色列表失败');
    }
  };

  const fetchDepartments = async () => {
    try {
      const response = await api.get('/dictionary/items/by-type/DEPARTMENT');
      setDepartments(response.data || []);
    } catch (error) {
      message.error('获取部门列表失败');
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
        department: user.department,
      });
    } else {
      setEditingUser(null);
      form.resetFields();
      form.setFieldsValue({
        is_active: true,
      });
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
      render: (_text: string, record: User) => record.username,
    },
    {
      title: '姓名',
      dataIndex: 'full_name',
      key: 'full_name',
    },
    {
      title: '所属部门',
      dataIndex: 'department_name',
      key: 'department_name',
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
      render: (_: any, record: any) => (
        <span>
          {hasPermission('user.edit') && (
            <Button icon={<EditOutlined />} onClick={() => showModal(record)} style={{ marginRight: 8 }}>
              编辑
            </Button>
          )}
          {hasPermission('user.delete') && (
            <Button icon={<DeleteOutlined />} onClick={() => handleDelete(record.id)} danger>
              删除
            </Button>
          )}
        </span>
      ),
    },
  ];

  return (
    <div>
      <Form form={searchForm} layout="inline" style={{ marginBottom: 16 }}>
        <Form.Item name="full_name" label="姓名">
          <Input placeholder="请输入姓名" style={{ width: 150 }} />
        </Form.Item>
        <Form.Item name="department" label="所属部门">
          <Select placeholder="请选择部门" style={{ width: 150 }}>
            {departments.map((dept) => (
              <Option key={dept.item_key} value={dept.item_key}>
                {dept.item_value}
              </Option>
            ))}
          </Select>
        </Form.Item>
        <Form.Item name="is_active" label="状态">
          <Select placeholder="请选择状态" style={{ width: 120 }}>
            <Option value={true}>启用</Option>
            <Option value={false}>禁用</Option>
          </Select>
        </Form.Item>
      </Form>
      <div style={{ marginBottom: 16 }}>
        <Button type="primary" onClick={handleSearch}>
          查询
        </Button>
        <Button onClick={handleReset} style={{ marginLeft: 8 }}>
          重置
        </Button>
        {hasPermission('user.create') && (
          <Button type="primary" icon={<PlusOutlined />} onClick={() => showModal()} style={{ marginLeft: 8 }}>
            新增用户
          </Button>
        )}
      </div>
      <Table
        dataSource={users}
        columns={columns}
        rowKey="id"
        pagination={{
          pageSize: 10,
          showSizeChanger: true,
          pageSizeOptions: ['10', '20', '50', '100'],
          showTotal: (total) => `共 ${total} 条`,
        }}
      />

      <Modal
        title={editingUser ? '编辑用户' : '新增用户'}
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
          <Form.Item
            name="department"
            label="所属部门"
            rules={[{ required: true, message: '请选择所属部门' }]}
          >
            <Select>
              {departments.map((dept) => (
                <Option key={dept.item_key} value={dept.item_key}>
                  {dept.item_value}
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
