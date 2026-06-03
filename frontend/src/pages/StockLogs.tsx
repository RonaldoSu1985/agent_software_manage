import React, { useState, useEffect } from 'react';
import { Table, Form, Input, Select, Button, Space, message, Tag, DatePicker } from 'antd';
import { DownloadOutlined } from '@ant-design/icons';
import api from '../api';
import dayjs from 'dayjs';

const { Option } = Select;
const { RangePicker } = DatePicker;

const StockLogs: React.FC = () => {
  const [form] = Form.useForm();
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [systemTypes, setSystemTypes] = useState([]);
  const [softwareList, setSoftwareList] = useState([]);

  const changeTypeOptions = [
    { value: '', label: '请选择' },
    { value: 'purchase', label: '采购' },
    { value: 'transfer', label: '划拨' },
    { value: 'installation', label: '商户安装' },
  ];

  const fetchData = async (values: any = {}) => {
    setLoading(true);
    try {
      const params: any = {};
      
      if (values.system_type) params.system_type = values.system_type;
      if (values.agent_code) params.agent_code = values.agent_code;
      if (values.agent_name) params.agent_name = values.agent_name;
      if (values.software_name) params.software_name = values.software_name;
      if (values.change_type) {
        if (values.change_type === 'transfer') {
          params.change_type = 'transfer';
        } else {
          params.change_type = values.change_type;
        }
      }
      if (values.date_range && values.date_range.length === 2) {
        params.start_date = values.date_range[0].format('YYYY-MM-DD');
        params.end_date = values.date_range[1].format('YYYY-MM-DD');
      }

      const response = await api.get('/inventory/logs', { params });
      setData(response.data);
    } catch (error) {
      message.error('获取变动记录失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // 从数据字典获取基础数据
    const fetchCommonData = async () => {
      try {
        const [systemRes, softRes] = await Promise.all([
          api.get('/dictionary/items/by-type/SYSTEM_TYPE'),
          api.get('/dictionary/items/by-type/SOFTWARE_NAME')
        ]);
        setSystemTypes(systemRes.data || []);
        setSoftwareList(softRes.data || []);
      } catch (error) {
        console.error('获取基础数据失败');
      }
    };
    
    fetchCommonData();
    
    // 从URL参数中获取查询条件
    const searchParams = new URLSearchParams(window.location.search);
    const initialValues: any = {};
    
    const systemType = searchParams.get('system_type');
    const agentCode = searchParams.get('agent_code');
    const agentName = searchParams.get('agent_name');
    const softwareName = searchParams.get('software_name');
    
    if (systemType) initialValues.system_type = systemType;
    if (agentCode) initialValues.agent_code = agentCode;
    if (agentName) initialValues.agent_name = agentName;
    if (softwareName) initialValues.software_name = softwareName;
    
    // 设置表单初始值
    if (Object.keys(initialValues).length > 0) {
      form.setFieldsValue(initialValues);
    }
    
    // 使用初始条件查询数据
    fetchData(initialValues);
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
      if (values.change_type) {
        if (values.change_type === 'transfer') {
          params.change_type = 'transfer';
        } else {
          params.change_type = values.change_type;
        }
      }
      if (values.date_range && values.date_range.length === 2) {
        params.start_date = values.date_range[0].format('YYYY-MM-DD');
        params.end_date = values.date_range[1].format('YYYY-MM-DD');
      }
      
      const queryParams = new URLSearchParams();
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          queryParams.append(key, value);
        }
      });
      
      const token = localStorage.getItem('token');
      const url = `http://localhost:8000/api/v1/inventory/logs/export/all?${queryParams.toString()}`;
      
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
      link.download = `库存变动记录_${dayjs().format('YYYYMMDDHHmmss')}.csv`;
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
    { 
      title: '变动类型', 
      dataIndex: 'change_type', 
      key: 'change_type',
      width: 100,
      render: (type: string) => {
        const types: any = {
          purchase: <Tag color="green">采购</Tag>,
          installation: <Tag color="blue">商户安装</Tag>,
          transfer_in: <Tag color="orange">划拨(划入)</Tag>,
          transfer_out: <Tag color="volcano">划拨(划出)</Tag>
        };
        return types[type] || type;
      }
    },
    { 
      title: '代理商', 
      key: 'agent_info',
      width: 200,
      render: (_, record: any) => (
        <div>
          <div><strong>{record.agent?.agent_code}</strong></div>
          <div style={{ fontSize: 12, color: '#666' }}>{record.agent?.agent_name}</div>
          <div style={{ fontSize: 12, color: '#999' }}>{record.agent?.system_type}</div>
        </div>
      )
    },
    { title: '软件', dataIndex: ['software', 'name'], key: 'software_name', width: 100 },
    { 
      title: '库存变动', 
      key: 'qty_change',
      width: 180,
      align: 'center',
      render: (_, record: any) => (
        <div style={{ textAlign: 'center' }}>
          <div style={{ color: '#999', fontSize: 12 }}>{record.before_qty}</div>
          <div style={{ fontSize: 16, fontWeight: 'bold', color: record.change_qty > 0 ? '#52c41a' : '#f5222d' }}>
            {record.change_qty > 0 ? '+' : ''}{record.change_qty}
          </div>
          <div style={{ color: '#52c41a', fontSize: 12 }}>{record.after_qty}</div>
        </div>
      )
    },
    { 
      title: '关联方', 
      key: 'related',
      width: 150,
      render: (_, record: any) => {
        if (record.change_type === 'purchase') {
          return <span style={{ color: '#999' }}>采购入库</span>;
        } else if (record.change_type === 'installation') {
          return (
            <div>
              <div><strong>{record.merchant_code}</strong></div>
              <div style={{ fontSize: 12, color: '#666' }}>{record.merchant_name}</div>
            </div>
          );
        } else {
          return (
            <div>
              <div><strong>{record.related_agent_code}</strong></div>
              <div style={{ fontSize: 12, color: '#666' }}>{record.related_agent_name}</div>
              <div style={{ fontSize: 12, color: '#999' }}>{record.related_system_type}</div>
            </div>
          );
        }
      }
    },
    { title: '变动时间', dataIndex: 'created_at', key: 'created_at', width: 160, render: (val: string) => dayjs(val).format('YYYY-MM-DD HH:mm') },
    { title: '操作人', dataIndex: 'operator_id', key: 'operator_id', width: 80 },
  ];

  return (
    <div>
      <div style={{ 
        background: '#fff', 
        padding: 16, 
        borderRadius: 8, 
        marginBottom: 16,
        boxShadow: '0 2px 8px rgba(0,0,0,0.06)'
      }}>
        <Form form={form} layout="inline" onFinish={handleSearch} style={{ flexWrap: 'wrap', gap: '16px' }}>
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
          <Form.Item name="change_type" label="变动类型">
            <Select style={{ width: 150 }}>
              {changeTypeOptions.map((opt) => (
                <Option key={opt.value} value={opt.value}>{opt.label}</Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item name="date_range" label="变动日期区间">
            <RangePicker style={{ width: 250 }} />
          </Form.Item>
          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">查询</Button>
              <Button onClick={handleReset}>重置</Button>
              <Button icon={<DownloadOutlined />} htmlType="button" onClick={handleExport}>导出</Button>
            </Space>
          </Form.Item>
        </Form>
      </div>
      <Table 
        columns={columns} 
        dataSource={data} 
        rowKey="id" 
        loading={loading}
        bordered={false}
        style={{ background: '#fff', borderRadius: 8, boxShadow: '0 2px 8px rgba(0,0,0,0.06)' }}
        pagination={{
          showSizeChanger: true,
          showTotal: (total) => `共 ${total} 条记录`,
          pageSizeOptions: ['10', '20', '50', '100']
        }}
      />
    </div>
  );
};

export default StockLogs;