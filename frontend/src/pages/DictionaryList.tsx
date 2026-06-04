import React, { useState, useEffect, useMemo } from 'react';
import { Table, Form, Input, Select, Button, Space, message, Modal, Switch } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, SearchOutlined, SyncOutlined, DownloadOutlined } from '@ant-design/icons';
import api from '../api';
import dayjs from 'dayjs';

const { Option } = Select;

const DictionaryList: React.FC = () => {
  const [form] = Form.useForm();
  const [modalForm] = Form.useForm();
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [modalType, setModalType] = useState<'add' | 'edit'>('add');
  const [selectedItem, setSelectedItem] = useState<any>(null);
  const [dictionaryTypes, setDictionaryTypes] = useState<any[]>([]);

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

  // 获取字典类型列表和初始数据
  useEffect(() => {
    fetchDictionaryTypes();
    fetchData();
  }, []);

  const fetchDictionaryTypes = async () => {
    try {
      const response = await api.get('/dictionary/types', { params: { page_size: 100 } });
      setDictionaryTypes(response.data.items || []);
    } catch (error) {
      message.error('获取字典类型失败');
    }
  };

  const fetchData = async (values: any = {}) => {
    setLoading(true);
    try {
      const params: any = {
        page: 1,
        page_size: 100
      };
      
      if (values.type_code) params.type_code = values.type_code;
      if (values.item_name) params.item_name = values.item_name;
      if (values.item_key) params.item_key = values.item_key;
      if (values.status && values.status !== 'all') {
        params.status = values.status === 'enabled';
      }
      
      const response = await api.get('/dictionary/items', { params });
      setData(response.data.items || []);
    } catch (error) {
      message.error('获取字典列表失败');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (values: any) => {
    fetchData(values);
  };

  const handleReset = () => {
    form.resetFields();
    fetchData();
  };

  const handleAdd = () => {
    if (!dictionaryTypes || dictionaryTypes.length === 0) {
      message.warning('字典类型数据尚未加载，请稍后再试');
      return;
    }
    setModalType('add');
    setSelectedItem(null);
    modalForm.setFieldsValue({
      type_id: dictionaryTypes[0]?.id || '',
      item_key: '',
      item_value: '',
      item_name: '',
      remark: ''
    });
    setIsModalVisible(true);
  };

  const handleEdit = (record: any) => {
    setModalType('edit');
    setSelectedItem(record);
    modalForm.setFieldsValue({
      type_id: record.type_id,
      item_key: record.item_key,
      item_value: record.item_value,
      item_name: record.item_name,
      remark: record.remark || ''
    });
    setIsModalVisible(true);
  };

  const handleDelete = async (record: any) => {
    try {
      await api.delete(`/dictionary/items/${record.id}`);
      message.success('删除成功');
      fetchData();
    } catch (error) {
      message.error('删除失败');
    }
  };

  const handleStatusChange = async (record: any, checked: boolean) => {
    try {
      await api.put(`/dictionary/items/${record.id}`, { status: checked });
      message.success('状态更新成功');
      fetchData();
    } catch (error) {
      message.error('状态更新失败');
    }
  };

  const handleModalSubmit = async (values: any) => {
    try {
      if (modalType === 'add') {
        await api.post('/dictionary/items', {
          type_id: values.type_id,
          item_key: values.item_key,
          item_value: values.item_value,
          item_name: values.item_name,
          remark: values.remark
        });
      } else {
        await api.put(`/dictionary/items/${selectedItem.id}`, {
          item_key: values.item_key,
          item_value: values.item_value,
          item_name: values.item_name,
          remark: values.remark
        });
      }
      message.success(modalType === 'add' ? '新增成功' : '修改成功');
      setIsModalVisible(false);
      modalForm.resetFields();
      fetchData();
    } catch (error: any) {
      message.error(error.response?.data?.detail || (modalType === 'add' ? '新增失败' : '修改失败'));
    }
  };

  const handleExport = async () => {
    try {
      const values = form.getFieldsValue();
      const params = new URLSearchParams();
      if (values.type_code) params.append('type_code', values.type_code);
      
      const token = localStorage.getItem('token');
      const url = `/api/v1/dictionary/items/export?${params.toString()}`;
      
      const response = await fetch(url, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (!response.ok) throw new Error('导出失败');
      
      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = `字典数据_${dayjs().format('YYYYMMDDHHmmss')}.csv`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(downloadUrl);
      
      message.success('导出成功');
    } catch (error) {
      message.error('导出失败');
    }
  };

  const columns = [
    { title: '字典编号', dataIndex: 'id', key: 'id', width: 100 },
    { title: '字典类型', dataIndex: 'type_name', key: 'type_name' },
    { title: '字典名称', dataIndex: 'item_name', key: 'item_name' },
    { title: '字典KEY', dataIndex: 'item_key', key: 'item_key' },
    { title: '字典VALUE', dataIndex: 'item_value', key: 'item_value' },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: boolean, record: any) => (
        <Switch
          checked={status}
          onChange={(checked) => handleStatusChange(record, checked)}
          checkedChildren="启用"
          unCheckedChildren="禁用"
        />
      )
    },
    { title: '备注', dataIndex: 'remark', key: 'remark', ellipsis: true },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 160,
      render: (text: string) => dayjs(text).format('YYYY-MM-DD HH:mm:ss')
    },
    {
      title: '操作',
      key: 'action',
      width: 140,
      render: (_: any, record: any) => (
        <span>
          {hasPermission('dictionary.edit') && (
            <Button
              icon={<EditOutlined />}
              onClick={() => handleEdit(record)}
              style={{ marginRight: 8 }}
            >
              编辑
            </Button>
          )}
          {hasPermission('dictionary.delete') && (
            <Button
              danger
              icon={<DeleteOutlined />}
              onClick={() => handleDelete(record)}
            >
              删除
            </Button>
          )}
        </span>
      )
    }
  ];

  return (
    <div>
      <h2 style={{ margin: 0, marginBottom: 16 }}>数据字典管理</h2>

      <Form form={form} onFinish={handleSearch} layout="inline" style={{ marginBottom: 16 }}>
        <Form.Item name="item_name">
          <Input placeholder="字典名称" style={{ width: 180 }} />
        </Form.Item>
        <Form.Item name="item_key">
          <Input placeholder="字典KEY" style={{ width: 180 }} />
        </Form.Item>
        <Form.Item name="type_code">
          <Select placeholder="字典类型" style={{ width: 180 }}>
            <Option value="">全部</Option>
            {dictionaryTypes.map((type: any) => (
              <Option key={type.id} value={type.type_code}>{type.type_name}</Option>
            ))}
          </Select>
        </Form.Item>
        <Form.Item name="status">
          <Select placeholder="状态" style={{ width: 120 }}>
            <Option value="all">全部</Option>
            <Option value="enabled">启用</Option>
            <Option value="disabled">禁用</Option>
          </Select>
        </Form.Item>
      </Form>
      <div style={{ marginBottom: 20 }}>
        <Space>
          <Button type="primary" onClick={() => form.submit()} icon={<SearchOutlined />}>
            查询
          </Button>
          <Button onClick={handleReset} icon={<SyncOutlined />}>
            重置
          </Button>
          <Button onClick={handleExport} icon={<DownloadOutlined />}>
            导出
          </Button>
          {hasPermission('dictionary.create') && (
            <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
              新增
            </Button>
          )}
        </Space>
      </div>

      <Table
        columns={columns}
        dataSource={data}
        loading={loading}
        rowKey="id"
        pagination={{
          pageSize: 10,
          showSizeChanger: true,
          pageSizeOptions: ['10', '20', '50', '100'],
          showTotal: (total) => `共 ${total} 条`,
        }}
      />

      <Modal
        title={modalType === 'add' ? '新增字典项' : '修改字典项'}
        open={isModalVisible}
        onCancel={() => setIsModalVisible(false)}
        onOk={() => modalForm.submit()}
        width={500}
      >
        <Form form={modalForm} layout="vertical" onFinish={handleModalSubmit}>
          {modalType === 'add' && (
            <Form.Item name="type_id" label="字典类型" rules={[{ required: true, message: '请选择字典类型' }]}>
              <Select placeholder="请选择字典类型">
                {dictionaryTypes.map((type: any) => (
                  <Option key={type.id} value={type.id}>{type.type_name}</Option>
                ))}
              </Select>
            </Form.Item>
          )}
          <Form.Item name="item_key" label="字典KEY" rules={[{ required: true, message: '请输入字典KEY' }]}>
            <Input placeholder="请输入字典KEY" />
          </Form.Item>
          <Form.Item name="item_value" label="字典VALUE" rules={[{ required: true, message: '请输入字典VALUE' }]}>
            <Input placeholder="请输入字典VALUE" />
          </Form.Item>
          <Form.Item name="item_name" label="字典名称" rules={[{ required: true, message: '请输入字典名称' }]}>
            <Input placeholder="请输入字典名称" />
          </Form.Item>
          <Form.Item name="remark" label="备注">
            <Input.TextArea placeholder="请输入备注" rows={3} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default DictionaryList;
