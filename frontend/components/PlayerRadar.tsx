import React from "react";
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Legend,
  Tooltip
} from "recharts";

export interface RadarMetric {
  metric: string;
  player_value: number;
  player_percentile: number;
  match_value: number;
  match_percentile: number;
}

export interface MatchPlayer {
  player_id: number;
  player_name: string;
  similarity_score: number;
  radar_comparison: RadarMetric[];
  explanation: string;
  umap_x: number;
  umap_y: number;
}

interface PlayerRadarProps {
  playerName: string;
  matchPlayer: MatchPlayer;
}

export default function PlayerRadar({ playerName, matchPlayer }: PlayerRadarProps) {
  // Format data for Recharts Radar
  const chartData = matchPlayer.radar_comparison.map((item) => ({
    metric: item.metric,
    [playerName]: item.player_percentile,
    [matchPlayer.player_name]: item.match_percentile,
  }));

  return (
    <div className="bg-card border border-border rounded-xl p-5 space-y-6 shadow-md">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-border/50 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-lg font-bold text-slate-100">{playerName}</span>
            <span className="text-xs text-muted-foreground">vs</span>
            <span className="text-lg font-bold text-green-400">{matchPlayer.player_name}</span>
          </div>
          <div className="text-xs text-muted-foreground mt-0.5">
            Statistical profile comparison based on Percentiles (0 - 100%)
          </div>
        </div>
        <div className="bg-green-500/10 text-green-400 border border-green-500/20 px-3 py-1.5 rounded-lg text-sm font-semibold text-center md:text-left self-start md:self-auto">
          Similarity Index: {(matchPlayer.similarity_score * 100).toFixed(1)}%
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6 items-center">
        {/* Radar Chart (Recharts) */}
        <div className="lg:col-span-3 h-[320px] w-full flex items-center justify-center">
          <ResponsiveContainer width="100%" height="100%">
            <RadarChart cx="50%" cy="50%" outerRadius="75%" data={chartData}>
              <PolarGrid stroke="#334155" />
              <PolarAngleAxis dataKey="metric" tick={{ fill: "#94a3b8", fontSize: 9 }} />
              <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fill: "#64748b", fontSize: 8 }} />
              <Radar
                name={playerName}
                dataKey={playerName}
                stroke="#3b82f6"
                fill="#3b82f6"
                fillOpacity={0.25}
              />
              <Radar
                name={matchPlayer.player_name}
                dataKey={matchPlayer.player_name}
                stroke="#22c55e"
                fill="#22c55e"
                fillOpacity={0.25}
              />
              <Tooltip
                contentStyle={{ backgroundColor: "#1e293b", borderColor: "#334155", color: "#f1f5f9", fontSize: 11 }}
              />
              <Legend wrapperStyle={{ fontSize: 11, paddingTop: 10 }} />
            </RadarChart>
          </ResponsiveContainer>
        </div>

        {/* Explainable Strengths & Weaknesses */}
        <div className="lg:col-span-2 space-y-4">
          <div>
            <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-2">
              Similarity Explanation
            </h4>
            <p className="text-sm text-slate-300 leading-relaxed bg-background/40 border border-border/50 p-4 rounded-lg">
              {matchPlayer.explanation}
            </p>
          </div>

          <div className="space-y-2.5">
            <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Direct Metric Comparison
            </h4>
            <div className="max-h-[160px] overflow-y-auto pr-1 space-y-1.5 text-xs">
              {matchPlayer.radar_comparison.map((item, idx) => {
                const diff = Math.abs(item.player_value - item.match_value);
                const isClose = diff < 0.1 || (item.metric.includes("Rate") && diff < 0.05);
                
                return (
                  <div
                    key={idx}
                    className={`flex items-center justify-between p-2 rounded border ${
                      isClose ? "bg-green-500/5 border-green-500/10" : "bg-background/20 border-border/30"
                    }`}
                  >
                    <span className="font-medium text-slate-300">{item.metric}</span>
                    <div className="flex gap-3 text-right">
                      <span className="text-blue-400">
                        {item.player_value.toFixed(2)} ({item.player_percentile.toFixed(0)}th)
                      </span>
                      <span className="text-green-400">
                        {item.match_value.toFixed(2)} ({item.match_percentile.toFixed(0)}th)
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
