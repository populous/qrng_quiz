from flask import Flask, jsonify, render_template_string
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

app = Flask(__name__)
sim = AerSimulator()
qc = QuantumCircuit(1, 1)
qc.h(0)
qc.measure(0, 0)
PRESET = '10110010'

@app.get('/bit/<int:i>')
def bit(i):
    i %= 8
    b = sim.run(qc, shots=1, memory=True).result().get_memory()[0]
    return jsonify(a=int(PRESET[i]), b=int(b), i=i)

@app.get('/')
def index():
    return render_template_string(HTML)

HTML = '''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>난수 전시 퀴즈</title>
<style>
html,body{margin:0;height:100%}
body{background:#0b1020;color:#e8ecff;font:clamp(16px,2vw,26px) sans-serif;text-align:center;overflow:hidden}
#bg{position:fixed;inset:0;width:100vw;height:100vh;z-index:-2}
#shade{position:fixed;inset:0;z-index:-1;background:rgba(11,16,32,.25)}
.ui{position:relative;z-index:1}
h1{position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);width:100%;margin:0;z-index:1}
.bits{font:700 clamp(32px,7vw,96px) monospace;letter-spacing:.12em;margin:.25em;white-space:pre}
#logo{position:fixed;bottom:12px;left:50%;transform:translateX(-50%);width:min(600px,90vw);filter:invert(1) hue-rotate(180deg);opacity:.95}
</style>
<canvas id="bg"></canvas><div id="shade"></div>
<div class="ui"><h1>양자난수가 그리는 그림</h1>
<p class="bits"><span id="a"></span></p><p class="bits"><span id="b"></span></p>
<p id="res"></p><p id="label"></p></div>
<img id="logo" src="/static/logo.png" alt="Lattice Co., Ltd.">
<script>
const $=id=>document.getElementById(id), canvas=$('bg'), ctx=canvas.getContext('2d'), photo=new Image();
const tiles=16;
let a='', b='', code='';
photo.src='/static/bg.jpg';
function rows(){$('a').textContent=a.padEnd(8,' ');$('b').textContent=b.padEnd(8,' ');}
function shuffled(){
 const W=photo.naturalWidth,H=photo.naturalHeight,tw=W/tiles,th=H/tiles;
 const perm=Array.from({length:tiles*tiles},(_,i)=>i);
 let s=parseInt(code,2);
 for(let i=perm.length-1;i>0;i--){s=(Math.imul(s,1664525)+1013904223)>>>0;const j=Math.floor(s/4294967296*(i+1));[perm[i],perm[j]]=[perm[j],perm[i]];}
 const off=document.createElement('canvas');off.width=W;off.height=H;const o=off.getContext('2d');
 perm.forEach((src,d)=>o.drawImage(photo,(src%tiles)*tw,Math.floor(src/tiles)*th,tw,th,(d%tiles)*tw,Math.floor(d/tiles)*th,tw,th));
 return off;
}
function render(){
 if(!photo.naturalWidth)return;
 canvas.width=innerWidth;canvas.height=innerHeight;
 const src=code?shuffled():photo;
 const s=Math.max(canvas.width/src.width,canvas.height/src.height);
 const w=src.width*s,h=src.height*s;
 ctx.drawImage(src,(canvas.width-w)/2,(canvas.height-h)/2,w,h);
 $('label').textContent=code?`배치 코드: ${code} · 256조각`:'';
}
photo.onload=render;window.onresize=render;rows();
let busy=false;
async function tick(){if(busy)return;busy=true;try{
 if(b.length===8){a='';b='';code='';rows();$('res').textContent='';render();await new Promise(r=>setTimeout(r,400));}
 const r=await fetch('/bit/'+b.length,{cache:'no-store'});if(!r.ok)throw Error(r.status);const d=await r.json();a+=d.a;b+=d.b;rows();if(b.length===8){code=b;render();await new Promise(r=>setTimeout(r,8000));}
 }catch(e){$('res').textContent='비트 수신 지연 · 재시도 중';}finally{busy=false;}}
setInterval(tick,1000);
</script></html>'''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
