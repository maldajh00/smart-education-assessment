interface Props {
  kind: "loading" | "error" | "empty";
  title?: string;
  message?: string;
  onRetry?: () => void;
}

export function StatusMessage({ kind, title, message, onRetry }: Props) {
  const defaults = {
    loading: { title: "Loading…", message: "Fetching the latest data." },
    error: { title: "Something went wrong", message: "Please try again in a moment." },
    empty: { title: "Nothing here yet", message: "There is no data to display." },
  }[kind];

  return (
    <div className={`status status--${kind}`} role="status" aria-live="polite">
      <div className="status__title">{title ?? defaults.title}</div>
      <div className="status__message">{message ?? defaults.message}</div>
      {kind === "error" && onRetry ? (
        <button className="btn btn--secondary" onClick={onRetry}>
          Retry
        </button>
      ) : null}
    </div>
  );
}
