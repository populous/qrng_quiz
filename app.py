from flask import Flask, jsonify, render_template_string
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

app = Flask(__name__)
sim = AerSimulator()
qc = QuantumCircuit(1, 1)
qc.h(0)
qc.measure(0, 0)

PRESET = "10110010"
votes = {"A": 0, "B": 0}

def quantum_bit():
    r = sim.run(qc, shots=1, memory=True).result()
    return int(r.get_memory()[0])

@app.get("/bit/<int:i>")
def bit(i):
    i %= 8
    return jsonify(a=int(PRESET[i]), b=quantum_bit(), i=i)

@app.post("/vote/<c>")
def vote(c):
    if c in votes:
        votes[c] += 1
    return jsonify(votes)

@app.get("/")
def index():
    return render_template_string(HTML)

HTML = """<!doctype html><html lang="ko"><meta charset="utf-8">
<title>양자난수 vs 일반수</title>
<style>
body{background:linear-gradient(rgba(11,16,32,.25),rgba(11,16,32,.25)),
 url('/static/bg.jpg') center/cover fixed #0b1020;
 color:#e8ecff;font-family:sans-serif;text-align:center;overflow-x:hidden;padding-bottom:240px}
h1{margin-top:30px}
.row{display:flex;justify-content:center;gap:10px;margin:12px;align-items:center}
.outer{flex-direction:column;gap:8px}
.lab{font-size:min(42px,5vw)}
.cell{width:min(105px,10.5vw);aspect-ratio:7/9;border:2px solid #345;border-radius:10px;
 font:700 min(72px,7vw) monospace;display:flex;align-items:center;justify-content:center;transition:opacity .4s}
.cell.on{background:#16305a;border-color:#6cf}
.cell.fade{opacity:0}
button{font-size:39px;padding:21px 45px;margin:10px;border-radius:12px;border:0;
 background:#2a6df4;color:#fff;cursor:pointer}
#res{font-size:39px;min-height:60px;margin-top:20px;color:#ffd166}
#logo{position:fixed;bottom:12px;left:50%;transform:translateX(-50%);
 width:min(600px,90vw);filter:invert(1) hue-rotate(180deg);opacity:.95}
</style>
<h1>어느 줄이 양자난수일까요?</h1>
<div class="row outer"><div class="lab">A</div><div id="ra" class="row"></div></div>
<div class="row outer"><div class="lab">B</div><div id="rb" class="row"></div></div>
<div>
 <button onclick="vote('A')">A가 양자</button>
 <button onclick="vote('B')">B가 양자</button>
</div>
<div id="res"></div>
<img id="logo" src="/static/logo.png" alt="Lattice Co., Ltd.">
<script>
const mk=id=>{const e=document.getElementById(id);e.innerHTML='';
 for(let k=0;k<8;k++){const d=document.createElement('div');d.className='cell';d.textContent='?';e.appendChild(d)}
 return [...e.children]};
let A=mk('ra'),B=mk('rb'),i=0;
async function tick(){
 if(i===8){
  [...A,...B].forEach(c=>c.classList.add('fade'));
  await new Promise(r=>setTimeout(r,600));
  A=mk('ra');B=mk('rb');i=0;document.getElementById('res').textContent='';
 }
 const d=await (await fetch('/bit/'+i)).json();
 A[i].textContent=d.a;B[i].textContent=d.b;
 A[i].classList.add('on');B[i].classList.add('on');i++;
}
setInterval(tick,1000);
async function vote(c){
 const v=await (await fetch('/vote/'+c,{method:'POST'})).json();
 document.getElementById('res').textContent=
  `투표 A:${v.A} B:${v.B}`;
}
</script></html>"""

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)