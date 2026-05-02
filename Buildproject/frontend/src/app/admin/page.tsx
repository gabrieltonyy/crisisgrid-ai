import { Typography } from 'antd';

const { Title, Paragraph } = Typography;

export default function AdminDashboard() {
  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <Title level={2}>Admin Dashboard</Title>
        <Paragraph>
          Emergency response command center - Coming soon in Phase 8 implementation
        </Paragraph>
        
        <div className="mt-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className="bg-white p-6 rounded-lg shadow">
            <Title level={4}>Active Alerts</Title>
            <Paragraph>Real-time alert monitoring and verification</Paragraph>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow">
            <Title level={4}>Resource Dispatch</Title>
            <Paragraph>Emergency response coordination and routing</Paragraph>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow">
            <Title level={4}>Incident Map</Title>
            <Paragraph>Geographic visualization of active incidents</Paragraph>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow">
            <Title level={4}>Analytics</Title>
            <Paragraph>Response metrics and performance tracking</Paragraph>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow">
            <Title level={4}>Advisory System</Title>
            <Paragraph>Public safety advisory management</Paragraph>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow">
            <Title level={4}>Reports</Title>
            <Paragraph>Citizen report verification queue</Paragraph>
          </div>
        </div>
      </div>
    </div>
  );
}

// Made with Bob
