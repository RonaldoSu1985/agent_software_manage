import React, { useState, useEffect, useMemo } from 'react';
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
      { title: '代理商采购', key: 'purchase.create' },
      { title: '代理商间划拨', key: 'transfer.create' },
      { title: '商户安装', key: 'installation.create' },
    ],
  },
  {
    title: '采购管理',
    key: 'purchase',
    children: [
      { title: '采购查看', key: 'purchase.view' },
    ],
  },
  {
    title: '安装管理',
    key: 'installation',
    children: [
      { title: '安装查看', key: 'installation.view' },
    ],
  },
  {
    title: '划拨管理',
    key: 'transfer',
    children: [
      { title: '划拨查看', key: 'transfer.view' },
    ],
  },
  {
    title: '库存记录',
    key: 'logs',
    children: [
      { title: '库存记录查看', key: 'logs.view' },
    ],
  },
  {
    title: '数据字典',
    key: 'dictionary',
    children: [
      { title: '字典查看', key: 'dictionary.view' },
      { title: '字典新增', key: 'dictionary.create' },
      { title: '字典编辑', key: 'dictionary.edit' },
      { title: '字典删除', key: 'dictionary.delete' },
    ],
  },
  {
    title: '系统管理',
    key: 'system',
    children: [
      { title: '用户查看', key: 'user.view' },
      { title: '用户新增', key: 'user.create' },
      { title: '用户编辑', key: 'user.edit' },
      { title: '用户删除', key: 'user.delete' },
      { title: '角色查看', key: 'role.view' },
      { title: '角色新增', key: 'role.create' },
      { title: '角色编辑', key: 'role.edit' },
      { title: '角色删除', key: 'role.delete' },
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
  const [checkedKeys, setCheckedKeys] = useState<string[]>([]);
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
    fetchRoles();
  }, []);

  const fetchRoles = async (params: any = {}) => {
    try {
      const response = await api.get('/roles', { params });
      setRoles(response.data);
    } catch (error) {
      message.error('获取角色列表失败');
    }
  };

  const handleSearch = () => {
    const values = searchForm.getFieldsValue();
    fetchRoles(values);
  };

  const handleReset = () => {
    searchForm.resetFields();
    fetchRoles();
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

  const onCheckAllChange = (e: any) => {
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

  const getGroupKeys = (item: PermissionItem): string[] => {
    const keys: string[] = [];
    const traverse = (data: PermissionItem[]) => {
      data.forEach((child) => {
        if (child.children) {
          traverse(child.children);
        } else {
          keys.push(child.key);
        }
      });
    };
    if (item.children) {
      traverse(item.children);
    }
    return keys;
  };

  const handleGroupCheck = (item: PermissionItem) => {
    const groupKeys = getGroupKeys(item);
    let newKeys = [...checkedKeys];
    
    // 检查是否已全选该分组
    const allChecked = groupKeys.every(k => newKeys.includes(k));
    
    if (allChecked) {
      // 取消全选
      newKeys = newKeys.filter(k => !groupKeys.includes(k));
    } else {
      // 全选该分组
      groupKeys.forEach(k => {
        if (!newKeys.includes(k)) {
          newKeys.push(k);
        }
      });
    }
    
    // 过滤掉 '*'
    newKeys = newKeys.filter(k => k !== '*');
    
    // 检查是否选中了所有权限
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
        const groupKeys = getGroupKeys(item);
        const allChecked = groupKeys.every(k => checkedKeys.includes(k));
        const partialChecked = groupKeys.some(k => checkedKeys.includes(k)) && !allChecked;
        
        return (
          <div key={item.key} style={{ marginBottom: 8 }}>
            <div style={{ paddingLeft: level * 16 }}>
              <Checkbox
                checked={allChecked}
                indeterminate={partialChecked}
                onChange={() => handleGroupCheck(item)}
                style={{ fontWeight: 'bold' }}
              >
                {item.title}
              </Checkbox>
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
      render: (_: any, record: any) => (
        <Space>
          {hasPermission('role.edit') && (
            <Button icon={<EditOutlined />} onClick={() => showModal(record)}>
              编辑
            </Button>
          )}
          {hasPermission('role.delete') && (
            <Button icon={<DeleteOutlined />} onClick={() => handleDelete(record.id)} danger>
              删除
            </Button>
          )}
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Form form={searchForm} layout="inline" style={{ marginBottom: 16 }}>
        <Form.Item name="name" label="角色名称">
          <Input placeholder="请输入角色名称" style={{ width: 200 }} />
        </Form.Item>
      </Form>
      <div style={{ marginBottom: 16 }}>
        <Button type="primary" onClick={handleSearch}>
          查询
        </Button>
        <Button onClick={handleReset} style={{ marginLeft: 8 }}>
          重置
        </Button>
        {hasPermission('role.create') && (
          <Button type="primary" icon={<PlusOutlined />} onClick={() => showModal()} style={{ marginLeft: 8 }}>
            新增角色
          </Button>
        )}
      </div>
      <Table
        dataSource={roles}
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
        title={editingRole ? '编辑角色' : '新增角色'}
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
