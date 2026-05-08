import type { Metadata } from "next";
import { cookies } from "next/headers";
import "./globals.css";
import NavBar from "@/components/NavBar";
import Footer from "@/components/Footer";
import { LocaleProvider } from "@/lib/LocaleProvider";
import { DEFAULT_LOCALE, LOCALES, STORAGE_KEY, type Locale } from "@/lib/i18n";

export const metadata: Metadata = {
  title: "B-Wave | Ship PSC Defect Scanner",
  description: "AI-powered Port State Control defect detection for maritime vessels",
};

export default async function RootLayout({ children }: { children: React.ReactNode }) {
  const cookieStore = await cookies();
  const stored = cookieStore.get(STORAGE_KEY)?.value;
  const initialLocale: Locale =
    stored && stored in LOCALES ? (stored as Locale) : DEFAULT_LOCALE;

  return (
    <html lang={initialLocale}>
      <body>
        <LocaleProvider initialLocale={initialLocale}>
          <NavBar />
          <main className="min-h-screen pt-16">{children}</main>
          <Footer />
        </LocaleProvider>
      </body>
    </html>
  );
}
