/* Browser-only reproduction of the research Poisson baseline.
 * Source algorithm: src/football_intel/model.py
 * Only bundled fictional match data is accepted.
 */
export const CUTOFF = "2025-07-19";
const MS_PER_DAY = 86400000;
const asUtc = value => Date.parse(value + "T00:00:00Z");

export function parseMatches(csv) {
  const lines = String(csv).trim().replace(/^\uFEFF/, "").split(/\r?\n/);
  if (lines.shift() !== "Date,HomeTeam,AwayTeam,FTHG,FTAG") throw new Error("Unsupported match-data format");
  const matches = lines.filter(Boolean).map(line => {
    const cells = line.split(",");
    if (cells.length !== 5) throw new Error("Invalid match row");
    const [date, home, away, gh, ga] = cells;
    const day = asUtc(date);
    if (!Number.isFinite(day) || new Date(day).toISOString().slice(0,10) !== date ||
      !/^Demo (North|South|East|West|City|United)$/.test(home) ||
      !/^Demo (North|South|East|West|City|United)$/.test(away) ||
      home === away || !/^\d+$/.test(gh) || !/^\d+$/.test(ga) ||
      Number(gh) > 30 || Number(ga) > 30) throw new Error("Unsupported demonstration record");
    return {date, home, away, homeGoals:Number(gh), awayGoals:Number(ga)};
  });
  if (!matches.length) throw new Error("No fictional fixtures available");
  return matches;
}

export function demoTeams(matches) {
  return [...new Set(matches.flatMap(m => [m.home, m.away]))].sort();
}

function add(map,key,value) { map.set(key,(map.get(key) ?? 0)+value); }
function ratio(total,count,team,prior,shrink=6) {
  return ((total.get(team) ?? 0)+prior*shrink)/((count.get(team) ?? 0)+shrink)/prior;
}
function poisson(lambda,limit) {
  const result=[Math.exp(-lambda)];
  for(let n=1;n<=limit;n++) result.push(result[n-1]*lambda/n);
  return result;
}

export function demoForecast(matches,home,away,cutoff=CUTOFF) {
  if (!matches.length || !home || !away || home === away) throw new Error("Select two different demo teams");
  const teams=demoTeams(matches);
  if (!teams.includes(home) || !teams.includes(away)) throw new Error("Unknown fictional team");
  const deadline=asUtc(cutoff);
  if (!Number.isFinite(deadline)) throw new Error("Invalid cutoff date");
  const past=matches.filter(m=>asUtc(m.date)<deadline);
  if (!past.length) throw new Error("No recorded fictional matches before cutoff");
  const homeFor=new Map(),homeAgainst=new Map(),homeCount=new Map();
  const awayFor=new Map(),awayAgainst=new Map(),awayCount=new Map();
  let sumHome=0,sumAway=0,weights=0;
  for(const m of past) {
    const age=(deadline-asUtc(m.date))/MS_PER_DAY;
    const w=Math.exp(-Math.log(2)*age/365);
    sumHome+=w*m.homeGoals;
    sumAway+=w*m.awayGoals;
    weights+=w;
    add(homeFor,m.home,w*m.homeGoals);
    add(homeAgainst,m.home,w*m.awayGoals);
    add(homeCount,m.home,w);
    add(awayFor,m.away,w*m.awayGoals);
    add(awayAgainst,m.away,w*m.homeGoals);
    add(awayCount,m.away,w);
  }
  const bh=Math.max(sumHome/weights,.10),ba=Math.max(sumAway/weights,.10);
  const lh=bh*ratio(homeFor,homeCount,home,bh)*ratio(awayAgainst,awayCount,away,bh);
  const la=ba*ratio(awayFor,awayCount,away,ba)*ratio(homeAgainst,homeCount,home,ba);
  const largest=Math.max(lh,la);
  const limit=Math.max(20,Math.floor(largest+12*Math.sqrt(largest)));
  const ph=poisson(lh,limit),pa=poisson(la,limit);
  const mass=ph.reduce((a,b)=>a+b,0)*pa.reduce((a,b)=>a+b,0);
  const probs={home_win:0,draw:0,away_win:0,over_2_5:0,both_teams_score:0};
  const scorelines=[];
  for(let i=0;i<ph.length;i++) for(let j=0;j<pa.length;j++){
    const p=ph[i]*pa[j]/mass;
    probs[i>j?"home_win":i===j?"draw":"away_win"]+=p;
    if(i+j>=3) probs.over_2_5+=p;
    if(i>=1&&j>=1) probs.both_teams_score+=p;
    scorelines.push({score:`${i}-${j}`,probability:p,i,j});
  }
  scorelines.sort((a,b)=>b.probability-a.probability||b.i-a.i||b.j-a.j);
  return {
    model:"weighted_poisson_baseline_v0.1",as_of:cutoff,home_team:home,away_team:away,
    expected_goals:{home:lh,away:la},
    probabilities:{...probs,under_2_5:1-probs.over_2_5},
    top_scorelines:scorelines.slice(0,5),
    historical_matches_used:past.length,
    latest_training_match:past.reduce((a,m)=>m.date>a?m.date:a,"")
  };
}
