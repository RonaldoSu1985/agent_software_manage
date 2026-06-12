import React, { useState, useEffect } from 'react';
import { Card, Button, Input, message, Typography, Space, Divider } from 'antd';
import { CopyOutlined, ReloadOutlined, RobotOutlined } from '@ant-design/icons';
import api from '../api';

const { Title, Paragraph, Text } = Typography;

const MCPSettings: React.FC = () => {
  const [mcpKey, setMcpKey] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    fetchMcpKey();
  }, []);

  const fetchMcpKey = async () => {
    try {
      const response = await api.get('/auth/mcp-key');
      setMcpKey(response.data.mcp_key || '');
    } catch (error) {
      message.error('获取 MCP Key 失败');
    }
  };

  const handleGenerateKey = async () => {
    setLoading(true);
    try {
      const response = await api.post('/auth/mcp-key');
      setMcpKey(response.data.mcp_key);
      message.success('MCP Key 已更新');
    } catch (error) {
      message.error('生成 MCP Key 失败');
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text: string, label: string) => {
    navigator.clipboard.writeText(text);
    message.success(`${label} 已复制到剪贴板`);
  };

  const sseUrl = `${window.location.protocol}//${window.location.host}/api/v1/mcp/sse?key=${mcpKey}`;

  return (
    <div style={{ maxWidth: 800, margin: '0 auto' }}>
      <Title level={2}>
        <RobotOutlined style={{ marginRight: 8 }} />
        AI 助手设置
      </Title>
      <Paragraph>
        Model Context Protocol (MCP) 允许您将此系统连接到 AI 助手（如 Claude Desktop, Cursor 等），使 AI 能够直接查询库存和记录业务操作。
      </Paragraph>

      <Card title="您的 MCP 配置" bordered={false} style={{ marginBottom: 24 }}>
        <Space direction="vertical" size="middle" style={{ width: '100%' }}>
          <div>
            <Text strong>个人 MCP Key</Text>
            <div style={{ display: 'flex', marginTop: 8 }}>
              <Input.Password
                value={mcpKey}
                readOnly
                placeholder="尚未生成 Key"
                style={{ marginRight: 8 }}
              />
              <Button 
                icon={<CopyOutlined />} 
                disabled={!mcpKey}
                onClick={() => copyToClipboard(mcpKey, 'Key')}
              >
                复制
              </Button>
              <Button 
                type="primary" 
                danger 
                icon={<ReloadOutlined />} 
                loading={loading}
                onClick={handleGenerateKey}
                style={{ marginLeft: 8 }}
              >
                {mcpKey ? '重新生成' : '生成 Key'}
              </Button>
            </div>
            <Text type="secondary" style={{ fontSize: '12px', display: 'block', marginTop: 4 }}>
              注意：重新生成 Key 将导致旧的 AI 助手连接失效。
            </Text>
          </div>

          <Divider />

          <div>
            <Text strong>SSE 连接 URL</Text>
            <div style={{ display: 'flex', marginTop: 8 }}>
              <Input
                value={mcpKey ? sseUrl : '生成 Key 后显示'}
                readOnly
                style={{ marginRight: 8 }}
              />
              <Button 
                icon={<CopyOutlined />} 
                disabled={!mcpKey}
                onClick={() => copyToClipboard(sseUrl, 'URL')}
              >
                复制
              </Button>
            </div>
            <Text type="secondary" style={{ fontSize: '12px', display: 'block', marginTop: 4 }}>
              在 AI 助手的 MCP 设置中使用此 URL。
            </Text>
          </div>
        </Space>
      </Card>

      <Card title="快速开始建议" bordered={false}>
        <Title level={4}>在 Claude Desktop 中使用</Title>
        <Paragraph>
          编辑您的 <Text code>claude_desktop_config.json</Text> 文件，添加以下内容：
        </Paragraph>
        <pre style={{ background: '#f5f5f5', padding: 16, borderRadius: 4, overflow: 'auto' }}>
{`{
  "mcpServers": {
    "softmanage": {
      "url": "${mcpKey ? sseUrl : 'YOUR_SSE_URL'}",
      "transport": "sse"
    }
  }
}`}
        </pre>

        <Divider />

        <Title level={4}>在 WorkBuddy 中使用</Title>
        <Paragraph>
          WorkBuddy 支持通过 MCP 协议连接到本系统，使 AI 能够直接查询库存和记录业务操作。
        </Paragraph>
        <Paragraph>
          <Text strong>配置步骤：</Text>
        </Paragraph>
        <ol style={{ marginLeft: 20, marginTop: 8 }}>
          <li>在 WorkBuddy 中点击右上角的「配置 MCP」按钮</li>
          <li>在 MCP 服务管理页面编辑配置文件</li>
          <li>在 <Text code>mcpServers</Text> 对象中添加以下配置</li>
        </ol>
        <Paragraph style={{ marginTop: 12 }}>
          在配置文件中添加 softmanage 服务器：
        </Paragraph>
        <pre style={{ background: '#f5f5f5', padding: 16, borderRadius: 4, overflow: 'auto' }}>
{`{
  "mcpServers": {
    "softmanage": {
      "type": "sse",
      "url": "${mcpKey ? sseUrl : 'YOUR_SSE_URL'}",
      "disabled": false
    }
  }
}`}
        </pre>
        <Paragraph style={{ marginTop: 12 }}>
          配置完成后点击「保存」按钮，您就可以在 WorkBuddy 中通过 AI 助手查询库存、记录采购、安装和划拨等业务操作了。
        </Paragraph>
      </Card>
    </div>
  );
};

export default MCPSettings;
