import Chip from "./Chip";

type Props = {
  weekLabel: string;
  dateRange?: string;
  rightSlot?: React.ReactNode; // ex: <WeekPicker .../>
  weeks?: string[];
  onWeekChange?: (w: string) => void | Promise<void>;
};

export default function Hero({
  weekLabel,
  dateRange,
  rightSlot,
  weeks = [],
  onWeekChange,
}: Props) {
  const selectId = "week-picker";

  return (
    <header className="bg-white border-b">
      {/* Barre supérieure : logo + sélecteur */}
      <div className="max-w-6xl mx-auto px-4 py-6 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="text-3xl font-serif tracking-wide">VEILLE</div>
          <Chip>MAG</Chip>
        </div>

        {/* Slot custom ou select intégré */}
        {rightSlot ? (
          <div className="flex items-center">{rightSlot}</div>
        ) : onWeekChange ? (
          <div className="flex items-center gap-3">
            <label htmlFor={selectId} className="text-sm text-neutral-500">
              Semaine
            </label>
            <select
              id={selectId}
              className="border rounded-md px-3 py-2 text-sm bg-neutral-50 hover:border-neutral-300 focus:outline-none focus:ring-2 focus:ring-neutral-200"
              value={weekLabel}
              onChange={(e) => onWeekChange(e.target.value)}
            >
              {weeks.map((w) => (
                <option key={w} value={w}>
                  {w}
                </option>
              ))}
            </select>
          </div>
        ) : null}
      </div>

      {/* Bandeau éditorial */}
      <div className="max-w-6xl mx-auto px-4 pb-6">
        <div className="bg-neutral-50 border rounded-2xl p-6">
          <div className="text-xs font-semibold tracking-widest">
            Semaine {weekLabel}
          </div>
          <h1 className="text-2xl md:text-3xl font-bold mt-2">
            Data • Analytics • ML — la semaine en un coup d’œil
          </h1>
          {dateRange && <p className="text-neutral-600 mt-2">{dateRange}</p>}
          <div className="h-1 bg-gradient-to-r from-neutral-300 to-neutral-200 w-24 mt-4 rounded-full" />
        </div>
      </div>
    </header>
  );
}