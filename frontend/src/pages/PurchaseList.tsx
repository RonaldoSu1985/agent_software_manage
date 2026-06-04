import React, { useState, useEffect } from 'react';
import { Table, Form, Input, Select, Button, Space, message, Modal, DatePicker } from 'antd';
import { DownloadOutlined } from '@ant-design/icons';
import api from '../api';
import dayjs from 'dayjs';

const { Option } = Select;
const { RangePicker } = DatePicker;

const PurchaseList: React.FC = () => {
  const [form] = Form.useForm();
  const [addForm] = Form.useForm();
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [softwareList, setSoftwareList] = useState([]);
  const [agentList, setAgentList] = useState([]);
  const [currentUser, setCurrentUser] = useState('');
  const [systemTypes, setSystemTypes] = useState([]);

  const fetchData = async (values: any = {}) => {
    setLoading(true);
    try {
      const params: any = { change_type: 'purchase' };
      
      if (values.system_type) params.system_type = values.system_type;
      if (values.agent_code) params.agent_code = values.agent_code;
      if (values.agent_name) params.agent_name = values.agent_name;
      if (values.software_name) params.software_name = values.software_name;
      if (values.date_range && values.date_range.length === 2) {
        params.start_date = values.date_range[0].format('YYYY-MM-DD');
        params.end_date = values.date_range[1].format('YYYY-MM-DD');
      }
      if (values.operator) params.operator = values.operator;

      const response = await api.get('/inventory/logs', { params });
      setData(response.data);
    } catch (error) {
      message.error('获取采购记录失败');
    } finally {
      setLoading(false);
    }
  };

  const fetchCommonData = async () => {
    try {
      const [softRes, agentRes, systemRes] = await Promise.all([
        api.get('/dictionary/items/by-type/SOFTWARE_NAME'),
        api.get('/common/agents'),
        api.get('/dictionary/items/by-type/SYSTEM_TYPE')
      ]);
      setSoftwareList(softRes.data || []);
      setAgentList(agentRes.data);
      setSystemTypes(systemRes.data || []);
    } catch (error) {
      console.error('获取基础数据失败');
    }
  };

  useEffect(() => {
    fetchData();
    fetchCommonData();
    
    const token = localStorage.getItem('token');
    if (token) {
      try {
        const payload = token.split('.')[1];
        const decoded = JSON.parse(atob(payload));
        setCurrentUser(decoded.sub || 'admin');
      } catch {
        setCurrentUser('admin');
      }
    }
  }, []);

  const handleSearch = (values: any) => {
    fetchData(values);
  };

  const handleReset = () => {
    form.resetFields();
    fetchData();
  };

  const handleExport = async () => {
    try {
      const values = form.getFieldsValue();
      const params: any = {};
      
      if (values.system_type) params.system_type = values.system_type;
      if (values.agent_code) params.agent_code = values.agent_code;
      if (values.agent_name) params.agent_name = values.agent_name;
      if (values.software_name) params.software_name = values.software_name;
      if (values.date_range && values.date_range.length === 2) {
        params.start_date = values.date_range[0].format('YYYY-MM-DD');
        params.end_date = values.date_range[1].format('YYYY-MM-DD');
      }
      if (values.operator) params.operator = values.operator;
      
      const queryParams = new URLSearchParams();
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          queryParams.append(key, value);
        }
      });
      
      const token = localStorage.getItem('token');
      const url = `/api/v1/inventory/logs/export/purchase?${queryParams.toString()}`;
      
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
      link.download = `采购记录_${dayjs().format('YYYYMMDDHHmmss')}.csv`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(downloadUrl);
      
      message.success('导出成功');
    } catch (error) {
      message.error('导出失败');
    }
  };

  const handleAdd = async (values: any) => {
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
      setIsModalVisible(false);
      addForm.resetFields();
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
    { title: '采购数量', dataIndex: 'change_qty', key: 'quantity' },
    { title: '备注', dataIndex: 'remark', key: 'remark' },
    { title: '采购日期', dataIndex: 'created_at', key: 'date', render: (val: string) => dayjs(val).format('YYYY-MM-DD') },
    { title: '操作人', dataIndex: 'operator_id', key: 'operator' },
  ];

  const handleShowModal = () => {
    addForm.setFieldsValue({
      purchase_date: dayjs(),
      operator: currentUser,
    });
    setIsModalVisible(true);
  };

  return (
    <div>
      <Form form={form} layout="inline" onFinish={handleSearch} style={{ marginBottom: 16 }}>
        <Form.Item name="system_type" label="代理商所属系统">
          <Select style={{ width: 150 }}>
            <Option value="">请选择</Option>
            {systemTypes.map((item: any) => (
              <Option key={item.item_key} value={item.item_value}>{item.item_name}</Option>
            ))}
          </Select>
        </Form.Item>
        <Form.Item name="agent_code" label="代理商编号">
          <Input style={{ width: 150 }} placeholder="请输入代理商编号" />
        </Form.Item>
        <Form.Item name="agent_name" label="代理商名称">
          <Input style={{ width: 150 }} placeholder="请输入代理商名称" />
        </Form.Item>
        <Form.Item name="software_name" label="软件名称">
          <Select style={{ width: 150 }}>
            <Option value="">请选择</Option>
            {softwareList.map((item: any) => (
              <Option key={item.item_key} value={item.item_value}>{item.item_name}</Option>
            ))}
          </Select>
        </Form.Item>
        <Form.Item name="date_range" label="采购日期区间">
          <RangePicker style={{ width: 250 }} />
        </Form.Item>
        <Form.Item name="operator" label="操作人">
          <Input style={{ width: 120 }} placeholder="请输入操作人" />
        </Form.Item>
        <Form.Item>
          <Space>
            <Button type="primary" htmlType="submit">查询</Button>
            <Button onClick={handleReset}>重置</Button>
            <Button icon={<DownloadOutlined />} htmlType="button" onClick={handleExport}>导出</Button>
            <Button type="primary" onClick={handleShowModal}>新增采购</Button>
          </Space>
        </Form.Item>
      </Form>

      <Table columns={columns} dataSource={data} rowKey="id" loading={loading} />

      <Modal
        title="代理商新增采购软件"
        open={isModalVisible}
        onCancel={() => setIsModalVisible(false)}
        onOk={() => addForm.submit()}
        width={500}
      >
        <Form form={addForm} layout="vertical" onFinish={handleAdd}>
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
          <Form.Item name="operator" label="操作人" rules={[{ required: true, message: '请输入操作人' }]}>
            <Input placeholder="请输入操作人" />
          </Form.Item>
          <Form.Item name="remark" label="备注">
            <Input.TextArea placeholder="请输入备注" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default PurchaseList;
