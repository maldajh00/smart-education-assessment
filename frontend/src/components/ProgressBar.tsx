interface Props {
  value: number; // 0..100
  label?: string;
}

export function ProgressBar({ value, label }: Props) {
  const clamped = Math.max(0, Math.min(100, value));
  return (
    <div className="progress" aria-label={label ?? "progress"}>
      <div
        className="progress__bar"
        role="progressbar"
        aria-valuenow={clamped}
        aria-valuemin={0}
        aria-valuemax={100}
        style={{ width: `${clamped}%` }}
      />
      <span className="progress__text">{clamped}%</span>
    </div>
  );
}
