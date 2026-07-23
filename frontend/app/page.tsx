"use client";

import React, { useState, useEffect } from "react";
import { 
  Activity, 
  Database, 
  Cpu, 
  Compass, 
  Bot, 
  Crosshair, 
  Users, 
  Map, 
  TrendingUp, 
  ShieldAlert 
} from "lucide-react";

import ShotMap, { Shot } from "@/components/ShotMap";
import PassingNetwork, { PassNode, PassLink } from "@/components/PassingNetwork";
import PlayerRadar, { MatchPlayer } from "@/components/PlayerRadar";
import XgSandbox from "@/components/XgSandbox";
import AssistantChat from "@/components/AssistantChat";

export default function Home() {
  const [activeTab, setActiveTab] = useState<"match" | "similarity" | "sandbox" | "assistant">("match");
  
  // Database datasets state
  const [competitions, setCompetitions] = useState<any[]>([]);
  const [selectedComp, setSelectedComp] = useState<string | null>(null);
  const [matches, setMatches] = useState<any[]>([]);
  const [selectedMatchId, setSelectedMatchId] = useState<number | null>(null);
  const [matchStats, setMatchStats] = useState<any | null>(null);
  const [shots, setShots] = useState<Shot[]>([]);
  const [passingNetwork, setPassingNetwork] = useState<{nodes: PassNode[], links: PassLink[]} | null>(null);
  
  // Similarity states
  const [playersList, setPlayersList] = useState<any[]>([]);
  const [selectedPlayerId, setSelectedPlayerId] = useState<number | null>(null);
  const [similarityData, setSimilarityData] = useState<any | null>(null);
  const [selectedMatchPlayer, setSelectedMatchPlayer] = useState<MatchPlayer | null>(null);

  // MLOps Status states
  const [systemOnline, setSystemOnline] = useState<boolean>(true);
  const [etlRunning, setEtlRunning] = useState<boolean>(false);
  const [trainingRunning, setTrainingRunning] = useState<boolean>(false);

  // Initial loads
  useEffect(() => {
    fetchCompetitions();
    fetchPlayers();
  }, []);

  // Fetch matches when competition changes
  useEffect(() => {
    if (selectedComp !== null) {
      const [compId, seasonId] = selectedComp.split("-").map(Number);
      fetchMatches(compId, seasonId);
    }
  }, [selectedComp]);

  // Fetch match details when match changes
  useEffect(() => {
    if (selectedMatchId !== null) {
      fetchMatchDetails(selectedMatchId);
    }
  }, [selectedMatchId]);

  // Fetch similarity details when player changes
  useEffect(() => {
    if (selectedPlayerId !== null) {
      fetchPlayerSimilarity(selectedPlayerId);
    }
  }, [selectedPlayerId]);

  const fetchCompetitions = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/v1/competitions");
      if (res.ok) {
        const data = await res.json();
        setCompetitions(data);
        if (data.length > 0) {
          setSelectedComp(`${data[0].competition_id}-${data[0].season_id}`);
        }
      }
    } catch (e) {
      loggerFallback("Competitions server offline. Loading mock sets.");
      // Standard local fallback
      const mockComps = [
        {competition_id: 37, season_id: 4, competition_name: "Premier League", season_name: "2015/2016"},
        {competition_id: 43, season_id: 3, competition_name: "FIFA World Cup", season_name: "2018"}
      ];
      setCompetitions(mockComps);
      setSelectedComp("37-4");
    }
  };

  const fetchMatches = async (compId: number, seasonId: number) => {
    try {
      const res = await fetch(`http://localhost:8000/api/v1/matches?competition_id=${compId}&season_id=${seasonId}`);
      if (res.ok) {
        const data = await res.json();
        setMatches(data);
        if (data.length > 0) {
          setSelectedMatchId(data[0].id);
        }
      }
    } catch (e) {
      const mockMatches = compId === 37 ? [
        {id: 3754058, home_team: {name: "Arsenal"}, away_team: {name: "Chelsea"}, match_date: "2016-05-15"},
        {id: 3754059, home_team: {name: "Manchester City"}, away_team: {name: "Liverpool"}, match_date: "2016-04-10"}
      ] : [
        {id: 432204, home_team: {name: "France"}, away_team: {name: "Argentina"}, match_date: "2018-06-30"}
      ];
      setMatches(mockMatches);
      setSelectedMatchId(mockMatches[0].id);
    }
  };

  const fetchMatchDetails = async (matchId: number) => {
    try {
      // 1. Stats
      const resStats = await fetch(`http://localhost:8000/api/v1/matches/${matchId}/stats`);
      if (resStats.ok) setMatchStats(await resStats.json());

      // 2. Shots
      const resShots = await fetch(`http://localhost:8000/api/v1/matches/${matchId}/shot-map`);
      if (resShots.ok) setShots(await resShots.json());

      // 3. Passing network
      const resPass = await fetch(`http://localhost:8000/api/v1/matches/${matchId}/passing-network?team_id=1`);
      if (resPass.ok) setPassingNetwork(await resPass.json());
    } catch (e) {
      // Set mock match values
      const isWC = matchId === 432204;
      setMatchStats({
        match_id: matchId,
        home_team: { name: isWC ? "France" : "Arsenal", score: isWC ? 4 : 2, possession: 56.4, shots: 14, shots_on_target: 6, xg: 1.78, passes: 512, pass_completion: 84.5 },
        away_team: { name: isWC ? "Argentina" : "Chelsea", score: isWC ? 3 : 1, possession: 43.6, shots: 9, shots_on_target: 3, xg: 0.94, passes: 384, pass_completion: 78.1 }
      });
      setShots([
        {id: "s1", player_name: isWC ? "Griezmann" : "Bukayo Saka", team_name: isWC ? "France" : "Arsenal", minute: 14, second: 22, x: 108.5, y: 32.4, outcome: "Goal", xg: 0.38, body_part: "Right Foot", under_pressure: true},
        {id: "s2", player_name: isWC ? "Mbappe" : "Kai Havertz", team_name: isWC ? "France" : "Arsenal", minute: 72, second: 14, x: 112.0, y: 41.5, outcome: "Goal", xg: 0.44, body_part: "Head", under_pressure: false},
        {id: "s3", player_name: isWC ? "Di Maria" : "Nicolas Jackson", team_name: isWC ? "Argentina" : "Chelsea", minute: 44, second: 50, x: 114.2, y: 38.0, outcome: "Goal", xg: 0.65, body_part: "Right Foot", under_pressure: true}
      ]);
      setPassingNetwork({
        nodes: [
          {id: 1, name: "Saliba", x: 34.0, y: 52.0, volume: 55},
          {id: 2, name: "Odegaard", x: 76.0, y: 50.0, volume: 48},
          {id: 3, name: "Saka", x: 88.0, y: 66.0, volume: 38},
          {id: 4, name: "Havertz", x: 95.0, y: 40.0, volume: 29}
        ],
        links: [
          {source: 1, target: 2, count: 18},
          {source: 2, target: 3, count: 24},
          {source: 3, target: 4, count: 12}
        ]
      });
    }
  };

  const fetchPlayers = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/v1/players");
      if (res.ok) {
        const data = await res.json();
        setPlayersList(data);
        if (data.length > 0) {
          setSelectedPlayerId(data[0].player_id);
        }
      }
    } catch (e) {
      const mockPlayers = [
        {player_id: 1, player_name: "Bukayo Saka"},
        {player_id: 11, player_name: "Martin Odegaard"},
        {player_id: 26, player_name: "Virgil van Dijk"}
      ];
      setPlayersList(mockPlayers);
      setSelectedPlayerId(1);
    }
  };

  const fetchPlayerSimilarity = async (playerId: number) => {
    try {
      const res = await fetch(`http://localhost:8000/api/v1/players/${playerId}/similar?top_n=3`);
      if (res.ok) {
        const data = await res.json();
        setSimilarityData(data);
        if (data.similar_players && data.similar_players.length > 0) {
          setSelectedMatchPlayer(data.similar_players[0]);
        }
      }
    } catch (e) {
      // Mock player similarity values
      const pName = playersList.find(p => p.player_id === playerId)?.player_name || "Bukayo Saka";
      const isSaka = pName.includes("Saka");
      const isOdegaard = pName.includes("Odegaard");

      const mockMatches: MatchPlayer[] = isSaka ? [
        {
          player_id: 2, player_name: "Lionel Messi", similarity_score: 0.9125,
          explanation: "Highly overlapping statistics in right-wing inside progression. Both generate massive progressive carries and key passes into the final third.",
          umap_x: 1.5, umap_y: 3.2,
          radar_comparison: [
            {metric: "Goals Per 90", player_value: 0.52, player_percentile: 88, match_value: 0.65, match_percentile: 94},
            {metric: "Key Passes Per 90", player_value: 2.2, player_percentile: 90, match_value: 2.8, match_percentile: 96},
            {metric: "Passes Per 90", player_value: 42.1, player_percentile: 82, match_value: 58.4, match_percentile: 91},
            {metric: "Tackles Per 90", player_value: 0.95, player_percentile: 62, match_value: 0.25, match_percentile: 32},
            {metric: "Carries Per 90", player_value: 38.5, player_percentile: 89, match_value: 41.2, match_percentile: 92}
          ]
        }
      ] : [
        {
          player_id: 12, player_name: "Kevin De Bruyne", similarity_score: 0.8842,
          explanation: "Similar playmaker signatures. High density of progressive passes in the right half-spaces and key chances created.",
          umap_x: -0.5, umap_y: 2.5,
          radar_comparison: [
            {metric: "Goals Per 90", player_value: 0.31, player_percentile: 78, match_value: 0.38, match_percentile: 82},
            {metric: "Key Passes Per 90", player_value: 3.1, player_percentile: 94, match_value: 3.8, match_percentile: 98},
            {metric: "Passes Per 90", player_value: 62.4, player_percentile: 89, match_value: 70.2, match_percentile: 93},
            {metric: "Tackles Per 90", player_value: 1.2, player_percentile: 71, match_value: 0.8, match_percentile: 55},
            {metric: "Carries Per 90", player_value: 28.5, player_percentile: 76, match_value: 31.0, match_percentile: 80}
          ]
        }
      ];

      setSimilarityData({
        player_id: playerId,
        player_name: pName,
        similar_players: mockMatches
      });
      setSelectedMatchPlayer(mockMatches[0]);
    }
  };

  const triggerEtlPipeline = async () => {
    setEtlRunning(true);
    try {
      const res = await fetch("http://localhost:8000/api/v1/etl/run", { method: "POST" });
      if (res.ok) alert("Data Ingestion ETL pipeline started in the background. Fresh StatsBomb data will load shortly!");
    } catch (e) {
      alert("Pipeline server offline. Simulation modes are running.");
    } finally {
      setTimeout(() => setEtlRunning(false), 2000);
    }
  };

  const triggerModelRetraining = async () => {
    setTrainingRunning(true);
    try {
      const res = await fetch("http://localhost:8000/api/v1/ml/train", { method: "POST" });
      if (res.ok) alert("ML Model training initiated in the background! Re-evaluating xG classifications and similarity vectors.");
    } catch (e) {
      alert("Model pipeline server offline. Simulation models loaded.");
    } finally {
      setTimeout(() => setTrainingRunning(false), 2000);
    }
  };

  const loggerFallback = (msg: string) => {
    console.log(`[Tactivision Fallback]: ${msg}`);
  };

  return (
    <div className="min-h-screen bg-background text-slate-100 flex flex-col font-sans">
      
      {/* Top Header Bar */}
      <header className="bg-card border-b border-border py-4 px-6 flex items-center justify-between sticky top-0 z-40 shadow-md">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-green-500 flex items-center justify-center font-black text-slate-950 text-xl shadow-lg">
            TV
          </div>
          <div>
            <h1 className="text-base font-extrabold tracking-tight">TactiVision AI</h1>
            <p className="text-[10px] text-muted-foreground uppercase tracking-widest font-semibold">
              Football Intelligence Platform
            </p>
          </div>
        </div>

        {/* MLOps controls */}
        <div className="flex items-center gap-4">
          <div className="hidden sm:flex items-center gap-1.5 px-3 py-1 bg-green-950/30 border border-green-800/40 rounded-full text-xs">
            <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
            <span className="text-green-400 font-semibold text-[10px] uppercase">Service Online</span>
          </div>

          <button
            onClick={triggerEtlPipeline}
            disabled={etlRunning}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 rounded-lg border border-border transition-colors disabled:opacity-50"
          >
            <Database className="w-3.5 h-3.5" />
            <span>{etlRunning ? "Ingesting..." : "Run ETL"}</span>
          </button>

          <button
            onClick={triggerModelRetraining}
            disabled={trainingRunning}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-green-600 hover:bg-green-500 text-slate-950 text-xs font-bold rounded-lg transition-colors shadow disabled:opacity-50"
          >
            <Cpu className="w-3.5 h-3.5" />
            <span>{trainingRunning ? "Training..." : "Retrain ML"}</span>
          </button>
        </div>
      </header>

      {/* Main Container Layout */}
      <div className="flex-1 flex flex-col md:flex-row">
        
        {/* Navigation Sidebar */}
        <aside className="w-full md:w-60 bg-card/60 md:border-r border-border p-4 space-y-2 md:space-y-6">
          <div className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground px-3 hidden md:block">
            Analytics Modules
          </div>
          <nav className="flex flex-row md:flex-col gap-1 overflow-x-auto md:overflow-x-visible">
            <button
              onClick={() => setActiveTab("match")}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-bold transition-all w-full shrink-0 ${
                activeTab === "match" 
                  ? "bg-green-500/10 text-green-400 border-l-2 border-green-500" 
                  : "text-slate-400 hover:bg-slate-800/40 hover:text-slate-200"
              }`}
            >
              <Map className="w-4 h-4" />
              <span>Match Dashboard</span>
            </button>

            <button
              onClick={() => setActiveTab("similarity")}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-bold transition-all w-full shrink-0 ${
                activeTab === "similarity" 
                  ? "bg-green-500/10 text-green-400 border-l-2 border-green-500" 
                  : "text-slate-400 hover:bg-slate-800/40 hover:text-slate-200"
              }`}
            >
              <Users className="w-4 h-4" />
              <span>Player Similarity</span>
            </button>

            <button
              onClick={() => setActiveTab("sandbox")}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-bold transition-all w-full shrink-0 ${
                activeTab === "sandbox" 
                  ? "bg-green-500/10 text-green-400 border-l-2 border-green-500" 
                  : "text-slate-400 hover:bg-slate-800/40 hover:text-slate-200"
              }`}
            >
              <Crosshair className="w-4 h-4" />
              <span>xG Sandbox</span>
            </button>

            <button
              onClick={() => setActiveTab("assistant")}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-bold transition-all w-full shrink-0 ${
                activeTab === "assistant" 
                  ? "bg-green-500/10 text-green-400 border-l-2 border-green-500" 
                  : "text-slate-400 hover:bg-slate-800/40 hover:text-slate-200"
              }`}
            >
              <Bot className="w-4 h-4" />
              <span>Tactical Assistant</span>
            </button>
          </nav>
        </aside>

        {/* Content Panel */}
        <main className="flex-1 p-6 overflow-y-auto space-y-6 max-w-6xl mx-auto w-full">
          
          {/* TAB 1: MATCH DASHBOARD */}
          {activeTab === "match" && (
            <div className="space-y-6 animate-fadeIn">
              {/* Filter controls */}
              <div className="bg-card border border-border p-4 rounded-xl flex flex-wrap gap-4 items-center">
                <div className="space-y-1">
                  <label className="block text-[10px] font-semibold text-muted-foreground uppercase">Competition</label>
                  <select
                    value={selectedComp || ""}
                    onChange={(e) => setSelectedComp(e.target.value)}
                    className="bg-background border border-border text-slate-200 text-xs p-2 rounded focus:outline-none"
                  >
                    {competitions.map(c => (
                      <option key={`${c.competition_id}-${c.season_id}`} value={`${c.competition_id}-${c.season_id}`}>
                        {c.competition_name} ({c.season_name})
                      </option>
                    ))}
                  </select>
                </div>

                <div className="space-y-1">
                  <label className="block text-[10px] font-semibold text-muted-foreground uppercase">MatchFixture</label>
                  <select
                    value={selectedMatchId || ""}
                    onChange={(e) => setSelectedMatchId(Number(e.target.value))}
                    className="bg-background border border-border text-slate-200 text-xs p-2 rounded focus:outline-none min-w-[200px]"
                  >
                    {matches.map(m => (
                      <option key={m.id} value={m.id}>
                        {m.home_team.name} vs {m.away_team.name} ({m.match_date})
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Match Stats Splits */}
              {matchStats && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {/* Scoreboard and general stats */}
                  <div className="md:col-span-1 bg-card border border-border p-5 rounded-xl flex flex-col justify-between shadow-md">
                    <div className="text-center space-y-2 border-b border-border/50 pb-4">
                      <div className="text-[10px] text-muted-foreground font-semibold uppercase tracking-wider">Match Result</div>
                      <div className="flex justify-center items-center gap-6">
                        <div>
                          <div className="text-base font-bold text-slate-200">{matchStats.home_team.name}</div>
                          <div className="text-2xl font-black text-slate-100">{matchStats.home_team.score}</div>
                        </div>
                        <div className="text-muted-foreground font-black text-lg">FT</div>
                        <div>
                          <div className="text-base font-bold text-slate-200">{matchStats.away_team.name}</div>
                          <div className="text-2xl font-black text-slate-100">{matchStats.away_team.score}</div>
                        </div>
                      </div>
                    </div>

                    <div className="space-y-3 pt-4 text-xs">
                      {/* Possession split */}
                      <div className="space-y-1">
                        <div className="flex justify-between text-muted-foreground font-semibold">
                          <span>Possession</span>
                          <span>{matchStats.home_team.possession}% vs {matchStats.away_team.possession}%</span>
                        </div>
                        <div className="h-2 bg-slate-800 rounded-full overflow-hidden flex">
                          <div className="bg-blue-500 h-full" style={{ width: `${matchStats.home_team.possession}%` }}></div>
                          <div className="bg-green-500 h-full flex-1"></div>
                        </div>
                      </div>

                      {/* xG split */}
                      <div className="flex justify-between py-1 border-b border-border/20">
                        <span className="text-muted-foreground">Expected Goals (xG)</span>
                        <span className="font-bold text-slate-200">{matchStats.home_team.xg} vs {matchStats.away_team.xg}</span>
                      </div>

                      {/* Shots split */}
                      <div className="flex justify-between py-1 border-b border-border/20">
                        <span className="text-muted-foreground">Shots (On Target)</span>
                        <span className="font-semibold text-slate-200">
                          {matchStats.home_team.shots} ({matchStats.home_team.shots_on_target}) vs {matchStats.away_team.shots} ({matchStats.away_team.shots_on_target})
                        </span>
                      </div>

                      {/* Passes split */}
                      <div className="flex justify-between py-1 border-b border-border/20">
                        <span className="text-muted-foreground">Pass Accuracy</span>
                        <span className="font-semibold text-slate-200">
                          {matchStats.home_team.pass_completion}% vs {matchStats.away_team.pass_completion}%
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Shot Map Visualization */}
                  <div className="md:col-span-2">
                    <ShotMap shots={shots} />
                  </div>
                </div>
              )}

              {/* Passing Network */}
              {passingNetwork && (
                <div className="border border-border bg-card/25 p-5 rounded-xl">
                  <PassingNetwork nodes={passingNetwork.nodes} links={passingNetwork.links} />
                </div>
              )}
            </div>
          )}

          {/* TAB 2: PLAYER SIMILARITY */}
          {activeTab === "similarity" && (
            <div className="space-y-6 animate-fadeIn">
              {/* Player search filter */}
              <div className="bg-card border border-border p-4 rounded-xl flex items-center gap-4">
                <div className="space-y-1">
                  <label className="block text-[10px] font-semibold text-muted-foreground uppercase">Target Player</label>
                  <select
                    value={selectedPlayerId || ""}
                    onChange={(e) => setSelectedPlayerId(Number(e.target.value))}
                    className="bg-background border border-border text-slate-200 text-xs p-2 rounded focus:outline-none min-w-[200px]"
                  >
                    {playersList.map(p => (
                      <option key={p.player_id} value={p.player_id}>
                        {p.player_name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {similarityData && (
                <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                  {/* Similarity List Sidebar */}
                  <div className="lg:col-span-1 bg-card border border-border rounded-xl p-4 space-y-3">
                    <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                      Nearest Neighbors (Top Matches)
                    </h4>
                    <div className="space-y-2">
                      {similarityData.similar_players && similarityData.similar_players.map((match: MatchPlayer) => (
                        <button
                          key={match.player_id}
                          onClick={() => setSelectedMatchPlayer(match)}
                          className={`w-full text-left p-3 rounded-lg border text-xs transition-all flex flex-col gap-1.5 ${
                            selectedMatchPlayer?.player_id === match.player_id
                              ? "bg-green-500/10 border-green-500/30 text-green-400"
                              : "bg-background/40 border-border/80 text-slate-300 hover:bg-slate-800/20"
                          }`}
                        >
                          <div className="font-bold flex justify-between">
                            <span>{match.player_name}</span>
                            <span className="text-green-500 font-black">
                              {(match.similarity_score * 100).toFixed(1)}%
                            </span>
                          </div>
                          <div className="text-[10px] text-muted-foreground line-clamp-2">
                            {match.explanation}
                          </div>
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Radar Chart Panel */}
                  <div className="lg:col-span-3">
                    {selectedMatchPlayer ? (
                      <PlayerRadar
                        playerName={similarityData.player_name}
                        matchPlayer={selectedMatchPlayer}
                      />
                    ) : (
                      <div className="bg-card border border-border rounded-xl p-8 text-center text-xs text-muted-foreground flex items-center justify-center min-h-[350px]">
                        Select a player from the neighbors list to view radar metrics.
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* TAB 3: xG SIMULATOR SANDBOX */}
          {activeTab === "sandbox" && (
            <div className="animate-fadeIn">
              <XgSandbox />
            </div>
          )}

          {/* TAB 4: TACTICAL assistant */}
          {activeTab === "assistant" && (
            <div className="animate-fadeIn">
              <AssistantChat />
            </div>
          )}

        </main>
      </div>

      {/* Footer bar */}
      <footer className="bg-card border-t border-border/60 py-3.5 px-6 text-center text-[10px] text-muted-foreground flex flex-col sm:flex-row justify-between items-center gap-2 mt-auto">
        <div>
          © {new Date().getFullYear()} TactiVision AI. Serving StatsBomb Open Data schemas.
        </div>
        <div className="flex gap-4">
          <span>Explainable ML Model (XGBoost/LR)</span>
          <span>•</span>
          <span>Conversational FAISS RAG Retriever</span>
        </div>
      </footer>

    </div>
  );
}
