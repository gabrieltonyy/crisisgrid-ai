'use client';

import Link from 'next/link';
import { Alert, Button, Card, Col, Row, Space, Typography } from 'antd';
import {
  AlertOutlined,
  EnvironmentOutlined,
  FileTextOutlined,
  PhoneOutlined,
  SafetyOutlined,
  WarningOutlined,
} from '@ant-design/icons';

const { Title, Paragraph, Text } = Typography;

const portalCards = [
  {
    title: 'Report Emergency',
    description: 'Submit a report with location, description, and optional media for AI verification.',
    href: '/citizen/report',
    icon: <AlertOutlined />,
    tone: 'text-red-600 bg-red-50 border-red-100',
  },
  {
    title: 'Nearby Alerts',
    description: 'View active public warnings on the map and filter by severity or crisis type.',
    href: '/citizen/alerts',
    icon: <EnvironmentOutlined />,
    tone: 'text-sky-700 bg-sky-50 border-sky-100',
  },
  {
    title: 'Safety Advisories',
    description: 'Get crisis-specific guidance and immediate safety actions from the advisory agent.',
    href: '/citizen/advisory',
    icon: <SafetyOutlined />,
    tone: 'text-emerald-700 bg-emerald-50 border-emerald-100',
  },
  {
    title: 'My Reports',
    description: 'Track verification status, confidence, and response activity for submitted reports.',
    href: '/citizen/reports',
    icon: <FileTextOutlined />,
    tone: 'text-indigo-700 bg-indigo-50 border-indigo-100',
  },
];

export default function CitizenPortal() {
  return (
    <div className="space-y-8">
      <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm md:p-8">
        <div className="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
          <div className="max-w-3xl">
            <div className="page-kicker mb-2">Citizen safety portal</div>
            <Title level={1} className="!mb-3 !text-4xl">
              Crisis reporting and local safety intelligence
            </Title>
            <Paragraph className="!mb-0 text-base text-slate-600">
              Send verified field reports, monitor active alerts, and access clear safety guidance during fast-moving incidents.
            </Paragraph>
          </div>
          <Space wrap>
            <Link href="/citizen/report">
              <Button type="primary" size="large" icon={<WarningOutlined />}>
                Report Crisis
              </Button>
            </Link>
            <a href="tel:911">
              <Button danger size="large" icon={<PhoneOutlined />}>
                Call 911
              </Button>
            </a>
          </Space>
        </div>
      </section>

      <Alert
        type="warning"
        showIcon
        icon={<WarningOutlined />}
        message="For life-threatening emergencies, call 911 immediately."
        description="Use CrisisGrid AI to share situational details when it is safe, and follow all official instructions from local authorities."
      />

      <Row gutter={[16, 16]}>
        {portalCards.map((card) => (
          <Col xs={24} md={12} xl={6} key={card.href}>
            <Link href={card.href}>
              <Card hoverable className="h-full border border-slate-200">
                <div className="space-y-4">
                  <div className={`flex h-12 w-12 items-center justify-center rounded-lg border text-2xl ${card.tone}`}>
                    {card.icon}
                  </div>
                  <div>
                    <Title level={4} className="!mb-2">{card.title}</Title>
                    <Text type="secondary">{card.description}</Text>
                  </div>
                </div>
              </Card>
            </Link>
          </Col>
        ))}
      </Row>
    </div>
  );
}

// Made with Bob
