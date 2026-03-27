/**
 * import_map.js  (SQL-file mode — no external npm packages needed)
 * ================================================================
 * Writes output to C:\Temp\gemstone_map_import.sql
 * then run:  mysql -u root gemstone_dev < C:\Temp\gemstone_map_import.sql
 */
'use strict';

const fs   = require('fs');
const path = require('path');

const BATCH_SIZE = 300;
const MAP_DIR    = 'N:\\GemStoneIVServer';
const OUT_FILE   = 'C:\\Temp\\gemstone_map_import.sql';

// ── Direction normalisation ─────────────────────────────────────────
const SIMPLE_DIRS = new Set([
  'north','south','east','west',
  'northeast','northwest','southeast','southwest',
  'up','down','out','in',
  'n','s','e','w','ne','nw','se','sw','u','d',
]);
const DIR_NORM = {
  n:'north',s:'south',e:'east',w:'west',
  ne:'northeast',nw:'northwest',se:'southeast',sw:'southwest',
  u:'up',d:'down',
};

// ── Known location → zone slug ──────────────────────────────────────
const KNOWN_ZONES = {
  "wehnimer's landing":'wehnimers_landing',"wehnimers landing":'wehnimers_landing',
  "the landing":'wehnimers_landing',"upper trollfang":'wehnimers_landing',
  "lower trollfang":'wehnimers_landing',"the kobold village":'wehnimers_landing',
  "the graveyard":'wehnimers_landing',"the cemetery":'wehnimers_landing',
  "darkling wood":'wehnimers_landing',"krag forest":'wehnimers_landing',
  "the defile":'wehnimers_landing',"black sands":'wehnimers_landing',
  "the old mine road":'wehnimers_landing',"the abandoned mine":'wehnimers_landing',
  "the edge of the forest":'wehnimers_landing',"the trail":'wehnimers_landing',
  "the abandoned inn":'wehnimers_landing',
  "icemule trace":'icemule_trace',"icemule":'icemule_trace',
  "the foothills":'icemule_trace',"white mountain path":'icemule_trace',
  "the frozen battlefield":'icemule_trace',"thanatoph":'icemule_trace',
  "the icemule arena":'icemule_trace',
  "ta'vaalor":'tavaalor',"tavaalor":'tavaalor',"victory road":'tavaalor',
  "the red forest":'tavaalor',"the blighted forest":'tavaalor',"vaalor keep":'tavaalor',
  "ta'illistim":'taillistim',"taillistim":'taillistim',
  "the gossamer valley":'taillistim',"crystal meadow":'taillistim',
  "the shattered vale":'taillistim',
  "solhaven":'solhaven',"vornavis":'solhaven',"the greater vornavis":'solhaven',
  "the caravansary":'solhaven',
  "river's rest":'rivers_rest',"rivers rest":'rivers_rest',"the confluence":'rivers_rest',
  "teras isle":'teras_isle',"kharam dzu":'teras_isle',"the volcano":'teras_isle',
  "zul logoth":'zul_logoth',"zul'logoth":'zul_logoth',
  "mist harbor":'mist_harbor',"the floating isle":'mist_harbor',
  "cysaegir":'cysaegir',"the sylvan settlement":'cysaegir',
  "kraken's fall":'krakens_fall',"krakens fall":'krakens_fall',
  "the moonglae inn":'premium_moonglae',"moonglae inn":'premium_moonglae',
  "the gryphon inn":'premium_gryphon',"the four winds":'premium_four_winds',
  "the elven nations road":'elven_nations_road',"the elven nations":'elven_nations_road',
  "the dragonsclaw mountains":'dragonsclaw_mountains',
  "the dragonsclaw foothills":'dragonsclaw_mountains',
  "the wastelands":'wastelands',"the deadfall":'deadfall',
  "the rift":'the_rift',"plane of the titans":'plane_of_titans',
};

function slugify(str){
  return str.toLowerCase().replace(/[^a-z0-9]+/g,'_')
    .replace(/^_+|_+$/g,'').slice(0,64)||'unknown';
}
function locationToSlug(loc){
  const k=(loc||'').toLowerCase().trim();
  if(KNOWN_ZONES[k]) return KNOWN_ZONES[k];
  for(const [kk,v] of Object.entries(KNOWN_ZONES)){
    if(k.includes(kk)||kk.includes(k)) return v;
  }
  return slugify(loc||'unknown');
}
function esc(s){
  if(s==null) return 'NULL';
  return "'"+String(s).replace(/\\/g,'\\\\').replace(/'/g,"\\'")
    .replace(/\n/g,'\\n').replace(/\r/g,'').slice(0,65000)+"'";
}
function escInt(n){const i=parseInt(n,10);return isNaN(i)?'NULL':String(i);}
function isIndoor(room){
  const t=room.tags||[];
  if(t.some(x=>x==='indoor'||x==='indoors')) return 1;
  if(t.some(x=>x==='outdoor'||x==='outdoors')) return 0;
  return((room.climate||'').toLowerCase()==='none'&&(room.terrain||'').toLowerCase()==='none')?1:0;
}
function parseTags(tags){
  const t=tags||[];
  return{
    isSafe:t.some(x=>x==='safe'||x==='bank'||x.startsWith('sanctuary'))?1:0,
    isSupernode:t.some(x=>x==='supernode'||x.includes('node'))?1:0,
  };
}
function cleanTitle(arr){
  const r=(arr&&arr[0])?arr[0]:'';
  return r.replace(/^\[/,'').replace(/\]$/,'').slice(0,199);
}
function parseWayto(val){
  if(!val||typeof val!=='string') return null;
  const v=val.trim();
  if(SIMPLE_DIRS.has(v.toLowerCase())){
    return{direction:DIR_NORM[v.toLowerCase()]||v.toLowerCase(),exitVerb:null,isSpecial:0};
  }
  const gM=v.match(/^go\s+(.+)$/i);
  if(gM) return{direction:'go_'+gM[1].trim().toLowerCase().replace(/\s+/g,'_').slice(0,28),exitVerb:'go',isSpecial:1};
  const eM=v.match(/^enter\s+(.+)$/i);
  if(eM) return{direction:'enter_'+eM[1].trim().toLowerCase().replace(/\s+/g,'_').slice(0,25),exitVerb:'enter',isSpecial:1};
  const cM=v.match(/^climb\s+(.+)$/i);
  if(cM) return{direction:'climb_'+cM[1].trim().toLowerCase().replace(/\s+/g,'_').slice(0,25),exitVerb:'climb',isSpecial:1};
  if(v.startsWith(';')||v.startsWith('#')) return null;
  if(v.length<=20&&/^[a-z_ ]+$/i.test(v)){
    return{direction:v.toLowerCase().replace(/\s+/g,'_').slice(0,31),exitVerb:null,isSpecial:1};
  }
  return null;
}

// ── Main ─────────────────────────────────────────────────────────────
let mapFile = process.argv[2]||path.join(MAP_DIR,
  fs.readdirSync(MAP_DIR).find(f=>f.match(/^map-.*\.json$/))||'map.json');

console.log(`Reading ${path.basename(mapFile)}...`);
const rooms = JSON.parse(fs.readFileSync(mapFile,'utf8'));
console.log(`Parsed: ${rooms.length} rooms`);

// Pass 1 – collect zones
const zoneMap = new Map();
for(const r of rooms){
  const s=locationToSlug(r.location||'unknown');
  if(!zoneMap.has(s)) zoneMap.set(s,r.location||'unknown');
}
console.log(`Zones: ${zoneMap.size}`);

// Write SQL
console.log(`Writing SQL to ${OUT_FILE}...`);
const out = fs.createWriteStream(OUT_FILE,{encoding:'utf8'});

out.on('error', e=>{ console.error('Stream error:',e); process.exit(1); });

out.write('-- GemStone IV map import\nUSE gemstone_dev;\n');
out.write('SET FOREIGN_KEY_CHECKS=0;\nSET SESSION max_allowed_packet=67108864;\n\n');

// Zones
let zb=[];
for(const[s,n] of zoneMap){
  zb.push(`(${esc(s)},${esc(n.slice(0,127))},'Elanthia')`);
  if(zb.length>=BATCH_SIZE){
    out.write(`INSERT INTO zones(slug,name,region)VALUES\n${zb.join(',\n')}\nON DUPLICATE KEY UPDATE name=VALUES(name);\n\n`);
    zb=[];
  }
}
if(zb.length){out.write(`INSERT INTO zones(slug,name,region)VALUES\n${zb.join(',\n')}\nON DUPLICATE KEY UPDATE name=VALUES(name);\n\n`);}

// Temp zone map
out.write('DROP TEMPORARY TABLE IF EXISTS tmp_zone;\n');
out.write('CREATE TEMPORARY TABLE tmp_zone(slug VARCHAR(64) PRIMARY KEY,zone_id SMALLINT UNSIGNED);\n');
out.write('INSERT INTO tmp_zone(slug,zone_id)SELECT slug,id FROM zones;\n\n');

// Rooms
let rb=[]; let rc=0;
const flushRooms=()=>{
  if(!rb.length) return;
  out.write(
    'INSERT INTO rooms(id,zone_id,title,description,lich_uid,paths_text,location_name,tags_json,is_safe,is_supernode,is_indoor,terrain_type,climate,terrain,indoor)VALUES\n'+
    rb.join(',\n')+'\nON DUPLICATE KEY UPDATE zone_id=VALUES(zone_id),title=VALUES(title),description=VALUES(description),lich_uid=VALUES(lich_uid),paths_text=VALUES(paths_text),location_name=VALUES(location_name),tags_json=VALUES(tags_json),is_safe=VALUES(is_safe),is_supernode=VALUES(is_supernode),is_indoor=VALUES(is_indoor),terrain_type=VALUES(terrain_type),climate=VALUES(climate),terrain=VALUES(terrain),indoor=VALUES(indoor);\n\n'
  );
  rc+=rb.length; rb=[];
};

for(const r of rooms){
  const slug=locationToSlug(r.location||'unknown');
  const title=cleanTitle(r.title);
  const desc=r.description&&r.description[0]?r.description[0]:null;
  const paths=r.paths&&r.paths[0]?r.paths[0].slice(0,254):null;
  const uid=r.uid&&r.uid[0]?r.uid[0]:null;
  const tags=r.tags||[];
  const{isSafe,isSupernode}=parseTags(tags);
  const indoor=isIndoor(r);
  const tType=((r.terrain||'none').toLowerCase()==='none')?'urban':r.terrain;
  rb.push(`(${escInt(r.id)},(SELECT zone_id FROM tmp_zone WHERE slug=${esc(slug)}),${esc(title)},${esc(desc)},${escInt(uid)},${esc(paths)},${esc((r.location||'').slice(0,127))},${esc(JSON.stringify(tags))},${isSafe},${isSupernode},${indoor},${esc(tType)},${esc(r.climate||null)},${esc(r.terrain||null)},${indoor})`);
  if(rb.length>=BATCH_SIZE) flushRooms();
}
flushRooms();
console.log(`Rooms batched: ${rc}`);

// Exits
const allIds=new Set(rooms.map(r=>r.id));
let eb=[]; let ec=0; let es=0;
const flushExits=()=>{
  if(!eb.length) return;
  out.write(
    'INSERT INTO room_exits(room_id,direction,exit_verb,target_room_id,is_hidden,is_special,search_dc)VALUES\n'+
    eb.join(',\n')+'\nON DUPLICATE KEY UPDATE exit_verb=VALUES(exit_verb),target_room_id=VALUES(target_room_id),is_special=VALUES(is_special);\n\n'
  );
  ec+=eb.length; eb=[];
};

for(const r of rooms){
  if(!r.wayto||typeof r.wayto!=='object') continue;
  if(!allIds.has(r.id)) continue;
  for(const[ts,cmd] of Object.entries(r.wayto)){
    const toId=parseInt(ts,10);
    if(isNaN(toId)||!allIds.has(toId)){es++;continue;}
    const p=parseWayto(cmd);
    if(!p){es++;continue;}
    eb.push(`(${r.id},${esc(p.direction.slice(0,31))},${esc(p.exitVerb)},${toId},0,${p.isSpecial},0)`);
    if(eb.length>=BATCH_SIZE) flushExits();
  }
}
flushExits();
console.log(`Exits batched: ${ec}  skipped: ${es}`);

out.write('SET FOREIGN_KEY_CHECKS=1;\nDROP TEMPORARY TABLE IF EXISTS tmp_zone;\n');
out.write('SELECT COUNT(*) AS zones FROM zones;\n');
out.write('SELECT COUNT(*) AS rooms FROM rooms;\n');
out.write('SELECT COUNT(*) AS exits FROM room_exits;\n');

out.end(()=>{
  const bytes=fs.statSync(OUT_FILE).size;
  console.log(`\nSQL file: ${OUT_FILE} (${(bytes/1024/1024).toFixed(1)} MB)`);
  console.log('Run: mysql -u root gemstone_dev < C:\\Temp\\gemstone_map_import.sql');
});
