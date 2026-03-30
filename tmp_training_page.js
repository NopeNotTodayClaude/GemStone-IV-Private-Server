
const TOKEN='TOKEN';
let char=null,pending={},activeTab='skills',weaponState=null,weaponBusy=false;
let weaponFilters={category:'all',type:'all',availability:'all'};
const SKILL_INFO = {"1": {"d": "Wield a weapon in each hand simultaneously.", "m": "Off-hand AS uses the normal melee formula, then adds TWC bonus/3 and reduces the untrained -25 off-hand penalty by TWC bonus/2. TWC roundtime also uses main speed plus off-hand speed and weight."}, "2": {"d": "Reduces the action penalty of heavier armor, letting you move and fight more freely inside it.", "m": "Every 2 ranks remove 1 point of armor action penalty, helping your AS, DS, and maneuver performance in heavier armor."}, "3": {"d": "Proficiency with shields of all sizes.", "m": "Block DS uses Shield Use ranks + STR/4 + DEX/4, then adds shield size bonus and enchant. Shield size also changes evade penalties: small -22%, medium -30%, large -38%, tower -46%."}, "4": {"d": "Specialized combat techniques including feints, parries, weapon-technique access, and other combat maneuvers.", "m": "Melee AS adds Combat Maneuvers ranks/2. Open aimed attacks use 25% of your CM bonus, and many maneuver checks and weapon-technique unlocks key directly from this skill."}, "5": {"d": "Mastery of swords, daggers, and all bladed weapons.", "m": "Your Edged Weapons skill bonus is added directly to melee AS, and your edged ranks also feed parry DS when an edged weapon is in hand. Skill bonus follows the GS4 curve: +5/rank to 10, +4/rank to 20, +3/rank to 30, +2/rank to 40, then +1/rank."}, "6": {"d": "Proficiency with maces, hammers, clubs, and other crushing weapons.", "m": "Your Blunt Weapons skill bonus is added directly to melee AS, and your blunt ranks also feed parry DS when a blunt weapon is in hand. Skill bonus follows the GS4 curve: +5/rank to 10, then +4, +3, +2, and +1 tiers."}, "7": {"d": "Skill with greatswords, war mattocks, halberds, and other two-handed weapons.", "m": "Your Two-Handed Weapons skill bonus is added directly to melee AS, and your two-handed ranks also feed parry DS when a two-handed weapon is in hand. Skill bonus follows the GS4 curve: +5/rank to 10, then +4, +3, +2, and +1 tiers."}, "8": {"d": "Accuracy and power with bows, crossbows, and other ranged weapons.", "m": "Your Ranged Weapons skill bonus drives ranged AS for READY and FIRE. Aimed ranged shots also key off your stored AIM location and the normal aimed-shot checks."}, "9": {"d": "Technique for hurling axes, daggers, javelins, and other projectiles with precision.", "m": "Your Thrown Weapons skill bonus drives thrown AS for HURL. Thrown attacks also use aimed-shot handling when you target a body part."}, "10": {"d": "Fighting with spears, tridents, pikes, and other pole weapons. Long reach is their hallmark.", "m": "Your Polearm Weapons skill bonus is added directly to melee AS, and your polearm ranks also feed parry DS when a polearm is in hand. Skill bonus follows the GS4 curve: +5/rank to 10, then +4, +3, +2, and +1 tiers."}, "11": {"d": "Unarmed combat covering punches, kicks, and grapples. Also governs brawling weapons.", "m": "UAF = (Brawling ranks x2) + CM/2 + STR bonus/2 + AGI bonus/2, plus UCS enchant bonuses. Brawling ranks also feed parry DS when you are using brawling attacks or bare-handed defense."}, "12": {"d": "The art of handling multiple opponents at once without being overwhelmed.", "m": "MSTRIKE currently gives 2 swings minimum, then adds 1 more swing per 25 MoC ranks, up to 5 total swings."}, "13": {"d": "General conditioning that improves stamina, maneuver defense, and physical endurance.", "m": "SMRv2 defense averages Dodging, CM, Perception, and Physical Fitness ranks. Physical Fitness also adds 25% of its skill bonus to CLIMB and 20% to SWIM checks."}, "14": {"d": "The ability to read attacks and move out of the way. Pure defensive value.", "m": "Evade DS starts from Dodging ranks + AGI bonus + INT bonus/4, then armor, shield size, and stance modify the final result."}, "15": {"d": "Knowledge of magical glyphs, runes, and symbols inscribed on scrolls and items.", "m": "Used directly by READ and INVOKE checks for scrolls and magical writing. More ranks improve your odds with higher-level or unfamiliar arcane material."}, "16": {"d": "Activating wands, scrolls, and enchanted objects without formal spell training.", "m": "Used for charged-item activation with wands, rods, and similar devices. More ranks improve reliability when the item's magic is outside your own circles."}, "17": {"d": "Accuracy when targeting creatures with bolt spells and directed magical attacks.", "m": "Each point of Spell Aiming bonus adds +1 bolt AS. Bolt AS = Spell Aiming bonus + stance (+30 offensive to -30 defensive) + any bolt/AS buffs."}, "18": {"d": "The capacity to draw ambient mana from the environment and store it for casting.", "m": "Max mana = base mana from your profession's mana stats + Harness Power ranks capped at level + your Harness Power skill bonus."}, "19": {"d": "Fine control over elemental mana flows. Essential for wizards and sorcerers.", "m": "Mana regen uses +1 per 10 ranks for single-sphere users, or +1 per 10 ranks in the higher sphere and +1 per 20 in the lower sphere for two-sphere users."}, "20": {"d": "Fine control over spiritual mana. Essential for clerics, empaths, and paladins.", "m": "Mana regen uses +1 per 10 ranks for single-sphere users, or +1 per 10 ranks in the higher sphere and +1 per 20 in the lower sphere for two-sphere users."}, "21": {"d": "Control over mental mana flows used by monks, bards, and mental lore specialists.", "m": "Mana regen uses +1 per 10 ranks for single-sphere users, or +1 per 10 ranks in the higher sphere and +1 per 20 in the lower sphere for two-sphere users."}, "22": {"d": "Scholarly pursuit and memorization of new spells beyond your base circle.", "m": "Each trained rank is one more spell rank known. Your profession's rank-per-level cap controls how many total spell ranks you can carry at your level."}, "23": {"d": "Wilderness craft covering tracking, foraging, and the art of skinning creatures for their hides.", "m": "TRACK reads real trails up to 900 seconds old, while Survival also supports FORAGE, FORAGE SENSE, and skinning quality."}, "24": {"d": "Detecting and safely neutralizing mechanical traps on chests, doors, and containers.", "m": "Disarm checks use your training, your stats, and your tools together. Better ranks and better disarm tools raise your odds on trapped boxes and containers."}, "25": {"d": "Coaxing open locks without the original key. The bread and butter of any rogue.", "m": "Lockpicking checks use your training, your stats, focus, and pick quality together. Better picks and more ranks raise your odds on tough locks."}, "26": {"d": "Moving unseen and melting into shadows. Drives your HIDE roll and your stealth-based ambush accuracy and weighting.", "m": "HIDE rolls open d100 + (3 x ranks) + Discipline bonus + profession bonus + room mods - armor penalty against the room's current hiding difficulty."}, "27": {"d": "Sharp awareness of your surroundings for spotting hidden creatures, traps, and passages.", "m": "Perception feeds stealth detection and is one of the equally weighted skills in SMRv2 defense, alongside Dodging, Combat Maneuvers, and Physical Fitness."}, "28": {"d": "Scaling walls, cliffs, ladders, and grates. Without training vertical travel is treacherous.", "m": "CLIMB uses open d100 + Climbing bonus + 25% of Physical Fitness bonus + DEX bonus + AGI/2 - encumbrance - armor. At 50 ranks, climbs are forced to succeed."}, "29": {"d": "Moving through water without drowning. Required for water rooms and some crossings.", "m": "SWIM uses open d100 + Swimming bonus + 20% of Physical Fitness bonus + STR bonus + CON bonus + DEX/2 - encumbrance - armor. At 50 ranks, swims are forced to succeed."}, "30": {"d": "Tending wounds with bandages and herbs to reduce injury severity after combat.", "m": "TEND chance is 40% + First Aid bonus/2 - 15 per wound rank, capped from 5% to 95%. Herb roundtime is reduced by 1 second per 20 First Aid bonus, to a 3 second minimum."}, "31": {"d": "The merchant's art covering haggling, appraisal, and knowing when the price is right.", "m": "Shop buy price is reduced by 0.2% per rank, capped at 15% off. More Trading means cheaper purchases anywhere this modifier is used."}, "32": {"d": "Lifting coin purses and small items from NPCs and other players without being noticed.", "m": "STEAL uses your Pickpocketing bonus, DEX bonus, Discipline bonus, and part of AGI, then applies hiding, rogue, hand-full, armor, and encumbrance modifiers."}, "33": {"d": "Knowledge of spiritual blessings covering warding spells, protective prayers, and holy shields.", "m": "Currently hooks into 304 Bless, 307 Benediction, 1604 Consecrate, 1611 Patron's Blessing, and 1625 Holy Weapon."}, "34": {"d": "Theological knowledge of the Arkati pantheon and their divine practices.", "m": "Currently hooks into 317 Divine Fury, 319 Soul Ward, 320 Ethereal Censer, 1614 Aura of the Arkati, and 1615 Repentance."}, "35": {"d": "The art of summoning spirits, elementals, and other entities to serve your will.", "m": "Currently hooks into Spirit Servant and other summon-style effects where summoning magic is implemented."}, "36": {"d": "Mastery of air-based elemental lore covering wind, lightning, and movement magic.", "m": "Currently hooks into 501 Sleep, 505 Hand of Tonis, 535 Haste, and 912 Call Wind."}, "37": {"d": "Mastery of earth-based elemental lore covering stone, metal, and endurance magic.", "m": "Currently hooks into 509 Strength, 514 Stone Fist, and 917 Earthen Fury."}, "38": {"d": "Mastery of fire-based elemental lore covering flame, heat, and destruction magic.", "m": "Currently hooks into 906 Minor Fire, 908 Major Fire, 915 Weapon Fire, and 519 Immolation."}, "39": {"d": "Mastery of water-based elemental lore covering ice, tides, and healing magic.", "m": "Currently hooks into 903 Minor Water and 512 Cold Snap."}, "40": {"d": "Mental lore focused on influencing and bending the will of others.", "m": "Currently hooks into Confusion-style control magic and other supported manipulation effects."}, "41": {"d": "Mental lore focused on mind-to-mind communication and reading surface thoughts.", "m": "Currently hooks into Mindward-style defense and other supported telepathy effects."}, "42": {"d": "Mental lore focused on transferring energy to drain foes and bolster allies.", "m": "Currently hooks into Powersink-style draining and other supported transference effects."}, "43": {"d": "The skill for aimed strikes and precision attacks, especially from hiding.", "m": "Hidden aimed attacks use 25% of your Ambush bonus toward aiming and add extra crit weighting. Open aiming uses 25% of Ambush bonus plus 25% of Combat Maneuvers bonus."}, "44": {"d": "Mental lore concerned with foresight, omens, and predictive insight.", "m": "Currently hooks into Foresight, Premonition, and other supported divination effects."}, "45": {"d": "Mental lore concerned with reshaping the body through force of will.", "m": "Currently hooks into Mind over Body and other supported transformation effects."}, "46": {"d": "Sorcerous lore focused on demonic entities, planar bargains, and summoning.", "m": "Currently hooks into Minor Summoning and other supported demonology or shadow-defense effects."}, "47": {"d": "Sorcerous lore focused on undeath, corpses, and gravebound power.", "m": "Currently hooks into Animate Dead, Grasp of the Grave, and other supported necromancy effects."}};

/* ── Skill bonus formula ── */
function bonus(r){
  if(r<=0)return 0;
  if(r<=10)return r*5;
  if(r<=20)return 50+((r-10)*4);
  if(r<=30)return 90+((r-20)*3);
  if(r<=40)return 120+((r-30)*2);
  return r+100;
}

/* ── Initial load ── */
async function load(){
  try{
    const r=await fetch('/api/character?token='+TOKEN);
    char=await r.json();
    if(char.error){mainErr(char.error);return;}
    render();
    initStatsModal();
    initConvModal();
  }catch(e){mainErr('Could not connect to game server.');}
}

function mainErr(msg){
  const main=document.getElementById('main');
  if(!main)return;
  main.innerHTML='<div style="color:var(--red);padding:1.2rem 0.2rem;font-family:Cinzel,serif;">'+msg+'</div>';
}

async function loadWeaponData(){
  try{
    const r=await fetch('/api/weapon?token='+TOKEN);
    weaponState=await r.json();
  }catch(e){
    weaponState={error:'Could not reach weapon technique service.'};
  }
}

async function switchTab(tab){
  activeTab=tab;
  if(tab==='weapon' && !weaponState){
    await loadWeaponData();
  }
  render();
}

/* ════════════════════════════════════════════════════
   SKILL TRAINING
   ════════════════════════════════════════════════════ */
function render(){
  document.getElementById('char-badge').textContent=char.name+' \u00b7 Level '+char.level;
  refreshTP();
  const main=document.getElementById('main');main.innerHTML='';
  const tabs=document.createElement('div');tabs.className='top-tabs';
  tabs.innerHTML=
    '<button class="top-tab'+(activeTab==='skills'?' active':'')+'" onclick="switchTab(\'skills\')">Skills</button>'+
    '<button class="top-tab'+(activeTab==='weapon'?' active':'')+'" onclick="switchTab(\'weapon\')">Weapon Techniques</button>';
  main.appendChild(tabs);
  const content=document.createElement('div');content.className='tab-panel';content.id='tab-panel';
  main.appendChild(content);
  if(activeTab==='weapon'){renderWeaponTechniques(content);return;}
  renderSkills(content);
}

function renderSkills(main){
  const preferredOrder = ['Combat', 'Magic', 'Survival', 'General', 'Lore'];
  const orderedCats = [];
  for(const cat of preferredOrder){
    if(char.categories && Object.prototype.hasOwnProperty.call(char.categories, cat)){
      orderedCats.push([cat, char.categories[cat]]);
    }
  }
  for(const [cat, ids] of Object.entries(char.categories || {})){
    if(!preferredOrder.includes(cat)) orderedCats.push([cat, ids]);
  }
  for(const[cat,ids]of orderedCats){
    const sec=document.createElement('div');sec.className='cat';
    sec.innerHTML='<div class="cat-title">'+cat+'</div><div class="sk-head"><span>Skill</span><span style="text-align:center">Ranks</span><span style="text-align:center">Bonus</span><span style="text-align:center">PTP</span><span style="text-align:center">MTP</span><span style="text-align:center">Rnk/Cap</span><span></span></div>';
    for(const id of ids){const sk=char.skills[id];if(sk)sec.appendChild(mkRow(id,sk));}
    main.appendChild(sec);
  }
}

function renderWeaponTechniques(main){
  if(!weaponState){main.innerHTML='<div class="wt-empty">Loading weapon techniques...</div>';return;}
  if(weaponState.error){main.innerHTML='<div class="wt-empty">'+weaponState.error+'</div>';return;}
  const summary=document.createElement('div');summary.className='wt-summary';
  summary.innerHTML=
    '<div class="wt-box"><div class="wt-box-label">Stamina</div><div class="wt-box-value">'+(weaponState.stamina||0)+'</div></div>'+
    '<div class="wt-box"><div class="wt-box-label">Roundtime</div><div class="wt-box-value">'+(weaponState.roundtime||0)+'s</div></div>'+
    '<div class="wt-box"><div class="wt-box-label">Room Targets</div><div class="wt-box-value">'+((weaponState.targets||[]).length||0)+'</div></div>'+
    '<div class="wt-box"><div class="wt-box-label">Active Assault</div><div class="wt-box-value">'+(weaponState.active_assault&&weaponState.active_assault.active?(weaponState.active_assault.mnemonic+' \u2192 '+weaponState.active_assault.target):'None')+'</div></div>';
  main.appendChild(summary);

  const controls=document.createElement('div');controls.className='wt-controls';
  controls.innerHTML=
    '<select id="wt-category" class="wt-select" onchange="setWeaponFilter(\'category\',this.value)">'+
      '<option value="all"'+(weaponFilters.category==='all'?' selected':'')+'>All categories</option>'+
      '<option value="brawling"'+(weaponFilters.category==='brawling'?' selected':'')+'>Brawling</option><option value="blunt"'+(weaponFilters.category==='blunt'?' selected':'')+'>Blunt Weapons</option><option value="edged"'+(weaponFilters.category==='edged'?' selected':'')+'>Edged Weapons</option><option value="polearm"'+(weaponFilters.category==='polearm'?' selected':'')+'>Polearm Weapons</option><option value="ranged"'+(weaponFilters.category==='ranged'?' selected':'')+'>Ranged Weapons</option><option value="twohanded"'+(weaponFilters.category==='twohanded'?' selected':'')+'>Two-Handed Weapons</option>'+
    '</select>'+
    '<select id="wt-type" class="wt-select" onchange="setWeaponFilter(\'type\',this.value)">'+
      '<option value="all"'+(weaponFilters.type==='all'?' selected':'')+'>All types</option>'+
      '<option value="setup"'+(weaponFilters.type==='setup'?' selected':'')+'>Setup</option><option value="assault"'+(weaponFilters.type==='assault'?' selected':'')+'>Assault</option><option value="reaction"'+(weaponFilters.type==='reaction'?' selected':'')+'>Reaction</option><option value="aoe"'+(weaponFilters.type==='aoe'?' selected':'')+'>AoE</option><option value="concentration"'+(weaponFilters.type==='concentration'?' selected':'')+'>Concentration</option>'+
    '</select>'+
    '<select id="wt-availability" class="wt-select" onchange="setWeaponFilter(\'availability\',this.value)">'+
      '<option value="all"'+(weaponFilters.availability==='all'?' selected':'')+'>All states</option>'+
      '<option value="learned"'+(weaponFilters.availability==='learned'?' selected':'')+'>Learned</option><option value="available"'+(weaponFilters.availability==='available'?' selected':'')+'>Available</option><option value="locked"'+(weaponFilters.availability==='locked'?' selected':'')+'>Locked</option><option value="profession_locked"'+(weaponFilters.availability==='profession_locked'?' selected':'')+'>Profession locked</option>'+
    '</select>';
  main.appendChild(controls);

  const status=document.createElement('div');status.className='wt-action-row';
  status.innerHTML=
    '<button class="wt-action-btn alt" onclick="refreshWeaponTechniques()" '+(weaponBusy?'disabled':'')+'>Refresh</button>'+
    '<button class="wt-action-btn" onclick="stopWeaponAssault()" '+((weaponState.active_assault&&weaponState.active_assault.active&&!weaponBusy)?'':'disabled')+'>Stop Assault</button>'+
    '<span id="wt-action-status" class="wt-status-msg" style="margin:0;flex:1 1 320px;">Use this tab for live weapon-technique details, requirements, and activation.</span>';
  main.appendChild(status);

  const categoryFilter=weaponFilters.category||'all';
  const typeFilter=weaponFilters.type||'all';
  const availabilityFilter=weaponFilters.availability||'all';

  const rows=(weaponState.techniques||[]).filter(t=>{
    if(categoryFilter!=='all'&&t.category!==categoryFilter)return false;
    if(typeFilter!=='all'&&t.type!==typeFilter)return false;
    if(availabilityFilter!=='all'&&t.availability!==availabilityFilter)return false;
    return true;
  });
  if(!rows.length){main.insertAdjacentHTML('beforeend','<div class="wt-empty">No weapon techniques match the current filter.</div>');return;}

  const grid=document.createElement('div');grid.className='wt-grid';
  for(const tech of rows){grid.appendChild(buildWeaponCard(tech));}
  main.appendChild(grid);
}

function buildWeaponCard(tech){
  const card=document.createElement('div');
  card.className='wt-card '+tech.availability;
  const learnedText=tech.learned_rank>0?('Learned Rank '+tech.learned_rank+'/'+tech.max_rank):('Current Max '+tech.max_rank+'/5');
  const tags=[
    '<span class="wt-tag">'+tech.category_label+'</span>',
    '<span class="wt-tag">'+String(tech.type||'').toUpperCase()+'</span>',
    '<span class="wt-tag '+(tech.profession_ok?'ok':'bad')+'">'+(tech.profession_ok?'Profession OK':'Profession Locked')+'</span>',
    '<span class="wt-tag '+(tech.loadout_ok?'ok':'bad')+'">'+(tech.loadout_ok?'Loadout OK':'Loadout Blocked')+'</span>',
  ];
  if(tech.cooldown_remaining>0)tags.push('<span class="wt-tag bad">Cooldown '+tech.cooldown_remaining+'s</span>');
  card.innerHTML=
    '<div class="wt-card-head"><div><div class="wt-name">'+tech.name+'</div><div class="wt-mnemonic">'+tech.mnemonic+'</div></div><div class="wt-rank">'+learnedText+'</div></div>'+
    '<div class="wt-tags">'+tags.join('')+'</div>'+
    '<div class="wt-desc">'+tech.description+'</div>'+
    '<div class="wt-meta">'+
      '<div><b>Weapon Skill:</b> '+tech.weapon_skill_label+' ('+tech.skill_ranks+' ranks)</div>'+
      '<div><b>Minimum:</b> '+tech.min_ranks+' ranks</div>'+
      '<div><b>Stamina:</b> '+tech.stamina_cost+'</div>'+
      '<div><b>Cooldown:</b> '+tech.cooldown+'s</div>'+
      '<div><b>Roundtime:</b> '+tech.base_rt+'s'+(tech.rt_mod?(' ('+(tech.rt_mod>0?'+':'')+tech.rt_mod+' mod)'):'')+'</div>'+
      '<div><b>Gear:</b> '+(tech.gear_requirement_label||'Standard')+'</div>'+
      '<div><b>Thresholds:</b> '+(tech.rank_thresholds||[]).join(', ')+'</div>'+
      '<div><b>Room Targeting:</b> '+(tech.is_aoe?'Room-wide / AoE':'Single target')+'</div>'+
      (tech.reaction_trigger?'<div><b>Reaction Trigger:</b> '+tech.reaction_trigger.replaceAll('_',' ')+'</div>':'')+
    '</div>'+
    (tech.loadout_message?'<div class="wt-note"><b>Loadout:</b> '+tech.loadout_message+'</div>':'')+
    (tech.mechanics_notes?'<div class="wt-note"><b>Mechanics:</b> '+tech.mechanics_notes+'</div>':'');

  const action=document.createElement('div');action.className='wt-inline';
  const targetOptions=['<option value="">'+(tech.is_aoe?'Entire room / auto-target':'Select room target')+'</option>']
    .concat((weaponState.targets||[]).map(t=>'<option value="'+t.replace(/"/g,'&quot;')+'">'+t+'</option>'));
  action.innerHTML=
    '<select class="wt-limb-select" id="wt-target-'+tech.mnemonic+'">'+targetOptions.join('')+'</select>'+
    (tech.valid_limbs&&tech.valid_limbs.length?'<select class="wt-limb-select" id="wt-limb-'+tech.mnemonic+'"><option value="">Choose limb</option>'+tech.valid_limbs.map(l=>'<option value="'+l+'">'+l+'</option>').join('')+'</select>':'')+
    '<input class="wt-input" id="wt-target-manual-'+tech.mnemonic+'" placeholder="'+(tech.is_aoe?'Optional explicit target':'Or type target name')+'">'+
    '<button class="wt-action-btn" onclick="useWeaponTechnique(\''+tech.mnemonic+'\')" '+((tech.profession_ok&&tech.loadout_ok&&!weaponBusy)?'':'disabled')+'>Use</button>';
  card.appendChild(action);
  return card;
}

async function refreshWeaponTechniques(statusMsg){
  weaponBusy=true;
  await loadWeaponData();
  weaponBusy=false;
  render();
  if(statusMsg){
    const el=document.getElementById('wt-action-status');
    if(el)el.textContent=statusMsg;
  }
}

function setWeaponFilter(key,value){
  weaponFilters[key]=value;
  render();
}

async function stopWeaponAssault(){
  weaponBusy=true;
  try{
    const res=await fetch('/api/weapon_action',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({token:TOKEN,action:'stop_assault'})});
    const result=await res.json();
    weaponState=result.state||weaponState;
    weaponBusy=false;
    render();
    const el=document.getElementById('wt-action-status');
    if(el)el.textContent=result.error||result.message||'Assault stopped.';
  }catch(e){
    weaponBusy=false;
    render();
    const el=document.getElementById('wt-action-status');
    if(el)el.textContent='Could not reach game server.';
  }
}

async function useWeaponTechnique(mnemonic){
  const targetSel=document.getElementById('wt-target-'+mnemonic);
  const manual=document.getElementById('wt-target-manual-'+mnemonic);
  const limbSel=document.getElementById('wt-limb-'+mnemonic);
  const target=(manual&&manual.value.trim())||(targetSel&&targetSel.value)||'';
  const limb=limbSel?limbSel.value:'';
  weaponBusy=true;
  try{
    const res=await fetch('/api/weapon_action',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({token:TOKEN,action:'execute',mnemonic,target,limb})});
    const result=await res.json();
    weaponState=result.state||weaponState;
    weaponBusy=false;
    render();
    const el=document.getElementById('wt-action-status');
    if(el)el.textContent=result.error||result.message||('Executed '+mnemonic+'.');
  }catch(e){
    weaponBusy=false;
    render();
    const el=document.getElementById('wt-action-status');
    if(el)el.textContent='Could not reach game server.';
  }
}
function mkRow(id,sk){
  const cur=pending[id]!==undefined?pending[id]:sk.ranks;
  const changed=cur!==sk.ranks,empty=cur===0;
  const atCap=sk.max_ranks>0&&cur>=sk.max_ranks;
  const row=document.createElement('div');
  row.className='sk-row'+(changed?' changed':'')+(!sk.trainable&&empty?' untrained':'');
  row.id='row-'+id;
  row.innerHTML=
    '<div class="sk-name'+(changed?' mod':empty&&!sk.trainable?' dim':'')+'\" id="nm-'+id+'">'+sk.name+'</div>'+
    '<div class="sk-ranks'+(changed?' mod':'')+'\" id="rk-'+id+'">'+cur+'</div>'+
    '<div class="sk-bonus" id="bn-'+id+'">+'+bonus(cur)+'</div>'+
    '<div class="sk-cost'+(sk.ptp?' act':'')+'\" id="cp-'+id+'">'+( sk.ptp?slotCost(sk.ptp,sk.limit||1,char.level,cur,cur+1):'\u2014')+'</div>'+
    '<div class="sk-cost'+(sk.mtp?' act':'')+'\" id="cm-'+id+'">'+( sk.mtp?slotCost(sk.mtp,sk.limit||1,char.level,cur,cur+1):'\u2014')+'</div>'+
    '<div class="sk-cost" id="cap-'+id+'" style="text-align:center;color:'+(atCap?'var(--amber)':'var(--muted)')+'">'+(sk.max_ranks>0?cur+'/'+sk.max_ranks:'\u2014')+'</div>'+
    '<div class="controls" id="ct-'+id+'"></div>';
  const ct=row.querySelector('#ct-'+id);
  if(sk.trainable){
    const m=document.createElement('button');m.className='btn minus';m.textContent='\u2212';m.title='Remove rank';m.onclick=()=>adj(id,-1);
    const inp=document.createElement('input');inp.type='number';inp.className='rk-input';inp.id='inp-'+id;inp.value=cur;inp.min=0;inp.max=sk.max_ranks>0?sk.max_ranks:9999;inp.onchange=()=>setRk(id,parseInt(inp.value)||0);inp.oninput=()=>setRk(id,parseInt(inp.value)||0);
    const p=document.createElement('button');p.className='btn plus';p.textContent='+';p.title='Add rank (cap: '+sk.max_ranks+')';p.onclick=()=>adj(id,1);
    ct.appendChild(m);ct.appendChild(inp);ct.appendChild(p);
  }else{ct.innerHTML='<span style="color:var(--muted);font-size:0.8rem">N/A</span>';}
  ttAttach(row,id);
  return row;
}
function adj(id,d){const cur=pending[id]!==undefined?pending[id]:char.skills[id].ranks;setRk(id,Math.max(0,cur+d));}
function setRk(id,v){
  const sk=char.skills[id];v=Math.max(0,v);
  if(sk.max_ranks>0&&v>sk.max_ranks){v=sk.max_ranks;}
  if(v===sk.ranks)delete pending[id];else pending[id]=v;
  const inp=document.getElementById('inp-'+id);if(inp&&parseInt(inp.value)!==v)inp.value=v;
  const rkEl=document.getElementById('rk-'+id);if(rkEl){rkEl.textContent=v;rkEl.className='sk-ranks'+(v!==sk.ranks?' mod':'');}
  const bnEl=document.getElementById('bn-'+id);if(bnEl)bnEl.textContent='+'+bonus(v);
  const lim=sk.limit||1;
  const cpEl=document.getElementById('cp-'+id);if(cpEl&&sk.ptp)cpEl.textContent=slotCost(sk.ptp,lim,char.level,v,v+1);
  const cmEl=document.getElementById('cm-'+id);if(cmEl&&sk.mtp)cmEl.textContent=slotCost(sk.mtp,lim,char.level,v,v+1);
  const nmEl=document.getElementById('nm-'+id);if(nmEl)nmEl.className='sk-name'+(v!==sk.ranks?' mod':v===0&&!sk.trainable?' dim':'');
  const row=document.getElementById('row-'+id);if(row)row.classList.toggle('changed',v!==sk.ranks);
  const capEl=document.getElementById('cap-'+id);if(capEl){const atCap=sk.max_ranks>0&&v>=sk.max_ranks;capEl.textContent=v+'/'+sk.max_ranks;capEl.style.color=atCap?'var(--amber)':'var(--muted)';}
  refreshTP();
}
function slotCost(base,limit,level,fromRank,toRank){
  if(limit<=0)limit=1;const prevCap=limit*(level-1);let t=0;
  for(let r=fromRank+1;r<=toRank;r++){const sp=r<=prevCap?1:Math.min(r-prevCap,2);t+=base*sp;}return t;
}
function tpDelta(){
  let p=0,m=0;
  for(const[s,v]of Object.entries(pending)){
    const id=parseInt(s);const sk=char.skills[id];const lim=sk.limit||1;
    if(v>sk.ranks){p+=slotCost(sk.ptp,lim,char.level,sk.ranks,v);m+=slotCost(sk.mtp,lim,char.level,sk.ranks,v);}
    else{const d=sk.ranks-v;p-=sk.ptp*d;m-=sk.mtp*d;}
  }
  return[p,m];
}
function refreshTP(){
  if(!char)return;
  const[dp,dm]=tpDelta(),rp=char.physical_tp-dp,rm=char.mental_tp-dm;
  const pEl=document.getElementById('ptp'),mEl=document.getElementById('mtp');
  pEl.textContent=rp;mEl.textContent=rm;
  pEl.className='tp-val '+(rp<0?'over':rp<5?'low':'ok');
  mEl.className='tp-val '+(rm<0?'over':rm<5?'low':'ok');
  document.getElementById('save-btn').disabled=Object.keys(pending).length===0||rp<0||rm<0;
}
async function doSave(){
  const btn=document.getElementById('save-btn');btn.disabled=true;btn.innerHTML='<span class="spinner"></span>Saving...';
  const skills={};for(const[s,sk]of Object.entries(char.skills)){const id=parseInt(s);skills[id]=pending[id]!==undefined?pending[id]:sk.ranks;}
  try{
    const res=await fetch('/api/save',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({token:TOKEN,skills})});
    const result=await res.json();
    if(result.error){showSkillModal('Error','<span style="color:var(--red)">'+result.error+'</span>',true);btn.disabled=false;btn.textContent='Save Skills';return;}
    let html='';
    if(result.changes&&result.changes.length)result.changes.forEach(l=>html+='<div class="chg">\u2756 '+l+'</div>');else html='No changes recorded.';
    html+='<hr style="border:none;border-top:1px solid var(--border);margin:0.9rem 0">';
    html+='Physical TPs: <strong style="color:var(--gold)">'+result.physical_tp+'</strong>&nbsp;&nbsp;Mental TPs: <strong style="color:var(--gold)">'+result.mental_tp+'</strong>';
    showSkillModal('Training Complete',html,false);
    char.physical_tp=result.physical_tp;char.mental_tp=result.mental_tp;
    for(const[s,v]of Object.entries(pending)){const id=parseInt(s);char.skills[id].ranks=v;char.skills[id].bonus=bonus(v);}
    pending={};btn.textContent='Save Skills';
  }catch(e){showSkillModal('Error','<span style="color:var(--red)">Could not reach game server.</span>',true);btn.disabled=false;btn.textContent='Save Skills';}
}
function showSkillModal(title,body,isErr){
  document.getElementById('skill-m-title').textContent=title;
  document.getElementById('skill-m-title').style.color=isErr?'var(--red)':'var(--gold)';
  document.getElementById('skill-m-body').innerHTML=body;
  document.getElementById('skill-overlay').classList.add('show');
}
function closeSkillModal(){document.getElementById('skill-overlay').classList.remove('show');render();}

/* ════════════════════════════════════════════════════
   STAT REALLOCATION MODAL
   ════════════════════════════════════════════════════ */
const STAT_NAMES=['strength','constitution','dexterity','agility','discipline','aura','logic','intuition','wisdom','influence'];
const STAT_LABELS={strength:'Strength',constitution:'Constitution',dexterity:'Dexterity',agility:'Agility',discipline:'Discipline',aura:'Aura',logic:'Logic',intuition:'Intuition',wisdom:'Wisdom',influence:'Influence'};
const STAT_BASE_CAP=130;
const STAT_STEP=5;
let statDraft={};

function _statBonus(s){return 0;}  // bonus tracking deferred — stats rewrite pending
function _totalBonuses(){return 0;}
function _totalDraftExcept(s){let t=0;for(const n of STAT_NAMES)if(n!==s)t+=statDraft[n];return t;}

function initStatsModal(){
  const grid=document.getElementById('stat-grid');grid.innerHTML='';
  for(const s of STAT_NAMES){
    const baseVal=Math.min(char.base_stats[s]||50, STAT_BASE_CAP);
    statDraft[s]=baseVal;
    let bonusHtml='';
    const div=document.createElement('div');div.className='stat-row';
    // Use data-s attribute to avoid all quoting issues in onclick
    div.innerHTML=
      '<div class="stat-label">'+STAT_LABELS[s]+'</div>'+
      '<div class="stat-stepper" id="stepper-'+s+'">'+
        '<button class="stat-step-btn minus" id="sminus-'+s+'" data-s="'+s+'" onclick="stepStat(this.dataset.s,false)" title="Decrease by 5">\u2212</button>'+
        '<div class="stat-sep"></div>'+
        '<div class="stat-val" id="sval-'+s+'">'+baseVal+'</div>'+
        '<div class="stat-sep"></div>'+
        '<button class="stat-step-btn plus" id="splus-'+s+'" data-s="'+s+'" onclick="stepStat(this.dataset.s,true)" title="Increase by 5">+</button>'+
      '</div>'+
      bonusHtml+
      '<span style="font-size:0.78rem;margin-left:4px;" id="sd-'+s+'"></span>';
    grid.appendChild(div);
    _refreshStatButtons(s);
  }
  updateStatTotal();
  const avail=document.getElementById('fixstat-avail');
  if(char.fixstat_can){
    avail.innerHTML=char.level<20
      ?'<span style="color:var(--green);">\u2714 '+char.fixstat_uses+' free use'+(char.fixstat_uses===1?'':'s')+' remaining (before level 20)</span>'
      :'<span style="color:var(--green);">\u2714 Free reallocation available (1 per 24 hours after level 20)</span>';
  }else{
    avail.innerHTML='<span style="color:var(--amber);">\u26a0 '+char.fixstat_reason+'</span>';
    document.getElementById('fixstat-save-btn').disabled=true;
  }
}

function stepStat(s,increase){
  const current=statDraft[s];
  const budget=char.total_stats-_totalBonuses();
  const spentElsewhere=_totalDraftExcept(s);
  let v=increase?current+STAT_STEP:current-STAT_STEP;
  v=Math.max(1,Math.min(STAT_BASE_CAP,v));
  if(increase){
    const remaining=budget-spentElsewhere;
    if(v>remaining)v=remaining;
    if(v<=current)return;
  }
  if(v===current)return;
  statDraft[s]=v;
  _refreshStat(s);
  updateStatTotal();
}

function _refreshStat(s){
  const v=statDraft[s];
  const base=char.base_stats[s]||50;
  const diff=v-base;
  const valEl=document.getElementById('sval-'+s);
  if(valEl){valEl.textContent=v;valEl.className='stat-val'+(v!==base?' changed':'');}
  const dEl=document.getElementById('sd-'+s);
  if(dEl){dEl.textContent=diff===0?'':(diff>0?'+'+diff:''+diff);dEl.style.color=diff>0?'var(--green)':diff<0?'var(--red)':'var(--muted)';}
  _refreshStatButtons(s);
}

function _refreshStatButtons(s){
  const v=statDraft[s];
  const budget=char.total_stats-_totalBonuses();
  const spentElsewhere=_totalDraftExcept(s);
  const remaining=budget-spentElsewhere;
  const mb=document.getElementById('sminus-'+s);
  const pb=document.getElementById('splus-'+s);
  if(mb)mb.disabled=(v<=1);
  if(pb)pb.disabled=(v>=STAT_BASE_CAP||v>=remaining);
}

function updateStatTotal(){
  const bonusTotal=_totalBonuses();
  const baseDraftTotal=Object.values(statDraft).reduce((a,b)=>a+b,0);
  const budget=char.total_stats-bonusTotal;
  const el=document.getElementById('stat-total-display');
  el.textContent=baseDraftTotal+' / '+budget;
  const ok=(baseDraftTotal===budget);
  el.className=ok?'stat-total-ok':(baseDraftTotal>budget?'stat-total-over':'stat-total-under');
  document.getElementById('fixstat-save-btn').disabled=!ok||!char.fixstat_can;
  for(const s of STAT_NAMES)_refreshStatButtons(s);
}
function openStatsModal(){
  if(!char){return;}
  initStatsModal();
  document.getElementById('stats-overlay').classList.add('show');
}
function closeStatsModal(){document.getElementById('stats-overlay').classList.remove('show');}
async function doFixstatSave(){
  const btn=document.getElementById('fixstat-save-btn');
  btn.disabled=true;btn.innerHTML='<span class="spinner"></span>Applying...';
  try{
    const res=await fetch('/api/fixstats',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({token:TOKEN,stats:statDraft})});
    const result=await res.json();
    if(result.error){
      alert('\u26a0 '+result.error);btn.disabled=false;btn.textContent='Apply Stats';return;
    }
    // Update local char stats
    for(const s of STAT_NAMES)char.stats[s]=statDraft[s];
    char.fixstat_uses=result.fixstat_uses;
    if(result.fixstat_uses===0&&char.level<20)char.fixstat_can=false;
    let msg='<div style="margin-bottom:0.5rem;color:var(--green);font-family:Cinzel,serif">Stats updated!</div>';
    result.changes.forEach(l=>msg+='<div class="chg">\u2756 '+l+'</div>');
    msg+='<div style="margin-top:0.6rem;color:var(--muted);font-size:0.85rem">'+result.uses_msg+'</div>';
    const body=document.getElementById('skill-m-body');body.innerHTML=msg;
    document.getElementById('skill-m-title').textContent='Stat Reallocation Complete';
    document.getElementById('skill-m-title').style.color='var(--blue)';
    document.getElementById('skill-overlay').classList.add('show');
    closeStatsModal();
    btn.textContent='Apply Stats';
  }catch(e){alert('Could not reach game server.');btn.disabled=false;btn.textContent='Apply Stats';}
}

/* ════════════════════════════════════════════════════
   CONVERT TP MODAL
   ════════════════════════════════════════════════════ */
function initConvModal(){
  const rate=char.convert_rate||2;
  const pl=char.ptp_loaned||0, ml=char.mtp_loaned||0;
  let loanHtml='';
  if(pl>0||ml>0){
    loanHtml='<div style="margin-top:0.5rem;padding:0.4rem 0.6rem;border:1px solid var(--amber);background:var(--surface);font-size:0.85rem;">';
    loanHtml+='<span style="color:var(--amber);font-family:Cinzel,serif;font-size:0.75rem;">OUTSTANDING LOANS</span>';
    if(pl>0)loanHtml+='<br><span style="color:var(--amber)">PTP loan: '+pl+' PTP borrowed (refund: return '+pl+' PTP, recover '+(pl*rate)+' MTP)</span>';
    if(ml>0)loanHtml+='<br><span style="color:var(--amber)">MTP loan: '+ml+' MTP borrowed (refund: return '+ml+' MTP, recover '+(ml*rate)+' PTP)</span>';
    loanHtml+='</div>';
  }
  document.getElementById('conv-info').innerHTML=
    'Current TPs &mdash; Physical: <strong style="color:var(--green)" id="cv-ptp">'+char.physical_tp+'</strong>&nbsp;&nbsp;'+
    'Mental: <strong style="color:var(--green)" id="cv-mtp">'+char.mental_tp+'</strong>'+
    '<br><span style="color:var(--muted)">Exchange rate: '+rate+' → 1 (both directions)</span>'+loanHtml;
  document.getElementById('conv-ptp-amount').value='';
  document.getElementById('conv-mtp-amount').value='';
  document.getElementById('conv-ptp-cost').textContent='';
  document.getElementById('conv-mtp-cost').textContent='';
  // Show/hide refund buttons based on loan balances
  const refundAll=document.getElementById('conv-refund-all-btn');
  const refundPtp=document.getElementById('conv-refund-ptp-btn');
  const refundMtp=document.getElementById('conv-refund-mtp-btn');
  if(refundAll)refundAll.style.display=(pl>0||ml>0)?'inline-block':'none';
  if(refundPtp)refundPtp.style.display=pl>0?'inline-block':'none';
  if(refundMtp)refundMtp.style.display=ml>0?'inline-block':'none';
  const res=document.getElementById('conv-result');res.style.display='none';res.innerHTML='';
}
function updateConvCost(dir){
  const rate=char.convert_rate||2;
  if(dir==='ptp'){
    const v=parseInt(document.getElementById('conv-ptp-amount').value)||0;
    const cost=v*rate;
    document.getElementById('conv-ptp-cost').textContent=v>0?'costs '+cost+' MTP':'';
  }else{
    const v=parseInt(document.getElementById('conv-mtp-amount').value)||0;
    const cost=v*rate;
    document.getElementById('conv-mtp-cost').textContent=v>0?'costs '+cost+' PTP':'';
  }
}
function openConvModal(){if(!char)return;initConvModal();document.getElementById('conv-overlay').classList.add('show');}
function closeConvModal(){document.getElementById('conv-overlay').classList.remove('show');}
async function doRefund(scope){
  const btn=document.getElementById('conv-refund-all-btn');
  if(btn){btn.disabled=true;btn.innerHTML='<span class="spinner"></span>';}
  try{
    const res=await fetch('/api/refund',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({token:TOKEN,scope:scope||'all'})});
    const result=await res.json();
    const resBox=document.getElementById('conv-result');
    if(result.error){
      resBox.style.display='block';resBox.innerHTML='<span style="color:var(--red)">⚠ '+result.error+'</span>';
    }else{
      char.physical_tp=result.physical_tp;char.mental_tp=result.mental_tp;
      char.ptp_loaned=result.ptp_loaned||0;char.mtp_loaned=result.mtp_loaned||0;
      document.getElementById('ptp').textContent=result.physical_tp;
      document.getElementById('mtp').textContent=result.mental_tp;
      let html='';
      result.changes.forEach(l=>html+='<div style="color:var(--green)">✔ '+l+'</div>');
      html+='<span style="color:var(--muted);font-size:0.88rem">Physical: '+result.physical_tp+'&nbsp;&nbsp;Mental: '+result.mental_tp+'</span>';
      resBox.style.display='block';resBox.innerHTML=html;
      initConvModal();  // refresh loan display + hide refund buttons if loans cleared
    }
    if(btn){btn.disabled=false;btn.textContent='Refund All';}
  }catch(e){
    alert('Could not reach game server.');
    if(btn){btn.disabled=false;btn.textContent='Refund All';}
  }
}
async function doConvert(dir){
  const amtEl=document.getElementById('conv-'+dir+'-amount');
  const amount=parseInt(amtEl.value)||0;
  if(amount<=0){alert('Enter a positive amount to convert.');return;}
  const btnId='conv-'+dir+'-btn';const btn=document.getElementById(btnId);
  btn.disabled=true;btn.innerHTML='<span class="spinner"></span>';
  try{
    const res=await fetch('/api/convert',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({token:TOKEN,direction:dir,amount})});
    const result=await res.json();
    const resBox=document.getElementById('conv-result');
    if(result.error){
      resBox.style.display='block';resBox.innerHTML='<span style="color:var(--red)">\u26a0 '+result.error+'</span>';
    }else{
      char.physical_tp=result.physical_tp;char.mental_tp=result.mental_tp;
      if(result.ptp_loaned!==undefined)char.ptp_loaned=result.ptp_loaned;
      if(result.mtp_loaned!==undefined)char.mtp_loaned=result.mtp_loaned;
      document.getElementById('cv-ptp').textContent=result.physical_tp;
      document.getElementById('cv-mtp').textContent=result.mental_tp;
      document.getElementById('ptp').textContent=result.physical_tp;
      document.getElementById('mtp').textContent=result.mental_tp;
      resBox.style.display='block';
      resBox.innerHTML='<span style="color:var(--green)">\u2714 '+result.message+'</span>'+
        '<br><span style="color:var(--muted);font-size:0.88rem">Physical: '+result.physical_tp+'&nbsp;&nbsp;Mental: '+result.mental_tp+'</span>';
      amtEl.value='';
      updateConvCost(dir);
      initConvModal();
    }
    btn.disabled=false;btn.textContent=dir==='ptp'?'Convert \u2192 PTP':'Convert \u2192 MTP';
  }catch(e){alert('Could not reach game server.');btn.disabled=false;btn.textContent=dir==='ptp'?'Convert \u2192 PTP':'Convert \u2192 MTP';}
}

/* ════════════════════════════════════════════════════
   TOOLTIP
   ════════════════════════════════════════════════════ */
const _tt=document.getElementById('tt'),_ttN=document.getElementById('tt-name'),_ttD=document.getElementById('tt-desc'),_ttM=document.getElementById('tt-math');
let _ttT=null,_ttOn=false;
function _ttShow(id,x,y){
  const info=SKILL_INFO[id];if(!info)return;
  const sk=char&&char.skills[id];
  _ttN.textContent=sk?sk.name:'Skill '+id;_ttD.textContent=info.d;
  _ttM.innerHTML=info.m.replace(/([\d]+ ?[x\/] ?[\d]+|~?[\d]+%|>= ?[\d]+|[\d]+ ?ranks?|\bmin\b|\bmax\b|d100|\bAS\b|\bDS\b|\bDEX\b|\bDISC\b|\bPF\b|\bPTP\b|\bMTP\b)/g,'<b>$1</b>');
  _ttOn=true;_ttPos(x,y);_tt.classList.add('show');
}
function _ttPos(x,y){
  const W=window.innerWidth,H=window.innerHeight,tw=_tt.offsetWidth||300,th=_tt.offsetHeight||130;
  let lx=x+18,ly=y+18;
  if(lx+tw>W-8)lx=x-tw-8;if(ly+th>H-8)ly=y-th-8;
  _tt.style.left=Math.max(4,lx)+'px';_tt.style.top=Math.max(4,ly)+'px';
}
document.addEventListener('mousemove',e=>{if(_ttOn)_ttPos(e.clientX,e.clientY);});
function ttAttach(el,id){
  el.addEventListener('mouseenter',e=>{clearTimeout(_ttT);_ttT=setTimeout(()=>_ttShow(id,e.clientX,e.clientY),900);});
  el.addEventListener('mouseleave',()=>{clearTimeout(_ttT);_tt.classList.remove('show');_ttOn=false;});
}

/* ── Close overlays on Escape ── */
document.addEventListener('keydown',e=>{
  if(e.key==='Escape'){
    document.querySelectorAll('.overlay.show').forEach(o=>o.classList.remove('show'));
  }
});

load();
