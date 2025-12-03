// src/App.tsx
import React from "react";
import Hero from "./components/Hero";
import WeekPicker from "./components/WeekPicker";
import Top3 from "./components/Top3";
import SectionCard from "./components/SectionCard";
import Overview from "./components/Overview";               // ⬅️ ajoute ça
import { loadWeeksIndex, loadLatestWeek, loadWeekSummary, type WeekMeta } from "./lib/parse";

export default function App() {
  const [weeks, setWeeks] = React.useState<WeekMeta[]>([]);
  const [currentWeek, setCurrentWeek] = React.useState<WeekMeta | null>(null);
  const [data, setData] = React.useState<{ overview: string; top3: any[]; sections: any[] } | null>(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    (async () => {
      try {
        const ws = await loadWeeksIndex();
        setWeeks(ws);
        const latest = ws[0] || (await loadLatestWeek());
        setCurrentWeek(latest);
        setData(await loadWeekSummary(latest));
      } catch (e: any) {
        setError(e.message ?? String(e));
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const onWeekChange = async (weekId: string) => {
    try {
      setLoading(true);
      const w = weeks.find((x) => x.week === weekId);
      if (!w) throw new Error("Semaine inconnue");
      setCurrentWeek(w);
      setData(await loadWeekSummary(w));
    } catch (e: any) {
      setError(e.message ?? String(e));
    } finally {
      setLoading(false);
    }
  };

  if (error) return <div className="p-6 text-red-600">{error}</div>;
  if (loading || !currentWeek || !data) return <div className="p-6">Chargement…</div>;

  return (
    <div className="min-h-screen bg-neutral-50">
      <Hero
        weekLabel={currentWeek.week}
        dateRange={currentWeek.range}
        weeks={weeks.map(w => w.week)}
        onWeekChange={onWeekChange}
      />
      <main className="max-w-6xl mx-auto px-4 py-8 space-y-8">
        <Overview content={data.overview} />        {/* ⬅️ ici */}
        <Top3 items={data.top3} />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {data.sections.map((sec: any) =>
            sec.items?.length ? (
              <SectionCard
                key={sec.title}
                title={sec.title}
                bullets={sec.items.map((it: any) => ({
                  title: it.title,
                  url: it.url,
                  source: it.source,
                  score: it.score,
                  description: it.description,
                }))}
              />
            ) : null
          )}
        </div>
      </main>
    </div>
  );
}