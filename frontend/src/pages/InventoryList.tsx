import React, { useState, useEffect } from 'react';
import { Table, Form, Input, Select, Button, Space, message, Modal } from 'antd';
import api from '../api';
import dayjs from 'dayjs';

const { Option } = Select;

const InventoryList: React.FC = () => {
  const [form] = Form.useForm();
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [softwareList, setSoftwareList] = useState([]);

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

  const fetchCommonData = async () => {
    try {
      const softRes = await api.get('/common/software');
      setSoftwareList(softRes.data);
    } catch (error) {
      console.error('获取基础数据失败');
    }
  };

  useEffect(() => {
    fetchData();
    fetchCommonData();
  }, []);

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
          <Button type="link" onClick={() => window.location.href = `/logs?${params.toString()}`}>
            库存变动记录
          </Button>
        );
      },
    },
  ];

  return (
    <div>
      <Form form={form} layout="inline" onFinish={fetchData} style={{ marginBottom: 20 }}>
        <Form.Item name="system_type" label="代理商所属系统" initialValue="all">
          <Select style={{ width: 120 }}>
            <Option value="all">请选择</Option>
            <Option value="V3系统">V3系统</Option>
            <Option value="LTB系统">LTB系统</Option>
          </Select>
        </Form.Item>
        <Form.Item name="agent_code" label="代理商编号">
          <Input placeholder="请输入" />
        </Form.Item>
        <Form.Item name="agent_name" label="代理商名称">
          <Input placeholder="请输入" />
        </Form.Item>
        <Form.Item name="software_name" label="软件名称" initialValue="all">
          <Select style={{ width: 120 }}>
            <Option value="all">请选择</Option>
            {softwareList.map((s: any) => (
              <Option key={s.id} value={s.name}>{s.name}</Option>
            ))}
          </Select>
        </Form.Item>
        <Form.Item>
          <Space>
            <Button type="primary" htmlType="submit">查询</Button>
            <Button onClick={() => { form.resetFields(); fetchData(); }}>重置</Button>
            <Button>导出</Button>
          </Space>
        </Form.Item>
      </Form>
      <Table
        columns={columns}
        dataSource={data}
        rowKey="id"
        loading={loading}
        pagination={{ pageSize: 10 }}
      />
    </div>
  );
};

export default InventoryList;
