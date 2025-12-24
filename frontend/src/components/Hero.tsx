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
      <div className="max-w-6xl mx-auto px-4 py-4 sm:py-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3 sm:gap-4">
            <div className="text-2xl sm:text-3xl font-serif tracking-wide">VEILLE</div>
            <Chip>MAG</Chip>
          </div>

          {/* Slot custom ou select intégré */}
          {rightSlot ? (
            <div className="flex items-center w-full sm:w-auto">{rightSlot}</div>
          ) : onWeekChange ? (
            <div className="flex items-center gap-3 w-full sm:w-auto">
              <label htmlFor={selectId} className="text-sm text-neutral-500 whitespace-nowrap">
                Semaine
              </label>
              <select
                id={selectId}
                className="flex-1 sm:flex-none border rounded-md px-3 py-2 text-sm bg-neutral-50 hover:border-neutral-300 focus:outline-none focus:ring-2 focus:ring-neutral-200"
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
      </div>

      {/* Bandeau éditorial */}
      <div className="max-w-6xl mx-auto px-4 pb-4 sm:pb-6">
        <div className="bg-neutral-50 border rounded-2xl p-4 sm:p-6">
          <div className="text-xs font-semibold tracking-widest uppercase text-neutral-500">
            Semaine {weekLabel}
          </div>
          <h1 className="text-xl sm:text-2xl md:text-3xl font-bold mt-2 leading-tight">
            Les 3 articles essentiels de la semaine
          </h1>
          <p className="text-sm sm:text-base text-neutral-600 mt-2">
            Data • Analytics • ML — le meilleur, sans la surcharge
          </p>
          {dateRange && <p className="text-xs sm:text-sm text-neutral-500 mt-1">{dateRange}</p>}
          <div className="h-1 bg-gradient-to-r from-neutral-300 to-neutral-200 w-16 sm:w-24 mt-3 sm:mt-4 rounded-full" />
        </div>
      </div>
    </header>
  );
}