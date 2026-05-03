'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Layout, Menu, Button, Drawer, Tag } from 'antd';
import type { MenuProps } from 'antd';
import {
  AlertOutlined,
  AppstoreOutlined,
  ClusterOutlined,
  DashboardOutlined,
  FileTextOutlined,
  HomeOutlined,
  MenuOutlined,
  SendOutlined,
  UserOutlined,
} from '@ant-design/icons';

const { Header, Sider, Content } = Layout;

type MenuItem = Required<MenuProps>['items'][number];

const navItems: MenuItem[] = [
  {
    key: '/admin/dashboard',
    icon: <DashboardOutlined />,
    label: <Link href="/admin/dashboard">Command Center</Link>,
  },
  {
    key: '/admin/reports',
    icon: <FileTextOutlined />,
    label: <Link href="/admin/reports">Reports</Link>,
  },
  {
    key: '/admin/alerts',
    icon: <AlertOutlined />,
    label: <Link href="/admin/alerts">Alerts</Link>,
  },
  {
    key: '/admin/dispatch',
    icon: <SendOutlined />,
    label: <Link href="/admin/dispatch">Dispatch</Link>,
  },
  {
    key: '/admin/incidents',
    icon: <ClusterOutlined />,
    label: <Link href="/admin/incidents">Incidents</Link>,
  },
];

function getSelectedKey(pathname: string) {
  return navItems.find((item) => item && 'key' in item && pathname.startsWith(String(item.key)))?.key?.toString() || '/admin/dashboard';
}

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const selectedKey = getSelectedKey(pathname);
  const [drawerOpen, setDrawerOpen] = useState(false);

  const desktopMenu = (
    <Menu
      mode="inline"
      theme="dark"
      selectedKeys={[selectedKey]}
      items={navItems}
      className="border-0 bg-transparent"
      onClick={() => setDrawerOpen(false)}
    />
  );

  const drawerMenu = (
    <Menu
      mode="inline"
      selectedKeys={[selectedKey]}
      items={navItems}
      className="border-0"
      onClick={() => setDrawerOpen(false)}
    />
  );

  return (
    <Layout className="min-h-screen">
      <Sider
        width={280}
        breakpoint="lg"
        collapsedWidth={0}
        className="hidden border-r border-slate-800 bg-slate-950 lg:block"
        theme="dark"
      >
        <div className="flex h-full flex-col">
          <div className="px-6 py-6">
            <Link href="/admin/dashboard" className="flex items-center gap-3 text-white">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-sky-500 text-xl">
                <AppstoreOutlined />
              </div>
              <div>
                <div className="text-lg font-bold leading-tight">CrisisGrid AI</div>
                <div className="text-xs text-slate-400">Operations Console</div>
              </div>
            </Link>
          </div>

          <div className="px-3">{desktopMenu}</div>

          <div className="mt-auto px-6 py-6">
            <div className="rounded-lg border border-slate-800 bg-slate-900 p-4">
              <div className="mb-2 text-xs font-semibold uppercase text-slate-400">Mission Mode</div>
              <Tag color="processing" className="m-0">Live monitoring</Tag>
              <p className="mb-0 mt-3 text-xs leading-relaxed text-slate-400">
                Verification, alerting, and dispatch feeds refresh automatically for demo operations.
              </p>
            </div>
          </div>
        </div>
      </Sider>

      <Layout>
        <Header className="sticky top-0 z-40 flex h-16 items-center justify-between border-b border-slate-200 bg-white/90 px-4 shadow-sm backdrop-blur lg:px-6">
          <div className="flex items-center gap-3">
            <Button
              type="text"
              icon={<MenuOutlined />}
              className="lg:hidden"
              aria-label="Open admin navigation"
              onClick={() => setDrawerOpen(true)}
            />
            <Link href="/admin/dashboard" className="flex items-center gap-2 font-bold text-slate-900 lg:hidden">
              <AppstoreOutlined className="text-sky-600" />
              CrisisGrid AI
            </Link>
            <div className="hidden items-center gap-2 text-sm text-slate-500 lg:flex">
              <HomeOutlined />
              <span>Admin</span>
              <span>/</span>
              <span className="font-medium text-slate-700">
                {selectedKey.replace('/admin/', '').replace(/^\w/, (value) => value.toUpperCase())}
              </span>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Link href="/citizen">
              <Button icon={<UserOutlined />}>Citizen Portal</Button>
            </Link>
          </div>
        </Header>

        <Content className="min-h-[calc(100vh-64px)] p-4 md:p-6 lg:p-8">
          <div className="mx-auto max-w-[1600px]">{children}</div>
        </Content>
      </Layout>

      <Drawer
        title="CrisisGrid Operations"
        placement="left"
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        width={300}
      >
        {drawerMenu}
      </Drawer>
    </Layout>
  );
}

// Made with Bob
