import React, { useState, useEffect } from 'react';
import { Table, Form, Input, Select, Button, Space, message, Modal, DatePicker } from 'antd';
import { DownloadOutlined } from '@ant-design/icons';
import api from '../api';
import dayjs from 'dayjs';

const { Option } = Select;
const { RangePicker } = DatePicker;

const TransferList: React.FC = () => {
  const [form] = Form.useForm();
  const [addForm] = Form.useForm();
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [softwareList, setSoftwareList] = useState([]);
  const [currentUser, setCurrentUser] = useState('');
  const [systemTypes, setSystemTypes] = useState([]);

  const fetchData = async (values: any = {}) => {
    setLoading(true);
    try {
      const params: any = { change_type: 'transfer_out' };
      
      if (values.from_system_type) params.from_system_type = values.from_system_type;
      if (values.from_agent_code) params.from_agent_code = values.from_agent_code;
      if (values.from_agent_name) params.from_agent_name = values.from_agent_name;
      if (values.to_system_type) params.to_system_type = values.to_system_type;
      if (values.to_agent_code) params.to_agent_code = values.to_agent_code;
      if (values.to_agent_name) params.to_agent_name = values.to_agent_name;
      if (values.software_name) params.software_name = values.software_name;
      if (values.date_range && values.date_range.length === 2) {
        params.start_date = values.date_range[0].format('YYYY-MM-DD');
        params.end_date = values.date_range[1].format('YYYY-MM-DD');
      }
      if (values.operator) params.operator = values.operator;

      const response = await api.get('/inventory/logs', { params });
      setData(response.data);
    } catch (error) {
      message.error('获取划拨记录失败');
    } finally {
      setLoading(false);
    }
  };

  const fetchCommonData = async () => {
    try {
      const [softRes, systemRes] = await Promise.all([
        api.get('/dictionary/items/by-type/SOFTWARE_NAME'),
        api.get('/dictionary/items/by-type/SYSTEM_TYPE')
      ]);
      setSoftwareList(softRes.data || []);
      setSystemTypes(systemRes.data || []);
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
    
    // 检测URL参数，自动打开新增弹窗
    const params = new URLSearchParams(window.location.search);
    if (params.get('add') === 'true') {
      handleShowModal();
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
      
      if (values.from_system_type) params.from_system_type = values.from_system_type;
      if (values.from_agent_code) params.from_agent_code = values.from_agent_code;
      if (values.from_agent_name) params.from_agent_name = values.from_agent_name;
      if (values.to_system_type) params.to_system_type = values.to_system_type;
      if (values.to_agent_code) params.to_agent_code = values.to_agent_code;
      if (values.to_agent_name) params.to_agent_name = values.to_agent_name;
      if (values.software_name) params.software_name = values.software_name;
      if (values.date_range && values.date_range.length === 2) {
        params.start_date = values.date_range[0].format('YYYY-MM-DD');
        params.end_date = values.date_range[1].format('YYYY-MM-DD');
      }
      if (values.operator) params.operator = values.operator;
      
      const queryParams = new URLSearchParams();
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          queryParams.append(key, String(value));
        }
      });
      
      const token = localStorage.getItem('token');
      const url = `/api/v1/inventory/logs/export/transfer?${queryParams.toString()}`;
      
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
      link.download = `划拨记录_${dayjs().format('YYYYMMDDHHmmss')}.csv`;
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
      setIsModalVisible(false);
      addForm.resetFields();
      fetchData();
    } catch (error: any) {
      message.error(error.response?.data?.detail || '操作失败');
    }
  };

  const columns = [
    { title: '划出代理商所属系统', dataIndex: ['agent', 'system_type'], key: 'from_system_type' },
    { title: '划出代理商编号', dataIndex: ['agent', 'agent_code'], key: 'from_agent_code' },
    { title: '划出代理商名称', dataIndex: ['agent', 'agent_name'], key: 'from_agent_name' },
    { title: '软件名称', dataIndex: ['software', 'name'], key: 'software_name' },
    { title: '划拨数量', dataIndex: 'change_qty', key: 'quantity', render: (val: number) => Math.abs(val) },
    { title: '划入代理商所属系统', dataIndex: 'related_system_type', key: 'to_system_type' },
    { title: '划入代理商编号', dataIndex: 'related_agent_code', key: 'to_agent_code' },
    { title: '划入代理商名称', dataIndex: 'related_agent_name', key: 'to_agent_name' },
    { title: '划拨日期', dataIndex: 'created_at', key: 'date', render: (val: string) => dayjs(val).format('YYYY-MM-DD') },
    { title: '备注', dataIndex: 'remark', key: 'remark' },
    { title: '操作人', dataIndex: 'operator_id', key: 'operator' },
  ];

  const handleShowModal = () => {
    // 每次打开弹窗时重新从localStorage获取最新的用户名
    const username = getUsername();
    addForm.setFieldsValue({
      transfer_date: dayjs(),
      operator: username,
    });
    setIsModalVisible(true);
  };

  return (
    <div>
      <Form form={form} layout="inline" onFinish={handleSearch} style={{ marginBottom: 16 }}>
        <Form.Item name="from_system_type" label="划出代理商所属系统">
          <Select style={{ width: 150 }}>
            <Option value="">请选择</Option>
            {systemTypes.map((item: any) => (
              <Option key={item.item_key} value={item.item_value}>{item.item_name}</Option>
            ))}
          </Select>
        </Form.Item>
        <Form.Item name="from_agent_code" label="划出代理商编号">
          <Input style={{ width: 150 }} placeholder="请输入代理商编号" />
        </Form.Item>
        <Form.Item name="from_agent_name" label="划出代理商名称">
          <Input style={{ width: 150 }} placeholder="请输入代理商名称" />
        </Form.Item>
        <Form.Item name="to_system_type" label="划入代理商所属系统">
          <Select style={{ width: 150 }}>
            <Option value="">请选择</Option>
            {systemTypes.map((item: any) => (
              <Option key={item.item_key} value={item.item_value}>{item.item_name}</Option>
            ))}
          </Select>
        </Form.Item>
        <Form.Item name="to_agent_code" label="划入代理商编号">
          <Input style={{ width: 150 }} placeholder="请输入代理商编号" />
        </Form.Item>
        <Form.Item name="to_agent_name" label="划入代理商名称">
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
        <Form.Item name="date_range" label="划拨日期区间">
          <RangePicker style={{ width: 250 }} />
        </Form.Item>
        <Form.Item name="operator" label="操作人">
          <Input style={{ width: 120 }} placeholder="请输入操作人" />
        </Form.Item>
      </Form>
      <div style={{ marginBottom: 20 }}>
        <Space>
          <Button type="primary" onClick={() => form.submit()}>查询</Button>
          <Button onClick={handleReset}>重置</Button>
          <Button icon={<DownloadOutlined />} htmlType="button" onClick={handleExport}>导出</Button>
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
        title="代理商之间软件库存划拨"
        open={isModalVisible}
        onCancel={() => setIsModalVisible(false)}
        onOk={() => addForm.submit()}
        width={600}
      >
        <Form form={addForm} layout="vertical" onFinish={handleAdd}>
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
    </div>
  );
};

export default TransferList;