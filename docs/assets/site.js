"use strict";
import { CUTOFF, parseMatches, demoTeams, demoForecast } from "./forecast.mjs";

const $ = selector => document.querySelector(selector);
const set = (selector, value) => { $(selector).textContent = String(value); };
const pct = number => (number * 100).toFixed(1) + "%";
const dateLabel = date => new Date(date + "T00:00:00Z").toLocaleDateString("en-GB", { day:"numeric",month:"short",year:"numeric",timeZone:"UTC" });
let matches = [];

function showError(message) {
  const node = $("#forecast-error");
  node.textContent = message;
  node.hidden = false;
}
function clearError() {
  $("#forecast-error").textContent = "";
  $("#forecast-error").hidden = true;
}
function renderForecast(result) {
  $("#result-placeholder").hidden = true;
  $("#result-content").hidden = false;
  set("#match-title", result.home_team + " vs " + result.away_team);
  set("#match-meta", "Historical cutoff / " + dateLabel(result.as_of));
  set("#home-goals", result.expected_goals.home.toFixed(2));
  set("#away-goals", result.expected_goals.away.toFixed(2));
  for (const name of ["home_win","draw","away_win"]) {
    const row = document.querySelector('[data-outcome="' + name + '"]');
    row.querySelector("strong").textContent = pct(result.probabilities[name]);
    row.querySelector("b").style.width = pct(result.probabilities[name]);
  }
  set("#over-goals", pct(result.probabilities.over_2_5));
  set("#btts", pct(result.probabilities.both_teams_score));
  const list = $("#scorelines");
  list.replaceChildren();
  result.top_scorelines.forEach(item => {
    const cell = document.createElement("div");
    const score = document.createElement("strong");
    const chance = document.createElement("span");
    score.textContent = item.score;
    chance.textContent = pct(item.probability);
    cell.append(score,chance);
    list.append(cell);
  });
  const latest = result.latest_training_match;
  const daysOld = Math.round((Date.parse(result.as_of+"T00:00:00Z")-Date.parse(latest+"T00:00:00Z"))/86400000);
  set("#forecast-provenance", result.historical_matches_used + " fictional matches used · Last eligible fictional match: " + dateLabel(latest) + " · " + daysOld + " days before cutoff · Research assumptions: independent goal counts, 365-day recency half-life, team strength shrinkage. No real forecasting accuracy is claimed.");
}
function fillTeams(teams) {
  const home = $("#home-team"), away = $("#away-team");
  for (const select of [home,away]) {
    select.replaceChildren();
    teams.forEach(name => {
      const option = document.createElement("option");
      option.value = name;
      option.textContent = name;
      select.append(option);
    });
  }
  home.value = teams.includes("Demo City") ? "Demo City" : teams[0];
  away.value = teams.includes("Demo East") ? "Demo East" : teams[1];
  if (home.value === away.value) away.value = teams.find(t => t !== home.value);
  $("#cutoff").value = CUTOFF;
}
function submit(event) {
  event.preventDefault();
  clearError();
  $("#result-content").hidden = true;
  $("#result-placeholder").hidden = false;
  try {
    const result=demoForecast(matches,$("#home-team").value,$("#away-team").value,$("#cutoff").value);
    renderForecast(result);
  } catch(error) {
    showError(error instanceof Error ? error.message : "Forecast calculation failed");
  }
}
async function initialize() {
  $("#forecast-form").addEventListener("submit",submit);
  try {
    const response = await fetch("./assets/matches.csv", {cache:"no-store"});
    if(!response.ok) throw new Error("Fictional demo data could not be loaded");
    matches=parseMatches(await response.text());
    const teams=demoTeams(matches);
    if (teams.length !== 6) throw new Error("Demo data does not contain six fictional clubs");
    fillTeams(teams);
    set("#match-count",matches.length);
    const last=matches.reduce((a,m)=>m.date>a?m.date:a,"");
    set("#dataset-line","DATA SOURCE / BUNDLED FICTIONAL CSV · "+matches.length+" MATCHES · LATEST RECORD "+dateLabel(last)+" · NOT LIVE");
    set("#load-status","Fictional demo data loaded — select any two different teams.");
    $("#forecast-button").disabled=false;
    renderForecast(demoForecast(matches,$("#home-team").value,$("#away-team").value,CUTOFF));
  } catch(error) {
    set("#load-status","Fictional demo data unavailable.");
    showError(error instanceof Error ? error.message : "Demo initialization failed");
  }
}
void initialize();
