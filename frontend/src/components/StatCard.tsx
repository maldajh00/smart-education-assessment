interface Props {
  label: string;
  value: string | number;
  icon?: string;
}

export function StatCard({ label, value, icon }: Props) {
  return (
    <div className="stat">
      {icon ? <div className="stat__icon" aria-hidden="true">{icon}</div> : null}
      <div className="stat__value">{value}</div>
      <div className="stat__label">{label}</div>
    </div>
  );
}
