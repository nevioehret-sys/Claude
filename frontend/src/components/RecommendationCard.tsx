import { Recommendation } from "@/lib/types";

const tagClass: Record<string, string> = {
  "Starker Value": "tag-strong",
  "Guter Value": "tag-good",
  "Leichter Value": "tag-light",
  "Kein Value": "tag-none",
};

export default function RecommendationCard({ title, rec }: { title: string; rec: Recommendation | null }) {
  if (!rec) {
    return (
      <div className="card">
        <div className="label">{title}</div>
        <div>Keine passende Wette gefunden.</div>
      </div>
    );
  }
  return (
    <div className="card">
      <div className="label">{title}</div>
      <div className="value">{rec.market}</div>
      <p>
        Wahrscheinlichkeit: {(rec.probability * 100).toFixed(1)}% · Faire Quote: {rec.fair_odds} · Marktquote:{" "}
        {rec.market_odds}
      </p>
      <p>
        Edge: {rec.edge_pct}% · EV: {rec.expected_value} · Kelly Stake: {rec.kelly_stake_pct}% · Konfidenz:{" "}
        {rec.confidence_score}/100
      </p>
      <span className={`tag ${tagClass[rec.value_class] ?? "tag-none"}`}>{rec.value_class}</span>
    </div>
  );
}
