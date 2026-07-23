import React, { useState } from "react";
import Pitch from "./Pitch";

export interface Shot {
  id: string;
  player_name: string;
  team_name: string;
  minute: number;
  second: number;
  x: number;
  y: number;
  outcome: string;
  xg: number;
  body_part: string;
  under_pressure: boolean;
}

interface ShotMapProps {
  shots: Shot[];
}

export default function ShotMap({ shots }: ShotMapProps) {
  const [hoveredShot, setHoveredShot] = useState<Shot | null>(null);

  const getShotColor = (outcome: string) => {
    switch (outcome.toLowerCase()) {
      case "goal":
        return "#22c55e"; // bright green
      case "saved":
      case "saved to post":
        return "#eab308"; // yellow
      case "off target":
      case "wayward":
        return "#ef4444"; // red
      case "blocked":
        return "#64748b"; // slate
      default:
        return "#3b82f6"; // blue
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-slate-100">Shot Map & Expected Goals (xG)</h3>
        <div className="flex gap-4 text-xs font-medium">
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-green-500"></span>
            <span className="text-slate-400">Goal</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-yellow-500"></span>
            <span className="text-slate-400">Saved</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-red-500"></span>
            <span className="text-slate-400">Off Target</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-slate-500"></span>
            <span className="text-slate-400">Blocked</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Main interactive pitch */}
        <div className="lg:col-span-3">
          <Pitch>
            {shots.map((shot) => {
              // Scale radius by xG: higher xG = bigger circle
              // Statsbomb xG is [0, 1]. Map it to radius [2, 7]
              const r = 2.5 + (shot.xg || 0.05) * 6;
              const color = getShotColor(shot.outcome);

              return (
                <circle
                  key={shot.id}
                  cx={shot.x}
                  cy={shot.y}
                  r={r}
                  fill={color}
                  fillOpacity="0.8"
                  stroke="#ffffff"
                  strokeWidth="0.5"
                  className="transition-all hover:scale-125 hover:fill-opacity-100 cursor-pointer"
                  onMouseEnter={() => setHoveredShot(shot)}
                  onMouseLeave={() => setHoveredShot(null)}
                />
              );
            })}
          </Pitch>
        </div>

        {/* Dynamic Details Inspector */}
        <div className="lg:col-span-1 flex flex-col justify-between p-5 bg-card border border-border rounded-xl min-h-[220px]">
          <div>
            <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-3">
              Shot Inspector
            </h4>
            {hoveredShot ? (
              <div className="space-y-3">
                <div>
                  <div className="text-sm font-bold text-slate-100">{hoveredShot.player_name}</div>
                  <div className="text-xs text-muted-foreground">{hoveredShot.team_name}</div>
                </div>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div className="bg-background/40 p-2 rounded border border-border/50">
                    <div className="text-muted-foreground">Minute</div>
                    <div className="font-semibold text-slate-200">{hoveredShot.minute}'</div>
                  </div>
                  <div className="bg-background/40 p-2 rounded border border-border/50">
                    <div className="text-muted-foreground">Expected Goal</div>
                    <div className="font-bold text-green-400">{(hoveredShot.xg || 0).toFixed(2)} xG</div>
                  </div>
                  <div className="bg-background/40 p-2 rounded border border-border/50">
                    <div className="text-muted-foreground">Body Part</div>
                    <div className="font-semibold text-slate-200">{hoveredShot.body_part}</div>
                  </div>
                  <div className="bg-background/40 p-2 rounded border border-border/50">
                    <div className="text-muted-foreground">Pressure?</div>
                    <div className="font-semibold text-slate-200">
                      {hoveredShot.under_pressure ? "Yes" : "No"}
                    </div>
                  </div>
                </div>
                <div className="text-xs pt-1">
                  <span className="text-muted-foreground">Outcome: </span>
                  <span
                    className="font-semibold"
                    style={{ color: getShotColor(hoveredShot.outcome) }}
                  >
                    {hoveredShot.outcome}
                  </span>
                </div>
              </div>
            ) : (
              <div className="h-32 flex items-center justify-center text-center text-xs text-muted-foreground">
                Hover over a shot on the pitch map to inspect telemetry details and xG features.
              </div>
            )}
          </div>
          
          <div className="text-[10px] text-muted-foreground border-t border-border/50 pt-2 mt-4">
            Circle size is proportional to probability value (xG). Outlines denote custom model estimations.
          </div>
        </div>
      </div>
    </div>
  );
}
