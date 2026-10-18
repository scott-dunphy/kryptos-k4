"""Sanborn signature system (K1/K2/Cyrillic Projector): ONE keyword-mixed alphabet T used as the tableau
(PT, CT, key all indexed in T), any periodic key p 1..24, Vig/Beau/Var. All 396k dictionary-keyed alphabets (fwd/rev)
+ lore. Residue-consistency crib test with m>=4 collisions (FP ~26^-m)."""
import numpy as np, time
from numba import njit, prange
from k4lib import CT, CRIB_POS, keyed_alphabet
from run_alphapairs import load_words, pos_table
CI=np.array(sorted(CRIB_POS)); PL=np.array([ord(CRIB_POS[i])-65 for i in CI]); CL=np.array([ord(CT[i])-65 for i in CI])
@njit(parallel=True, cache=True)
def scan(TB, PL, CL, CI, out):
    for b in prange(TB.shape[0]):
        key=np.empty(32,dtype=np.int64); k=np.empty(24,dtype=np.int64)
        for rule in range(3):
            for t in range(24):
                ip=TB[b,PL[t]]; ic=TB[b,CL[t]]
                k[t]=(ic-ip)%26 if rule==0 else ((ic+ip)%26 if rule==1 else (ip-ic)%26)
            for p in range(1,25):
                for r in range(p): key[r]=-1
                ok=True; distinct=0
                for t in range(24):
                    r=CI[t]%p
                    if key[r]==-1: key[r]=k[t]; distinct+=1
                    elif key[r]!=k[t]: ok=False; break
                if ok and 24-distinct>=4: out[b]=rule*100+p
if __name__=="__main__":
    lore,words=load_words(); seen=set(); al=[]
    for w in words+lore+["SHADOW","MEDUSA","KRYPTOS","PALIMPSEST","ABSCISSA"]:
        for rev in (0,1):
            a=keyed_alphabet(w); a=a[::-1] if rev else a
            if a not in seen: seen.add(a); al.append((w,rev,a))
    TB=np.array([pos_table(a) for _,_,a in al]); out=np.zeros(len(al),dtype=np.int64); t=time.time()
    scan(TB,PL,CL,CI,out)
    hits=np.nonzero(out)[0]
    print("alphabets",len(al),"hits",len(hits),round(time.time()-t,1),"s",[ (al[h][0],al[h][1],int(out[h])) for h in hits[:10]])
    rng=np.random.default_rng(0); R=np.array([np.argsort(rng.permutation(26)) for _ in range(len(al)//4)])
    o2=np.zeros(len(R),dtype=np.int64); scan(R,PL,CL,CI,o2); print("null random alphabets hits",int((o2>0).sum()),"of",len(R))
