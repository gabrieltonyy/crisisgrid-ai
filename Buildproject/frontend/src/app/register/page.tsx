'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Form, Input, Button, Card, message, Typography, Select } from 'antd';
import { UserOutlined, LockOutlined, MailOutlined, PhoneOutlined } from '@ant-design/icons';
import Link from 'next/link';
import { useAuth } from '@/hooks/useAuth';

const { Title, Text } = Typography;
const { Option } = Select;
const demoRoleSelectorEnabled = process.env.NEXT_PUBLIC_DEMO_AUTH_ROLES === 'true';

export default function RegisterPage() {
  const router = useRouter();
  const { register } = useAuth();
  const [loading, setLoading] = useState(false);

  const onFinish = async (values: {
    name: string;
    email: string;
    phone_number?: string;
    password: string;
    confirmPassword: string;
    role?: 'CITIZEN' | 'AUTHORITY' | 'ADMIN';
  }) => {
    const payload = {
      name: values.name,
      email: values.email,
      password: values.password,
      phone_number: values.phone_number || undefined,
      role: demoRoleSelectorEnabled ? values.role || 'CITIZEN' : 'CITIZEN',
    };

    setLoading(true);
    const result = await register(payload);
    setLoading(false);

    if (result.success) {
      message.success('Registration successful! Please login.');
      router.replace('/login?registered=1');
    } else {
      message.error(result.error || 'Registration failed');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4 py-8">
      <Card className="w-full max-w-md">
        <div className="text-center mb-8">
          <Title level={2}>Create Account</Title>
          <Text type="secondary">Join CrisisGrid AI</Text>
        </div>

        <Form
          name="register"
          onFinish={onFinish}
          layout="vertical"
          size="large"
          initialValues={{ role: 'CITIZEN' }}
        >
          <Form.Item
            name="name"
            rules={[{ required: true, message: 'Please input your name!' }]}
          >
            <Input
              prefix={<UserOutlined />}
              placeholder="Full Name"
            />
          </Form.Item>

          <Form.Item
            name="email"
            rules={[
              { required: true, message: 'Please input your email!' },
              { type: 'email', message: 'Please enter a valid email!' },
            ]}
          >
            <Input
              prefix={<MailOutlined />}
              placeholder="Email"
              autoComplete="email"
            />
          </Form.Item>

          <Form.Item
            name="phone_number"
          >
            <Input
              prefix={<PhoneOutlined />}
              placeholder="Phone Number (optional)"
            />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[
              { required: true, message: 'Please input your password!' },
              { min: 8, message: 'Password must be at least 8 characters!' },
            ]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="Password (min 8 characters)"
              autoComplete="new-password"
            />
          </Form.Item>

          <Form.Item
            name="confirmPassword"
            dependencies={['password']}
            rules={[
              { required: true, message: 'Please confirm your password!' },
              ({ getFieldValue }) => ({
                validator(_, value) {
                  if (!value || getFieldValue('password') === value) {
                    return Promise.resolve();
                  }
                  return Promise.reject(new Error('Passwords do not match!'));
                },
              }),
            ]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="Confirm Password"
              autoComplete="new-password"
            />
          </Form.Item>

          {demoRoleSelectorEnabled && (
            <Form.Item
              name="role"
              label="Account Type"
            >
              <Select>
                <Option value="CITIZEN">Citizen</Option>
                <Option value="AUTHORITY">Authority</Option>
                <Option value="ADMIN">Admin</Option>
              </Select>
            </Form.Item>
          )}

          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              loading={loading}
              block
            >
              Register
            </Button>
          </Form.Item>

          <div className="text-center">
            <Text type="secondary">
              Already have an account?{' '}
              <Link href="/login" className="text-blue-600 hover:text-blue-800">
                Sign in here
              </Link>
            </Text>
          </div>
        </Form>
      </Card>
    </div>
  );
}

// Made with Bob
