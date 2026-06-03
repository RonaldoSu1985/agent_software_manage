import React, { useState, useEffect } from 'react';
import { Table, Button, Modal, Form, Input, message, Checkbox, Space } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import api from '../api';

interface Role {
  id: number;
  name: string;
  permissions: string[];
}

interface PermissionItem {
  title: string;
  key: string;
  children?: PermissionItem[];
}

const permissionTreeData: PermissionItem[] = [
  {
    title: '库存管理',
    key: 'inventory',
    children: [
      { title: '库存查看', key: 'inventory.view' },
      { title: '库存编辑', key: 'inventory.edit' },
    ],
  },
  {
    title: '采购管理',
    key: 'purchase',
    children: [
      { title: '采购查看', key: 'purchase.view' },
      { title: '采购创建', key: 'purchase.create' },
    ],
  },
  {
    title: '安装管理',
    key: 'installation',
    children: [
      { title: '安装查看', key: 'installation.view' },
      { title: '安装创建', key: 'installation.create' },
    ],
  },
  {
    title: '划拨管理',
    key: 'transfer',
    children: [
      { title: '划拨查看', key: 'transfer.view' },
      { title: '划拨创建', key: 'transfer.create' },
    ],
  },
  {
    title: '数据字典',
    key: 'dictionary',
    children: [
      { title: '字典管理', key: 'dictionary.manage' },
    ],
  },
  {
    title: '系统管理',
    key: 'system',
    children: [
      { title: '用户管理', key: 'user.manage' },
      { title: '角色管理', key: 'role.manage' },
    ],
  },
];

const getAllPermissionKeys = (treeData: PermissionItem[]): string[] => {
  const keys: string[] = [];
  const traverse = (data: PermissionItem[]) => {
    data.forEach((item) => {
      if (item.children) {
        traverse(item.children);
      } else {
        keys.push(item.key);
      }
    });
  };
  traverse(treeData);
  return keys;
};

const allPermissionKeys = getAllPermissionKeys(permissionTreeData);

const RoleList: React.FC = () => {
  const [roles, setRoles] = useState<Role[]>([]);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [editingRole, setEditingRole] = useState<Role | null>(null);
  const [form] = Form.useForm();
  const [checkedKeys, setCheckedKeys] = useState<string[]>([]);

  useEffect(() => {
    fetchRoles();
  }, []);

  const fetchRoles = async () => {
    try {
      const response = await api.get('/roles');
      setRoles(response.data);
    } catch (error) {
      message.error('获取角色列表失败');
    }
  };

  const showModal = (role?: Role) => {
    if (role) {
      setEditingRole(role);
      let perms = role.permissions;
      // 如果权限包含 '*'（全部权限），同时添加所有子权限
      if (perms.includes('*')) {
        perms = ['*', ...allPermissionKeys];
      }
      setCheckedKeys(perms);
      form.setFieldsValue({
        name: role.name,
        permissions: perms,
      });
    } else {
      setEditingRole(null);
      setCheckedKeys([]);
      form.resetFields();
    }
    setIsModalVisible(true);
  };

  const handleOk = async () => {
    try {
      const values = await form.validateFields();
      let permissions = values.permissions as string[] || [];
      
      if (permissions.includes('*')) {
        permissions = ['*'];
      } else {
        permissions = permissions.filter(p => p !== '*');
      }
      
      const roleData = {
        name: values.name,
        permissions: permissions
      };
      
      if (editingRole) {
        await api.put(`/roles/${editingRole.id}`, roleData);
        message.success('角色更新成功');
      } else {
        await api.post('/roles', roleData);
        message.success('角色创建成功');
      }
      setIsModalVisible(false);
      fetchRoles();
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || '操作失败';
      message.error(errorMessage);
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await api.delete(`/roles/${id}`);
      message.success('角色删除成功');
      fetchRoles();
    } catch (error) {
      message.error('删除失败');
    }
  };

  const onCheckAllChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.checked) {
      const newKeys = ['*', ...allPermissionKeys];
      setCheckedKeys(newKeys);
      form.setFieldsValue({ permissions: newKeys });
    } else {
      setCheckedKeys([]);
      form.setFieldsValue({ permissions: [] });
    }
  };

  const onCheckItem = (key: string) => {
    let newKeys: string[];
    if (checkedKeys.includes(key)) {
      newKeys = checkedKeys.filter(k => k !== key);
    } else {
      newKeys = [...checkedKeys, key];
    }
    
    newKeys = newKeys.filter(k => k !== '*');
    
    const hasAllLeafPermissions = allPermissionKeys.every(k => newKeys.includes(k));
    if (hasAllLeafPermissions) {
      newKeys = ['*', ...newKeys];
    }
    
    setCheckedKeys(newKeys);
    form.setFieldsValue({ permissions: newKeys });
  };

  const renderTree = (data: PermissionItem[], level: number = 0) => {
    return data.map((item) => {
      if (item.children) {
        return (
          <div key={item.key} style={{ marginBottom: 8 }}>
            <div style={{ fontWeight: 'bold', marginBottom: 4, paddingLeft: level * 16 }}>
              {item.title}
            </div>
            <div style={{ paddingLeft: 16 }}>
              {renderTree(item.children, level + 1)}
            </div>
          </div>
        );
      } else {
        return (
          <Checkbox
            key={item.key}
            checked={checkedKeys.includes(item.key)}
            onChange={() => onCheckItem(item.key)}
            style={{ display: 'block', paddingLeft: level * 16 }}
          >
            {item.title}
          </Checkbox>
        );
      }
    });
  };

  const columns = [
    {
      title: '角色名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '权限',
      dataIndex: 'permissions',
      key: 'permissions',
      render: (permissions: string[]) => (
        <div>
          {permissions.includes('*') ? (
            <span>全部权限</span>
          ) : (
            permissions.map((p) => {
              const findLabel = (treeData: PermissionItem[], key: string): string => {
                for (const item of treeData) {
                  if (item.key === key) return item.title;
                  if (item.children) {
                    const found = findLabel(item.children, key);
                    if (found) return found;
                  }
                }
                return p;
              };
              return <div key={p}>{findLabel(permissionTreeData, p)}</div>;
            })
          )}
        </div>
      ),
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Space>
          <Button icon={<EditOutlined />} onClick={() => showModal(record)}>
            编辑
          </Button>
          <Button icon={<DeleteOutlined />} onClick={() => handleDelete(record.id)} danger>
            删除
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Button type="primary" icon={<PlusOutlined />} onClick={() => showModal()} style={{ marginBottom: 16 }}>
        添加角色
      </Button>
      <Table dataSource={roles} columns={columns} rowKey="id" />

      <Modal
        title={editingRole ? '编辑角色' : '添加角色'}
        open={isModalVisible}
        onOk={handleOk}
        onCancel={() => setIsModalVisible(false)}
        width={500}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="name"
            label="角色名称"
            rules={[{ required: true, message: '请输入角色名称' }]}
          >
            <Input />
          </Form.Item>
          <Form.Item name="permissions" label="权限">
            <div style={{ marginBottom: 12 }}>
              <Checkbox
                checked={checkedKeys.includes('*')}
                onChange={onCheckAllChange}
              >
                全部权限
              </Checkbox>
            </div>
            <div style={{ borderTop: '1px solid #f0f0f0', paddingTop: 12 }}>
              {renderTree(permissionTreeData)}
            </div>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default RoleList;
