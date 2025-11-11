import React from "react";
import type { WeekMeta } from "../lib/parse";

type Props = {
  weeks: WeekMeta[];
  value: string;
  onChange: (week: string) => void | Promise<void>;
};

export default function WeekPicker({ weeks, value, onChange }: Props) {
  return (
    <div className="flex flex-col text-sm">
      <label htmlFor="week-select" className="font-medium text-neutral-600">
        Semaine
      </label>
      <select
        id="week-select"
        className="mt-1 rounded-md border border-neutral-300 bg-white px-3 py-2 shadow-sm 
                   hover:border-neutral-400 focus:outline-none focus:ring-2 focus:ring-neutral-300"
        value={value}
        onChange={(e) => onChange(e.target.value)}
      >
        {weeks.map((w) => (
          <option key={w.week} value={w.week}>
            {w.week} {w.range ? `— ${w.range}` : ""}
          </option>
        ))}
      </select>
    </div>
  );
}