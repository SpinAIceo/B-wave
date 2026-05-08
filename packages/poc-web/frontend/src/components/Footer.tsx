"use client";
import { useT } from "@/lib/i18n";

export default function Footer() {
  const t = useT();
  return (
    <footer className="border-t border-navy-700 py-8 text-center text-sm text-gray-500">
      <p>{t("footer_copyright")}</p>
      <p className="mt-1 text-xs">{t("footer_model_meta")}</p>
    </footer>
  );
}
