import { DailyCount } from "@/lib/api";

function shortLabel(date: string): string {
  const d = new Date(`${date}T00:00:00`);
  return d.toLocaleDateString(undefined, { weekday: "short" });
}

export function UsageChart({ data }: { data: DailyCount[] }) {
  const max = Math.max(1, ...data.map((d) => d.count));

  return (
    <div className="flex h-48 items-end gap-1.5 sm:gap-3">
      {data.map((d) => {
        const height = d.count === 0 ? 4 : Math.max(10, Math.round((d.count / max) * 160));
        return (
          <div
            key={d.date}
            className="group flex flex-1 flex-col items-center justify-end gap-1.5"
            title={`${d.count} events on ${shortLabel(d.date)}`}
          >
            <span className="text-[10px] font-medium text-muted-foreground opacity-0 transition-opacity group-hover:opacity-100">
              {d.count}
            </span>
            <div
              className="w-full rounded-t-md bg-primary/70 transition-colors group-hover:bg-primary"
              style={{ height: `${height}px` }}
            />
            <span className="text-[10px] text-muted-foreground">{shortLabel(d.date)}</span>
          </div>
        );
      })}
    </div>
  );
}
