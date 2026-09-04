import type { ReactNode } from "react";

interface Props {
  title?: ReactNode;
  eyebrow?: ReactNode;
  footer?: ReactNode;
  children: ReactNode;
  className?: string;
}

export function Card({ title, eyebrow, footer, children, className = "" }: Props) {
  return (
    <article className={`card ${className}`}>
      {eyebrow ? <div className="card__eyebrow">{eyebrow}</div> : null}
      {title ? <h3 className="card__title">{title}</h3> : null}
      <div className="card__body">{children}</div>
      {footer ? <div className="card__footer">{footer}</div> : null}
    </article>
  );
}
