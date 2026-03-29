"""
pet_server.py
-------------
Moonwhisker Menagerie web portal.

Accessible only while physically inside the pet shop via one-time token URL.
"""

import asyncio
import datetime
import json
import logging
import os
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

log = logging.getLogger(__name__)

WEB_PORT = 8767
TOKEN_TTL = 600
FLOOFER_ASSET_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "..",
        "clientmedia",
        "pets",
    )
)
FLOOFER_ASSET_CANDIDATES = (
    "Floof.jpg",
    "floofer.jpg",
    "Floof.jpeg",
    "floofer.jpeg",
    "Floof.png",
    "floofer.png",
)


def _json_safe(value):
    if isinstance(value, (datetime.datetime, datetime.date)):
        return value.isoformat(sep=" ")
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_json_safe(v) for v in value]
    return value


def _svg_floofer() -> str:
    return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
<defs>
  <linearGradient id="bg" x1="0" x2="1" y1="0" y2="1">
    <stop offset="0%" stop-color="#ffe1f4"/>
    <stop offset="50%" stop-color="#d1b0ff"/>
    <stop offset="100%" stop-color="#8f6cff"/>
  </linearGradient>
  <radialGradient id="fur" cx="50%" cy="36%" r="62%">
    <stop offset="0%" stop-color="#ffd6ef"/>
    <stop offset="58%" stop-color="#d79cff"/>
    <stop offset="100%" stop-color="#9b6cf6"/>
  </radialGradient>
</defs>
<rect width="512" height="512" rx="48" fill="#10222b"/>
<circle cx="256" cy="260" r="138" fill="url(#fur)"/>
<path d="M160 150 L116 56 L214 120 Z" fill="#ef9dd8"/>
<path d="M352 150 L398 56 L298 120 Z" fill="#ef9dd8"/>
<path d="M176 154 L138 82 L210 124 Z" fill="#ffd7ef"/>
<path d="M336 154 L374 82 L302 124 Z" fill="#ffd7ef"/>
<ellipse cx="206" cy="248" rx="42" ry="54" fill="#1b1832"/>
<ellipse cx="306" cy="248" rx="42" ry="54" fill="#1b1832"/>
<circle cx="194" cy="234" r="12" fill="#ffffff"/>
<circle cx="294" cy="234" r="12" fill="#ffffff"/>
<circle cx="214" cy="262" r="6" fill="#8ab7ff"/>
<circle cx="314" cy="262" r="6" fill="#8ab7ff"/>
<path d="M240 304 Q256 290 272 304 Q256 334 240 304 Z" fill="#ff93bf"/>
<path d="M226 332 Q256 354 286 332" stroke="#ffe3f4" stroke-width="6" fill="none" stroke-linecap="round"/>
<path d="M120 404 Q178 352 240 406" stroke="#f7bbff" stroke-width="28" fill="none" stroke-linecap="round"/>
<circle cx="120" cy="404" r="10" fill="#f0d8ff"/>
<circle cx="88" cy="178" r="5" fill="#9be7ff"/>
<circle cx="122" cy="140" r="6" fill="#ffd6ff"/>
<circle cx="404" cy="164" r="6" fill="#9be7ff"/>
<circle cx="426" cy="206" r="5" fill="#ffd6ff"/>
<circle cx="156" cy="94" r="4" fill="#ffffff"/>
<circle cx="358" cy="94" r="4" fill="#ffffff"/>
</svg>"""


def _find_floofer_asset():
    for filename in FLOOFER_ASSET_CANDIDATES:
        path = os.path.join(FLOOFER_ASSET_DIR, filename)
        if os.path.exists(path):
            return path
    return None


class PetRequestHandler(BaseHTTPRequestHandler):
    server_ref = None

    def log_message(self, format, *args):
        pass

    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        if parsed.path == "/pets":
            self._serve_page(params)
        elif parsed.path == "/api/pets/state":
            self._serve_state(params)
        elif parsed.path == "/assets/floofer":
            self._serve_floofer_asset()
        else:
            self._send_html("<h1>404</h1>", 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        try:
            data = json.loads(body)
        except Exception:
            self._json_error("Invalid JSON", 400)
            return

        if parsed.path == "/api/pets/buy":
            self._handle_buy_pet(data)
        elif parsed.path == "/api/pets/buy-item":
            self._handle_buy_item(data)
        elif parsed.path == "/api/pets/swap":
            self._handle_swap(data)
        elif parsed.path == "/api/pets/rename":
            self._handle_rename(data)
        elif parsed.path == "/api/pets/delete":
            self._handle_delete(data)
        else:
            self._json_error("Unknown endpoint", 404)

    def _resolve_token(self, token_str):
        if not token_str:
            return None, "No token provided"
        server = PetRequestHandler.server_ref
        tokens = getattr(server, "pet_tokens", {})
        entry = tokens.get(token_str)
        if not entry:
            return None, "Invalid or expired token. Type PET SHOP again in the menagerie."
        if time.time() > entry["expires"]:
            del tokens[token_str]
            return None, "Token expired. Type PET SHOP again in the menagerie."
        return entry["session"], None

    def _ensure_session_in_shop(self, session):
        if not session:
            return False, "Invalid session."
        pets = getattr(self.server_ref, "pets", None)
        room = getattr(session, "current_room", None)
        if not pets or not room or not pets.is_pet_shop_room(getattr(room, "id", 0)):
            return False, "Return to Moonwhisker Menagerie to use the companion catalogue."
        return True, None

    def _token_from_params(self, params):
        return params.get("token", [None])[0]

    def _serve_page(self, params):
        token = self._token_from_params(params)
        session, err = self._resolve_token(token)
        if not session:
            self._send_html(_error_page(err), 401)
            return
        ok, err = self._ensure_session_in_shop(session)
        if not ok:
            self._send_html(_error_page(err), 403)
            return
        self._send_html(_build_html(token), 200)

    def _serve_state(self, params):
        token = self._token_from_params(params)
        session, err = self._resolve_token(token)
        if not session:
            self._json_error(err, 401)
            return
        ok, err = self._ensure_session_in_shop(session)
        if not ok:
            self._json_error(err, 403)
            return
        payload = self.server_ref.pets.portal_payload(session)
        self._json_response(payload)

    def _serve_floofer_asset(self):
        asset_path = _find_floofer_asset()
        if asset_path:
            with open(asset_path, "rb") as handle:
                body = handle.read()
            ext = os.path.splitext(asset_path)[1].lower()
            content_type = "image/jpeg" if ext in {".jpg", ".jpeg"} else "image/png"
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
            self.end_headers()
            self.wfile.write(body)
            return

        body = _svg_floofer().encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "image/svg+xml; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.end_headers()
        self.wfile.write(body)

    def _handle_buy_pet(self, data):
        token = data.get("token")
        session, err = self._resolve_token(token)
        if not session:
            self._json_error(err, 401)
            return
        ok, err = self._ensure_session_in_shop(session)
        if not ok:
            self._json_error(err, 403)
            return
        ok, msg, pet = self.server_ref.pets.buy_pet(session, data.get("species_key"))
        if not ok:
            self._json_error(msg, 400)
            return
        if session.pet_progress.get("quest_state") != "completed":
            self._run_coro(self.server_ref.pets.complete_first_pet_quest(session))
        self._json_response({
            "ok": True,
            "message": msg,
            "pet_id": pet.get("id") if pet else None,
            "pet_name": pet.get("pet_name") if pet else None,
            "state": self.server_ref.pets.portal_payload(session),
        })

    def _handle_buy_item(self, data):
        token = data.get("token")
        session, err = self._resolve_token(token)
        if not session:
            self._json_error(err, 401)
            return
        ok, err = self._ensure_session_in_shop(session)
        if not ok:
            self._json_error(err, 403)
            return
        ok, msg = self.server_ref.pets.buy_pet_item(session, data.get("treat_key"), data.get("quantity", 1))
        if not ok:
            self._json_error(msg, 400)
            return
        self._json_response({
            "ok": True,
            "message": msg,
            "state": self.server_ref.pets.portal_payload(session),
        })

    def _handle_swap(self, data):
        token = data.get("token")
        session, err = self._resolve_token(token)
        if not session:
            self._json_error(err, 401)
            return
        ok, err = self._ensure_session_in_shop(session)
        if not ok:
            self._json_error(err, 403)
            return
        ok, msg = self.server_ref.pets.set_active_pet_from_shop(session, data.get("pet_id"))
        if not ok:
            self._json_error(msg, 400)
            return
        self._json_response({
            "ok": True,
            "message": msg,
            "state": self.server_ref.pets.portal_payload(session),
        })

    def _handle_rename(self, data):
        token = data.get("token")
        session, err = self._resolve_token(token)
        if not session:
            self._json_error(err, 401)
            return
        ok, err = self._ensure_session_in_shop(session)
        if not ok:
            self._json_error(err, 403)
            return
        ok, msg = self.server_ref.pets.rename_pet_from_shop(session, data.get("pet_id"), data.get("pet_name"))
        if not ok:
            self._json_error(msg, 400)
            return
        self._json_response({
            "ok": True,
            "message": msg,
            "state": self.server_ref.pets.portal_payload(session),
        })

    def _handle_delete(self, data):
        token = data.get("token")
        session, err = self._resolve_token(token)
        if not session:
            self._json_error(err, 401)
            return
        ok, err = self._ensure_session_in_shop(session)
        if not ok:
            self._json_error(err, 403)
            return
        ok, msg = self.server_ref.pets.delete_pet_from_shop(session, data.get("pet_id"))
        if not ok:
            self._json_error(msg, 400)
            return
        self._json_response({
            "ok": True,
            "message": msg,
            "state": self.server_ref.pets.portal_payload(session),
        })

    def _run_coro(self, coro):
        loop = getattr(self.server_ref, "_loop", None)
        if loop and loop.is_running():
            asyncio.run_coroutine_threadsafe(coro, loop)

    def _json_response(self, payload, status=200):
        body = json.dumps(_json_safe(payload)).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.end_headers()
        self.wfile.write(body)

    def _json_error(self, message, status=400):
        self._json_response({"error": message}, status=status)

    def _send_html(self, html, status=200):
        body = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.end_headers()
        self.wfile.write(body)


def _error_page(message):
    return f"""<!doctype html><html><body style="background:#0d1218;color:#f4d7a6;font-family:Georgia,serif;padding:2rem">
    <h1>Moonwhisker Menagerie</h1><p>{message}</p></body></html>"""


_HTML = """<!doctype html>
<html><head><meta charset="utf-8"/><title>Moonwhisker Menagerie</title>
<style>
:root{--bg:#0d1318;--panel:#14202a;--gold:#f2c97f;--ink:#f6ead0;--muted:#9cb2c2;--rose:#f08bd7;--vio:#9f7df5;--green:#6fd39b;--red:#ef7171}
*{box-sizing:border-box}body{margin:0;font-family:Georgia,"Palatino Linotype",serif;background:radial-gradient(circle at top,#243744 0,#0d1318 58%);color:var(--ink)}
.wrap{max-width:1180px;margin:0 auto;padding:24px}
.hero{display:grid;grid-template-columns:320px 1fr;gap:24px;align-items:stretch}
.card{background:linear-gradient(180deg,#16232d 0,#101920 100%);border:1px solid #314756;border-radius:20px;padding:20px;box-shadow:0 18px 40px rgba(0,0,0,.28)}
.portrait{width:100%;aspect-ratio:1/1;border-radius:18px;object-fit:cover;background:#0a1015;border:1px solid #41596a}.portrait-stage{width:100%;aspect-ratio:1/1;border-radius:18px;background:#0a1015;border:1px solid #41596a;display:flex;align-items:center;justify-content:center;padding:18px;text-align:center}
.headline{font-size:2rem;color:var(--gold);margin:0 0 .25rem}
.sub{color:var(--muted);margin:0 0 1rem}
.tabs{display:flex;gap:10px;flex-wrap:wrap;margin:24px 0 18px}
.tab{border:none;border-radius:999px;padding:10px 16px;background:#1d2c38;color:var(--ink);cursor:pointer;font-weight:700}
.tab.active{background:linear-gradient(90deg,var(--rose),var(--vio));color:#fff}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:16px}
.pet-card,.item-card{background:#111a22;border:1px solid #314756;border-radius:18px;padding:16px}
.pet-card h3,.item-card h3{margin:0 0 8px;color:var(--gold)}
.price{color:var(--green);font-weight:700}
.muted{color:var(--muted)}
.btn{border:none;border-radius:12px;padding:10px 14px;background:linear-gradient(90deg,var(--rose),var(--vio));color:#fff;font-weight:700;cursor:pointer}
.btn.alt{background:#203342}
.btn.danger{background:linear-gradient(90deg,#7d1a32,#bb3953)}
.section{display:none}.section.active{display:block}
.owned{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px}
.bar{height:10px;background:#0b0f14;border-radius:999px;overflow:hidden;border:1px solid #2f4657}
.fill{height:100%;background:linear-gradient(90deg,var(--rose),var(--vio))}
.row{display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.ability-list{display:grid;gap:10px;margin:14px 0}
.ability{padding:10px 12px;border-radius:14px;background:#0d151b;border:1px solid #2b404e}
.ability h4{margin:0 0 4px;color:var(--gold);font-size:1rem}
.ability .ability-status{color:var(--green);font-weight:700;margin-bottom:4px}
.ability .ability-next{color:var(--muted);margin-top:4px}
.input{width:100%;padding:10px 12px;border-radius:12px;border:1px solid #324755;background:#0d151b;color:var(--ink)}
#msg{margin:14px 0 0;color:var(--muted);min-height:20px}
@media (max-width:820px){.hero{grid-template-columns:1fr}.wrap{padding:14px}}
</style></head>
<body><div class="wrap">
  <div class="hero">
    <div class="card"><div id="hero-empty" class="portrait-stage muted">Select a pet card to preview it here.</div><img id="hero-img" class="portrait" alt="Selected pet portrait" style="display:none"/></div>
    <div class="card">
      <h1 class="headline">Moonwhisker Menagerie</h1>
      <p class="sub">A boutique companion house for bonded pets, care items, and long-term training.</p>
      <div id="shopkeeper" class="muted"></div>
      <div style="margin-top:16px" id="summary"></div>
      <div id="msg"></div>
    </div>
  </div>
  <div class="tabs">
    <button class="tab active" data-tab="sale">Pets For Sale</button>
    <button class="tab" data-tab="items">Pet Items</button>
    <button class="tab" data-tab="training">Pet Training</button>
    <button class="tab" data-tab="swap">Swap Pet</button>
  </div>
  <section class="section active" id="sale"></section>
  <section class="section" id="items"></section>
  <section class="section" id="training"></section>
  <section class="section" id="swap"></section>
</div>
<script>
const TOKEN = "TOKEN_PLACEHOLDER";
const ASSET_VERSION = '20260328e';
let state = null;
const $ = s => document.querySelector(s);
const el = (tag, cls, html) => { const e=document.createElement(tag); if(cls)e.className=cls; if(html!==undefined)e.innerHTML=html; return e; };
document.querySelectorAll('.tab').forEach(btn => btn.onclick = () => {
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
  btn.classList.add('active'); document.getElementById(btn.dataset.tab).classList.add('active');
});
function say(msg, good=false){ const n=$('#msg'); n.style.color=good?'var(--green)':'var(--muted)'; n.textContent=msg; }
async function api(path, body){
  const res = await fetch(path,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({...body,token:TOKEN})});
  const data = await res.json();
  if(data.error) throw new Error(data.error);
  return data;
}
function assetUrl(path){
  if(!path) return '';
  return path + (path.includes('?') ? '&' : '?') + 'v=' + ASSET_VERSION;
}
function escapeHtml(value){
  return String(value ?? '')
    .replaceAll('&','&amp;')
    .replaceAll('<','&lt;')
    .replaceAll('>','&gt;')
    .replaceAll('"','&quot;')
    .replaceAll("'",'&#39;');
}
function setHero(imagePath, label='', hint='Select a pet card to preview it here.'){
  const img = $('#hero-img');
  const empty = $('#hero-empty');
  if(imagePath){
    img.src = assetUrl(imagePath);
    img.alt = label || 'Selected pet portrait';
    img.style.display = 'block';
    empty.style.display = 'none';
    return;
  }
  img.removeAttribute('src');
  img.style.display = 'none';
  empty.style.display = 'flex';
  empty.textContent = hint;
}
function renderAbilityList(abilities){
  if(!abilities || !abilities.length) return '<div class="muted">No abilities listed.</div>';
  return '<div class="ability-list">' + abilities.map(ab => {
    const status = ab.status ? '<div class="ability-status">'+escapeHtml(ab.status)+'</div>' : '';
    const next = ab.next_summary ? '<div class="ability-next">Next ('+escapeHtml(String(ab.next_level || ''))+'): '+escapeHtml(ab.next_summary)+'</div>' : '';
    return '<div class="ability">'
      + '<h4>'+escapeHtml(ab.label)+'</h4>'
      + status
      + '<div>'+escapeHtml(ab.current_summary || ab.description || '')+'</div>'
      + next
      + '</div>';
  }).join('') + '</div>';
}
function renderHeader(){
  const c = state.character, shop = state.shop;
  const activePet = (state.pets || []).find(p => p.active);
  if(activePet){
    setHero(activePet.image_path || '/assets/floofer', activePet.pet_name + ' portrait');
  }else{
    setHero('', '', 'Select a pet card to preview it here.');
  }
  $('#shopkeeper').textContent = (shop.shopkeeper.full_name || 'Virelle') + ' — ' + (shop.shopkeeper.title || 'Moonwhisker keeper');
  const delivery = state.item_delivery || {};
  const deliveryLine = delivery.available
    ? '<div class="muted" style="margin-top:8px">Pet items will be delivered to your '+escapeHtml(delivery.location || 'container')+'.</div>'
    : '<div class="muted" style="margin-top:8px;color:#f85149">Pet item delivery blocked: '+escapeHtml(delivery.reason || 'No storage space available.')+'</div>';
  $('#summary').innerHTML = '<div class="row"><strong>'+c.name+'</strong><span class="price">'+c.silver.toLocaleString()+' silver</span></div>'
    + '<div class="muted" style="margin-top:8px">Quest state: '+c.progress.quest_state+' • First pet claimed: '+(c.progress.first_pet_claimed?'yes':'no')+'</div>'
    + deliveryLine;
}
function renderSale(){
  const root = $('#sale'); root.innerHTML = '<div class="grid"></div>'; const g=root.firstChild;
  state.species_for_sale.forEach(spec => {
    const card = el('div','pet-card');
    card.innerHTML = '<h3>'+spec.label+'</h3><div class="muted" style="margin-bottom:10px">'+spec.description+'</div>'
      + '<div class="row" style="justify-content:space-between"><span class="price">'+(spec.price===0?'FREE':spec.price.toLocaleString()+' silver')+'</span></div>'
      + renderAbilityList(spec.abilities || [])
      + '<button class="btn">Purchase</button>';
    card.addEventListener('click', () => setHero(spec.image_path || '/assets/floofer', spec.label + ' portrait'));
    card.querySelector('button').onclick = async () => {
      try{
        const result = await api('/api/pets/buy',{species_key:spec.species_key});
        state = result.state; renderAll(); say(result.message,true);
        await promptForPetName(result.pet_id, spec.label);
      }catch(err){ say(err.message); }
    };
    g.appendChild(card);
  });
}
function renderItems(){
  const root = $('#items'); root.innerHTML = '<div class="grid"></div>'; const g=root.firstChild;
  const delivery = state.item_delivery || {};
  state.treats.forEach(item => {
    const card = el('div','item-card');
    const disabledAttr = delivery.available ? '' : ' disabled';
    const deliveryText = delivery.available
      ? '<div class="muted" style="margin-top:10px">Delivers to your '+escapeHtml(delivery.location || 'container')+'.</div>'
      : '<div class="muted" style="margin-top:10px;color:#f85149">'+escapeHtml(delivery.reason || 'No storage space available.')+'</div>';
    card.innerHTML = '<h3>'+item.label+'</h3><div class="muted">Training treat tier '+item.tier+'. Field-usable every two real-world hours per pet.</div>'
      + deliveryText
      + '<div class="row" style="justify-content:space-between;margin-top:12px"><span class="price">'+item.price.toLocaleString()+' silver</span>'
      + '<button class="btn"'+disabledAttr+'>Buy</button></div>';
    card.querySelector('button').onclick = async () => {
      if(!delivery.available){ say(delivery.reason || 'No storage space available for pet items.'); return; }
      try{
        const result = await api('/api/pets/buy-item',{treat_key:item.key,quantity:1});
        state = result.state; renderAll(); say(result.message,true);
      }catch(err){ say(err.message); }
    };
    g.appendChild(card);
  });
}
function renderTraining(){
  const root = $('#training'); root.innerHTML = '<div class="owned"></div>'; const g=root.firstChild;
  if(!state.pets.length){ g.appendChild(el('div','card','<strong>No pets owned yet.</strong><div class="muted">Claim your first Floofer from the sale tab.</div>')); return; }
  state.pets.forEach(pet => {
    const card = el('div','pet-card');
    const pct = pet.xp_to_next>0 ? Math.max(0,Math.min(100,(pet.xp_into_level / pet.xp_to_next)*100)) : 100;
    card.innerHTML = '<h3>'+pet.pet_name+'</h3><div class="muted">Level '+pet.level+' • XP '+pet.xp+'</div>'
      + '<div class="bar" style="margin:10px 0"><div class="fill" style="width:'+pct+'%"></div></div>'
      + renderAbilityList(pet.abilities || [])
      + '<div class="muted">Train in the field with PET FEED &lt;treat&gt;. Menagerie purchases place treats directly in your inventory.</div>';
    card.addEventListener('click', () => setHero(pet.image_path || '/assets/floofer', pet.pet_name + ' portrait'));
    g.appendChild(card);
  });
}
function renderSwap(){
  const root = $('#swap'); root.innerHTML = '<div class="owned"></div>'; const g=root.firstChild;
  if(!state.pets.length){ g.appendChild(el('div','card','<strong>No pets owned yet.</strong>')); return; }
  state.pets.forEach(pet => {
    const card = el('div','pet-card');
    card.innerHTML = '<h3>'+pet.pet_name+'</h3><div class="muted">Level '+pet.level+(pet.active?' • currently active':'')+'</div>'
      + '<div class="row" style="margin-top:12px">'
      + '<button class="btn">'+(pet.active?'Active':'Make Active')+'</button>'
      + '<button class="btn alt">Rename</button>'
      + '<button class="btn danger">Permanent Remove</button></div>';
    card.addEventListener('click', () => setHero(pet.image_path || '/assets/floofer', pet.pet_name + ' portrait'));
    const buttons = card.querySelectorAll('button');
    buttons[0].onclick = async () => {
      try{
        const result = await api('/api/pets/swap',{pet_id:pet.id});
        state = result.state; renderAll(); say(result.message,true);
      }catch(err){ say(err.message); }
    };
    buttons[1].onclick = async () => {
      await promptForPetName(pet.id, pet.pet_name);
    };
    buttons[2].onclick = async () => {
      if(!confirm('Permanently remove '+pet.pet_name+'? This cannot be undone.')) return;
      try{
        const result = await api('/api/pets/delete',{pet_id:pet.id});
        state = result.state; renderAll(); say(result.message,true);
      }catch(err){ say(err.message); }
    };
    g.appendChild(card);
  });
}
async function promptForPetName(petId, fallbackLabel){
  if(!petId) return;
  const current = (state.pets || []).find(p => Number(p.id) === Number(petId));
  const defaultValue = current && current.pet_name && !current.pet_name.startsWith('Unnamed ') ? current.pet_name : '';
  const label = fallbackLabel || (current ? current.pet_name : 'pet');
  const proposed = window.prompt('Name your new companion:', defaultValue);
  if(proposed === null) return;
  try{
    const result = await api('/api/pets/rename',{pet_id:petId,pet_name:proposed});
    state = result.state; renderAll(); say(result.message,true);
  }catch(err){
    say(err.message);
    if(current && (!current.pet_name || current.pet_name.startsWith('Unnamed '))){
      await promptForPetName(petId, label);
    }
  }
}
function renderAll(){ renderHeader(); renderSale(); renderItems(); renderTraining(); renderSwap(); }
async function load(){
  try{
    const res = await fetch('/api/pets/state?token='+encodeURIComponent(TOKEN));
    state = await res.json();
    if(state.error){ document.body.innerHTML = '<div class="wrap"><div class="card">'+state.error+'</div></div>'; return; }
    renderAll();
  }catch(err){
    document.body.innerHTML = '<div class="wrap"><div class="card">Could not open the companion catalogue.</div></div>';
  }
}

load();
</script></body></html>"""


def _build_html(token):
    return _HTML.replace("TOKEN_PLACEHOLDER", token)


class PetWebServer:
    def __init__(self, game_server, port=WEB_PORT):
        self.game_server = game_server
        self.port = port
        self._httpd = None
        self._thread = None

    def start(self):
        PetRequestHandler.server_ref = self.game_server
        self.game_server.pet_tokens = {}
        self._httpd = HTTPServer(("0.0.0.0", self.port), PetRequestHandler)
        self._thread = threading.Thread(target=self._httpd.serve_forever, daemon=True, name="PetWebServer")
        self._thread.start()
        log.info("Pet web portal: http://127.0.0.1:%d", self.port)

    def generate_token(self, session):
        token = str(uuid.uuid4())
        self.game_server.pet_tokens[token] = {
            "session": session,
            "expires": time.time() + TOKEN_TTL,
        }
        return token

    def stop(self):
        if self._httpd:
            self._httpd.shutdown()
