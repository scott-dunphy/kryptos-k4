import numpy as np, json, sys
LEFT=open(__import__("os").path.join(__import__("os").path.dirname(__file__),"..","..","data","sculpture_left.txt")).read().split("\n")[:28]
D=dict(H=2.75,y0=0.05,L=2.85,Rc=1.45,mTop=0.055,mBot=0.055,mSide=0.023)
def cpoint(r,i,p,mode="justify"):
    n=len(LEFT[r]); vTop=1-p["mTop"]; vBot=p["mBot"]; v=vTop-(r+.5)*(vTop-vBot)/28
    u=p["mSide"]+(i+.5)*(1-2*p["mSide"])/(31 if mode=="pitch" else n)
    ph=p["L"]/p["Rc"]; Ccx=-p["Rc"]*np.sin(ph/2); Ccz=-p["Rc"]*np.cos(ph/2)
    th=np.pi/2+ph/2-u*ph
    return np.array([Ccx+p["Rc"]*np.cos(th), p["y0"]+v*p["H"], Ccz+p["Rc"]*np.sin(th)])
assert np.allclose(cpoint(0,31,D),[-0.0632,2.605,0.0876],atol=2e-4), cpoint(0,31,D)
OBS=[(0,31,25,127),(0,4,542,128),(24,5,520,705),(24,24,170,702),(25,24,165,722),(27,5,520,772),(26,5,520,750)]
W,Hh=768,1024
def rod(w):
    t=np.linalg.norm(w)
    if t<1e-12: return np.eye(3)
    k=w/t; K=np.array([[0,-k[2],k[1]],[k[2],0,-k[0]],[-k[1],k[0],0]]); return np.eye(3)+np.sin(t)*K+(1-np.cos(t))*K@K
R0=np.array([[-1,0,0],[0,-1,0],[0,0,1.]])  # rows: right=-x, down=-y, forward=+z
def proj(cam,X):
    w,C,f=cam[:3],cam[3:6],cam[6]
    Xc=(rod(w)@R0)@(X-C); return np.array([W/2+f*Xc[0]/Xc[2], Hh/2+f*Xc[1]/Xc[2]]), Xc[2]
def resid(x,p,mode,fitgeo):
    cam=x[:7]; q=dict(p)
    if fitgeo: q.update(Rc=x[7],L=x[8],H=x[9],y0=x[10])
    out=[]
    for r,i,u,v in OBS:
        uv,z=proj(cam,cpoint(r,i,q,mode)); out+= [uv[0]-u, uv[1]-v] if z>0 else [1e4,1e4]
    return np.array(out)
def lm(f,x,iters=400):
    lam=1e-2
    for _ in range(iters):
        r=f(x); J=np.zeros((len(r),len(x)))
        for j in range(len(x)):
            h=1e-6*max(1,abs(x[j])); xp=x.copy(); xp[j]+=h; J[:,j]=(f(xp)-r)/h
        A=J.T@J; g=J.T@r
        while True:
            dx=-np.linalg.solve(A+lam*np.diag(np.diag(A)+1e-9),g); rn=f(x+dx)
            if rn@rn<r@r: x=x+dx; lam=max(lam/3,1e-9); break
            lam*=4
            if lam>1e9: return x
    return x
best=None
for mode in ("justify","pitch"):
  for fitgeo in (False,True):
    for cz in (-1.5,-2.5,-3.5):
      for cx in (-0.6,-1.2,-1.8):
        x0=np.array([0,0,0,cx,1.5,cz,700.]+([1.45,2.85,2.75,0.05] if fitgeo else []))
        x=lm(lambda x:resid(x,D,mode,fitgeo),x0)
        r=resid(x,D,mode,fitgeo); rms=np.sqrt(np.mean(r**2))
        if best is None or (mode,fitgeo)!=best.get("key") or rms<best["rms"]:
            pass
        key=(mode,fitgeo); 
        if not hasattr(sys.modules[__name__],"res"): res={}
        if key not in res or rms<res[key]["rms"]: res[key]=dict(rms=rms,x=x.tolist(),r=r.round(1).tolist())
for k,v in res.items():
    x=v["x"]; print(k,"RMS px %.1f"%v["rms"],"cam C",np.round(x[3:6],2),"f %.0f"%x[6], ("geo Rc %.2f L %.2f H %.2f y0 %.2f"%tuple(x[7:11]) if k[1] else ""))
    print("   residuals",v["r"])
json.dump({str(k):v for k,v in res.items()},open(__import__("os").path.join(__import__("os").path.dirname(__file__),"calib.json"),"w"))
