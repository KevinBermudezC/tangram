import Link from "next/link";

import { TemplatesStrip } from "@/components/templates-strip";
import { Card } from "@/components/ui/card";

/**
 * Templates page.
 *
 * The strip on the library page lives here too — for now this is the same
 * four cards plus a "more coming" placeholder. When the patterns library
 * lands (`add-patterns-library` was merged but the UI side isn't built),
 * this page will pull templates from `patterns/` instead of mock data.
 */
export default function TemplatesPage() {
  return (
    <main className="flex flex-col gap-6 p-8">
      <header className="flex flex-col gap-1">
        <div className="flex items-baseline gap-2.5">
          <h1 className="font-serif text-[24px] font-medium tracking-tight text-ink-strong">
            Templates
          </h1>
          <span aria-hidden className="font-serif text-[17px] text-ink-faint">
            型
          </span>
        </div>
        <p className="text-[13px] text-ink-muted">
          Curated starting points for the eight component types. Fork one
          into your library and edit freely.
        </p>
      </header>

      <TemplatesStrip />

      <Card className="border-dashed bg-transparent p-6">
        <div className="flex flex-col gap-1 text-center">
          <p className="font-serif text-[17px] font-medium tracking-wide text-ink-strong">
            More templates coming
          </p>
          <p className="text-[12.5px] text-ink-muted">
            We're curating them in{" "}
            <Link
              href="https://github.com/KevinBermudezC/tangram/tree/main/patterns"
              className="text-accent hover:text-accent-strong"
            >
              <code>patterns/</code>
            </Link>
            . Contributions welcome.
          </p>
        </div>
      </Card>
    </main>
  );
}
