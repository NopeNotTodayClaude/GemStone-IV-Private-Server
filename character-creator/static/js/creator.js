/**
 * GemStone IV — Character Creator
 * Multi-step wizard + live canvas portrait renderer
 *
 * Portrait renders based on: gender, race, hair color, profession
 * Everything else (eye color, skin, style) is text-only — no 100k image matrix.
 *
 * Steps: 1=Name  2=Gender  3=Race  4=Profession  5=Culture
 *        6=Stats  7=Appearance  8=Age  9=Summary
 */

"use strict";

// ─── Token from URL ───────────────────────────────────────────────────────────
const TOKEN = new URLSearchParams(location.search).get("token") || "";

// ─── State ────────────────────────────────────────────────────────────────────
const State = {
  step: 1,
  totalSteps: 9,
  data: {},        // game data from API
  ch: {            // character being built
    name:          "",
    gender:        "",
    race_id:       null,
    starting_room: null,
    prof_id:       null,
    culture_key:   null,
    culture_name:  "",
    stats:         Array(10).fill(20),
    hair_color:    "",
    hair_style:    "",
    eye_color:     "",
    skin_tone:     "",
    height:        68,
    age_stage:     null,
    age_value:     null,
  },
  nameValid:  false,
  nameChecked: false,
  nameTimer: null,
};

// ─── Age ranges (race-independent defaults; production would load from API) ───
const AGE_RANGES = [
  [20,25],[26,31],[32,37],[38,43],[44,49],
  [50,55],[56,61],[62,67],[68,73],[74,79],[80,999],
];

// ─── Boot ─────────────────────────────────────────────────────────────────────
window.addEventListener("DOMContentLoaded", async () => {
  if (!TOKEN) {
    document.getElementById("creator-main").innerHTML =
      '<p style="color:var(--red);font-style:italic;margin-top:2rem">No token provided. Please launch character creation from the game.</p>';
    return;
  }
  try {
    const resp = await fetch(`/api/cc/data?token=${TOKEN}`);
    if (!resp.ok) throw new Error(await resp.text());
    State.data = await resp.json();
  } catch(e) {
    document.getElementById("creator-main").innerHTML =
      `<p style="color:var(--red);font-style:italic;margin-top:2rem">Failed to load game data: ${e.message}</p>`;
    return;
  }
  // Init stats to proper minimums once we have data
  State.ch.stats = Array(10).fill(20);
  State.ch.starting_room = State.data.default_starting_room || 221;
  renderStep();
  buildStepPills();
  Portrait.draw();
});

// ─── Step pills ───────────────────────────────────────────────────────────────
const STEP_LABELS = ["Name","Gender","Race","Profession","Culture","Stats","Appearance","Age","Summary"];

function buildStepPills() {
  const el = document.getElementById("step-pills");
  el.innerHTML = STEP_LABELS.map((_, i) =>
    `<div class="step-pill" id="pill-${i+1}"></div>`
  ).join("");
  updatePills();
}

function updatePills() {
  STEP_LABELS.forEach((_, i) => {
    const pill = document.getElementById(`pill-${i+1}`);
    if (!pill) return;
    pill.className = "step-pill" +
      (i+1 < State.step ? " done" : i+1 === State.step ? " active" : "");
  });
  document.getElementById("step-counter").textContent =
    `Step ${State.step} of ${State.totalSteps}`;
}

// ─── Navigation ───────────────────────────────────────────────────────────────
const Creator = window.Creator = {
  next() {
    if (!canAdvance()) return;
    if (State.step === State.totalSteps) {
      showConfirmModal();
      return;
    }
    State.step++;
    renderStep();
    updatePills();
    window.scrollTo(0, 0);
  },
  back() {
    if (State.step <= 1) return;
    State.step--;
    renderStep();
    updatePills();
    window.scrollTo(0, 0);
  },
  closeConfirmModal() {
    document.getElementById("confirm-overlay").style.display = "none";
  },
  async submitCharacter() {
    const btn = document.getElementById("confirm-create-btn");
    const spinner = document.getElementById("create-spinner");
    btn.disabled = true;
    spinner.style.display = "inline-block";

    const race = getSelectedRace();
    const prof = getSelectedProf();

    const payload = {
      token:           TOKEN,
      name:            State.ch.name,
      gender:          State.ch.gender,
      race_id:         State.ch.race_id,
      starting_room:   State.ch.starting_room,
      race_name:       race ? race.name : "",
      profession_id:   State.ch.prof_id,
      profession_name: prof ? prof.name : "",
      culture_key:     State.ch.culture_key,
      culture_name:    State.ch.culture_name,
      stats:           State.ch.stats,
      hair_color:      State.ch.hair_color,
      hair_style:      State.ch.hair_style,
      eye_color:       State.ch.eye_color,
      skin_tone:       State.ch.skin_tone,
      height:          State.ch.height,
      age:             State.ch.age_value,
    };

    try {
      const resp = await fetch("/api/cc/create", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify(payload),
      });
      const result = await resp.json();
      if (!resp.ok || result.error) {
        alert("Error: " + (result.error || "Unknown error"));
        btn.disabled = false;
        spinner.style.display = "none";
        return;
      }
      Creator.closeConfirmModal();
      showSuccessScreen(result);
    } catch(e) {
      alert("Network error: " + e.message);
      btn.disabled = false;
      spinner.style.display = "none";
    }
  }
};

function canAdvance() {
  const ch = State.ch;
  switch(State.step) {
    case 1: return State.nameValid && State.nameChecked;
    case 2: return !!ch.gender;
    case 3: return ch.race_id !== null;
    case 4: return ch.prof_id !== null;
    case 5: return true; // culture always optional
    case 6: return getRemainingPoints() === 0;
    case 7: return ch.hair_color && ch.hair_style && ch.eye_color && ch.skin_tone;
    case 8: return ch.age_value !== null;
    case 9: return true;
    default: return true;
  }
}

function setNextEnabled(enabled) {
  document.getElementById("btn-next").disabled = !enabled;
}

function setBackEnabled(enabled) {
  document.getElementById("btn-back").disabled = !enabled;
}

// ─── Render dispatcher ────────────────────────────────────────────────────────
function renderStep() {
  const main = document.getElementById("creator-main");
  setBackEnabled(State.step > 1);
  setNextEnabled(canAdvance());

  // Update next button label
  const nextBtn = document.getElementById("btn-next");
  nextBtn.textContent = State.step === State.totalSteps ? "Create Character →" : "Next →";

  switch(State.step) {
    case 1: renderName(main);       break;
    case 2: renderGender(main);     break;
    case 3: renderRace(main);       break;
    case 4: renderProfession(main); break;
    case 5: renderCulture(main);    break;
    case 6: renderStats(main);      break;
    case 7: renderAppearance(main); break;
    case 8: renderAge(main);        break;
    case 9: renderSummary(main);    break;
  }
}

// ─── Step 1: Name ─────────────────────────────────────────────────────────────
function renderName(main) {
  main.innerHTML = `
    <div class="step-panel">
      <div class="step-title">Choose Your Name</div>
      <div class="step-subtitle">Your name will be known throughout Elanthia. Choose wisely.</div>
      <div class="name-input-wrap">
        <input class="name-input" id="name-input" type="text"
          placeholder="Enter name..." maxlength="20"
          value="${esc(State.ch.name)}" autocomplete="off" autocorrect="off"
          spellcheck="false">
        <div class="name-status" id="name-status">2–20 letters, no spaces or numbers.</div>
      </div>
    </div>`;

  const inp = document.getElementById("name-input");
  inp.focus();
  inp.addEventListener("input", onNameInput);
  inp.addEventListener("keydown", e => { if(e.key === "Enter") Creator.next(); });

  // Restore prior validation state
  if (State.ch.name) {
    validateNameLocal(State.ch.name);
    if (State.nameValid) setNextEnabled(true);
  }
}

function onNameInput(e) {
  const val = e.target.value.trim();
  State.ch.name = val;
  State.nameValid = false;
  State.nameChecked = false;
  setNextEnabled(false);
  clearTimeout(State.nameTimer);
  validateNameLocal(val);
  if (State.nameValid) {
    State.nameTimer = setTimeout(() => checkNameRemote(val), 480);
  }
}

function validateNameLocal(val) {
  const inp = document.getElementById("name-input");
  const status = document.getElementById("name-status");
  if (!inp) return;
  if (!val || val.length < 2) {
    setStatus(status, "2–20 letters, no spaces or numbers.", "");
    inp.className = "name-input";
    State.nameValid = false;
    return;
  }
  if (!/^[A-Za-z]+$/.test(val)) {
    setStatus(status, "Letters only — no spaces, numbers, or symbols.", "bad");
    inp.className = "name-input invalid";
    State.nameValid = false;
    return;
  }
  if (val.length > 20) {
    setStatus(status, "Maximum 20 characters.", "bad");
    inp.className = "name-input invalid";
    State.nameValid = false;
    return;
  }
  State.nameValid = true;
  setStatus(status, "Checking availability...", "checking");
  inp.className = "name-input";
}

async function checkNameRemote(val) {
  const status = document.getElementById("name-status");
  const inp    = document.getElementById("name-input");
  if (!status || !inp) return;
  try {
    const resp = await fetch("/api/cc/check_name", {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({token: TOKEN, name: val}),
    });
    const result = await resp.json();
    if (result.available) {
      setStatus(status, `✓ "${cap(val)}" is available.`, "ok");
      inp.className = "name-input valid";
      State.nameChecked = true;
      State.ch.name = cap(val);
      updateAvatarName();
      setNextEnabled(true);
    } else {
      setStatus(status, result.reason || "Name unavailable.", "bad");
      inp.className = "name-input invalid";
      State.nameChecked = false;
      State.nameValid   = false;
      setNextEnabled(false);
    }
  } catch {
    setStatus(status, "Could not verify — check your connection.", "bad");
  }
}

function setStatus(el, msg, cls) {
  if (!el) return;
  el.textContent = msg;
  el.className = "name-status" + (cls ? " " + cls : "");
}

// ─── Step 2: Gender ───────────────────────────────────────────────────────────
function renderGender(main) {
  main.innerHTML = `
    <div class="step-panel">
      <div class="step-title">Choose Your Gender</div>
      <div class="step-subtitle">This affects your character's portrait and in-game pronouns.</div>
      <div class="gender-grid">
        ${genderCard("female","Female","♀")}
        ${genderCard("male","Male","♂")}
      </div>
    </div>`;

  main.querySelectorAll(".select-card").forEach(card => {
    card.addEventListener("click", () => {
      State.ch.gender = card.dataset.value;
      main.querySelectorAll(".select-card").forEach(c => c.classList.remove("selected"));
      card.classList.add("selected");
      Portrait.draw();
      setNextEnabled(true);
    });
  });

  // Restore selection
  if (State.ch.gender) {
    const sel = main.querySelector(`[data-value="${State.ch.gender}"]`);
    if (sel) sel.classList.add("selected");
  }
}

function genderCard(val, label, symbol) {
  const sel = State.ch.gender === val ? " selected" : "";
  return `<div class="select-card${sel}" data-value="${val}" style="text-align:center;padding:2rem 1rem;">
    <div style="font-size:2.5rem;margin-bottom:0.5rem;color:var(--gold)">${symbol}</div>
    <div class="card-name">${label}</div>
  </div>`;
}

// ─── Step 3: Race ─────────────────────────────────────────────────────────────
function renderRace(main) {
  const abbrevs = State.data.stat_abbrevs || [];
  const raceCards = State.data.races.map(r => {
    const mods = r.stat_mods || [];
    const modStr = mods.map((m,i)=>m!==0?(m>0?`+${m}`:`${m}`)+" "+abbrevs[i]:null)
                       .filter(Boolean).join(" · ");
    const sel = State.ch.race_id === r.id ? " selected" : "";
    return `<div class="select-card race-card${sel}" data-id="${r.id}">
      <div class="card-name">${r.name}</div>
      <div class="card-desc">${r.desc}</div>
      <div class="card-desc">Starts in ${esc(r.start_town || "Unknown")}</div>
      ${modStr ? `<div class="card-mods">${modStr}</div>` : ""}
    </div>`;
  }).join("");

  main.innerHTML = `
    <div class="step-panel">
      <div class="step-title">Choose Your Race</div>
      <div class="step-subtitle">Race controls your stat modifiers and starting city.</div>
      <div class="card-grid">${raceCards}</div>
    </div>`;

  main.querySelectorAll(".race-card").forEach(card => {
    card.addEventListener("click", () => {
      State.ch.race_id = parseInt(card.dataset.id);
      const race = getSelectedRace();
      State.ch.starting_room = Number((race && race.start_room) || State.data.default_starting_room || 221);
      State.ch.culture_key  = null;  // reset culture on race change
      State.ch.culture_name = "";
      main.querySelectorAll(".race-card").forEach(c => c.classList.remove("selected"));
      card.classList.add("selected");
      Portrait.draw();
      updateAvatarLines();
      setNextEnabled(canAdvance());
    });
  });

}

// ─── Step 4: Profession ───────────────────────────────────────────────────────
function renderProfession(main) {
  const abbrevs = State.data.stat_abbrevs || [];
  const cards = State.data.professions.map(p => {
    const sel = State.ch.prof_id === p.id ? " selected" : "";
    const p1 = abbrevs[p.primes[0]] || "";
    const p2 = abbrevs[p.primes[1]] || "";
    const manaStr = p.mana > 0 ? ` &nbsp;·&nbsp; Mana/lvl: ${p.mana}` : "";
    return `<div class="select-card${sel}" data-id="${p.id}">
      <div class="type-badge ${p.type}">${p.type}</div>
      <div class="card-name">${p.name}</div>
      <div class="card-desc">${p.desc}</div>
      <div class="card-meta">HP/lvl: ${p.hp}${manaStr}</div>
      <div class="card-meta" style="color:var(--gold-dim)">Primes: ${p1} &amp; ${p2}</div>
    </div>`;
  }).join("");

  main.innerHTML = `
    <div class="step-panel">
      <div class="step-title">Choose Your Profession</div>
      <div class="step-subtitle">Your profession determines training costs, prime requisites, and playstyle.</div>
      <div class="card-grid">${cards}</div>
    </div>`;

  main.querySelectorAll(".select-card").forEach(card => {
    card.addEventListener("click", () => {
      State.ch.prof_id = parseInt(card.dataset.id);
      main.querySelectorAll(".select-card").forEach(c => c.classList.remove("selected"));
      card.classList.add("selected");
      Portrait.draw();
      updateAvatarLines();
      setNextEnabled(true);
      resetStatsForProf();
    });
  });
}

function resetStatsForProf() {
  const prof = getSelectedProf();
  if (!prof) return;
  const st = Array(10).fill(20);
  st[prof.primes[0]] = 30;
  st[prof.primes[1]] = 30;
  State.ch.stats = st;
}

// ─── Step 5: Culture ──────────────────────────────────────────────────────────
function renderCulture(main) {
  const cdata = (State.data.cultures || {})[String(State.ch.race_id)];
  if (!cdata) {
    State.step++;
    renderStep();
    updatePills();
    return;
  }
  const cards = cdata.options.map(opt => {
    const sel = State.ch.culture_key === opt.key ? " selected" : "";
    return `<div class="select-card${sel}" data-key="${esc(opt.key)}" data-name="${esc(opt.name)}">
      <div class="card-name">${opt.name}</div>
      <div class="card-desc">${opt.desc}</div>
    </div>`;
  }).join("");

  const race = getSelectedRace();
  main.innerHTML = `
    <div class="step-panel">
      <div class="step-title">${cdata.label}</div>
      <div class="step-subtitle">${race ? race.name : ""} cultural background. You may skip this and set it later with <span class="cinzel text-gold">TITLE SET CULTURE</span> in-game.</div>
      <div class="culture-grid">${cards}</div>
    </div>`;

  main.querySelectorAll(".select-card").forEach(card => {
    card.addEventListener("click", () => {
      State.ch.culture_key  = card.dataset.key === "none" ? null : card.dataset.key;
      State.ch.culture_name = card.dataset.name;
      main.querySelectorAll(".select-card").forEach(c => c.classList.remove("selected"));
      card.classList.add("selected");
    });
  });

  setNextEnabled(true);
}

// ─── Step 6: Stats ────────────────────────────────────────────────────────────
function renderStats(main) {
  const prof   = getSelectedProf();
  State.ch.stats = normalizeStatsArray(State.ch.stats, prof);
  const race   = getSelectedRace();
  const primes = prof ? prof.primes : [0,1];
  const descs  = State.data.stat_descriptions || {};
  const abbrevs = State.data.stat_abbrevs || [];
  const names  = State.data.stat_names || [];
  const mods   = race ? (race.stat_mods || Array(10).fill(0)) : Array(10).fill(0);
  const total  = TOTAL_STAT_POINTS();
  const remain = getRemainingPoints();

  const rows = names.map((name, i) => {
    const isPrime = primes.includes(i);
    const base    = State.ch.stats[i];
    const rmod    = mods[i] || 0;
    const tot     = base + rmod;
    const bonus   = statBonus(tot);
    const pct     = Math.max(0, Math.min(100, tot));
    const bonStr  = bonus >= 0 ? `+${bonus}` : `${bonus}`;
    const modStr  = rmod >= 0  ? `+${rmod}`  : `${rmod}`;
    const minVal  = isPrime ? 30 : 20;

    return `<tr class="stat-row${isPrime ? " prime-row":""}" data-idx="${i}"
                title="${descs[i] || ""}">
      <td style="cursor:help" title="${descs[i]||""}">${name}${isPrime?'<span class="text-gold" style="font-size:0.8em"> ★</span>':''}</td>
      <td class="stat-base" id="stat-base-${i}">${base}</td>
      <td class="stat-mod">${modStr}</td>
      <td class="stat-total" id="stat-total-${i}">${tot}</td>
      <td class="stat-bonus" id="stat-bonus-${i}">${bonStr}</td>
      <td class="stat-bar-cell">
        <div class="stat-bar-bg"><div class="stat-bar-fill" id="bar-${i}"
          style="width:${pct}%"></div></div>
      </td>
      <td>
        <div class="stat-controls">
          <button class="s-btn minus" data-idx="${i}" data-dir="-1"
            ${base <= minVal ? "disabled":""}>−</button>
          <input class="s-input" id="sinput-${i}" type="number"
            value="${base}" min="${minVal}" max="100" step="5" data-idx="${i}">
          <button class="s-btn plus" data-idx="${i}" data-dir="1"
            ${remain <= 0 ? "disabled":""}>+</button>
        </div>
      </td>
    </tr>`;
  }).join("");

  const [ptp, mtp] = calcTP(State.ch.stats, prof, mods);

  main.innerHTML = `
    <div class="step-panel">
      <div class="step-title">Assign Statistics</div>
      <div class="step-subtitle">Distribute ${total} points across 10 stats. Prime requisites (★) start at 30 and receive a free +10.</div>

      <div class="stat-pool">
        <div class="pool-block">
          <div class="pool-label">Points Spent</div>
          <div class="pool-val ${remain===0?"done":remain<0?"over":"ok"}" id="pool-used">${total-remain} / ${total}</div>
        </div>
        <div class="pool-block">
          <div class="pool-label">Remaining</div>
          <div class="pool-val ${remain===0?"done":remain<0?"over":"ok"}" id="pool-remain">${remain}</div>
        </div>
        <div class="pool-block">
          <div class="pool-label">Phys TP / Lvl</div>
          <div class="pool-val ok" id="ptp-val">${ptp}</div>
        </div>
        <div class="pool-block">
          <div class="pool-label">Ment TP / Lvl</div>
          <div class="pool-val ok" id="mtp-val">${mtp}</div>
        </div>
        <div style="margin-left:auto;display:flex;gap:0.5rem;align-items:center">
          <button class="stat-reset-btn" onclick="Creator_resetStats()">Reset</button>
          <button class="stat-suggest-btn" onclick="Creator_suggestStats()">Suggest</button>
        </div>
      </div>

      <table class="stat-table">
        <thead class="stat-head">
          <tr>
            <th style="text-align:left">Stat</th>
            <th>Base</th>
            <th>Race</th>
            <th>Total</th>
            <th>Bonus</th>
            <th>Bar</th>
            <th></th>
          </tr>
        </thead>
        <tbody>${rows}</tbody>
      </table>
      <div class="prime-note">★ Prime requisite stats start at 30 (minimum) and grant +10 free training points in their stat formula.</div>
    </div>`;

  // Wire up +/- buttons
  main.querySelectorAll(".s-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const idx = parseInt(btn.dataset.idx);
      const dir = parseInt(btn.dataset.dir);
      adjustStat(idx, dir * 5);
    });
  });

  // Wire up direct input
  main.querySelectorAll(".s-input").forEach(inp => {
    inp.addEventListener("change", () => {
      const idx = parseInt(inp.dataset.idx);
      const val = parseInt(inp.value) || 0;
      setStatDirect(idx, val);
    });
  });
}

window.Creator_resetStats = function() {
  resetStatsForProf();
  renderStats(document.getElementById("creator-main"));
};

window.Creator_suggestStats = function() {
  const prof = getSelectedProf();
  if (!prof) return;
  const sugg = prof.suggested_stats || Array(10).fill(20);
  State.ch.stats = normalizeStatsArray(sugg, prof);
  renderStats(document.getElementById("creator-main"));
};

function adjustStat(idx, delta) {
  const prof   = getSelectedProf();
  const primes = prof ? prof.primes : [0,1];
  const minVal = primes.includes(idx) ? 30 : 20;
  const remain = getRemainingPoints();
  let val = State.ch.stats[idx] + delta;
  if (delta > 0 && remain < delta) return;
  val = Math.max(minVal, Math.min(100, val));
  if (val === State.ch.stats[idx]) return;
  State.ch.stats[idx] = val;
  refreshStatRow(idx);
  refreshStatPool();
}

function setStatDirect(idx, val) {
  const prof   = getSelectedProf();
  const old    = State.ch.stats[idx];
  val = snapStatValue(val, idx, prof);
  if (val > old) {
    const remain = getRemainingPoints();
    const maxGain = Math.max(0, Math.floor(remain / 5) * 5);
    if ((val - old) > maxGain) {
      val = old + maxGain;
    }
  }
  State.ch.stats[idx] = val;
  refreshStatRow(idx);
  refreshStatPool();
}

function refreshStatRow(idx) {
  const race   = getSelectedRace();
  const prof   = getSelectedProf();
  const primes = prof ? prof.primes : [0,1];
  const mods   = race ? (race.stat_mods || Array(10).fill(0)) : Array(10).fill(0);
  const base   = State.ch.stats[idx];
  const rmod   = mods[idx] || 0;
  const tot    = base + rmod;
  const bonus  = statBonus(tot);
  const pct    = Math.max(0, Math.min(100, tot));

  const baseEl  = document.getElementById(`stat-base-${idx}`);
  const totEl   = document.getElementById(`stat-total-${idx}`);
  const bonEl   = document.getElementById(`stat-bonus-${idx}`);
  const barEl   = document.getElementById(`bar-${idx}`);
  const inpEl   = document.getElementById(`sinput-${idx}`);
  if (baseEl) baseEl.textContent = base;
  if (totEl)  totEl.textContent  = tot;
  if (bonEl)  bonEl.textContent  = bonus >= 0 ? `+${bonus}` : `${bonus}`;
  if (barEl)  barEl.style.width  = pct + "%";
  if (inpEl)  inpEl.value        = base;

  // Update +/- enabled state
  const remain  = getRemainingPoints();
  const minVal  = primes.includes(idx) ? 30 : 20;
  const row     = document.querySelector(`.s-btn[data-idx="${idx}"][data-dir="-1"]`);
  const rowPlus = document.querySelector(`.s-btn[data-idx="${idx}"][data-dir="1"]`);
  if (row)     row.disabled     = base <= minVal;
  if (rowPlus) rowPlus.disabled = remain <= 0;
}

function refreshStatPool() {
  const prof = getSelectedProf();
  const race = getSelectedRace();
  const mods = race ? (race.stat_mods || Array(10).fill(0)) : Array(10).fill(0);
  const total  = TOTAL_STAT_POINTS();
  const remain = getRemainingPoints();
  const [ptp, mtp] = calcTP(State.ch.stats, prof, mods);

  const used = document.getElementById("pool-used");
  const rem  = document.getElementById("pool-remain");
  const ptpEl = document.getElementById("ptp-val");
  const mtpEl = document.getElementById("mtp-val");

  const cls = remain===0?"done":remain<0?"over":"ok";
  if (used) { used.textContent = `${total-remain} / ${total}`; used.className = `pool-val ${cls}`; }
  if (rem)  { rem.textContent  = remain; rem.className = `pool-val ${cls}`; }
  if (ptpEl) ptpEl.textContent = ptp;
  if (mtpEl) mtpEl.textContent = mtp;

  // Re-enable all + buttons if points available
  if (remain > 0) {
    document.querySelectorAll(".s-btn[data-dir='1']").forEach(b => {
      const idx = parseInt(b.dataset.idx);
      b.disabled = State.ch.stats[idx] >= 100;
    });
  } else {
    document.querySelectorAll(".s-btn[data-dir='1']").forEach(b => b.disabled = true);
  }

  setNextEnabled(remain === 0);
}

// ─── Step 7: Appearance ───────────────────────────────────────────────────────
function renderAppearance(main) {
  const d = State.data;

  function swatchRow(list, field) {
    return list.map(v => {
      const sel = State.ch[field] === v ? " selected" : "";
      return `<div class="swatch${sel}" data-field="${field}" data-val="${esc(v)}">${v}</div>`;
    }).join("");
  }

  const h = State.ch.height;
  const ft = Math.floor(h/12), inch = h%12;

  main.innerHTML = `
    <div class="step-panel">
      <div class="step-title">Appearance</div>
      <div class="step-subtitle">These details shape how others will perceive you in Elanthia.</div>
      <div class="appearance-grid">

        <div class="app-section">
          <div class="app-label">Hair Color</div>
          <div class="swatch-grid" id="hair-color-wrap">
            ${swatchRow(d.hair_colors || [], "hair_color")}
          </div>
        </div>

        <div class="app-section">
          <div class="app-label">Hair Style</div>
          <div class="swatch-grid" id="hair-style-wrap">
            ${swatchRow(d.hair_styles || [], "hair_style")}
          </div>
        </div>

        <div class="app-section">
          <div class="app-label">Eye Color</div>
          <div class="swatch-grid" id="eye-color-wrap">
            ${swatchRow(d.eye_colors || [], "eye_color")}
          </div>
        </div>

        <div class="app-section">
          <div class="app-label">Skin Tone</div>
          <div class="swatch-grid" id="skin-tone-wrap">
            ${swatchRow(d.skin_tones || [], "skin_tone")}
          </div>
        </div>

        <div class="app-section">
          <div class="app-label">Height</div>
          <div class="height-wrap">
            <div class="height-display" id="height-display">${ft}' ${inch}"</div>
            <input class="height-slider" id="height-slider"
              type="range" min="48" max="84" value="${h}">
            <div class="text-muted" style="font-size:0.82rem">${h} inches</div>
          </div>
        </div>

      </div>
    </div>`;

  main.querySelectorAll(".swatch").forEach(s => {
    s.addEventListener("click", () => {
      const field = s.dataset.field;
      const val   = s.dataset.val;
      State.ch[field] = val;
      main.querySelectorAll(`.swatch[data-field="${field}"]`)
          .forEach(x => x.classList.remove("selected"));
      s.classList.add("selected");
      Portrait.draw();
      setNextEnabled(canAdvance());
    });
  });

  document.getElementById("height-slider").addEventListener("input", e => {
    const h = parseInt(e.target.value);
    State.ch.height = h;
    const ft = Math.floor(h/12), inch = h%12;
    document.getElementById("height-display").textContent = `${ft}' ${inch}"`;
    e.target.nextElementSibling.textContent = h + " inches";
  });

  setNextEnabled(canAdvance());
}

// ─── Step 8: Age ──────────────────────────────────────────────────────────────
function renderAge(main) {
  const stages  = State.data.age_stages || [];
  const cards   = stages.map((stage, i) => {
    const [lo, hi] = AGE_RANGES[i] || [20,25];
    const sel  = State.ch.age_stage === i ? " selected" : "";
    const hiStr = hi >= 999 ? "+" : String(hi);
    return `<div class="age-card${sel}" data-idx="${i}" data-lo="${lo}" data-hi="${hi}">
      <span class="age-stage">${stage}</span>
      <span class="age-range">${lo}–${hiStr}</span>
    </div>`;
  }).join("");

  main.innerHTML = `
    <div class="step-panel">
      <div class="step-title">Choose Your Age</div>
      <div class="step-subtitle">Age is cosmetic and affects your character's description. You can change it later with <span class="cinzel text-gold">AGE SET</span> in-game.</div>
      <div class="age-grid">${cards}</div>
    </div>`;

  main.querySelectorAll(".age-card").forEach(card => {
    card.addEventListener("click", () => {
      const idx = parseInt(card.dataset.idx);
      const lo  = parseInt(card.dataset.lo);
      const hi  = parseInt(card.dataset.hi);
      State.ch.age_stage = idx;
      State.ch.age_value = Math.floor((lo + Math.min(hi === 999 ? lo+20 : hi, lo+20)) / 2);
      main.querySelectorAll(".age-card").forEach(c => c.classList.remove("selected"));
      card.classList.add("selected");
      setNextEnabled(true);
    });
  });

  setNextEnabled(State.ch.age_value !== null);
}

// ─── Step 9: Summary ──────────────────────────────────────────────────────────
function renderSummary(main) {
  const ch    = State.ch;
  const race  = getSelectedRace();
  const prof  = getSelectedProf();
  const starterTown = getSelectedStarterTown();
  const mods  = race ? (race.stat_mods || Array(10).fill(0)) : Array(10).fill(0);
  const primes = prof ? prof.primes : [0,1];
  const names  = State.data.stat_names || [];
  const abbrevs = State.data.stat_abbrevs || [];
  const [ptp, mtp] = calcTP(ch.stats, prof, mods);

  const h   = ch.height || 68;
  const ft  = Math.floor(h/12), inch = h%12;
  const stages = State.data.age_stages || [];
  const ageLine = ch.age_stage !== null ? `${ch.age_value} (${stages[ch.age_stage]||""})` : "Not set";

  const statRows = names.map((name, i) => {
    const base  = ch.stats[i];
    const rmod  = mods[i] || 0;
    const tot   = base + rmod;
    const bonus = statBonus(tot);
    const modStr  = rmod  >= 0 ? `+${rmod}`  : `${rmod}`;
    const bonStr  = bonus >= 0 ? `+${bonus}` : `${bonus}`;
    const prime   = primes.includes(i);
    return `<div class="summary-stat-row">
      <div class="sstat-name">${name}${prime?'<span class="prime-star"> ★</span>':''}</div>
      <div class="sstat-base text-parch cinzel">${base}</div>
      <div class="sstat-mod text-muted">${modStr}</div>
      <div class="sstat-total">${tot}</div>
      <div class="sstat-bonus text-muted">${bonStr}</div>
    </div>`;
  }).join("");

  const cultureLine = ch.culture_name || '<span class="text-muted italic">None (set later in-game)</span>';

  main.innerHTML = `
    <div class="step-panel">
      <div class="step-title">Character Summary</div>
      <div class="step-subtitle">Review your choices. Click <em>Create Character</em> when you're ready to enter the world.</div>

      <div class="summary-grid">

        <div class="summary-section">
          <div class="summary-head">Identity</div>
          <div class="summary-row"><span class="summary-key">Name</span><span class="summary-val">${esc(ch.name)}</span></div>
          <div class="summary-row"><span class="summary-key">Gender</span><span class="summary-val">${cap(ch.gender)}</span></div>
          <div class="summary-row"><span class="summary-key">Race</span><span class="summary-val">${race?race.name:""}</span></div>
          <div class="summary-row"><span class="summary-key">Culture</span><span class="summary-val">${cultureLine}</span></div>
          <div class="summary-row"><span class="summary-key">Profession</span><span class="summary-val">${prof?prof.name:""} <span class="text-muted italic">(${prof?prof.type:""})</span></span></div>
          <div class="summary-row"><span class="summary-key">Height</span><span class="summary-val">${ft}' ${inch}"</span></div>
          <div class="summary-row"><span class="summary-key">Age</span><span class="summary-val">${ageLine}</span></div>

          <div class="summary-head" style="margin-top:1.2rem">Appearance</div>
          <div class="summary-row"><span class="summary-key">Hair</span><span class="summary-val">${ch.hair_style} ${ch.hair_color}</span></div>
          <div class="summary-row"><span class="summary-key">Eyes</span><span class="summary-val">${ch.eye_color}</span></div>
          <div class="summary-row"><span class="summary-key">Skin</span><span class="summary-val">${ch.skin_tone}</span></div>

          <div class="summary-head" style="margin-top:1.2rem">Starting Info</div>
          <div class="summary-row"><span class="summary-key">Starts In</span><span class="summary-val">${starterTown ? starterTown.name : "Unknown"}</span></div>
          <div class="summary-row"><span class="summary-key">HP / Level</span><span class="summary-val">${prof?prof.hp:10}</span></div>
          ${prof && prof.mana > 0 ? `<div class="summary-row"><span class="summary-key">Mana / Level</span><span class="summary-val">${prof.mana}</span></div>` : ""}
        </div>

        <div class="summary-section">
          <div class="summary-head">Statistics</div>
          <div class="summary-stat-row head">
            <div>Stat</div><div class="text-center">Base</div>
            <div class="text-center">Race</div>
            <div class="text-center">Total</div>
            <div class="text-center">Bonus</div>
          </div>
          ${statRows}
          <div class="tp-summary-row">
            <div>Phys TP/lvl: <span id="sum-ptp">${ptp}</span></div>
            <div>Ment TP/lvl: <span id="sum-mtp">${mtp}</span></div>
          </div>
        </div>

      </div>
    </div>`;

  setNextEnabled(true);
}

// ─── Confirm Modal ────────────────────────────────────────────────────────────
function showConfirmModal() {
  const ch   = State.ch;
  const race = getSelectedRace();
  const prof = getSelectedProf();
  const starterTown = getSelectedStarterTown();
  const body = document.getElementById("confirm-body");
  body.innerHTML = `
    <div><strong class="text-gold">${esc(ch.name)}</strong></div>
    <div>${race?race.name:""} &nbsp;·&nbsp; ${prof?prof.name:""} (${prof?prof.type:""})</div>
    <div style="margin-top:0.6rem">Starts in: <strong>${starterTown ? starterTown.name : "Unknown"}</strong></div>
    <div style="margin-top:0.4rem">${cap(ch.gender)} &nbsp;·&nbsp;
      ${ch.hair_style} ${ch.hair_color} hair &nbsp;·&nbsp;
      ${ch.eye_color} eyes &nbsp;·&nbsp; ${ch.skin_tone} skin
    </div>`;
  document.getElementById("confirm-overlay").style.display = "flex";
}

function showSuccessScreen(result) {
  document.getElementById("success-title").textContent = "Character Created!";
  document.getElementById("success-msg").textContent   = result.message || `${result.name} enters the world...`;
  document.getElementById("success-overlay").style.display = "flex";
}

// ─── Avatar sidebar updates ───────────────────────────────────────────────────
function updateAvatarName() {
  const el = document.getElementById("av-name");
  if (el) el.textContent = State.ch.name || "—";
}

function updateAvatarLines() {
  const race = getSelectedRace();
  const prof = getSelectedProf();
  const r = document.getElementById("av-race-line");
  const p = document.getElementById("av-prof-line");
  if (r) r.textContent = race ? race.name : "Choose a race";
  if (p) p.textContent = prof ? prof.name : "Choose a profession";
}

// ─── Canvas Portrait Renderer ─────────────────────────────────────────────────
// Anime/fantasy RPG style — no Roblox shapes, proper curves, shading, glow

// ─── Portrait Renderer ────────────────────────────────────────────────────────
// Uses real AI-generated portrait images when available.
// Falls back to procedural canvas renderer for any missing race/gender combos.
// Available images live at: /cc/static/images/race{id}_{gender}.png
// Currently available: all 13 females + race1_male.
// Missing males (2-13) use the canvas renderer automatically.

const Portrait = {

  // ── Image cache ────────────────────────────────────────────────────────────
  _cache: {},      // key: "race{id}_{gender}" -> HTMLImageElement (loaded) | false (failed)
  _loading: {},    // keys currently in-flight

  // Preload only called on boot to warm up cache quietly
  preloadAll() {
    // Only preload on-demand now — see _loadImage
  },

  // Load a specific portrait image; calls draw() when done
  _loadImage(raceId, gender) {
    const key = `race${raceId}_${gender}`;
    // Already loaded or failed — nothing to do
    if (key in this._cache) return;
    // Already in flight
    if (key in this._loading) return;
    this._loading[key] = true;
    const img = new window.Image();
    img.onload = () => {
      this._cache[key] = img;
      delete this._loading[key];
      this.draw();   // redraw now that image is ready
    };
    img.onerror = () => {
      this._cache[key] = false;   // false = confirmed missing, use canvas
      delete this._loading[key];
    };
    // Cache-bust once on first load to avoid stale browser cache
    img.src = `/cc/static/images/${key}.png?v=2`;
  },

  _getImage(raceId, gender) {
    const key = `race${raceId}_${gender}`;
    const cached = this._cache[key];
    // If loaded: return the image
    if (cached instanceof window.Image) return cached;
    // If not attempted yet: kick off load (will redraw when done)
    if (!(key in this._cache)) this._loadImage(raceId, gender);
    // Return null for now — canvas fallback until image arrives
    return null;
  },

  // ── Public entry point ────────────────────────────────────────────────────
  draw() {
    const canvas = document.getElementById("avatar-canvas");
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    const W = canvas.width, H = canvas.height;   // 220 × 300

    ctx.clearRect(0, 0, W, H);

    const ch     = State.ch;
    const race   = getSelectedRace();
    const prof   = getSelectedProf();
    const raceId = ch.race_id || 0;
    const profId = ch.prof_id || 0;
    const gender = (ch.gender === "male") ? "male" : "female";
    const female = gender === "female";

    // ── Try real image first ──────────────────────────────────────────────
    const img = raceId ? this._getImage(raceId, gender) : null;

    if (img) {
      // Draw the real portrait image
      ctx.drawImage(img, 0, 0, W, H);

      // Subtle dark vignette overlay so nameplate blends in
      const vig = ctx.createRadialGradient(W/2, H/2, W*0.28, W/2, H/2, W*0.76);
      vig.addColorStop(0,   "rgba(0,0,0,0)");
      vig.addColorStop(0.7, "rgba(0,0,0,0)");
      vig.addColorStop(1,   "rgba(0,0,0,0.55)");
      ctx.fillStyle = vig;
      ctx.fillRect(0, 0, W, H);

    } else {
      // ── Canvas fallback for missing images ────────────────────────────
      const rc = this._raceConfig(raceId, female);
      this._bg(ctx, W, H, rc);
      this._ambientParticles(ctx, W, H, rc);
      if (raceId === 11) this._wings(ctx, W, H);
      this._body(ctx, W, H, female, rc, profId);
      this._head(ctx, W, H, female, rc);
      this._hair(ctx, W, H, female, rc, ch.hair_color, ch.hair_style);
      this._face(ctx, W, H, female, rc);
      this._hairFringe(ctx, W, H, female, rc, ch.hair_color);
    }

    // Nameplate always drawn on top
    this._nameplate(ctx, W, H, ch.name, race, prof);

    // Glow border when race + prof chosen
    const glow = document.getElementById("avatar-glow");
    if (glow) glow.className = "avatar-glow" + (raceId && profId ? " active" : "");

    updateAvatarName();
    updateAvatarLines();
  },

  // ── Background ────────────────────────────────────────────────────────────
  _bg(ctx, W, H, rc) {
    // Deep atmosphere gradient
    const g = ctx.createLinearGradient(0, 0, 0, H);
    g.addColorStop(0,   rc.bgTop    || "#0d0e18");
    g.addColorStop(0.5, rc.bgMid    || "#0d0b10");
    g.addColorStop(1,   rc.bgBottom || "#080608");
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, W, H);

    // Ambient light bloom behind character
    const bloom = ctx.createRadialGradient(W/2, H*0.38, 10, W/2, H*0.38, W*0.72);
    bloom.addColorStop(0,   rc.bloomColor || "rgba(120,90,200,0.18)");
    bloom.addColorStop(0.5, "rgba(0,0,0,0.0)");
    bloom.addColorStop(1,   "rgba(0,0,0,0.0)");
    ctx.fillStyle = bloom;
    ctx.fillRect(0, 0, W, H);

    // Floor rim glow
    const floor = ctx.createLinearGradient(0, H*0.82, 0, H);
    floor.addColorStop(0, "rgba(0,0,0,0)");
    floor.addColorStop(1, rc.floorGlow || "rgba(80,60,120,0.22)");
    ctx.fillStyle = floor;
    ctx.fillRect(0, H*0.82, W, H*0.18);
  },

  // ── Floating particles ────────────────────────────────────────────────────
  _ambientParticles(ctx, W, H, rc) {
    const col = rc.particleColor || "rgba(180,160,255,0.45)";
    const pts = rc.particles || [
      {x:0.12,y:0.22,r:1.4},{x:0.82,y:0.18,r:1.0},{x:0.28,y:0.55,r:0.9},
      {x:0.74,y:0.44,r:1.2},{x:0.18,y:0.72,r:0.8},{x:0.88,y:0.68,r:1.1},
      {x:0.50,y:0.14,r:1.3},{x:0.62,y:0.78,r:0.7},{x:0.36,y:0.30,r:0.9},
    ];
    ctx.fillStyle = col;
    pts.forEach(p => {
      ctx.beginPath();
      ctx.arc(p.x*W, p.y*H, p.r, 0, Math.PI*2);
      ctx.fill();
    });
  },

  // ── Aelotoi wings ─────────────────────────────────────────────────────────
  _wings(ctx, W, H) {
    const cx = W/2, wy = H*0.36;
    ctx.save();
    ctx.globalAlpha = 0.55;
    // Wing membrane gradient
    const wg = ctx.createLinearGradient(cx-80, wy-40, cx, wy+60);
    wg.addColorStop(0, "rgba(160,210,255,0.7)");
    wg.addColorStop(1, "rgba(100,160,220,0.1)");
    ctx.fillStyle = wg;
    ctx.strokeStyle = "rgba(160,220,255,0.6)";
    ctx.lineWidth = 0.8;
    // Left wing
    ctx.beginPath();
    ctx.moveTo(cx-14, wy+5);
    ctx.bezierCurveTo(cx-55, wy-50, cx-90, wy-20, cx-78, wy+55);
    ctx.bezierCurveTo(cx-60, wy+70, cx-30, wy+42, cx-14, wy+20);
    ctx.closePath(); ctx.fill(); ctx.stroke();
    // Wing veins left
    ctx.strokeStyle = "rgba(200,235,255,0.4)";
    ctx.lineWidth = 0.6;
    [[cx-14,wy+5,cx-72,wy-12],[cx-14,wy+10,cx-78,wy+20],[cx-14,wy+16,cx-70,wy+48]].forEach(([x1,y1,x2,y2])=>{
      ctx.beginPath(); ctx.moveTo(x1,y1); ctx.lineTo(x2,y2); ctx.stroke();
    });
    // Right wing (mirror)
    ctx.fillStyle = wg;
    ctx.strokeStyle = "rgba(160,220,255,0.6)"; ctx.lineWidth = 0.8;
    ctx.beginPath();
    ctx.moveTo(cx+14, wy+5);
    ctx.bezierCurveTo(cx+55, wy-50, cx+90, wy-20, cx+78, wy+55);
    ctx.bezierCurveTo(cx+60, wy+70, cx+30, wy+42, cx+14, wy+20);
    ctx.closePath(); ctx.fill(); ctx.stroke();
    ctx.restore();
  },

  // ── Body ──────────────────────────────────────────────────────────────────
  _body(ctx, W, H, female, rc, profId) {
    const cx = W/2;
    // Outfit colours per profession
    const out = this._outfitColors(profId);

    // --- Clothing silhouette ---
    if (female) {
      // Dress / robe shape
      const bodyG = ctx.createLinearGradient(cx-38, H*0.52, cx+38, H*0.98);
      bodyG.addColorStop(0, out.light);
      bodyG.addColorStop(0.5, out.mid);
      bodyG.addColorStop(1, out.dark);
      ctx.fillStyle = bodyG;
      ctx.beginPath();
      ctx.moveTo(cx-22, H*0.515);
      ctx.bezierCurveTo(cx-30, H*0.60, cx-34, H*0.70, cx-38, H*0.98);
      ctx.lineTo(cx+38, H*0.98);
      ctx.bezierCurveTo(cx+34, H*0.70, cx+30, H*0.60, cx+22, H*0.515);
      ctx.closePath();
      ctx.fill();

      // Waist nip / belt suggestion
      ctx.fillStyle = out.accent;
      ctx.beginPath();
      ctx.ellipse(cx, H*0.625, 17, 3.5, 0, 0, Math.PI*2);
      ctx.fill();

      // Décolletage / neckline detail
      const neckG = ctx.createLinearGradient(cx-22, H*0.50, cx+22, H*0.56);
      neckG.addColorStop(0, out.mid);
      neckG.addColorStop(0.5, out.light);
      neckG.addColorStop(1, out.mid);
      ctx.fillStyle = neckG;
      ctx.beginPath();
      ctx.moveTo(cx-22, H*0.515);
      ctx.bezierCurveTo(cx-16, H*0.535, cx, H*0.545, cx+16, H*0.535);
      ctx.lineTo(cx+22, H*0.515);
      ctx.closePath(); ctx.fill();

      // Neckline trim
      ctx.strokeStyle = out.trim;
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(cx-16, H*0.515);
      ctx.bezierCurveTo(cx-8, H*0.528, cx, H*0.535, cx+8, H*0.528);
      ctx.lineTo(cx+16, H*0.515); ctx.stroke();

      // Shoulder fabric
      ctx.fillStyle = out.mid;
      ctx.beginPath(); ctx.ellipse(cx-26, H*0.515, 10, 5, -0.2, 0, Math.PI*2); ctx.fill();
      ctx.beginPath(); ctx.ellipse(cx+26, H*0.515, 10, 5,  0.2, 0, Math.PI*2); ctx.fill();

      // Arms / sleeves
      const armG = ctx.createLinearGradient(cx-44, H*0.52, cx-30, H*0.78);
      armG.addColorStop(0, out.mid); armG.addColorStop(1, out.dark);
      ctx.fillStyle = armG;
      ctx.beginPath();
      ctx.moveTo(cx-26, H*0.515);
      ctx.bezierCurveTo(cx-40, H*0.56, cx-42, H*0.70, cx-36, H*0.80);
      ctx.bezierCurveTo(cx-30, H*0.82, cx-24, H*0.74, cx-22, H*0.62);
      ctx.closePath(); ctx.fill();
      ctx.beginPath();
      ctx.moveTo(cx+26, H*0.515);
      ctx.bezierCurveTo(cx+40, H*0.56, cx+42, H*0.70, cx+36, H*0.80);
      ctx.bezierCurveTo(cx+30, H*0.82, cx+24, H*0.74, cx+22, H*0.62);
      ctx.closePath(); ctx.fill();

      // Hands (skin peek)
      ctx.fillStyle = rc.skin;
      ctx.beginPath(); ctx.ellipse(cx-36, H*0.81, 5, 7, 0.15, 0, Math.PI*2); ctx.fill();
      ctx.beginPath(); ctx.ellipse(cx+36, H*0.81, 5, 7, -0.15, 0, Math.PI*2); ctx.fill();

      // Outfit accent / embroidery lines
      ctx.strokeStyle = out.trim;
      ctx.lineWidth = 0.8;
      ctx.setLineDash([2,4]);
      ctx.beginPath();
      ctx.moveTo(cx, H*0.545);
      ctx.bezierCurveTo(cx-4, H*0.62, cx-8, H*0.72, cx-12, H*0.88);
      ctx.stroke();
      ctx.beginPath();
      ctx.moveTo(cx, H*0.545);
      ctx.bezierCurveTo(cx+4, H*0.62, cx+8, H*0.72, cx+12, H*0.88);
      ctx.stroke();
      ctx.setLineDash([]);

    } else {
      // Male — broader shoulders, armour-forward
      const bodyG = ctx.createLinearGradient(cx-42, H*0.50, cx+42, H*0.98);
      bodyG.addColorStop(0, out.light); bodyG.addColorStop(1, out.dark);
      ctx.fillStyle = bodyG;
      ctx.beginPath();
      ctx.moveTo(cx-30, H*0.505);
      ctx.bezierCurveTo(cx-38, H*0.58, cx-36, H*0.70, cx-32, H*0.98);
      ctx.lineTo(cx+32, H*0.98);
      ctx.bezierCurveTo(cx+36, H*0.70, cx+38, H*0.58, cx+30, H*0.505);
      ctx.closePath(); ctx.fill();

      // Chest plate / tunic highlight
      const chestG = ctx.createLinearGradient(cx-22, H*0.505, cx+22, H*0.64);
      chestG.addColorStop(0, out.light); chestG.addColorStop(1, out.mid);
      ctx.fillStyle = chestG;
      ctx.beginPath();
      ctx.moveTo(cx-22, H*0.505);
      ctx.lineTo(cx-18, H*0.64); ctx.lineTo(cx+18, H*0.64);
      ctx.lineTo(cx+22, H*0.505); ctx.closePath(); ctx.fill();

      ctx.strokeStyle = out.trim; ctx.lineWidth = 0.8;
      ctx.beginPath();
      ctx.moveTo(cx, H*0.505); ctx.lineTo(cx, H*0.65); ctx.stroke();

      // Shoulders / pauldrons
      ctx.fillStyle = out.accent;
      ctx.beginPath(); ctx.ellipse(cx-32, H*0.505, 13, 7, -0.2, 0, Math.PI*2); ctx.fill();
      ctx.beginPath(); ctx.ellipse(cx+32, H*0.505, 13, 7,  0.2, 0, Math.PI*2); ctx.fill();

      // Arms
      ctx.fillStyle = out.mid;
      ctx.beginPath();
      ctx.moveTo(cx-32, H*0.505);
      ctx.bezierCurveTo(cx-46, H*0.55, cx-48, H*0.70, cx-42, H*0.80);
      ctx.bezierCurveTo(cx-36, H*0.83, cx-28, H*0.72, cx-26, H*0.60);
      ctx.closePath(); ctx.fill();
      ctx.beginPath();
      ctx.moveTo(cx+32, H*0.505);
      ctx.bezierCurveTo(cx+46, H*0.55, cx+48, H*0.70, cx+42, H*0.80);
      ctx.bezierCurveTo(cx+36, H*0.83, cx+28, H*0.72, cx+26, H*0.60);
      ctx.closePath(); ctx.fill();

      // Hands
      ctx.fillStyle = rc.skin;
      ctx.beginPath(); ctx.ellipse(cx-42, H*0.81, 5, 7, 0.2, 0, Math.PI*2); ctx.fill();
      ctx.beginPath(); ctx.ellipse(cx+42, H*0.81, 5, 7, -0.2, 0, Math.PI*2); ctx.fill();
    }

    // Neck (skin)
    const neckG2 = ctx.createLinearGradient(cx-7, H*0.455, cx+7, H*0.515);
    neckG2.addColorStop(0, rc.skinLight);
    neckG2.addColorStop(1, rc.skinShad);
    ctx.fillStyle = neckG2;
    ctx.beginPath();
    ctx.moveTo(cx-7, H*0.455);
    ctx.bezierCurveTo(cx-8, H*0.48, cx-7, H*0.515, cx-6, H*0.518);
    ctx.lineTo(cx+6, H*0.518);
    ctx.bezierCurveTo(cx+7, H*0.515, cx+8, H*0.48, cx+7, H*0.455);
    ctx.closePath(); ctx.fill();

    // Collar bone suggestion
    ctx.strokeStyle = rc.skinShad;
    ctx.lineWidth = 0.7; ctx.globalAlpha = 0.5;
    ctx.beginPath();
    ctx.moveTo(cx-12, H*0.505); ctx.bezierCurveTo(cx-6, H*0.502, cx, H*0.500, cx+6, H*0.502);
    ctx.lineTo(cx+12, H*0.505); ctx.stroke();
    ctx.globalAlpha = 1;
  },

  // ── Head ──────────────────────────────────────────────────────────────────
  _head(ctx, W, H, female, rc) {
    const cx   = W/2;
    const fcy  = H*0.285;   // face centre Y
    const fRX  = female ? 27 : 29;   // face half-width
    const fRY  = female ? 33 : 35;   // face half-height

    // Ears (drawn behind head)
    this._ears(ctx, cx, fcy, fRX, fRY, rc);

    // Head shape — layered for depth
    // Back of head / hair base
    const headG = ctx.createRadialGradient(cx-6, fcy-8, 4, cx, fcy, fRX+6);
    headG.addColorStop(0, rc.skinLight);
    headG.addColorStop(0.7, rc.skin);
    headG.addColorStop(1, rc.skinShad);
    ctx.fillStyle = headG;
    ctx.beginPath();
    ctx.ellipse(cx, fcy, fRX, fRY, 0, 0, Math.PI*2);
    ctx.fill();

    // Jaw shadow
    ctx.fillStyle = rc.skinShad;
    ctx.globalAlpha = 0.28;
    ctx.beginPath();
    ctx.ellipse(cx, fcy+fRY*0.55, fRX*0.72, fRY*0.36, 0, 0, Math.PI);
    ctx.fill();
    ctx.globalAlpha = 1;

    // Cheek blush (female only)
    if (female) {
      ctx.fillStyle = rc.blush || "rgba(230,130,130,0.18)";
      ctx.beginPath(); ctx.ellipse(cx-fRX*0.52, fcy+4, 9, 5, 0, 0, Math.PI*2); ctx.fill();
      ctx.beginPath(); ctx.ellipse(cx+fRX*0.52, fcy+4, 9, 5, 0, 0, Math.PI*2); ctx.fill();
    }
  },

  // ── Ears ──────────────────────────────────────────────────────────────────
  _ears(ctx, cx, fcy, fRX, fRY, rc) {
    const earG = ctx.createLinearGradient(cx-fRX-18, fcy, cx-fRX, fcy);
    earG.addColorStop(0, rc.skinShad);
    earG.addColorStop(1, rc.skin);

    if (rc.earType === "pointed") {
      // Long elegant elven ears
      ctx.fillStyle = earG;
      // Left
      ctx.beginPath();
      ctx.moveTo(cx-fRX+4,  fcy-10);
      ctx.bezierCurveTo(cx-fRX-8, fcy-22, cx-fRX-20, fcy-38, cx-fRX-14, fcy-42);
      ctx.bezierCurveTo(cx-fRX-8, fcy-44, cx-fRX-2,  fcy-22, cx-fRX+2, fcy+4);
      ctx.closePath(); ctx.fill();
      ctx.strokeStyle = rc.skinShad; ctx.lineWidth = 0.6;
      ctx.beginPath();
      ctx.moveTo(cx-fRX+2, fcy-8); ctx.bezierCurveTo(cx-fRX-8, fcy-22, cx-fRX-14, fcy-40, cx-fRX-14, fcy-42);
      ctx.stroke();

      // Right (mirror)
      const earGR = ctx.createLinearGradient(cx+fRX, fcy, cx+fRX+18, fcy);
      earGR.addColorStop(0, rc.skin); earGR.addColorStop(1, rc.skinShad);
      ctx.fillStyle = earGR;
      ctx.beginPath();
      ctx.moveTo(cx+fRX-4,  fcy-10);
      ctx.bezierCurveTo(cx+fRX+8, fcy-22, cx+fRX+20, fcy-38, cx+fRX+14, fcy-42);
      ctx.bezierCurveTo(cx+fRX+8, fcy-44, cx+fRX+2,  fcy-22, cx+fRX-2, fcy+4);
      ctx.closePath(); ctx.fill();
      ctx.strokeStyle = rc.skinShad; ctx.lineWidth = 0.6;
      ctx.beginPath();
      ctx.moveTo(cx+fRX-2, fcy-8); ctx.bezierCurveTo(cx+fRX+8, fcy-22, cx+fRX+14, fcy-40, cx+fRX+14, fcy-42);
      ctx.stroke();

    } else if (rc.earType === "slight") {
      // Half-elf — moderate point
      ctx.fillStyle = rc.skin;
      ctx.beginPath();
      ctx.moveTo(cx-fRX+3, fcy-8);
      ctx.bezierCurveTo(cx-fRX-6, fcy-16, cx-fRX-12, fcy-26, cx-fRX-8, fcy-28);
      ctx.bezierCurveTo(cx-fRX-4, fcy-18, cx-fRX-1, fcy+2, cx-fRX+2, fcy+3);
      ctx.closePath(); ctx.fill();
      ctx.beginPath();
      ctx.moveTo(cx+fRX-3, fcy-8);
      ctx.bezierCurveTo(cx+fRX+6, fcy-16, cx+fRX+12, fcy-26, cx+fRX+8, fcy-28);
      ctx.bezierCurveTo(cx+fRX+4, fcy-18, cx+fRX+1, fcy+2, cx+fRX-2, fcy+3);
      ctx.closePath(); ctx.fill();

    } else {
      // Round ears
      ctx.fillStyle = rc.skin;
      ctx.beginPath(); ctx.ellipse(cx-fRX-3, fcy, 7, 10, 0, 0, Math.PI*2); ctx.fill();
      ctx.beginPath(); ctx.ellipse(cx+fRX+3, fcy, 7, 10, 0, 0, Math.PI*2); ctx.fill();
      ctx.strokeStyle = rc.skinShad; ctx.lineWidth = 0.5;
      ctx.beginPath(); ctx.arc(cx-fRX-3, fcy, 7, -0.7, 0.7); ctx.stroke();
      ctx.beginPath(); ctx.arc(cx+fRX+3, fcy, 7, Math.PI-0.7, Math.PI+0.7); ctx.stroke();
    }
  },

  // ── Face ──────────────────────────────────────────────────────────────────
  _face(ctx, W, H, female, rc) {
    const cx  = W/2;
    const fcy = H*0.285;
    const fRX = female ? 27 : 29;

    // Eye positions
    const eyeOff = female ? 9.5 : 11;
    const eyeY   = fcy - 3;

    // Eyes (left, right)
    this._eye(ctx, cx - eyeOff, eyeY, female, rc);
    this._eye(ctx, cx + eyeOff, eyeY, female, rc, true);

    // Nose — elegant, minimal
    ctx.strokeStyle = rc.skinShad;
    ctx.lineWidth = 0.9; ctx.globalAlpha = 0.55;
    ctx.beginPath();
    ctx.moveTo(cx - 2.5, eyeY + 8);
    ctx.bezierCurveTo(cx - 4, eyeY+14, cx-3, eyeY+18, cx-0.5, eyeY+19);
    ctx.bezierCurveTo(cx + 2, eyeY+18, cx+3.5, eyeY+16, cx+2, eyeY+14);
    ctx.stroke();
    // Nostril dots
    ctx.fillStyle = rc.skinShad; ctx.globalAlpha = 0.45;
    ctx.beginPath(); ctx.arc(cx-3, eyeY+19, 1.2, 0, Math.PI*2); ctx.fill();
    ctx.beginPath(); ctx.arc(cx+2, eyeY+19, 1.2, 0, Math.PI*2); ctx.fill();
    ctx.globalAlpha = 1;

    // Mouth
    const mY = fcy + (female ? 18 : 20);
    // Lip gradient
    const lipG = ctx.createLinearGradient(cx-9, mY-2, cx+9, mY+4);
    lipG.addColorStop(0, rc.lipColor || (female ? "#d47080" : "#c07060"));
    lipG.addColorStop(1, rc.lipDark  || (female ? "#a04050" : "#884038"));
    ctx.fillStyle = lipG;
    // Upper lip
    ctx.beginPath();
    ctx.moveTo(cx-9, mY);
    ctx.bezierCurveTo(cx-5, mY-2, cx-2, mY-3, cx, mY-2);
    ctx.bezierCurveTo(cx+2, mY-3, cx+5, mY-2, cx+9, mY);
    ctx.bezierCurveTo(cx+5, mY+1.5, cx, mY+2, cx-5, mY+1.5);
    ctx.closePath(); ctx.fill();
    // Lower lip
    ctx.beginPath();
    ctx.moveTo(cx-8, mY+0.5);
    ctx.bezierCurveTo(cx-4, mY+5, cx+4, mY+5, cx+8, mY+0.5);
    ctx.bezierCurveTo(cx+4, mY+2, cx-4, mY+2, cx-8, mY+0.5);
    ctx.closePath(); ctx.fill();
    // Lip highlight
    ctx.fillStyle = "rgba(255,220,220,0.35)";
    ctx.beginPath(); ctx.ellipse(cx+1, mY+2.5, 4, 1.5, 0, 0, Math.PI*2); ctx.fill();
  },

  // ── Single eye ────────────────────────────────────────────────────────────
  _eye(ctx, x, y, female, rc, right = false) {
    const eW = female ? 8.5 : 8;
    const eH = female ? 6   : 5.5;

    // Eyelid shape (almond)
    ctx.save();
    ctx.beginPath();
    // Upper lid curve
    ctx.moveTo(x - eW, y);
    ctx.bezierCurveTo(x - eW*0.3, y - eH*1.05, x + eW*0.3, y - eH*1.05, x + eW, y);
    // Lower lid curve
    ctx.bezierCurveTo(x + eW*0.6, y + eH*0.6, x - eW*0.6, y + eH*0.6, x - eW, y);
    ctx.closePath();
    ctx.clip();

    // White of eye
    ctx.fillStyle = "#f0ece4";
    ctx.fillRect(x - eW - 1, y - eH - 1, eW*2+2, eH*2+2);

    // Iris gradient
    const irisR = eH * 0.92;
    const irisG = ctx.createRadialGradient(x - 1, y - 1.5, 0.5, x, y, irisR);
    irisG.addColorStop(0,   rc.irisLight || "#8fbde0");
    irisG.addColorStop(0.4, rc.iris      || "#3a7ab0");
    irisG.addColorStop(0.75,rc.irisDark  || "#1a4878");
    irisG.addColorStop(1,   "#0a1828");
    ctx.fillStyle = irisG;
    ctx.beginPath(); ctx.arc(x, y, irisR, 0, Math.PI*2); ctx.fill();

    // Pupil
    ctx.fillStyle = "#050406";
    ctx.beginPath(); ctx.ellipse(x, y, irisR*0.45, irisR*0.52, 0, 0, Math.PI*2); ctx.fill();

    // Primary highlight
    ctx.fillStyle = "rgba(255,255,255,0.92)";
    ctx.beginPath(); ctx.ellipse(x + eW*0.26, y - eH*0.36, 1.8, 1.2, -0.5, 0, Math.PI*2); ctx.fill();
    // Secondary small highlight
    ctx.fillStyle = "rgba(255,255,255,0.55)";
    ctx.beginPath(); ctx.arc(x - eW*0.2, y + eH*0.1, 0.8, 0, Math.PI*2); ctx.fill();

    ctx.restore();

    // Lash line
    ctx.strokeStyle = "#14100e";
    ctx.lineWidth = female ? 1.4 : 1.2;
    ctx.beginPath();
    ctx.moveTo(x - eW, y);
    ctx.bezierCurveTo(x - eW*0.3, y - eH*1.05, x + eW*0.3, y - eH*1.05, x + eW, y);
    ctx.stroke();

    // Lashes (female)
    if (female) {
      ctx.strokeStyle = "#0d0a0c";
      ctx.lineWidth = 0.9;
      const lashPts = [-0.7, -0.35, 0, 0.35, 0.7];
      lashPts.forEach(t => {
        const lx = x + t * eW;
        const ly = y - eH * (1 - t*t*0.3) * 0.95;
        const angle = -0.9 + t * 0.4;
        ctx.beginPath();
        ctx.moveTo(lx, ly);
        ctx.lineTo(lx + Math.cos(angle)*3.5, ly - Math.sin(Math.abs(angle))*3.5);
        ctx.stroke();
      });
    }

    // Lower lash line
    ctx.strokeStyle = "rgba(20,16,14,0.5)";
    ctx.lineWidth = 0.6;
    ctx.beginPath();
    ctx.moveTo(x - eW*0.85, y + eH*0.05);
    ctx.bezierCurveTo(x, y + eH*0.55, x + eW*0.85, y + eH*0.05, x + eW*0.85, y + eH*0.05);
    ctx.stroke();

    // Eyebrow
    const brY = y - eH*1.6 - (female ? 5 : 4);
    const brW = eW * (female ? 1.05 : 1.15);
    ctx.strokeStyle = rc.browColor || "#3a2814";
    ctx.lineWidth = female ? 1.6 : 2;
    ctx.lineCap = "round";
    ctx.beginPath();
    ctx.moveTo(x - brW, brY + (right ? 2 : 2));
    ctx.bezierCurveTo(
      x - brW*0.3, brY - (female?2:1),
      x + brW*0.3, brY - (female?2:1),
      x + brW,     brY + (right ? 3 : 3)
    );
    ctx.stroke();
    ctx.lineCap = "butt";
  },

  // ── Hair (back layer) ─────────────────────────────────────────────────────
  _hair(ctx, W, H, female, rc, hairColor, style) {
    const cx  = W/2;
    const fcy = H*0.285;
    const fRX = female ? 27 : 29;
    const fRY = female ? 33 : 35;
    const hairTop = fcy - fRY + 2;

    const hc    = this._hairPalette(hairColor);
    const hairG = ctx.createLinearGradient(cx - fRX - 10, hairTop, cx + fRX + 10, H*0.85);
    hairG.addColorStop(0,   hc.light);
    hairG.addColorStop(0.25, hc.mid);
    hairG.addColorStop(0.65, hc.dark);
    hairG.addColorStop(1,   hc.darkest);
    ctx.fillStyle = hairG;
    ctx.strokeStyle = hc.darkest;
    ctx.lineWidth = 0.6;

    const st = style || "";

    if (st.includes("short") || st.includes("crop") || st.includes("shav")) {
      // ── Short / cropped ──
      ctx.beginPath();
      ctx.moveTo(cx - fRX - 4, fcy - 8);
      ctx.bezierCurveTo(cx - fRX - 6, fcy - 20, cx - fRX, hairTop - 6, cx, hairTop - 8);
      ctx.bezierCurveTo(cx + fRX, hairTop - 6, cx + fRX + 6, fcy - 20, cx + fRX + 4, fcy - 8);
      ctx.bezierCurveTo(cx + fRX + 2, fcy + 10, cx + fRX - 4, fcy + 20, cx + fRX - 8, fcy + 16);
      ctx.bezierCurveTo(cx, fcy + 22, cx - fRX + 8, fcy + 16, cx - fRX + 4, fcy + 10);
      ctx.bezierCurveTo(cx - fRX, fcy + 4, cx - fRX - 2, fcy - 4, cx - fRX - 4, fcy - 8);
      ctx.closePath(); ctx.fill(); ctx.stroke();

    } else if (st.includes("braided")) {
      // ── Braid (shoulder + thick braid tail) ──
      ctx.beginPath();
      ctx.moveTo(cx - fRX - 4, fcy - 10);
      ctx.bezierCurveTo(cx - fRX - 8, fcy - 20, cx - fRX, hairTop - 6, cx, hairTop - 8);
      ctx.bezierCurveTo(cx + fRX, hairTop - 6, cx + fRX + 8, fcy - 20, cx + fRX + 4, fcy - 10);
      ctx.bezierCurveTo(cx + fRX + 2, fcy + 16, cx + 20, fcy + 32, cx + 14, fcy + 36);
      ctx.bezierCurveTo(cx + 6, fcy + 38, cx - 6, fcy + 38, cx - 14, fcy + 36);
      ctx.bezierCurveTo(cx - 20, fcy + 32, cx - fRX - 2, fcy + 16, cx - fRX - 4, fcy - 10);
      ctx.closePath(); ctx.fill(); ctx.stroke();
      // Braid texture
      const bY0 = fcy + 40, bY1 = H * 0.78;
      for (let y = bY0; y < bY1; y += 13) {
        ctx.fillStyle = hc.mid;
        ctx.beginPath(); ctx.ellipse(cx, y + 6, 7, 7, 0, 0, Math.PI*2); ctx.fill();
        ctx.fillStyle = hc.dark;
        ctx.beginPath(); ctx.ellipse(cx - 3, y, 5, 5.5, -0.3, 0, Math.PI*2); ctx.fill();
        ctx.beginPath(); ctx.ellipse(cx + 3, y + 7, 5, 5.5, 0.3, 0, Math.PI*2); ctx.fill();
      }

    } else if (st.includes("tied") || st.includes("back") || st.includes("combed")) {
      // ── Tied back / ponytail ──
      ctx.beginPath();
      ctx.moveTo(cx - fRX - 4, fcy - 10);
      ctx.bezierCurveTo(cx - fRX - 8, fcy - 22, cx - fRX, hairTop - 5, cx, hairTop - 8);
      ctx.bezierCurveTo(cx + fRX, hairTop - 5, cx + fRX + 8, fcy - 22, cx + fRX + 4, fcy - 10);
      ctx.bezierCurveTo(cx + fRX + 2, fcy + 14, cx + 16, fcy + 24, cx + 10, fcy + 26);
      ctx.bezierCurveTo(cx + 4, fcy + 28, cx - 4, fcy + 28, cx - 10, fcy + 26);
      ctx.bezierCurveTo(cx - 16, fcy + 24, cx - fRX - 2, fcy + 14, cx - fRX - 4, fcy - 10);
      ctx.closePath(); ctx.fill(); ctx.stroke();
      // Ponytail
      ctx.fillStyle = hairG;
      ctx.beginPath();
      ctx.moveTo(cx - 9, fcy + 26);
      ctx.bezierCurveTo(cx - 18, fcy + 50, cx - 22, H*0.68, cx - 10, H*0.80);
      ctx.bezierCurveTo(cx - 2, H*0.84, cx + 2, H*0.84, cx + 10, H*0.80);
      ctx.bezierCurveTo(cx + 22, H*0.68, cx + 18, fcy + 50, cx + 9, fcy + 26);
      ctx.closePath(); ctx.fill(); ctx.stroke();

    } else if (st.includes("wavy") || st.includes("curly") || st.includes("wild")) {
      // ── Wavy / curly ──
      ctx.beginPath();
      ctx.moveTo(cx - fRX - 4, fcy - 10);
      ctx.bezierCurveTo(cx - fRX - 10, fcy - 24, cx - fRX, hairTop - 7, cx, hairTop - 10);
      ctx.bezierCurveTo(cx + fRX, hairTop - 7, cx + fRX + 10, fcy - 24, cx + fRX + 4, fcy - 10);
      // Right wave down
      ctx.bezierCurveTo(cx + fRX + 14, fcy + 20, cx + fRX + 6, fcy + 44, cx + fRX + 16, fcy + 60);
      ctx.bezierCurveTo(cx + fRX + 24, fcy + 76, cx + fRX + 8, fcy + 90, cx + fRX + 2, fcy + 95);
      ctx.lineTo(cx - fRX - 2, fcy + 95);
      ctx.bezierCurveTo(cx - fRX - 8, fcy + 90, cx - fRX - 24, fcy + 76, cx - fRX - 16, fcy + 60);
      ctx.bezierCurveTo(cx - fRX - 6, fcy + 44, cx - fRX - 14, fcy + 20, cx - fRX - 4, fcy - 10);
      ctx.closePath(); ctx.fill(); ctx.stroke();

    } else {
      // ── Long (default / shoulder / waist) — anime flowing ──
      const isWaist = st.includes("waist");
      const tailY   = isWaist ? H*0.90 : H*0.74;

      ctx.beginPath();
      ctx.moveTo(cx - fRX - 4, fcy - 12);
      ctx.bezierCurveTo(cx - fRX - 12, fcy - 26, cx - fRX, hairTop - 8, cx, hairTop - 10);
      ctx.bezierCurveTo(cx + fRX, hairTop - 8, cx + fRX + 12, fcy - 26, cx + fRX + 4, fcy - 12);
      // Right side flowing down
      ctx.bezierCurveTo(cx + fRX + 16, fcy + 18, cx + fRX + 20, fcy + 50, cx + fRX + 10, tailY);
      ctx.bezierCurveTo(cx + fRX + 2,  tailY + 10, cx + 16, tailY + 14, cx + 8, tailY + 12);
      ctx.lineTo(cx - 8, tailY + 12);
      ctx.bezierCurveTo(cx - 16, tailY + 14, cx - fRX - 2, tailY + 10, cx - fRX - 10, tailY);
      ctx.bezierCurveTo(cx - fRX - 20, fcy + 50, cx - fRX - 16, fcy + 18, cx - fRX - 4, fcy - 12);
      ctx.closePath(); ctx.fill(); ctx.stroke();

      // Inner hair strands for depth
      ctx.strokeStyle = hc.dark;
      ctx.lineWidth = 1.4;
      ctx.globalAlpha = 0.55;
      const strands = female ? [
        [cx+fRX+4, fcy+8, cx+fRX+12, fcy+50, cx+fRX+6, tailY-10],
        [cx+fRX-4, fcy+14, cx+fRX+2, fcy+60, cx+fRX-4, tailY],
        [cx-fRX-4, fcy+8, cx-fRX-12, fcy+50, cx-fRX-6, tailY-10],
      ] : [
        [cx+fRX+4, fcy+8, cx+fRX+10, fcy+40, cx+fRX+4, tailY-15],
      ];
      strands.forEach(([x1,y1,x2,y2,x3,y3]) => {
        ctx.beginPath(); ctx.moveTo(x1,y1); ctx.bezierCurveTo(x2,y2,x3-4,y3-8,x3,y3); ctx.stroke();
      });
      ctx.globalAlpha = 1;
    }

    // Shine streak across hair
    ctx.strokeStyle = "rgba(255,255,255,0.22)";
    ctx.lineWidth = 2.5;
    ctx.lineCap = "round";
    ctx.beginPath();
    ctx.moveTo(cx - fRX*0.2, hairTop + 2);
    ctx.bezierCurveTo(cx + fRX*0.3, hairTop + 8, cx + fRX*0.5, hairTop + 18, cx + fRX*0.3, hairTop + 28);
    ctx.stroke();
    ctx.lineWidth = 1.2;
    ctx.beginPath();
    ctx.moveTo(cx + fRX*0.1, hairTop + 4);
    ctx.bezierCurveTo(cx + fRX*0.55, hairTop + 12, cx + fRX*0.65, hairTop + 22, cx + fRX*0.45, hairTop + 34);
    ctx.stroke();
    ctx.lineCap = "butt";
  },

  // ── Hair fringe (on top of face) ──────────────────────────────────────────
  _hairFringe(ctx, W, H, female, rc, hairColor) {
    const cx  = W/2;
    const fcy = H*0.285;
    const fRX = female ? 27 : 29;
    const fRY = female ? 33 : 35;

    const hc   = this._hairPalette(hairColor);
    const topG = ctx.createLinearGradient(cx - fRX, fcy - fRY, cx + fRX, fcy - fRY + 20);
    topG.addColorStop(0, hc.mid);
    topG.addColorStop(1, hc.dark);
    ctx.fillStyle = topG;

    // Fringe — a few natural-looking bangs
    const bangs = female ? [
      // [startX, startY, cp1x, cp1y, cp2x, cp2y, endX, endY]
      [cx-26, fcy-32, cx-30, fcy-15, cx-20, fcy-8, cx-16, fcy-4],
      [cx-14, fcy-34, cx-16, fcy-14, cx-10, fcy-4, cx-6,  fcy-1],
      [cx-2,  fcy-35, cx-4,  fcy-12, cx+2,  fcy-3, cx+6,  fcy-1],
      [cx+10, fcy-34, cx+12, fcy-14, cx+18, fcy-5, cx+20, fcy-3],
      [cx+22, fcy-32, cx+26, fcy-14, cx+28, fcy-10, cx+24, fcy-6],
    ] : [
      [cx-22, fcy-33, cx-26, fcy-16, cx-18, fcy-6, cx-14, fcy-3],
      [cx-6,  fcy-35, cx-8,  fcy-14, cx-2,  fcy-4, cx+2,  fcy-1],
      [cx+8,  fcy-34, cx+10, fcy-14, cx+16, fcy-6, cx+18, fcy-3],
    ];

    bangs.forEach(([sx,sy,cp1x,cp1y,cp2x,cp2y,ex,ey]) => {
      ctx.beginPath();
      ctx.moveTo(sx, sy - 4);
      ctx.bezierCurveTo(sx - 3, sy - 2, sx - 1, sy, sx, sy);
      ctx.bezierCurveTo(cp1x, cp1y, cp2x, cp2y, ex, ey);
      ctx.bezierCurveTo(ex + 4, ey - 2, ex + 5, ey - 8, sx + 4, sy - 2);
      ctx.closePath();
      ctx.fill();
    });
  },

  // ── Nameplate ─────────────────────────────────────────────────────────────
  _nameplate(ctx, W, H, name, race, prof) {
    if (!name && !race && !prof) return;
    const plateH = 48;
    const y0 = H - plateH;

    // Background
    const plateG = ctx.createLinearGradient(0, y0, 0, H);
    plateG.addColorStop(0, "rgba(13,11,8,0)");
    plateG.addColorStop(0.3, "rgba(13,11,8,0.82)");
    plateG.addColorStop(1,   "rgba(13,11,8,0.97)");
    ctx.fillStyle = plateG;
    ctx.fillRect(0, y0, W, plateH);

    // Top border line
    ctx.strokeStyle = "rgba(201,168,76,0.4)";
    ctx.lineWidth = 0.6;
    ctx.beginPath(); ctx.moveTo(8, y0+14); ctx.lineTo(W-8, y0+14); ctx.stroke();

    // Name
    if (name) {
      ctx.font = "bold 13px 'Cinzel', serif";
      ctx.fillStyle = "#c9a84c";
      ctx.textAlign = "center";
      ctx.fillText(name.toUpperCase(), W/2, y0 + 28);
    }
    // Race + profession
    const sub = [race?.name, prof?.name].filter(Boolean).join("  ·  ");
    if (sub) {
      ctx.font = "italic 10.5px 'Crimson Text', Georgia, serif";
      ctx.fillStyle = "#b09b72";
      ctx.textAlign = "center";
      ctx.fillText(sub, W/2, y0 + 42);
    }
    ctx.textAlign = "left";
  },

  // ── Outfit colours ────────────────────────────────────────────────────────
  _outfitColors(profId) {
    const palettes = {
      0:  { light:"#2a2018", mid:"#1e1610", dark:"#140e08", accent:"#3a2810", trim:"rgba(201,168,76,0.3)" }, // default
      1:  { light:"#505862", mid:"#384048", dark:"#222830", accent:"#686870", trim:"rgba(180,190,210,0.5)" }, // Warrior — steel
      2:  { light:"#2a2218", mid:"#1e1810", dark:"#120e08", accent:"#3a2210", trim:"rgba(160,120,60,0.5)"  }, // Rogue — dark leather
      3:  { light:"#22183a", mid:"#180f2a", dark:"#0e0818", accent:"#382058", trim:"rgba(140,120,220,0.55)"}, // Wizard — deep violet
      4:  { light:"#2a2a1a", mid:"#1e1e10", dark:"#141408", accent:"#c9a84c", trim:"rgba(201,168,76,0.6)"  }, // Cleric — ivory/gold
      5:  { light:"#1a2a18", mid:"#101e10", dark:"#081408", accent:"#50a050", trim:"rgba(100,200,100,0.4)" }, // Empath — leaf green
      6:  { light:"#2a0a2a", mid:"#1a0818", dark:"#100510", accent:"#800880", trim:"rgba(180,60,180,0.5)"  }, // Sorcerer — dark purple
      7:  { light:"#1e2a12", mid:"#141e0c", dark:"#0c1406", accent:"#607840", trim:"rgba(120,160,80,0.45)" }, // Ranger — forest
      8:  { light:"#3a1410", mid:"#280e0c", dark:"#180806", accent:"#c04030", trim:"rgba(201,168,76,0.45)" }, // Bard — crimson
      9:  { light:"#2a2428", mid:"#1e1820", dark:"#100c14", accent:"#c9a84c", trim:"rgba(220,200,140,0.55)"}, // Paladin — silver/gold
      10: { light:"#1e1a10", mid:"#141208", dark:"#0c0c06", accent:"#786040", trim:"rgba(180,150,80,0.35)" }, // Monk — earthy
    };
    return palettes[profId] || palettes[0];
  },

  // ── Race config ───────────────────────────────────────────────────────────
  _raceConfig(raceId, female) {
    const cfgs = {
      0:  { skin:"#d0a870", skinLight:"#e8c898", skinShad:"#a07848", bgTop:"#0d0e18", bgMid:"#0d0b10", bgBottom:"#080608", bloomColor:"rgba(100,80,180,0.18)", floorGlow:"rgba(80,60,120,0.22)", particleColor:"rgba(180,160,255,0.4)", earType:"round", irisLight:"#8fbde0", iris:"#3a7ab0", irisDark:"#1a4878", lipColor:"#d47080", lipDark:"#a04050", browColor:"#3a2814", blush:"rgba(220,120,120,0.18)" },
      1:  { skin:"#d4a878", skinLight:"#ecc8a0", skinShad:"#a07848", bgTop:"#0e0d14", bgMid:"#0c0b10", bgBottom:"#080608", bloomColor:"rgba(100,80,180,0.16)", floorGlow:"rgba(80,60,120,0.20)", particleColor:"rgba(180,160,255,0.38)", earType:"round", irisLight:"#90c0e0", iris:"#4080b0", irisDark:"#205080", lipColor:"#d47080", lipDark:"#a04050", browColor:"#3a2814", blush:"rgba(220,120,120,0.18)" },
      2:  { skin: female?"#dcc898":"#c8b880", skinLight: female?"#f0e0b0":"#dccca0", skinShad: female?"#a89060":"#907848", bgTop:"#080e10", bgMid:"#060c0e", bgBottom:"#040808", bloomColor:"rgba(80,160,180,0.22)", floorGlow:"rgba(60,130,150,0.26)", particleColor:"rgba(160,220,240,0.5)", earType:"pointed", irisLight:"#80e0a0", iris:"#40a060", irisDark:"#206040", lipColor:"#c87880", lipDark:"#905060", browColor:"#6a5828", blush:"rgba(200,140,120,0.15)" },
      3:  { skin: female?"#9090a8":"#78788a", skinLight: female?"#b0b0c0":"#9898a8", skinShad: female?"#606070":"#505060", bgTop:"#050408", bgMid:"#080610", bgBottom:"#040308", bloomColor:"rgba(160,80,200,0.25)", floorGlow:"rgba(120,60,160,0.30)", particleColor:"rgba(200,140,255,0.5)", earType:"pointed", irisLight:"#e060a0", iris:"#a02060", irisDark:"#600040", lipColor:"#c04070", lipDark:"#801040", browColor:"#404048", blush:"rgba(160,80,120,0.20)" },
      4:  { skin: female?"#d0a068":"#c09060", skinLight: female?"#e8c090":"#d8b080", skinShad: female?"#a07848":"#907040", bgTop:"#0e0c14", bgMid:"#0c0a10", bgBottom:"#080608", bloomColor:"rgba(120,100,200,0.18)", floorGlow:"rgba(90,70,140,0.22)", particleColor:"rgba(190,170,255,0.40)", earType:"slight", irisLight:"#90c0d8", iris:"#4888a8", irisDark:"#205878", lipColor:"#d07880", lipDark:"#a04858", browColor:"#3a2814", blush:"rgba(210,130,120,0.18)" },
      5:  { skin: female?"#c89060":"#b07840", skinLight: female?"#e0b080":"#c89860", skinShad: female?"#906030":"#806028", bgTop:"#100808", bgMid:"#0e0606", bgBottom:"#080404", bloomColor:"rgba(200,100,60,0.20)", floorGlow:"rgba(160,80,50,0.24)", particleColor:"rgba(255,180,120,0.45)", earType:"round", irisLight:"#d0a060", iris:"#a07030", irisDark:"#604018", lipColor:"#c07060", lipDark:"#904040", browColor:"#4a2808", blush:"rgba(200,110,80,0.18)" },
      6:  { skin: female?"#d8b880":"#c8a870", skinLight: female?"#edd4a0":"#dac090", skinShad: female?"#a08848":"#907838", bgTop:"#050a06", bgMid:"#040806", bgBottom:"#030504", bloomColor:"rgba(60,160,80,0.20)", floorGlow:"rgba(40,120,60,0.24)", particleColor:"rgba(120,220,140,0.45)", earType:"round", irisLight:"#80d890", iris:"#409860", irisDark:"#206840", lipColor:"#c87870", lipDark:"#905048", browColor:"#3a2810", blush:"rgba(210,130,110,0.16)" },
      7:  { skin: female?"#c89060":"#a87040", skinLight: female?"#e0b080":"#c89060", skinShad: female?"#906030":"#785020", bgTop:"#060a0e", bgMid:"#050810", bgBottom:"#040608", bloomColor:"rgba(60,80,160,0.18)", floorGlow:"rgba(50,70,140,0.22)", particleColor:"rgba(120,150,255,0.40)", earType:"round", irisLight:"#80a8e0", iris:"#4070b0", irisDark:"#205080", lipColor:"#c07060", lipDark:"#904040", browColor:"#4a2808", blush:"rgba(190,110,90,0.16)" },
      8:  { skin: female?"#c8b878":"#b8a868", skinLight: female?"#ddd090":"#cec080", skinShad: female?"#988848":"#887838", bgTop:"#060a06", bgMid:"#060a06", bgBottom:"#040804", bloomColor:"rgba(80,160,80,0.18)", floorGlow:"rgba(60,120,60,0.22)", particleColor:"rgba(140,220,140,0.42)", earType:"slight", irisLight:"#90c880", iris:"#50a050", irisDark:"#306030", lipColor:"#c07870", lipDark:"#904850", browColor:"#3a2810", blush:"rgba(200,130,110,0.16)" },
      9:  { skin: female?"#d0c090":"#c0b080", skinLight: female?"#e4d8b0":"#d4c8a0", skinShad: female?"#a09060":"#907850", bgTop:"#060606", bgMid:"#050505", bgBottom:"#040404", bloomColor:"rgba(100,100,100,0.16)", floorGlow:"rgba(80,80,80,0.20)", particleColor:"rgba(200,200,200,0.38)", earType:"slight", irisLight:"#a0c8a0", iris:"#60a060", irisDark:"#308030", lipColor:"#c07870", lipDark:"#905050", browColor:"#3a2810", blush:"rgba(200,130,110,0.16)" },
      10: { skin: female?"#d8c8a0":"#c8b890", skinLight: female?"#ece0c0":"#d8ccb0", skinShad: female?"#a89870":"#907858", bgTop:"#0c0e14", bgMid:"#0c0c12", bgBottom:"#080a0c", bloomColor:"rgba(100,120,200,0.20)", floorGlow:"rgba(80,100,180,0.24)", particleColor:"rgba(180,200,255,0.45)", earType:"pointed", irisLight:"#a0d0e0", iris:"#60a8c0", irisDark:"#308098", lipColor:"#c07878", lipDark:"#905050", browColor:"#4a3818", blush:"rgba(200,130,110,0.16)" },
      11: { skin: female?"#d4c880":"#c4b870", skinLight: female?"#e8dcb0":"#d8cca0", skinShad: female?"#a09858":"#907848", bgTop:"#050a10", bgMid:"#060810", bgBottom:"#040608", bloomColor:"rgba(80,160,220,0.22)", floorGlow:"rgba(60,130,180,0.26)", particleColor:"rgba(160,210,255,0.50)", earType:"round", irisLight:"#80c0e0", iris:"#4090c0", irisDark:"#206090", lipColor:"#c07878", lipDark:"#905050", browColor:"#3a2810", blush:"rgba(200,130,110,0.16)" },
      12: { skin: female?"#c8b080":"#b8a070", skinLight: female?"#ddc8a0":"#ccb890", skinShad: female?"#988050":"#887040", bgTop:"#0c0808", bgMid:"#0c0808", bgBottom:"#080606", bloomColor:"rgba(180,80,60,0.18)", floorGlow:"rgba(140,60,40,0.22)", particleColor:"rgba(255,160,120,0.42)", earType:"slight", irisLight:"#e0b080", iris:"#b08040", irisDark:"#705020", lipColor:"#c07868", lipDark:"#904848", browColor:"#4a2808", blush:"rgba(190,110,90,0.16)" },
      13: { skin: female?"#a08060":"#907050", skinLight: female?"#c0a080":"#b09070", skinShad: female?"#706040":"#605030", bgTop:"#080a0c", bgMid:"#060808", bgBottom:"#040606", bloomColor:"rgba(60,80,100,0.20)", floorGlow:"rgba(50,70,90,0.24)", particleColor:"rgba(120,150,180,0.42)", earType:"round", irisLight:"#a0b8d0", iris:"#607898", irisDark:"#304858", lipColor:"#b07068", lipDark:"#804040", browColor:"#3a2810", blush:"rgba(180,110,90,0.14)" },
    };
    return cfgs[raceId] || cfgs[0];
  },

  // ── Hair palette ──────────────────────────────────────────────────────────
  _hairPalette(name) {
    const p = {
      "black":            { light:"#2a2428", mid:"#18141a", dark:"#0e0c10", darkest:"#080608" },
      "dark brown":       { light:"#3e2415", mid:"#2a180c", dark:"#1a0e06", darkest:"#0e0804" },
      "auburn":           { light:"#882818", mid:"#641a0e", dark:"#4a1008", darkest:"#300a04" },
      "brown":            { light:"#7a4820", mid:"#5a3014", dark:"#3a1e0c", darkest:"#221006" },
      "light brown":      { light:"#b07838", mid:"#8a5828", dark:"#5e3a18", darkest:"#3c2410" },
      "blonde":           { light:"#e8d070", mid:"#c8a838", dark:"#906820", darkest:"#604010" },
      "golden blonde":    { light:"#f0d860", mid:"#d4a830", dark:"#9a6c18", darkest:"#664408" },
      "platinum blonde":  { light:"#f0ecde", mid:"#d8d0b8", dark:"#b0a888", darkest:"#807858" },
      "red":              { light:"#c82018", mid:"#9a1410", dark:"#680c08", darkest:"#400804" },
      "copper":           { light:"#c86428", mid:"#9a4818", dark:"#682e0c", darkest:"#401c06" },
      "silver":           { light:"#d8d4d0", mid:"#b0aeac", dark:"#888684", darkest:"#605e5c" },
      "white":            { light:"#f4f0ec", mid:"#d8d0c8", dark:"#b0a8a0", darkest:"#888078" },
      "blue-black":       { light:"#1c1830", mid:"#121020", dark:"#0c0a14", darkest:"#08060c" },
      "strawberry blonde":{ light:"#e0a080", mid:"#c07858", dark:"#8a4c38", darkest:"#583020" },
    };
    return p[name] || p["brown"];
  },

  // ── hex → rgba helper ─────────────────────────────────────────────────────
  _rgba(hex, alpha) {
    const r = parseInt(hex.slice(1,3),16);
    const g = parseInt(hex.slice(3,5),16);
    const b = parseInt(hex.slice(5,7),16);
    return `rgba(${r},${g},${b},${alpha})`;
  },
};
// ─── Tooltip ─────────────────────────────────────────────────────────────────
const tt = (() => {
  const el = document.createElement("div");
  el.className = "tt";
  el.innerHTML = '<div class="tt-title" id="tt-title"></div><div id="tt-body"></div>';
  document.body.appendChild(el);

  document.addEventListener("mousemove", e => {
    const target = e.target.closest("[title]");
    if (target && target.title) {
      el.querySelector("#tt-title").textContent = target.dataset.label || "";
      el.querySelector("#tt-body").textContent  = target.title;
      const x = Math.min(e.clientX + 14, window.innerWidth - 290);
      const y = Math.min(e.clientY + 14, window.innerHeight - 80);
      el.style.left = x + "px";
      el.style.top  = y + "px";
      el.classList.add("show");
    } else {
      el.classList.remove("show");
    }
  });
  return el;
})();

// ─── Math helpers ─────────────────────────────────────────────────────────────
function TOTAL_STAT_POINTS() {
  return (State.data.total_stat_points || 660);
}

function statMinForIndex(idx, prof) {
  const primes = prof ? (prof.primes || [0,1]) : [0,1];
  return primes.includes(idx) ? 30 : 20;
}

function snapStatValue(value, idx, prof) {
  const minVal = statMinForIndex(idx, prof);
  const numeric = Number.isFinite(Number(value)) ? Number(value) : minVal;
  const clamped = Math.max(minVal, Math.min(100, numeric));
  return Math.round(clamped / 5) * 5;
}

function normalizeStatsArray(rawStats, prof) {
  const total = TOTAL_STAT_POINTS();
  const stats = Array.from({ length: 10 }, (_, idx) =>
    snapStatValue(Array.isArray(rawStats) ? rawStats[idx] : null, idx, prof)
  );
  const targets = Array.from({ length: 10 }, (_, idx) => {
    const raw = Array.isArray(rawStats) ? rawStats[idx] : null;
    return Number.isFinite(Number(raw)) ? Number(raw) : stats[idx];
  });

  let diff = total - stats.reduce((sum, value) => sum + value, 0);
  let guard = 0;
  while (diff !== 0 && guard < 200) {
    const dir = diff > 0 ? 1 : -1;
    const candidates = stats
      .map((value, idx) => ({ idx, value, target: targets[idx], min: statMinForIndex(idx, prof) }))
      .filter(({ value, min }) => (dir > 0 ? value < 100 : value > min));
    if (!candidates.length) break;

    candidates.sort((a, b) => {
      const aBias = dir > 0 ? (a.target - a.value) : (a.value - a.target);
      const bBias = dir > 0 ? (b.target - b.value) : (b.value - b.target);
      if (aBias !== bBias) return bBias - aBias;
      return dir > 0 ? a.value - b.value : b.value - a.value;
    });

    stats[candidates[0].idx] += dir * 5;
    diff -= dir * 5;
    guard += 1;
  }

  return stats;
}

function getRemainingPoints() {
  const total = TOTAL_STAT_POINTS();
  return total - State.ch.stats.reduce((a,b)=>a+b, 0);
}

function statBonus(stat) {
  return Math.floor((stat - 50) / 2);
}

function calcTP(stats, prof, raceMods) {
  if (!prof) return [25, 25];
  const primes = prof.primes || [0,1];
  const tot = stats.map((s,i) => s + (raceMods[i]||0));

  function eff(idx) {
    return primes.includes(idx) ? tot[idx]*2 : tot[idx];
  }

  const hybHalf = (eff(5) + eff(4)) / 2;
  const phys = eff(0)+eff(1)+eff(2)+eff(3)+hybHalf;
  const ment = eff(6)+eff(7)+eff(8)+eff(9)+hybHalf;
  return [25+Math.floor(phys/20), 25+Math.floor(ment/20)];
}

// ─── Getters ──────────────────────────────────────────────────────────────────
function getSelectedRace() {
  return (State.data.races||[]).find(r => r.id === State.ch.race_id) || null;
}

function getSelectedStarterTown() {
  const race = getSelectedRace();
  if (!race) return null;
  return {
    room_id: Number(race.start_room || State.ch.starting_room || 0),
    name: race.start_town || "Unknown",
  };
}

function getSelectedProf() {
  return (State.data.professions||[]).find(p => p.id === State.ch.prof_id) || null;
}

// ─── Utility ─────────────────────────────────────────────────────────────────
function esc(s) {
  if (!s) return "";
  return String(s)
    .replace(/&/g,"&amp;")
    .replace(/</g,"&lt;")
    .replace(/>/g,"&gt;")
    .replace(/"/g,"&quot;");
}

function cap(s) {
  if (!s) return "";
  return s.charAt(0).toUpperCase() + s.slice(1);
}
