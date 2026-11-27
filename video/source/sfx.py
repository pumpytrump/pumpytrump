import numpy as np, wave, sys
SR=48000; DUR=22.5; N=int(SR*DUR); rng=np.random.default_rng(3)
mus=np.zeros((N,2)); fx=np.zeros((N,2))
def add(buf,t,sig,gain=1.0,pan=0.0):
    i=int(t*SR); s=sig[:max(0,N-i)]*gain
    l=np.sqrt(.5*(1-pan)); r=np.sqrt(.5*(1+pan))
    buf[i:i+len(s),0]+=s*l*1.414; buf[i:i+len(s),1]+=s*r*1.414
def env(n,a,d): e=np.ones(n); ai=int(a*SR); e[:ai]=np.linspace(0,1,ai) if ai else 1; e*=np.exp(-np.arange(n)/(d*SR)); return e
def lp(x,c):  # one-pole lowpass, c in Hz (scalar or array)
    y=np.zeros_like(x); a=np.exp(-2*np.pi*np.asarray(c)/SR)*np.ones(len(x)); acc=0.0
    for i in range(len(x)): acc=(1-a[i])*x[i]+a[i]*acc; y[i]=acc
    return y
def ks(f,dur,bright=.5):  # Karplus-Strong pluck
    n=int(dur*SR); p=int(SR/f); buf=rng.uniform(-1,1,p); out=np.zeros(n)
    for i in range(n):
        out[i]=buf[i%p]; buf[i%p]=.5*(buf[i%p]+buf[(i+1)%p])*(.994+bright*.005)
    return out*env(n,.002,dur*.5)
def note(m): return 440*2**((m-69)/12)
# --- music: D hijaz, 100bpm
beat=.6; D=50
scale=[0,1,4,5,7,8,10,12]
def dum(): n=int(.5*SR); t=np.arange(n)/SR; f=110*np.exp(-t*18)+48; return np.sin(2*np.pi*np.cumsum(f)/SR)*env(n,.001,.16)
def tek(): n=int(.12*SR); return lp(rng.normal(0,1,n),5000)*env(n,.0005,.025)*.6
def section(t0,t1,inten):
    b=0; t=t0
    while t<t1-0.01:
        if b%4==0: add(mus,t,dum(),.9*inten)
        if b%4==2: add(mus,t,dum(),.6*inten)
        add(mus,t+beat/2,tek(),.45*inten,pan=.3)
        if inten>.8: add(mus,t+beat*.75,tek(),.3*inten,pan=-.3)
        t+=beat; b+=1
melody=[0,1,4,5,7,5,4,1, 0,4,7,8,7,5,4,1]
def mel(t0,t1,oct=12,g=.35):
    t=t0;i=0
    while t<t1-.05:
        m=D+oct+scale[melody[i%16]] if melody[i%16]<8 else D+oct
        add(mus,t,ks(note(D+oct+[0,1,4,5,7,8,10,12][melody[i%16]%8]),.9),g,pan=.2*np.sin(i))
        t+=beat/2;i+=1
def drone(t0,t1,g):
    n=int((t1-t0)*SR); t=np.arange(n)/SR
    s=(np.sin(2*np.pi*note(D-12)*t)+.5*np.sin(2*np.pi*note(D-5)*t)+.3*np.sin(2*np.pi*note(D)*t*1.002))
    e=np.minimum(1,np.minimum(t/.3,(t1-t0-t)/.3)); add(mus,t0,s*e,g)
drone(0,14.45,.09); drone(15.25,22.5,.11)
section(0.0,2.4,.6); section(2.45,14.4,.75); section(15.25,22.4,1.0)
mel(2.45,13.3,12,.22); mel(15.25,22.4,24,.25)
# --- fx
def whoosh(dur=.45,up=True):
    n=int(dur*SR); t=np.linspace(0,1,n); c=300+ (t if up else 1-t)*5000
    return lp(rng.normal(0,1,n),c)*np.sin(np.pi*t)**2*1.4
def boom(f0=70,dur=1.2):
    n=int(dur*SR); t=np.arange(n)/SR; f=f0*np.exp(-t*3)+30
    return (np.sin(2*np.pi*np.cumsum(f)/SR)+.3*lp(rng.normal(0,1,n),400))*env(n,.002,.35)
def riser(dur):
    n=int(dur*SR); t=np.linspace(0,1,n); return lp(rng.normal(0,1,n),200+t**2*7000)*t**2*.9
def pop(f=900):
    n=int(.15*SR); t=np.arange(n)/SR; return np.sin(2*np.pi*np.cumsum(f*(1+3*np.exp(-t*40)))/SR)*env(n,.001,.04)
def tick():
    n=int(.05*SR); return lp(rng.normal(0,1,n),7000)*env(n,.0003,.006)*1.2
# hook: riser into swoop, boom on "Steine"
add(fx,0,riser(1.6),.5); add(fx,1.6,boom(60,1.6),.9); add(fx,1.6,whoosh(.5,False),.4)
for tc in [2.45,5.6,9.5,13.4,15.25,18.1]: add(fx,tc-.25,whoosh(.5),.5,pan=rng.uniform(-.5,.5))
add(fx,3.76,boom(90,.8),.6); add(fx,5.12,pop(500),.5)
# dragging stone 5.6-9.5
n=int(3.9*SR); t=np.arange(n)/SR; drag=lp(rng.normal(0,1,n),250)*(0.6+0.4*np.abs(np.sin(t*2.6)))*np.minimum(1,np.minimum(t/.2,(3.9-t)/.2))
add(fx,5.6,drag,1.4)
add(fx,9.9,boom(110,.6),.8)  # block placed thunk
add(fx,9.9,pop(1200),.4)
# ticks accelerate 10.4-12.5
tt=10.4; k=0
while tt<12.5: add(fx,tt,tick(),.5,pan=(-1)**k*.3); tt+=max(.035,.22*(1-(tt-10.4)/2.1)); k+=1
add(fx,12.56,boom(55,1.4),1.0)
# sad trombone-ish slide + fall thud
n=int(.9*SR); t=np.arange(n)/SR; f=note(D+7)*np.exp(-t*.5); trb=np.sign(np.sin(2*np.pi*np.cumsum(f)/SR))*env(n,.02,.5)
add(fx,13.5,lp(trb,1500),.12)
add(fx,14.5,boom(45,1.0),1.1); add(fx,14.5,lp(rng.normal(0,1,int(.8*SR)),900)*env(int(.8*SR),.005,.25),.6)
# "Aber" impact + pops for workers
add(fx,15.25,boom(80,1.0),.7)
for i,st in enumerate([16.4,16.55,16.7,16.85,17.0,17.12,17.24,17.36,17.46,17.56,17.66,17.74,17.82,17.9]): add(fx,st,pop(700+i*60),.35,pan=rng.uniform(-.7,.7))
add(fx,18.2,pop(1000),.5); add(fx,19.16,boom(70,1.2),.8); add(fx,19.1,whoosh(.4),.4)
for tap in np.arange(18.6+.2,22.4,1/1.2): add(fx,tap,tick(),.35)
# wind bed
n=N; wb=lp(rng.normal(0,1,n),500)*(0.5+0.5*np.sin(np.arange(n)/SR*.7))*.18; fx[:,0]+=wb; fx[:,1]+=np.roll(wb,4000)
def write(fn,x):
    x=x/ (np.max(np.abs(x))+1e-9)*.9
    with wave.open(fn,'wb') as w: w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR);w.writeframes((x*32767).astype('<i2').tobytes())
write(sys.argv[1]+'/music.wav',mus); write(sys.argv[1]+'/fx.wav',fx)
print('done')
