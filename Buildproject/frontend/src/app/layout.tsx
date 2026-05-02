import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import { AntdRegistry } from '@ant-design/nextjs-registry';
import { ConfigProvider } from 'antd';
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
                colorSuccess: '#22c55e',
                borderRadius: 8,
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
