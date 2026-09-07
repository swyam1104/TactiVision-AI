import logging
import numpy as np
from sqlalchemy.orm import Session
from app.models.models import Event, Match, Team, Player, Lineup
from app.services.xg_service import xg_service
from app.services.fixtures_data import get_fixture_metadata, generate_fixture_shots, generate_fixture_passing_network

logger = logging.getLogger(__name__)

class AnalyticsService:
    def get_match_stats(self, db: Session, match_id: int) -> dict:
        """Calculate match statistics (possession, shots, passes, etc.)."""
        try:
            # Fetch match info
            match = db.query(Match).filter_by(id=match_id).first()
            if not match:
                return self._get_mock_match_stats(match_id)
                
            home_team = db.query(Team).filter_by(id=match.home_team_id).first()
            away_team = db.query(Team).filter_by(id=match.away_team_id).first()
            
            home_name = home_team.name if home_team else "Home Team"
            away_name = away_team.name if away_team else "Away Team"
            home_id = match.home_team_id or 1
            away_id = match.away_team_id or 2
            
            # Calculate stats from events
            events = db.query(
                Event.team_id, 
                Event.type, 
                Event.outcome, 
                Event.detail_json,
                Event.x,
                Event.y,
                Event.under_pressure
            ).filter_by(match_id=match_id).all()
            
            if not events:
                return self._get_mock_match_stats(match_id, home_name, away_name, home_id, away_id)
                
            stats = {
                home_id: {"name": home_name, "shots": 0, "shots_on_target": 0, "xg": 0.0, "passes": 0, "completed_passes": 0, "tackles": 0, "fouls": 0},
                away_id: {"name": away_name, "shots": 0, "shots_on_target": 0, "xg": 0.0, "passes": 0, "completed_passes": 0, "tackles": 0, "fouls": 0}
            }
            
            total_possession_events = 0
            possession_counts = {home_id: 0, away_id: 0}
            
            for team_id, ev_type, outcome, detail, ev_x, ev_y, ev_under_pressure in events:
                if team_id not in stats:
                    continue
                    
                # Possession calculation based on total event counts (standard approximation)
                possession_counts[team_id] += 1
                total_possession_events += 1
                
                detail = detail or {}
                
                if ev_type == "Shot":
                    stats[team_id]["shots"] += 1
                    if outcome in ["Goal", "Saved", "Saved to Post", "Saved Off Target"]:
                        stats[team_id]["shots_on_target"] += 1
                        
                    # Re-compute xG dynamically using our custom model so it exactly matches get_shot_map()
                    body_part = detail.get("body_part", "Foot")
                    technique = detail.get("technique", "Normal")
                    shot_type = detail.get("type", "Open Play")
                    
                    custom_xg = xg_service.predict_xg(
                        x=ev_x or 0.0,
                        y=ev_y or 0.0,
                        body_part=body_part,
                        technique=technique,
                        shot_type=shot_type,
                        under_pressure=bool(ev_under_pressure)
                    )
                    stats[team_id]["xg"] += custom_xg
                    
                elif ev_type == "Pass":
                    stats[team_id]["passes"] += 1
                    if not outcome or outcome == "Complete":
                        stats[team_id]["completed_passes"] += 1
                        
                elif ev_type in ["Tackle", "Duel"]:
                    stats[team_id]["tackles"] += 1
                    
                elif ev_type == "Foul Committed":
                    stats[team_id]["fouls"] += 1
                    
            # Format splits
            home_stats = stats[home_id]
            away_stats = stats[away_id]
            
            home_possession = round((possession_counts[home_id] / total_possession_events * 100), 1) if total_possession_events > 0 else 50.0
            away_possession = round(100.0 - home_possession, 1)
            
            return {
                "match_id": match_id,
                "home_team": {
                    "id": home_id,
                    "name": home_stats["name"],
                    "score": match.home_score if match.home_score is not None else 0,
                    "possession": home_possession,
                    "shots": home_stats["shots"],
                    "shots_on_target": home_stats["shots_on_target"],
                    "xg": round(home_stats["xg"], 2),
                    "passes": home_stats["passes"],
                    "pass_completion": round((home_stats["completed_passes"] / home_stats["passes"] * 100), 1) if home_stats["passes"] > 0 else 0.0,
                    "tackles": home_stats["tackles"],
                    "fouls": home_stats["fouls"]
                },
                "away_team": {
                    "id": away_id,
                    "name": away_stats["name"],
                    "score": match.away_score if match.away_score is not None else 0,
                    "possession": away_possession,
                    "shots": away_stats["shots"],
                    "shots_on_target": away_stats["shots_on_target"],
                    "xg": round(away_stats["xg"], 2),
                    "passes": away_stats["passes"],
                    "pass_completion": round((away_stats["completed_passes"] / away_stats["passes"] * 100), 1) if away_stats["passes"] > 0 else 0.0,
                    "tackles": away_stats["tackles"],
                    "fouls": away_stats["fouls"]
                }
            }
        except Exception as e:
            logger.warning(f"Error querying match stats from DB for match {match_id}: {e}. Returning mock stats.")
            return self._get_mock_match_stats(match_id)

    def get_shot_map(self, db: Session, match_id: int) -> list:
        """Get shot details with coordinates and custom xG valuation."""
        try:
            events = db.query(Event).filter(Event.match_id == match_id, Event.type == "Shot").all()
            if not events:
                match = db.query(Match).filter_by(id=match_id).first()
                home_name, away_name = "Arsenal", "Chelsea"
                home_id, away_id = 1, 2
                if match:
                    home_t = db.query(Team).filter_by(id=match.home_team_id).first()
                    away_t = db.query(Team).filter_by(id=match.away_team_id).first()
                    if home_t:
                        home_name, home_id = home_t.name, home_t.id
                    if away_t:
                        away_name, away_id = away_t.name, away_t.id
                return self._get_mock_shot_map(match_id, home_name, away_name, home_id, away_id)
                
            shots = []
            for ev in events:
                detail = ev.detail_json or {}
                
                # Predict dynamic xG using our trained model
                body_part = detail.get("body_part", "Foot")
                technique = detail.get("technique", "Normal")
                shot_type = detail.get("type", "Open Play")
                
                custom_xg = xg_service.predict_xg(
                    x=ev.x,
                    y=ev.y,
                    body_part=body_part,
                    technique=technique,
                    shot_type=shot_type,
                    under_pressure=ev.under_pressure
                )
                
                player_name = db.query(Player.name).filter_by(id=ev.player_id).scalar() or "Unknown Player"
                team_name = db.query(Team.name).filter_by(id=ev.team_id).scalar() or "Unknown Team"
                
                shots.append({
                    "id": ev.id,
                    "player_id": ev.player_id,
                    "player_name": player_name,
                    "team_id": ev.team_id,
                    "team_name": team_name,
                    "minute": ev.minute,
                    "second": ev.second,
                    "x": ev.x,
                    "y": ev.y,
                    "outcome": ev.outcome,
                    "xg": custom_xg,
                    "statsbomb_xg": detail.get("statsbomb_xg", 0.0),
                    "body_part": body_part,
                    "under_pressure": ev.under_pressure
                })
            return shots
        except Exception as e:
            logger.warning(f"Error querying shot map from DB for match {match_id}: {e}. Returning mock shot map.")
            return self._get_mock_shot_map(match_id)

    def get_passing_network(self, db: Session, match_id: int, team_id: int) -> dict:
        """Compute passing network nodes and link connections."""
        try:
            # Find players in lineup
            lineups = db.query(Lineup).filter_by(match_id=match_id, team_id=team_id).all()
            if not lineups:
                # Fallback: check if players exist for this match & team in Event table
                event_players = db.query(Event.player_id).filter(
                    Event.match_id == match_id,
                    Event.team_id == team_id,
                    Event.player_id.isnot(None)
                ).distinct().all()
                if not event_players:
                    return self._get_mock_passing_network(team_id, match_id=match_id)
                player_names = {p[0]: db.query(Player.name).filter_by(id=p[0]).scalar() or f"Player {p[0]}" for p in event_players}
            else:
                player_names = {l.player_id: db.query(Player.name).filter_by(id=l.player_id).scalar() or f"Player {l.player_id}" for l in lineups}
            
            # Select all complete passes using proper SQLAlchemy is_(None)
            passes = db.query(Event).filter(
                Event.match_id == match_id,
                Event.team_id == team_id,
                Event.type == "Pass",
                (Event.outcome.is_(None)) | (Event.outcome == "Complete")
            ).order_by(Event.index).all()
            
            if not passes:
                return self._get_mock_passing_network(team_id, player_names, match_id=match_id)
                
            # Calculate average positions for each player
            player_coords = {}
            pass_counts = {}
            
            for p in passes:
                pid = p.player_id
                px, py = p.x, p.y
                
                if pid not in player_coords:
                    player_coords[pid] = []
                if px is not None and py is not None:
                    player_coords[pid].append((px, py))
                    
                # Count links
                detail = p.detail_json or {}
                recipient_id = detail.get("recipient_id")
                
                # 1. Use recipient_id stored by ETL if available
                if recipient_id and recipient_id != pid:
                    pair = (pid, recipient_id)
                    pass_counts[pair] = pass_counts.get(pair, 0) + 1
                else:
                    # 2. Sequence matching fallback heuristic: look at next event
                    next_ev = db.query(Event).filter(
                        Event.match_id == match_id,
                        Event.index == p.index + 1
                    ).first()
                    
                    if next_ev and next_ev.team_id == team_id and next_ev.player_id and next_ev.player_id != pid:
                        pair = (pid, next_ev.player_id)
                        pass_counts[pair] = pass_counts.get(pair, 0) + 1
                    
            # Build nodes
            nodes = []
            for pid, coords in player_coords.items():
                if not coords:
                    continue
                avg_x = float(np.mean([c[0] for c in coords]))
                avg_y = float(np.mean([c[1] for c in coords]))
                
                # Total passes made by this player
                vol = sum(1 for p in passes if p.player_id == pid)
                
                nodes.append({
                    "id": pid,
                    "name": player_names.get(pid, f"Player {pid}"),
                    "x": round(avg_x, 1),
                    "y": round(avg_y, 1),
                    "volume": vol
                })
                
            # Build links
            links = []
            for (source, target), count in pass_counts.items():
                # Only include connections with at least 2 passes to show clear passing lanes
                if count >= 2:
                    links.append({
                        "source": source,
                        "target": target,
                        "count": count
                    })
                    
            return {
                "team_id": team_id,
                "nodes": nodes,
                "links": links
            }
        except Exception as e:
            logger.warning(f"Error computing passing network from DB for match {match_id}, team {team_id}: {e}. Returning mock network.")
            return self._get_mock_passing_network(team_id, match_id=match_id)

    def get_touches_heatmap(self, db: Session, match_id: int, team_id: int = None, player_id: int = None) -> list:
        """Get ball-touch coordinates for heatmap generation."""
        try:
            query = db.query(Event.x, Event.y).filter(
                Event.match_id == match_id,
                Event.x.isnot(None),
                Event.y.isnot(None),
                Event.type.in_(["Pass", "Carry", "Shot", "Ball Recovery", "Duel", "Interception"])
            )
            
            if team_id:
                query = query.filter(Event.team_id == team_id)
            if player_id:
                query = query.filter(Event.player_id == player_id)
                
            events = query.all()
            if not events:
                return self._get_mock_touches()
                
            return [{"x": round(e[0], 1), "y": round(e[1], 1)} for e in events]
        except Exception as e:
            logger.warning(f"Error querying touch heatmap from DB for match {match_id}: {e}. Returning mock touches.")
            return self._get_mock_touches()

    # Mock fallbacks for offline testing/development with deterministic values
    
    # Mock fallbacks for offline testing/development with deterministic values
    
    def _get_mock_match_stats(self, match_id: int, home_name: str = None, away_name: str = None, home_id: int = None, away_id: int = None) -> dict:
        fixture = get_fixture_metadata(match_id)
        # Deep copy to avoid mutating cache
        f = {
            "id": match_id,
            "competition_id": fixture.get("competition_id", 2),
            "season_id": fixture.get("season_id", 27),
            "home_team": {"id": home_id or fixture["home_team"]["id"], "name": home_name or fixture["home_team"]["name"]},
            "away_team": {"id": away_id or fixture["away_team"]["id"], "name": away_name or fixture["away_team"]["name"]},
            "home_score": fixture.get("home_score", 1),
            "away_score": fixture.get("away_score", 0),
            "stadium": fixture.get("stadium", "Stadium")
        }
        shots = generate_fixture_shots(f)
        h_shots = [s for s in shots if s["team_id"] == f["home_team"]["id"]]
        a_shots = [s for s in shots if s["team_id"] == f["away_team"]["id"]]
        
        home_xg = round(sum(s["xg"] for s in h_shots), 2)
        away_xg = round(sum(s["xg"] for s in a_shots), 2)
        
        h_score = f["home_score"]
        a_score = f["away_score"]
        home_poss = 56.4 if h_score >= a_score else 44.2
        away_poss = round(100.0 - home_poss, 1)

        return {
            "match_id": match_id,
            "home_team": {
                "id": f["home_team"]["id"],
                "name": f["home_team"]["name"],
                "score": h_score,
                "possession": home_poss,
                "shots": len(h_shots),
                "shots_on_target": len([s for s in h_shots if s["outcome"] in ["Goal", "Saved"]]),
                "xg": home_xg,
                "passes": 490 + (f["home_team"]["id"] % 60),
                "pass_completion": round(83.0 + (f["home_team"]["id"] % 5), 1),
                "tackles": 16 + (f["home_team"]["id"] % 8),
                "fouls": 10 + (f["home_team"]["id"] % 5)
            },
            "away_team": {
                "id": f["away_team"]["id"],
                "name": f["away_team"]["name"],
                "score": a_score,
                "possession": away_poss,
                "shots": len(a_shots),
                "shots_on_target": len([s for s in a_shots if s["outcome"] in ["Goal", "Saved"]]),
                "xg": away_xg,
                "passes": 400 + (f["away_team"]["id"] % 60),
                "pass_completion": round(79.0 + (f["away_team"]["id"] % 5), 1),
                "tackles": 19 + (f["away_team"]["id"] % 8),
                "fouls": 13 + (f["away_team"]["id"] % 5)
            }
        }

    def _get_mock_shot_map(self, match_id: int, home_name: str = None, away_name: str = None, home_id: int = None, away_id: int = None) -> list:
        fixture = get_fixture_metadata(match_id)
        f = {
            "id": match_id,
            "home_team": {"id": home_id or fixture["home_team"]["id"], "name": home_name or fixture["home_team"]["name"]},
            "away_team": {"id": away_id or fixture["away_team"]["id"], "name": away_name or fixture["away_team"]["name"]},
            "home_score": fixture.get("home_score", 1),
            "away_score": fixture.get("away_score", 0)
        }
        return generate_fixture_shots(f)

    def _get_mock_passing_network(self, team_id: int, names_map: dict = None, match_id: int = None) -> dict:
        fixture = get_fixture_metadata(match_id or 3754058)
        # If team_id doesn't match home or away, determine based on team_id parity
        home_id = fixture["home_team"]["id"]
        away_id = fixture["away_team"]["id"]
        target_id = team_id if team_id in [home_id, away_id] else (away_id if team_id % 2 == 0 else home_id)
        network = generate_fixture_passing_network(fixture, target_id)
        
        if names_map:
            for node in network["nodes"]:
                if node["id"] in names_map:
                    node["name"] = names_map[node["id"]]
        return network

    def _get_mock_touches(self) -> list:
        # Generate cluster of points on the right side and central third deterministically without modifying global RNG
        rng = np.random.RandomState(42)
        touches = []
        for _ in range(120):
            touches.append({"x": round(float(rng.normal(88.0, 8.0)), 1), "y": round(float(rng.normal(65.0, 7.0)), 1)})
        for _ in range(80):
            touches.append({"x": round(float(rng.normal(78.0, 10.0)), 1), "y": round(float(rng.normal(48.0, 10.0)), 1)})
        for _ in range(60):
            touches.append({"x": round(float(rng.uniform(20.0, 110.0)), 1), "y": round(float(rng.uniform(5.0, 75.0)), 1)})
            
        # Clean coordinates out of pitch bounds
        return [{"x": float(np.clip(t["x"], 0.0, 120.0)), "y": float(np.clip(t["y"], 0.0, 80.0))} for t in touches]

analytics_service = AnalyticsService()
