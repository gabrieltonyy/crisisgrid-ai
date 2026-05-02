import { Typography } from 'antd';

const { Title, Paragraph } = Typography;

export default function CitizenPortal() {
  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <Title level={2}>Citizen Portal</Title>
        <Paragraph>
          Public safety and emergency reporting - Coming soon in Phase 9 implementation
        </Paragraph>
        
        <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white p-6 rounded-lg shadow">
            <Title level={4}>Report Emergency</Title>
            <Paragraph>Submit emergency reports with location and media</Paragraph>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow">
            <Title level={4}>Safety Advisories</Title>
            <Paragraph>View active safety alerts in your area</Paragraph>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow">
            <Title level={4}>Incident Map</Title>
            <Paragraph>See nearby incidents and emergency zones</Paragraph>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow">
            <Title level={4}>My Reports</Title>
            <Paragraph>Track status of your submitted reports</Paragraph>
          </div>
        </div>
      </div>
    </div>
  );
}

// Made with Bob
