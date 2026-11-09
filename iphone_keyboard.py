"""
iPhone -> laptop keyboard.  Run this on the laptop; open the printed link on your iPhone.

Setup (once):   pip install pynput
Run:            python iphone_keyboard.py
Then:           laptop and iPhone on the same Wi-Fi (or laptop joined to the iPhone's
                Personal Hotspot). Open the printed URL in Safari on the iPhone.
Windows: click "Allow" on the firewall prompt (Private networks).
Mac: allow Terminal/Python under System Settings > Privacy > Accessibility.
"""
import json
import secrets
import socket
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

from pynput.keyboard import Controller, Key

PORT = 8765
TOKEN = f"{secrets.randbelow(10**6):06d}"  # new PIN every run; stops others on the network

kb = Controller()
NAMED = {
    "enter": Key.enter, "esc": Key.esc, "tab": Key.tab, "backspace": Key.backspace,
    "delete": Key.delete, "left": Key.left, "right": Key.right, "up": Key.up,
    "down": Key.down, "home": Key.home, "end": Key.end, "pageup": Key.page_up,
    "pagedown": Key.page_down, "space": Key.space,
    **{f"f{i}": getattr(Key, f"f{i}") for i in range(1, 13)},
}
MODS = {"ctrl": Key.ctrl, "alt": Key.alt, "shift": Key.shift, "win": Key.cmd}


def press(name, mods):
    key = NAMED.get(name, name if len(name) == 1 else None)
    if key is None:
        return
    held = [MODS[m] for m in mods if m in MODS]
    for m in held:
        kb.press(m)
    try:
        kb.press(key)
        kb.release(key)
    finally:
        for m in reversed(held):
            kb.release(m)


PAGE = r"""<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1">
<title>Phone Keyboard</title>
<style>
 body{font-family:-apple-system,sans-serif;margin:0;padding:10px;background:#f2f2f7;color:#111}
 #st{font-size:13px;color:#555;margin-bottom:6px}
 textarea{width:100%;box-sizing:border-box;height:90px;font-size:18px;border-radius:10px;border:1px solid #ccc;padding:8px}
 .row{display:flex;gap:6px;margin-top:6px}
 button{flex:1;padding:12px 2px;font-size:15px;border:0;border-radius:9px;background:#fff;box-shadow:0 1px 2px #0003}
 button:active{background:#d0d0d8} button.on{background:#0a84ff;color:#fff}
 .scroll{overflow-x:auto;white-space:nowrap}.scroll button{flex:none;width:52px;margin-right:6px}
 @media (prefers-color-scheme:dark){body{background:#000;color:#eee}textarea,button{background:#1c1c1e;color:#eee;border-color:#444}}
</style></head><body>
<div id="st">Connected - type below</div>
<textarea id="box" autocapitalize="off" autocorrect="off" autocomplete="off" spellcheck="false"
 placeholder="Type here - goes to the laptop"></textarea>
<div class="row" id="mods"></div>
<div class="row" id="r1"></div><div class="row" id="r2"></div><div class="row" id="r3"></div>
<div class="row" id="r4"></div>
<div class="row scroll" id="fk"></div>
<script>
const t=new URLSearchParams(location.search).get('t'),st=document.getElementById('st'),box=document.getElementById('box');
let mods=new Set(),prev='';const modBtns={};
function send(o){fetch('/send?t='+t,{method:'POST',body:JSON.stringify(o)}).then(r=>{st.textContent=r.ok?'Connected - type below':'Wrong PIN / link'}).catch(()=>st.textContent='Laptop not reachable')}
function clearMods(){mods.clear();Object.values(modBtns).forEach(b=>b.classList.remove('on'))}
function key(name,extra){send({type:'key',name:name,mods:[...mods,...(extra||[])]});clearMods()}
function add(id,label,fn,cls){const b=document.createElement('button');b.textContent=label;b.onclick=fn;document.getElementById(id).appendChild(b);return b}
['ctrl','alt','shift','win'].forEach(m=>{const b=add('mods',m[0].toUpperCase()+m.slice(1),()=>{mods.has(m)?mods.delete(m):mods.add(m);b.classList.toggle('on')});modBtns[m]=b});
[['Esc','esc'],['Tab','tab'],['Del','delete'],['Bksp','backspace'],['Enter','enter']].forEach(([l,k])=>add('r1',l,()=>key(k)));
[['←','left'],['↑','up'],['↓','down'],['→','right'],['Home','home'],['End','end']].forEach(([l,k])=>add('r2',l,()=>key(k)));
[['Copy','c'],['Paste','v'],['Cut','x'],['Undo','z'],['All','a']].forEach(([l,k])=>add('r3',l,()=>send({type:'key',name:k,mods:['ctrl']})));
add('r4','Alt+Tab',()=>send({type:'key',name:'tab',mods:['alt']}));
add('r4','Win',()=>send({type:'key',name:'win_tap',mods:[]}));
add('r4','Win+D',()=>send({type:'key',name:'d',mods:['win']}));
add('r4','Ctrl+Alt+Del',()=>send({type:'key',name:'delete',mods:['ctrl','alt']}));
for(let i=1;i<=12;i++)add('fk','F'+i,()=>key('f'+i));
box.addEventListener('input',()=>{
 const now=box.value;let i=0;
 while(i<prev.length&&i<now.length&&prev[i]===now[i])i++;
 for(let n=0;n<prev.length-i;n++)send({type:'key',name:'backspace',mods:[]});
 const added=now.slice(i);
 if(added){ if(mods.size){[...added].forEach(c=>send({type:'key',name:c.toLowerCase(),mods:[...mods]}));clearMods()}
            else send({type:'text',s:added}) }
 prev=now;
 if(now.length>200){box.value='';prev=''}
});
box.addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();key('enter')}});
</script></body></html>"""


def local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _ok(self):
        return parse_qs(urlparse(self.path).query).get("t", [""])[0] == TOKEN

    def do_GET(self):
        if not self._ok():
            self.send_error(403)
            return
        body = PAGE.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if not self._ok():
            self.send_error(403)
            return
        data = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        try:
            if data.get("type") == "text":
                kb.type(data.get("s", ""))
            elif data.get("type") == "key":
                if data.get("name") == "win_tap":
                    kb.press(Key.cmd)
                    kb.release(Key.cmd)
                else:
                    press(data.get("name", ""), data.get("mods", []))
        except Exception as e:  # keep serving even if one key fails
            print("key error:", e)
        self.send_response(204)
        self.end_headers()


if __name__ == "__main__":
    url = f"http://{local_ip()}:{PORT}/?t={TOKEN}"
    print("\nOpen this on your iPhone (Safari):\n\n   ", url, "\n\nCtrl+C to stop.")
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
