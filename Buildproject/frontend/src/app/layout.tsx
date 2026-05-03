import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import { AntdRegistry } from '@ant-design/nextjs-registry';
import { ConfigProvider } from 'antd';
import 'antd/dist/reset.css';
import './globals.css';
import { Providers } from './providers';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'CrisisGrid AI - Emergency Response Platform',
  description: 'AI-powered emergency response coordination system for real-time crisis management',
  keywords: ['emergency', 'crisis management', 'AI', 'disaster response', 'public safety'],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <AntdRegistry>
          <ConfigProvider
            theme={{
              token: {
                colorPrimary: '#0ea5e9',
                colorError: '#ef4444',
                colorWarning: '#f59e0b',
                colorSuccess: '#16a34a',
                colorInfo: '#0ea5e9',
                colorText: '#111827',
                colorTextSecondary: '#64748b',
                colorBgLayout: '#eef3f7',
                colorBorder: '#dbe4ef',
                borderRadius: 8,
                fontSize: 14,
              },
              components: {
                Button: {
                  controlHeight: 38,
                  fontWeight: 600,
                },
                Card: {
                  headerFontSize: 16,
                },
                Table: {
                  headerBg: '#f8fafc',
                  rowHoverBg: '#f0f9ff',
                },
              },
            }}
          >
            <Providers>
              {children}
            </Providers>
          </ConfigProvider>
        </AntdRegistry>
      </body>
    </html>
  );
}

// Made with Bob
