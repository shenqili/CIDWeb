import "./globals.css";
import type { Metadata } from "next";
import { DemoSessionProvider } from "../components/demo-context";
import { AppShell } from "../components/shell";

export const metadata: Metadata = {
  title: "CIDWeb Demo",
  description: "Skin analytics platform demo shell",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="zh-CN">
      <body>
        <DemoSessionProvider>
          <AppShell>{children}</AppShell>
        </DemoSessionProvider>
      </body>
    </html>
  );
}
