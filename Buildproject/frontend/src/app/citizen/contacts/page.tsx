'use client';

import { Button, Card, Col, Row, Typography } from 'antd';
import {
  AlertOutlined,
  MedicineBoxOutlined,
  PhoneOutlined,
  SafetyOutlined,
  TeamOutlined,
} from '@ant-design/icons';

const { Title, Paragraph, Text } = Typography;

const contacts = [
  {
    label: 'Emergency Services',
    number: '911',
    description: 'Police, fire, and medical emergencies requiring immediate response.',
    icon: <AlertOutlined />,
    tone: 'border-red-200 bg-red-50 text-red-700',
  },
  {
    label: 'Non-Emergency Line',
    number: '311',
    description: 'City services, non-urgent hazards, and public works coordination.',
    icon: <PhoneOutlined />,
    tone: 'border-sky-200 bg-sky-50 text-sky-700',
  },
  {
    label: 'Medical Triage',
    number: '911',
    description: 'Use emergency services for injuries, smoke exposure, or urgent medical needs.',
    icon: <MedicineBoxOutlined />,
    tone: 'border-emerald-200 bg-emerald-50 text-emerald-700',
  },
  {
    label: 'Community Safety Desk',
    number: '311',
    description: 'Shelter information, welfare checks, and public safety coordination.',
    icon: <TeamOutlined />,
    tone: 'border-indigo-200 bg-indigo-50 text-indigo-700',
  },
];

export default function ContactsPage() {
  return (
    <div className="space-y-6">
      <div>
        <div className="page-kicker mb-2">Emergency directory</div>
        <Title level={2} className="!mb-2">
          <SafetyOutlined className="mr-2 text-sky-600" />
          Emergency Contacts
        </Title>
        <Paragraph className="max-w-3xl text-slate-600">
          Keep these numbers available during an incident. CrisisGrid reports supplement emergency response but do not replace direct calls for urgent help.
        </Paragraph>
      </div>

      <Row gutter={[16, 16]}>
        {contacts.map((contact) => (
          <Col xs={24} md={12} key={contact.label}>
            <Card className="h-full">
              <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                <div className="flex gap-4">
                  <div className={`flex h-12 w-12 items-center justify-center rounded-lg border text-2xl ${contact.tone}`}>
                    {contact.icon}
                  </div>
                  <div>
                    <Title level={4} className="!mb-1">{contact.label}</Title>
                    <Text type="secondary">{contact.description}</Text>
                  </div>
                </div>
                <a href={`tel:${contact.number}`}>
                  <Button type={contact.number === '911' ? 'primary' : 'default'} danger={contact.number === '911'} icon={<PhoneOutlined />}>
                    Call {contact.number}
                  </Button>
                </a>
              </div>
            </Card>
          </Col>
        ))}
      </Row>
    </div>
  );
}

// Made with Bob
