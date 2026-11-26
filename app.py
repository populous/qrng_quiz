from flask import Flask, jsonify, render_template_string
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

app = Flask(__name__)
sim = AerSimulator()
qc = QuantumCircuit(1, 1)
qc.h(0)
qc.measure(0, 0)
PRESET = '10110010'
votes = {'A': 0, 'B': 0}

@app.get('/bit/<int:i>')
def bit(i):
    i %= 8
    b = sim.run(qc, shots=1, memory=True).result().get_memory()[0]
    return jsonify(a=int(PRESET[i]), b=int(b), i=i)

@app.post('/vote/<c>')
def vote(c):
    if c in votes:
        votes[c] += 1
    return jsonify(votes)

@app.get('/')
def index():
    return render_template_string(HTML)

HTML = '''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>난수 전시 퀴즈</title>
<style>body{background:#0b1020;color:white;font:clamp(16px,2vw,26px) sans-serif;text-align:center}section{display:flex;justify-content:center;gap:2vw}figure{margin:0;width:45vw}figure img,canvas{display:block;width:100%;height:30vh;object-fit:contain}.bits{font:700 clamp(24px,5vw,64px) monospace;letter-spacing:.12em;margin:.25em}button{font:inherit;padding:.5em 1em}footer img{max-width:45vw;height:8vh;object-fit:contain;filter:invert(1) hue-rotate(180deg)}</style>
<h1>어느 줄이 미리 정해진 숫자일까요?</h1><section><figure><figcaption>고정 원본</figcaption><img id="photo" src="/static/bg.jpg" alt="원본 사진"></figure><figure><figcaption id="label">첫 8비트 대기 중</figcaption><canvas id="view" aria-label="재배치된 사진"></canvas></figure></section>
<p class="bits">A <span id="a"></span></p><p class="bits">B <span id="b"></span></p><button onclick="vote('A')">A가 시뮬레이션</button> <button onclick="vote('B')">B가 시뮬레이션</button><p id="res"></p><footer>Aer 시뮬레이션 · 8비트 배치 코드<br><img src="/static/logo.png" alt="Lattice Co., Ltd."></footer>
<script>
const el=id=>document.getElementById(id), photo=el('photo'), view=el('view'), ctx=view.getContext('2d');
let a='', b='', latest='';
function rows(){el('a').textContent=a.padEnd(8,'?');el('b').textContent=b.padEnd(8,'?');}
function draw(){
 if(!photo.naturalWidth)return;
 view.width=1000;view.height=100*Math.max(1,Math.round(10*photo.naturalHeight/photo.naturalWidth));
 if(!latest){ctx.drawImage(photo,0,0,view.width,view.height);return;}
 let state=parseInt(latest,2);const order=Array.from({length:10000},(_,i)=>i);
 for(let i=9999;i>0;i--){state=(Math.imul(state,1664525)+1013904223)>>>0;const j=Math.floor(state/4294967296*(i+1));[order[i],order[j]]=[order[j],order[i]];}
 const w=photo.naturalWidth/100,h=photo.naturalHeight/100,dh=view.height/100;
 order.forEach((s,d)=>ctx.drawImage(photo,s%100*w,Math.floor(s/100)*h,w,h,d%100*10,Math.floor(d/100)*dh,10,dh));
 el('label').textContent='배치 코드: '+latest+' · 10,000조각';
}
photo.onload=draw;if(photo.complete)draw();rows();
let busy=false;
async function tick(){if(busy)return;busy=true;try{
 if(b.length===8){a='';b='';rows();el('res').textContent='';await new Promise(r=>setTimeout(r,400));}
 const r=await fetch('/bit/'+b.length,{cache:'no-store'});if(!r.ok)throw Error(r.status);const d=await r.json();a+=d.a;b+=d.b;rows();if(b.length===8){latest=b;draw();}
 }catch(e){el('res').textContent='비트 수신 지연 · 재시도 중';}finally{busy=false;}}
setInterval(tick,1000);
async function vote(c){const r=await fetch('/vote/'+c,{method:'POST'});if(r.ok){const v=await r.json();el('res').textContent=`투표 A:${v.A} B:${v.B}`;}}
</script></html>'''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
