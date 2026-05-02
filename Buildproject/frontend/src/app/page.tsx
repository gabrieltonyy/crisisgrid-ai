import Link from 'next/link';
import { Button, Card, Row, Col, Typography } from 'antd';
import { DashboardOutlined, UserOutlined, AlertOutlined, SafetyOutlined } from '@ant-design/icons';

const { Title, Paragraph } = Typography;

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-blue-100 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <Title level={1} className="!text-5xl !mb-4">
            <AlertOutlined className="mr-3" />
            CrisisGrid AI
          </Title>
          <Paragraph className="text-xl text-gray-600">
            AI-Powered Emergency Response Coordination System
          </Paragraph>
          <Paragraph className="text-lg text-gray-500 max-w-3xl mx-auto mt-4">
            Real-time crisis management platform leveraging IBM watsonx.ai for intelligent 
            alert verification, resource dispatch optimization, and citizen safety coordination.
          </Paragraph>
        </div>

        {/* Feature Cards */}
        <Row gutter={[24, 24]} className="mb-12">
          <Col xs={24} md={8}>
            <Card
              hoverable
              className="h-full"
              cover={
                <div className="bg-blue-500 h-32 flex items-center justify-center">
                  <AlertOutlined className="text-6xl text-white" />
                </div>
              }
            >
              <Card.Meta
                title="Real-Time Alert Processing"
                description="AI-powered verification and clustering of emergency reports from multiple sources"
              />
            </Card>
          </Col>
          <Col xs={24} md={8}>
            <Card
              hoverable
              className="h-full"
              cover={
                <div className="bg-green-500 h-32 flex items-center justify-center">
                  <SafetyOutlined className="text-6xl text-white" />
                </div>
              }
            >
              <Card.Meta
                title="Smart Resource Dispatch"
                description="Optimized emergency response coordination with geo-risk analysis and routing"
              />
            </Card>
          </Col>
          <Col xs={24} md={8}>
            <Card
              hoverable
              className="h-full"
              cover={
                <div className="bg-purple-500 h-32 flex items-center justify-center">
                  <UserOutlined className="text-6xl text-white" />
                </div>
              }
            >
              <Card.Meta
                title="Citizen Engagement"
                description="Public reporting portal with real-time safety advisories and incident updates"
              />
            </Card>
          </Col>
        </Row>

        {/* Portal Access Cards */}
        <Row gutter={[24, 24]} className="mt-8">
          <Col xs={24} md={12}>
            <Card
              className="text-center h-full"
              style={{ borderColor: '#0ea5e9', borderWidth: 2 }}
            >
              <DashboardOutlined className="text-6xl text-blue-500 mb-4" />
              <Title level={3}>Admin Dashboard</Title>
              <Paragraph className="mb-6">
                Access the command center for emergency response coordination, 
                alert management, and resource dispatch.
              </Paragraph>
              <Link href="/admin">
                <Button type="primary" size="large" icon={<DashboardOutlined />}>
                  Enter Admin Portal
                </Button>
              </Link>
            </Card>
          </Col>
          <Col xs={24} md={12}>
            <Card
              className="text-center h-full"
              style={{ borderColor: '#22c55e', borderWidth: 2 }}
            >
              <UserOutlined className="text-6xl text-green-500 mb-4" />
              <Title level={3}>Citizen Portal</Title>
              <Paragraph className="mb-6">
                Report emergencies, view safety advisories, and stay informed 
                about incidents in your area.
              </Paragraph>
              <Link href="/citizen">
                <Button type="primary" size="large" icon={<UserOutlined />} style={{ backgroundColor: '#22c55e' }}>
                  Enter Citizen Portal
                </Button>
              </Link>
            </Card>
          </Col>
        </Row>

        {/* Footer */}
        <div className="text-center mt-12 text-gray-500">
          <Paragraph>
            Powered by IBM watsonx.ai, IBM Cloudant, and IBM Granite Models
          </Paragraph>
          <Paragraph className="text-sm">
            Built for the IBM Call for Code 2024 Hackathon
          </Paragraph>
        </div>
      </div>
    </main>
  );
}

// Made with Bob
