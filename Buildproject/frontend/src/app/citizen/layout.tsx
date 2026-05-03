'use client';

import React, { useState } from 'react';
import { Layout, Menu, Button, Breadcrumb, Drawer } from 'antd';
import { 
  HomeOutlined, 
  AlertOutlined, 
  FileTextOutlined, 
  SafetyOutlined, 
  EnvironmentOutlined, 
  PhoneOutlined,
  MenuOutlined
} from '@ant-design/icons';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import type { MenuProps } from 'antd';

const { Header, Content, Footer } = Layout;

type MenuItem = Required<MenuProps>['items'][number];

const menuItems: MenuItem[] = [
  {
    key: '/citizen',
    icon: <HomeOutlined />,
    label: <Link href="/citizen">Home</Link>,
  },
  {
    key: '/citizen/report',
    icon: <AlertOutlined />,
    label: <Link href="/citizen/report">Report Emergency</Link>,
  },
  {
    key: '/citizen/reports',
    icon: <FileTextOutlined />,
    label: <Link href="/citizen/reports">My Reports</Link>,
  },
  {
    key: '/citizen/advisory',
    icon: <SafetyOutlined />,
    label: <Link href="/citizen/advisory">Safety Advisories</Link>,
  },
  {
    key: '/citizen/alerts',
    icon: <EnvironmentOutlined />,
    label: <Link href="/citizen/alerts">Nearby Alerts</Link>,
  },
  {
    key: '/citizen/contacts',
    icon: <PhoneOutlined />,
    label: <Link href="/citizen/contacts">Emergency Contacts</Link>,
  },
];

// Breadcrumb mapping
const breadcrumbNameMap: Record<string, string> = {
  '/citizen': 'Home',
  '/citizen/report': 'Report Emergency',
  '/citizen/reports': 'My Reports',
  '/citizen/advisory': 'Safety Advisories',
  '/citizen/alerts': 'Nearby Alerts',
  '/citizen/contacts': 'Emergency Contacts',
};

const getSelectedMenuKey = (path: string) => {
  if (path.startsWith('/citizen/reports/')) {
    return '/citizen/reports';
  }

  return [...menuItems]
    .reverse()
    .find((item) => item && 'key' in item && path.startsWith(String(item.key)))
    ?.key?.toString() || '/citizen';
};

// Dynamic breadcrumb handler for report details
const getDynamicBreadcrumb = (path: string): string | null => {
  if (path.startsWith('/citizen/reports/') && path !== '/citizen/reports') {
    return 'Report Details';
  }
  return null;
};

export default function CitizenLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const selectedMenuKey = getSelectedMenuKey(pathname);

  // Generate breadcrumb items
  const pathSnippets = pathname.split('/').filter((i) => i);
  const breadcrumbItems = pathSnippets.map((_, index) => {
    const url = `/${pathSnippets.slice(0, index + 1).join('/')}`;
    const title = breadcrumbNameMap[url] || getDynamicBreadcrumb(url) || url;
    return {
      title: index === 0 ? <HomeOutlined /> : title,
      href: url,
    };
  });

  return (
    <Layout className="min-h-screen">
      {/* Header */}
      <Header 
        className="fixed top-0 left-0 right-0 z-50 bg-white shadow-md px-4 md:px-8 flex items-center justify-between"
        style={{ height: '64px', lineHeight: '64px', padding: '0 24px' }}
      >
        {/* Logo and Title */}
        <div className="flex items-center gap-4">
          <div className="text-xl font-bold text-sky-500">
            CrisisGrid
          </div>
          <span className="hidden md:inline text-gray-600 text-sm">
            Citizen Portal
          </span>
        </div>

        {/* Desktop Navigation */}
        <div className="hidden lg:flex items-center gap-4 flex-1 justify-center">
          <Menu
            mode="horizontal"
            selectedKeys={[selectedMenuKey]}
            items={menuItems}
            className="flex-1 justify-center border-0"
            style={{ minWidth: 0, flex: 'auto' }}
          />
        </div>

        {/* Emergency Button - Desktop */}
        <Link href="/citizen/contacts" className="hidden md:block">
          <Button
            type="primary"
            danger
            size="large"
            icon={<PhoneOutlined />}
            className="bg-red-500 hover:bg-red-600 font-semibold"
            aria-label="Emergency Contacts"
          >
            Emergency
          </Button>
        </Link>

        {/* Mobile Menu Button */}
        <Button
          type="text"
          icon={<MenuOutlined />}
          onClick={() => setMobileMenuOpen(true)}
          className="lg:hidden"
          aria-label="Open menu"
        />
      </Header>

      {/* Mobile Drawer Menu */}
      <Drawer
        title="Menu"
        placement="right"
        onClose={() => setMobileMenuOpen(false)}
        open={mobileMenuOpen}
        width={280}
      >
        <Menu
          mode="vertical"
          selectedKeys={[selectedMenuKey]}
          items={menuItems}
          onClick={() => setMobileMenuOpen(false)}
          className="border-0"
        />
        <div className="mt-4 px-4">
          <Link href="/citizen/contacts" onClick={() => setMobileMenuOpen(false)}>
            <Button
              type="primary"
              danger
              size="large"
              icon={<PhoneOutlined />}
              block
              className="bg-red-500 hover:bg-red-600 font-semibold"
            >
              Emergency Contacts
            </Button>
          </Link>
        </div>
      </Drawer>

      {/* Main Content */}
      <Content 
        className="mt-16 min-h-screen"
        style={{ marginTop: '64px' }}
      >
        {/* Breadcrumb */}
        {pathname !== '/citizen' && (
          <div className="bg-gray-50 px-4 md:px-8 py-3 border-b">
            <div className="max-w-7xl mx-auto">
              <Breadcrumb
                items={breadcrumbItems}
                separator=">"
              />
            </div>
          </div>
        )}

        {/* Page Content */}
        <div className="p-4 md:p-8">
          <div className="max-w-7xl mx-auto">
            {children}
          </div>
        </div>
      </Content>

      {/* Footer */}
      <Footer className="bg-slate-950 text-white mt-auto">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-6">
            {/* Emergency Contacts */}
            <div>
              <h3 className="text-lg font-semibold mb-3 text-white">
                Emergency Contacts
              </h3>
              <ul className="space-y-2 text-gray-300">
                <li>
                  <a href="tel:911" className="inline-flex items-center gap-2 text-slate-300 hover:text-white transition-colors">
                    <PhoneOutlined />
                    Emergency: 911
                  </a>
                </li>
                <li>
                  <a href="tel:311" className="inline-flex items-center gap-2 text-slate-300 hover:text-white transition-colors">
                    <PhoneOutlined />
                    Non-Emergency: 311
                  </a>
                </li>
                <li>
                  <Link href="/citizen/contacts" className="inline-flex items-center gap-2 text-slate-300 hover:text-white transition-colors">
                    <FileTextOutlined />
                    All Contacts
                  </Link>
                </li>
              </ul>
            </div>

            {/* Quick Links */}
            <div>
              <h3 className="text-lg font-semibold mb-3 text-white">
                Quick Links
              </h3>
              <ul className="space-y-2 text-gray-300">
                <li>
                  <Link href="/citizen/report" className="hover:text-white transition-colors">
                    Report Emergency
                  </Link>
                </li>
                <li>
                  <Link href="/citizen/advisory" className="hover:text-white transition-colors">
                    Safety Advisories
                  </Link>
                </li>
                <li>
                  <Link href="/citizen/alerts" className="hover:text-white transition-colors">
                    Nearby Alerts
                  </Link>
                </li>
              </ul>
            </div>

            {/* About */}
            <div>
              <h3 className="text-lg font-semibold mb-3 text-white">
                About CrisisGrid
              </h3>
              <p className="text-gray-300 text-sm mb-3">
                AI-powered emergency response coordination system for real-time crisis management.
              </p>
              <p className="text-gray-400 text-xs">
                © 2026 CrisisGrid AI. All rights reserved.
              </p>
            </div>
          </div>

          {/* Bottom Bar */}
          <div className="border-t border-gray-700 pt-4 text-center text-gray-400 text-sm">
            <p>
              For life-threatening emergencies, always call 911 immediately.
            </p>
          </div>
        </div>
      </Footer>

      {/* Fixed Emergency Button - Mobile Only */}
      <div className="md:hidden fixed bottom-6 right-6 z-50">
        <Link href="/citizen/contacts">
          <Button
            type="primary"
            danger
            size="large"
            shape="circle"
            icon={<PhoneOutlined className="text-2xl" />}
            className="bg-red-500 hover:bg-red-600 shadow-lg w-16 h-16 flex items-center justify-center"
            aria-label="Emergency Contacts"
            style={{ width: '64px', height: '64px' }}
          />
        </Link>
      </div>
    </Layout>
  );
}

// Made with Bob
