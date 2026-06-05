import React, { useState, useEffect, useMemo } from 'react';
import { Table, Form, Input, Select, Button, Space, message, Modal, DatePicker } from 'antd';
import api from '../api';
import dayjs from 'dayjs';

const { Option } = Select;

const InventoryList: React.FC = () => {
  const [form] = Form.useForm();
  const [purchaseForm] = Form.useForm();
  const [transferForm] = Form.useForm();
  const [installForm] = Form.useForm();
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [systemTypes, setSystemTypes] = useState([]);
  const [softwareList, setSoftwareList] = useState([]);
  const [isPurchaseModalVisible, setIsPurchaseModalVisible] = useState(false);
  const [isTransferModalVisible, setIsTransferModalVisible] = useState(false);
  const [isInstallModalVisible, setIsInstallModalVisible] = useState(false);
  const [currentUser, setCurrentUser] = useState('');

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

  const fetchData = async (values: any = {}) => {
    setLoading(true);
    try {
      const params = {
        system_type: values.system_type === 'all' ? undefined : values.system_type,
        agent_code: values.agent_code,
        agent_name: values.agent_name,
        software_name: values.software_name === 'all' ? undefined : values.software_name,
      };
      const response = await api.get('/inventory/list', { params });
      setData(response.data);
    } catch (error) {
      message.error('获取库存列表失败');
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    try {
      const values = form.getFieldsValue();
      const params = {
        system_type: values.system_type === 'all' ? undefined : values.system_type,
        agent_code: values.agent_code,
        agent_name: values.agent_name,
        software_name: values.software_name === 'all' ? undefined : values.software_name,
      };
      
      // 构建查询参数
      const queryParams = new URLSearchParams();
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          queryParams.append(key, value);
        }
      });
      
      // 创建下载链接
      const token = localStorage.getItem('token');
      const url = `/api/v1/inventory/export?${queryParams.toString()}`;
      
      // 使用fetch下载文件
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!response.ok) {
        throw new Error('导出失败');
      }
      
      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = `库存列表_${dayjs().format('YYYYMMDDHHmmss')}.csv`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(downloadUrl);
      
      message.success('导出成功');
    } catch (error) {
      message.error('导出失败');
    }
  };

  const fetchCommonData = async () => {
    try {
      // 从数据字典获取代理商所属系统
      const systemRes = await api.get('/dictionary/items/by-type/SYSTEM_TYPE');
      setSystemTypes(systemRes.data || []);
      
      // 从数据字典获取软件名称
      const softRes = await api.get('/dictionary/items/by-type/SOFTWARE_NAME');
      setSoftwareList(softRes.data || []);
    } catch (error) {
      console.error('获取基础数据失败');
    }
  };

  const getUsername = () => {
    let username = localStorage.getItem('username');
    if (!username) {
      const token = localStorage.getItem('token');
      if (token) {
        try {
          const payload = token.split('.')[1];
          const decoded = JSON.parse(atob(payload));
          username = decoded.sub;
          if (username) {
            localStorage.setItem('username', username);
          }
        } catch {
          username = null;
        }
      }
    }
    return username || 'admin';
  };

  useEffect(() => {
    fetchData();
    fetchCommonData();
    
    setCurrentUser(getUsername());
  }, []);

  // 打开采购弹窗并自动填入数据
  const handleOpenPurchaseModal = (record: any) => {
    purchaseForm.setFieldsValue({
      system_type: record.agent?.system_type || '',
      agent_code: record.agent?.agent_code || '',
      agent_name: record.agent?.agent_name || '',
      software_name: record.software?.name || '',
      purchase_date: dayjs(),
      operator: currentUser || 'admin',
    });
    setIsPurchaseModalVisible(true);
  };

  // 提交采购
  const handlePurchaseSubmit = async (values: any) => {
    try {
      await api.post('/business/purchase', {
        ...values,
        purchase_date: values.purchase_date.format('YYYY-MM-DD'),
        system_type: values.system_type,
        agent_code: values.agent_code,
        agent_name: values.agent_name,
        software_name: values.software_name,
        operator: values.operator || currentUser,
      });
      message.success('新增采购成功');
      setIsPurchaseModalVisible(false);
      purchaseForm.resetFields();
      fetchData();
    } catch (error: any) {
      message.error(error.response?.data?.detail || '操作失败');
    }
  };

  // 打开划拨弹窗并自动填入数据
  const handleOpenTransferModal = (record: any) => {
    transferForm.setFieldsValue({
      from_system_type: record.agent?.system_type || '',
      from_agent_code: record.agent?.agent_code || '',
      from_agent_name: record.agent?.agent_name || '',
      software_name: record.software?.name || '',
      transfer_date: dayjs(),
      operator: currentUser || 'admin',
    });
    setIsTransferModalVisible(true);
  };

  // 提交划拨
  const handleTransferSubmit = async (values: any) => {
    try {
      await api.post('/business/transfer', {
        ...values,
        transfer_date: values.transfer_date.format('YYYY-MM-DD'),
        from_system_type: values.from_system_type,
        from_agent_code: values.from_agent_code,
        from_agent_name: values.from_agent_name,
        to_system_type: values.to_system_type,
        to_agent_code: values.to_agent_code,
        to_agent_name: values.to_agent_name,
        software_name: values.software_name,
        operator: values.operator || currentUser,
      });
      message.success('库存划拨成功');
      setIsTransferModalVisible(false);
      transferForm.resetFields();
      fetchData();
    } catch (error: any) {
      message.error(error.response?.data?.detail || '操作失败');
    }
  };

  // 打开安装弹窗并自动填入数据
  const handleOpenInstallModal = (record: any) => {
    installForm.setFieldsValue({
      system_type: record.agent?.system_type || '',
      agent_code: record.agent?.agent_code || '',
      agent_name: record.agent?.agent_name || '',
      software_name: record.software?.name || '',
      install_date: dayjs(),
      operator: currentUser || 'admin',
    });
    setIsInstallModalVisible(true);
  };

  // 提交安装
  const handleInstallSubmit = async (values: any) => {
    try {
      await api.post('/business/install', {
        ...values,
        install_date: values.install_date.format('YYYY-MM-DD'),
        system_type: values.system_type,
        agent_code: values.agent_code,
        agent_name: values.agent_name,
        software_name: values.software_name,
        operator: values.operator || currentUser,
      });
      message.success('商户安装记录已保存');
      setIsInstallModalVisible(false);
      installForm.resetFields();
      fetchData();
    } catch (error: any) {
      message.error(error.response?.data?.detail || '操作失败');
    }
  };

  const columns = [
    { title: '代理商所属系统', dataIndex: ['agent', 'system_type'], key: 'system_type' },
    { title: '代理商编号', dataIndex: ['agent', 'agent_code'], key: 'agent_code' },
    { title: '代理商名称', dataIndex: ['agent', 'agent_name'], key: 'agent_name' },
    { title: '软件名称', dataIndex: ['software', 'name'], key: 'software_name' },
    { title: '库存数量', dataIndex: 'quantity', key: 'quantity' },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: any) => {
        const params = new URLSearchParams({
          system_type: record.agent?.system_type || '',
          agent_code: record.agent?.agent_code || '',
          agent_name: record.agent?.agent_name || '',
          software_name: record.software?.name || '',
        });
        return (
          <Space>
            <Button type="link" onClick={() => window.location.href = `/logs?${params.toString()}`}>
              库存记录
            </Button>
            {hasPermission('purchase.create') && (
              <Button type="link" onClick={() => handleOpenPurchaseModal(record)}>
                采购
              </Button>
            )}
            {hasPermission('transfer.create') && (
              <Button type="link" onClick={() => handleOpenTransferModal(record)}>
                划拨
              </Button>
            )}
            {hasPermission('installation.create') && (
              <Button type="link" onClick={() => handleOpenInstallModal(record)}>
                安装
              </Button>
            )}
          </Space>
        );
      },
    },
  ];

  return (
    <div>
      <Form form={form} layout="inline" onFinish={fetchData} style={{ marginBottom: 16 }}>
        <Form.Item name="system_type" label="代理商所属系统" initialValue="all">
          <Select style={{ width: 150 }}>
            <Option value="all">请选择</Option>
            {systemTypes.map((item: any) => (
              <Option key={item.item_key} value={item.item_value}>{item.item_name}</Option>
            ))}
          </Select>
        </Form.Item>
        <Form.Item name="agent_code" label="代理商编号">
          <Input placeholder="请输入" style={{ width: 150 }} />
        </Form.Item>
        <Form.Item name="agent_name" label="代理商名称">
          <Input placeholder="请输入" style={{ width: 150 }} />
        </Form.Item>
        <Form.Item name="software_name" label="软件名称" initialValue="all">
          <Select style={{ width: 150 }}>
            <Option value="all">请选择</Option>
            {softwareList.map((item: any) => (
              <Option key={item.item_key} value={item.item_value}>{item.item_name}</Option>
            ))}
          </Select>
        </Form.Item>
      </Form>
      <div style={{ marginBottom: 20 }}>
        <Space>
          <Button type="primary" onClick={() => form.submit()}>查询</Button>
          <Button onClick={() => { form.resetFields(); fetchData(); }}>重置</Button>
          <Button htmlType="button" onClick={handleExport}>导出</Button>
          {hasPermission('purchase.create') && (
            <Button type="primary" onClick={() => window.location.href = '/purchase?add=true'}>代理商采购</Button>
          )}
          {hasPermission('transfer.create') && (
            <Button type="primary" onClick={() => window.location.href = '/transfer?add=true'}>代理商间划拨</Button>
          )}
          {hasPermission('installation.create') && (
            <Button type="primary" onClick={() => window.location.href = '/install?add=true'}>商户安装</Button>
          )}
        </Space>
      </div>
      <Table
        columns={columns}
        dataSource={data}
        rowKey="id"
        loading={loading}
        pagination={{
          pageSize: 10,
          showSizeChanger: true,
          pageSizeOptions: ['10', '20', '50', '100'],
          showTotal: (total) => `共 ${total} 条`,
        }}
      />

      <Modal
        title="代理商新增采购软件"
        open={isPurchaseModalVisible}
        onCancel={() => setIsPurchaseModalVisible(false)}
        onOk={() => purchaseForm.submit()}
        width={500}
      >
        <Form form={purchaseForm} layout="vertical" onFinish={handlePurchaseSubmit}>
          <Form.Item name="system_type" label="代理商所属系统" rules={[{ required: true, message: '请选择代理商所属系统' }]}>
            <Select placeholder="请选择">
              {systemTypes.map((item: any) => (
                <Option key={item.item_key} value={item.item_value}>{item.item_name}</Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item name="agent_code" label="代理商编号" rules={[{ required: true, message: '请输入代理商编号' }]}>
            <Input placeholder="请输入代理商编号" />
          </Form.Item>
          <Form.Item name="agent_name" label="代理商名称" rules={[{ required: true, message: '请输入代理商名称' }]}>
            <Input placeholder="请输入代理商名称" />
          </Form.Item>
          <Form.Item name="software_name" label="软件名称" rules={[{ required: true, message: '请选择软件名称' }]}>
            <Select placeholder="请选择">
              {softwareList.map((item: any) => (
                <Option key={item.item_key} value={item.item_value}>{item.item_name}</Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item name="quantity" label="采购数量" rules={[{ required: true, message: '请输入采购数量' }]}>
            <Input type="number" min={1} placeholder="请输入采购数量" />
          </Form.Item>
          <Form.Item name="purchase_date" label="采购日期" rules={[{ required: true, message: '请选择采购日期' }]}>
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="operator" label="操作人">
            <Input placeholder="请输入操作人" disabled />
          </Form.Item>
          <Form.Item name="remark" label="备注">
            <Input.TextArea placeholder="请输入备注" />
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        title="代理商之间软件库存划拨"
        open={isTransferModalVisible}
        onCancel={() => setIsTransferModalVisible(false)}
        onOk={() => transferForm.submit()}
        width={600}
      >
        <Form form={transferForm} layout="vertical" onFinish={handleTransferSubmit}>
          <Form.Item name="from_system_type" label="划出代理商所属系统" rules={[{ required: true, message: '请选择代理商所属系统' }]}>
            <Select placeholder="请选择">
              {systemTypes.map((item: any) => (
                <Option key={item.item_key} value={item.item_value}>{item.item_name}</Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item name="from_agent_code" label="划出代理商编号" rules={[{ required: true, message: '请输入代理商编号' }]}>
            <Input placeholder="请输入代理商编号" />
          </Form.Item>
          <Form.Item name="from_agent_name" label="划出代理商名称" rules={[{ required: true, message: '请输入代理商名称' }]}>
            <Input placeholder="请输入代理商名称" />
          </Form.Item>
          <Form.Item name="to_system_type" label="划入代理商所属系统" rules={[{ required: true, message: '请选择代理商所属系统' }]}>
            <Select placeholder="请选择">
              {systemTypes.map((item: any) => (
                <Option key={item.item_key} value={item.item_value}>{item.item_name}</Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item name="to_agent_code" label="划入代理商编号" rules={[{ required: true, message: '请输入代理商编号' }]}>
            <Input placeholder="请输入代理商编号" />
          </Form.Item>
          <Form.Item name="to_agent_name" label="划入代理商名称" rules={[{ required: true, message: '请输入代理商名称' }]}>
            <Input placeholder="请输入代理商名称" />
          </Form.Item>
          <Form.Item name="software_name" label="软件名称" rules={[{ required: true, message: '请选择软件名称' }]}>
            <Select placeholder="请选择">
              {softwareList.map((item: any) => (
                <Option key={item.item_key} value={item.item_value}>{item.item_name}</Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item name="quantity" label="划拨数量" rules={[{ required: true, message: '请输入划拨数量' }]}>
            <Input type="number" min={1} placeholder="请输入划拨数量" />
          </Form.Item>
          <Form.Item name="transfer_date" label="划拨日期" rules={[{ required: true, message: '请选择划拨日期' }]}>
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="operator" label="操作人">
            <Input placeholder="请输入操作人" disabled />
          </Form.Item>
          <Form.Item name="remark" label="备注">
            <Input.TextArea placeholder="请输入备注" />
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        title="商户安装软件"
        open={isInstallModalVisible}
        onCancel={() => setIsInstallModalVisible(false)}
        onOk={() => installForm.submit()}
        width={500}
      >
        <Form form={installForm} layout="vertical" onFinish={handleInstallSubmit}>
          <Form.Item name="system_type" label="代理商所属系统" rules={[{ required: true, message: '请选择代理商所属系统' }]}>
            <Select placeholder="请选择">
              {systemTypes.map((item: any) => (
                <Option key={item.item_key} value={item.item_value}>{item.item_name}</Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item name="agent_code" label="代理商编号" rules={[{ required: true, message: '请输入代理商编号' }]}>
            <Input placeholder="请输入代理商编号" />
          </Form.Item>
          <Form.Item name="agent_name" label="代理商名称" rules={[{ required: true, message: '请输入代理商名称' }]}>
            <Input placeholder="请输入代理商名称" />
          </Form.Item>
          <Form.Item name="software_name" label="软件名称" rules={[{ required: true, message: '请选择软件名称' }]}>
            <Select placeholder="请选择">
              {softwareList.map((item: any) => (
                <Option key={item.item_key} value={item.item_value}>{item.item_name}</Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item name="merchant_code" label="商户编号" rules={[{ required: true, message: '请输入商户编号' }]}>
            <Input placeholder="请输入商户编号" />
          </Form.Item>
          <Form.Item name="merchant_name" label="商户名称" rules={[{ required: true, message: '请输入商户名称' }]}>
            <Input placeholder="请输入商户名称" />
          </Form.Item>
          <Form.Item name="quantity" label="安装数量" rules={[{ required: true, message: '请输入安装数量' }]}>
            <Input type="number" min={1} placeholder="请输入安装数量" />
          </Form.Item>
          <Form.Item name="install_date" label="安装日期" rules={[{ required: true, message: '请选择安装日期' }]}>
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="operator" label="操作人">
            <Input placeholder="请输入操作人" disabled />
          </Form.Item>
          <Form.Item name="remark" label="备注">
            <Input.TextArea placeholder="请输入备注" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default InventoryList;
