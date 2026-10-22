import os, json, time, threading
from flask import Flask, request, redirect, url_for, session, flash, render_template_string
import requests

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET', 'change-this-secret-before-deploying')
TOKEN = os.environ.get('BOT_TOKEN', '').strip()
PASSWORD = os.environ.get('PANEL_PASSWORD', '').strip()
API = f'https://api.telegram.org/bot{TOKEN}' if TOKEN else ''
FILE = 'config.json'
DEFAULT = {'enabled': False, 'channels': [], 'emojis': ['❤️','🔥','👍','😍'], 'next_emoji': 0, 'last_status': 'Waiting for setup'}
try:
    with open(FILE, encoding='utf-8') as f: cfg = {**DEFAULT, **json.load(f)}
except Exception: cfg = dict(DEFAULT)
lock = threading.Lock()

def save():
    with lock:
        with open(FILE, 'w', encoding='utf-8') as f: json.dump(cfg, f, ensure_ascii=False, indent=2)

def call(method, payload=None, timeout=20):
    if not API: return {'ok': False, 'description': 'BOT_TOKEN is not configured'}
    try: return requests.post(f'{API}/{method}', json=payload or {}, timeout=timeout).json()
    except Exception as e: return {'ok': False, 'description': str(e)}

EMOJIS = ['❤️','🔥','👍','😍','👏','🎉','😁','😢','🤔','👎','💯','🥰']
HTML = '''<!doctype html><html lang="bn"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Multi Reaction Pro</title><style>
*{box-sizing:border-box}body{margin:0;background:#0b1020;color:#eef2ff;font-family:system-ui,sans-serif}.wrap{max-width:720px;margin:auto;padding:16px}.hero,.card{padding:18px;border:1px solid #293955;border-radius:18px;margin:12px 0;background:#111a2e}.hero{background:linear-gradient(135deg,#172554,#111827,#082f49)}h1{margin:8px 0;font-size:25px}h2{font-size:18px;margin:0 0 12px}.muted,small{color:#aab7d1;font-size:13px}.status{display:inline-block;background:#263449;border-radius:99px;padding:7px 10px;font-size:13px}input,button{width:100%;padding:12px;margin:6px 0;border-radius:10px;border:1px solid #34445f;background:#0b1222;color:white;font:inherit}button{background:#2563eb;border:0;font-weight:700}.secondary{background:#263449}.danger{background:#9f1239}.check{display:inline-flex;gap:6px;align-items:center;background:#0b1222;padding:9px;border-radius:10px;margin:4px}.check input{width:auto;margin:0}.channel{display:flex;align-items:center;gap:8px;border-bottom:1px solid #293955;padding:8px 0}.channel span{overflow-wrap:anywhere;flex:1}.channel form{width:auto}.channel button{width:auto}.warn{background:#3f1d24;color:#fecdd3;padding:12px;border-radius:10px}.muted{line-height:1.5}</style></head><body><main class="wrap"><div class="hero"><div style="font-size:30px">⚡</div><h1>Multi Reaction Pro</h1><div class="muted">Telegram multi-channel control panel</div><p><span class="status">{{'🟢 Auto Reaction ON' if cfg.enabled else '⚪ Auto Reaction OFF'}}</span></p><div class="muted">Status: {{cfg.last_status}}</div></div>
{% for m in get_flashed_messages() %}<div class="card">{{m}}</div>{% endfor %}
{% if not token_ok %}<div class="warn">Hosting Secrets-এ BOT_TOKEN যোগ করে অ্যাপ restart করো।</div>{% endif %}
<div class="card"><h2>🔐 Panel login</h2>{% if not logged %}<form method="post" action="/login"><input type="password" name="password" placeholder="Panel password" required><button>Login</button></form><small>PANEL_PASSWORD environment variable-এ সেট করা পাসওয়ার্ড ব্যবহার করো।</small>{% else %}<form method="post" action="/toggle"><button class="{{'danger' if cfg.enabled else ''}}">{{'⏸ Auto Reaction বন্ধ করো' if cfg.enabled else '▶ Auto Reaction চালু করো'}}</button></form><form method="post" action="/logout"><button class="secondary">Logout</button></form>{% endif %}</div>
{% if logged %}<div class="card"><h2>📡 Channel যোগ করো</h2><p class="muted">বটকে প্রতিটি চ্যানেলে Admin করো। Public @username অথবা -100 দিয়ে শুরু হওয়া channel ID যোগ করতে পারো।</p><form method="post" action="/add"><input name="channel" placeholder="@yourchannel অথবা -1001234567890" required><button>+ Add channel</button></form>{% for ch in cfg.channels %}<div class="channel"><span>{{ch}}</span><form method="post" action="/remove"><input type="hidden" name="channel" value="{{ch}}"><button class="danger">Remove</button></form></div>{% endfor %}</div>
<div class="card"><h2>❤️ Reaction নির্বাচন</h2><form method="post" action="/emojis">{% for e in all_emojis %}<label class="check"><input type="checkbox" name="emojis" value="{{e}}" {% if e in cfg.emojis %}checked{% endif %}>{{e}}</label>{% endfor %}<p class="muted">নির্বাচিত ইমোজিগুলো নতুন পোস্টে পালাক্রমে একটি করে ব্যবহার হবে।</p><button>Save reactions</button></form></div>
<div class="card"><h2>🧪 Bot connection test</h2><form method="post" action="/test"><button class="secondary">Test bot connection</button></form><p class="muted">{{test_result or 'এখনও পরীক্ষা করা হয়নি'}}</p></div>{% endif %}
<div class="card"><h2>⚠️ গুরুত্বপূর্ণ</h2><p class="muted">শুধু নতুন পোস্টে কাজ করবে। বটকে চ্যানেলে Admin করতে হবে এবং নির্বাচিত ইমোজি চ্যানেলের reaction settings-এ অনুমোদিত থাকতে হবে। এক পোস্টে সব ইমোজি নয়—একটি করে পালাক্রমে দেবে।</p></div><small>BOT_TOKEN এবং panel password গোপন রাখো।</small></main></body></html>'''

@app.get('/')
def home():
    return render_template_string(HTML, cfg=cfg, logged=bool(session.get('logged')), token_ok=bool(TOKEN), all_emojis=EMOJIS, test_result=session.pop('test_result', None))
@app.post('/login')
def login():
    if PASSWORD and request.form.get('password','') == PASSWORD:
        session['logged'] = True; flash('Login successful.')
    else: flash('Password ভুল, অথবা hosting-এ PANEL_PASSWORD সেট করা নেই।')
    return redirect(url_for('home'))
@app.post('/logout')
def logout(): session.clear(); return redirect(url_for('home'))
def auth():
    if not session.get('logged'): flash('আগে login করো।'); return False
    return True
@app.post('/toggle')
def toggle():
    if not auth(): return redirect(url_for('home'))
    cfg['enabled'] = not cfg['enabled']; cfg['last_status'] = 'Enabled' if cfg['enabled'] else 'Paused'; save(); return redirect(url_for('home'))
@app.post('/add')
def add():
    if not auth(): return redirect(url_for('home'))
    ch=request.form.get('channel','').strip()
    if ch and ch not in cfg['channels']: cfg['channels'].append(ch); save(); flash('Channel যোগ হয়েছে। বটকে Admin করা আছে কি না নিশ্চিত করো।')
    return redirect(url_for('home'))
@app.post('/remove')
def remove():
    if not auth(): return redirect(url_for('home'))
    ch=request.form.get('channel','').strip()
    if ch in cfg['channels']: cfg['channels'].remove(ch); save()
    return redirect(url_for('home'))
@app.post('/emojis')
def emojis():
    if not auth(): return redirect(url_for('home'))
    chosen=[e for e in request.form.getlist('emojis') if e in EMOJIS]
    if chosen: cfg['emojis']=chosen; cfg['next_emoji']=0; save(); flash('Reaction save হয়েছে।')
    else: flash('কমপক্ষে একটি reaction বেছে নাও।')
    return redirect(url_for('home'))
@app.post('/test')
def test():
    if not auth(): return redirect(url_for('home'))
    session['test_result']=json.dumps(call('getMe', timeout=15), ensure_ascii=False); return redirect(url_for('home'))

def poll():
    offset=0
    while True:
        try:
            if not TOKEN: time.sleep(5); continue
            r=requests.get(f'{API}/getUpdates', params={'offset':offset,'timeout':25,'allowed_updates':json.dumps(['channel_post'])}, timeout=35)
            data=r.json()
            if not data.get('ok'): cfg['last_status']=data.get('description','Telegram API error'); time.sleep(5); continue
            for update in data.get('result',[]):
                offset=update['update_id']+1
                post=update.get('channel_post')
                if not post or not cfg.get('enabled'): continue
                chat=post.get('chat',{}); candidates={str(chat.get('id')), '@'+chat.get('username','') if chat.get('username') else ''}
                if not (candidates & {str(x).strip() for x in cfg.get('channels',[])}): continue
                emojis=cfg.get('emojis') or ['❤️']; idx=cfg.get('next_emoji',0)%len(emojis); emoji=emojis[idx]
                result=call('setMessageReaction', {'chat_id':chat.get('id'),'message_id':post.get('message_id'),'reaction':[{'type':'emoji','emoji':emoji}]})
                cfg['last_status']=f"{chat.get('title','Channel')}: {emoji} — {'success' if result.get('ok') else result.get('description','failed')}"
                if result.get('ok'): cfg['next_emoji']=(idx+1)%len(emojis)
                save()
        except Exception as e: cfg['last_status']=f'Polling error: {e}'; time.sleep(5)
threading.Thread(target=poll, daemon=True).start()
if __name__ == '__main__': app.run(host='0.0.0.0', port=int(os.environ.get('PORT','8080')))
