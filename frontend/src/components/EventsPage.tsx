import React from "react";

type EventItem = {
  name: string;
  date: string;
  sortDate: string; // YYYY-MM-DD for sorting
  location: string;
  type: "conference" | "meetup";
  mode: "paris" | "online" | "international";
  url: string;
  description: string;
};

const EVENTS: EventItem[] = [
  // Conferences Paris
  {
    name: "pgDay Paris 2026",
    date: "26 mars 2026",
    sortDate: "2026-03-26",
    location: "Espace Saint-Martin, Paris",
    type: "conference",
    mode: "paris",
    url: "https://2026.pgday.paris/",
    description: "10e édition de la conférence PostgreSQL à Paris.",
  },
  {
    name: "Big Data & AI Paris 2026",
    date: "15-16 septembre 2026",
    sortDate: "2026-09-15",
    location: "Paris Expo Porte de Versailles",
    type: "conference",
    mode: "paris",
    url: "https://www.bigdataparis.com/",
    description:
      "15e édition du plus grand événement data & IA en France. 20 000+ participants.",
  },
  {
    name: "apidays Paris 2026",
    date: "1-3 décembre 2026",
    sortDate: "2026-12-01",
    location: "CNIT Forest, Paris",
    type: "conference",
    mode: "paris",
    url: "https://www.apidays.global/events/paris",
    description:
      "4 000+ participants, 300+ sessions sur les APIs, data et IA.",
  },
  {
    name: "Data Days 2026",
    date: "2026 (date TBD)",
    sortDate: "2026-06-01",
    location: "Lille",
    type: "conference",
    mode: "paris",
    url: "https://days.data-lille.fr/2026/",
    description: "Journée de conférences data & IA, 2 tracks.",
  },
  // International / Online
  {
    name: "Data Council 2026",
    date: "12-14 mai 2026",
    sortDate: "2026-05-12",
    location: "San Francisco (+ streaming)",
    type: "conference",
    mode: "international",
    url: "https://www.datacouncil.ai/data-council-2026",
    description:
      "Conférence vendor-neutral sur le data engineering & analytics.",
  },
  {
    name: "Databricks Data+AI Summit 2026",
    date: "15-18 juin 2026",
    sortDate: "2026-06-15",
    location: "San Francisco",
    type: "conference",
    mode: "international",
    url: "https://www.databricks.com/dataaisummit",
    description: "70 000+ participants attendus. Keynotes streamées en ligne.",
  },
  {
    name: "Snowflake Summit 2026",
    date: "1-4 juin 2026",
    sortDate: "2026-06-01",
    location: "San Francisco",
    type: "conference",
    mode: "international",
    url: "https://www.snowflake.com/en/summit/",
    description: "La plus grande conférence éducative Snowflake.",
  },
  {
    name: "Airflow Summit 2026",
    date: "31 août - 2 sept. 2026",
    sortDate: "2026-08-31",
    location: "Austin, TX",
    type: "conference",
    mode: "international",
    url: "https://airflowsummit.org/",
    description: "100+ sessions sur l'orchestration et les workflows data.",
  },
  {
    name: "dbt Coalesce 2026",
    date: "2026 (date TBD)",
    sortDate: "2026-10-01",
    location: "Las Vegas",
    type: "conference",
    mode: "international",
    url: "https://www.getdbt.com/coalesce-2026-waitlist",
    description:
      "Conférence dbt (anciennement Coalesce). Waitlist ouverte.",
  },
];

const MEETUPS = [
  {
    name: "Paris Data Engineers",
    url: "https://www.meetup.com/fr-FR/Paris-Data-Engineers/",
    description: "Talks data & ML engineering par des entreprises parisiennes.",
  },
  {
    name: "Data Council Paris",
    url: "https://www.meetup.com/DataCouncil-ai-Paris-Data-Engineering-Science/",
    description: "Data engineering & science — meetups réguliers.",
  },
  {
    name: "Future of Data: Paris",
    url: "https://www.meetup.com/futureofdata-paris/",
    description: "Projets data Apache Software Foundation.",
  },
  {
    name: "Paris Data Ladies",
    url: "https://www.meetup.com/paris-dataladies/",
    description: "Women in data — talks qualité et data engineering.",
  },
  {
    name: "Paris Machine Learning",
    url: "http://parismlgroup.org/",
    description:
      "3e plus grand groupe Data Science au monde. Meetups mensuels.",
  },
  {
    name: "Paris AI Meetup",
    url: "https://www.meetup.com/artificial-intelligence-meetup-paris/",
    description: "Meetups IA & ML à Paris.",
  },
];

type Filter = "all" | "paris" | "international";

export default function EventsPage() {
  const [filter, setFilter] = React.useState<Filter>("all");

  const now = new Date().toISOString().slice(0, 10);

  const filteredEvents = EVENTS.filter((e) => {
    if (filter === "all") return true;
    return e.mode === filter;
  }).sort((a, b) => a.sortDate.localeCompare(b.sortDate));

  const upcoming = filteredEvents.filter((e) => e.sortDate >= now);
  const past = filteredEvents.filter((e) => e.sortDate < now);

  return (
    <div className="space-y-8">
      {/* Intro */}
      <div className="text-center space-y-2">
        <p className="text-sm text-neutral-500">
          Événements data engineering, data science & IA — Paris & international
        </p>
      </div>

      {/* Filter chips */}
      <div className="flex justify-center gap-2">
        {(
          [
            ["all", "Tous"],
            ["paris", "Paris & France"],
            ["international", "International"],
          ] as const
        ).map(([key, label]) => (
          <button
            key={key}
            onClick={() => setFilter(key)}
            className={`px-4 py-2 text-sm rounded-full border transition-colors ${
              filter === key
                ? "bg-neutral-900 text-white border-neutral-900"
                : "bg-white text-neutral-600 border-neutral-300 hover:border-neutral-400"
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {/* Upcoming Events */}
      {upcoming.length > 0 && (
        <section className="space-y-4">
          <h2 className="text-base font-semibold text-neutral-900">
            A venir ({upcoming.length})
          </h2>
          <div className="space-y-3">
            {upcoming.map((event) => (
              <EventCard key={event.name} event={event} />
            ))}
          </div>
        </section>
      )}

      {/* Past Events */}
      {past.length > 0 && (
        <section className="space-y-4">
          <h2 className="text-base font-semibold text-neutral-400">
            Passés ({past.length})
          </h2>
          <div className="space-y-3 opacity-60">
            {past.map((event) => (
              <EventCard key={event.name} event={event} />
            ))}
          </div>
        </section>
      )}

      {/* Separator */}
      <div className="border-t border-neutral-200 pt-6">
        <h2 className="text-base font-semibold text-neutral-900 mb-4">
          Meetups réguliers à Paris
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {MEETUPS.map((m) => (
            <a
              key={m.name}
              href={m.url}
              target="_blank"
              rel="noopener noreferrer"
              className="block p-4 bg-white border border-neutral-200 rounded-lg hover:border-neutral-400 transition-colors"
            >
              <h3 className="text-sm font-medium text-neutral-900">
                {m.name}
              </h3>
              <p className="text-xs text-neutral-500 mt-1">{m.description}</p>
            </a>
          ))}
        </div>
      </div>

      {/* Sources */}
      <div className="text-center text-xs text-neutral-400 pt-4">
        Sources : sites officiels, Meetup, confs.tech
        <br />
        Dernière mise à jour manuelle — automatisation à venir via RSS Meetup &
        confs.tech API
      </div>
    </div>
  );
}

function EventCard({ event }: { event: EventItem }) {
  const modeLabels: Record<string, { text: string; color: string }> = {
    paris: { text: "Paris", color: "bg-blue-100 text-blue-700" },
    international: {
      text: "International",
      color: "bg-purple-100 text-purple-700",
    },
    online: { text: "Online", color: "bg-green-100 text-green-700" },
  };

  const badge = modeLabels[event.mode];

  return (
    <a
      href={event.url}
      target="_blank"
      rel="noopener noreferrer"
      className="block p-4 bg-white border border-neutral-200 rounded-lg hover:border-neutral-400 hover:shadow-sm transition-all"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <h3 className="text-sm font-medium text-neutral-900">{event.name}</h3>
          <p className="text-xs text-neutral-500 mt-1">{event.description}</p>
          <div className="flex items-center gap-3 mt-2 text-xs text-neutral-400">
            <span>{event.date}</span>
            <span>·</span>
            <span>{event.location}</span>
          </div>
        </div>
        <span
          className={`shrink-0 px-2 py-1 text-xs font-medium rounded-full ${badge.color}`}
        >
          {badge.text}
        </span>
      </div>
    </a>
  );
}
