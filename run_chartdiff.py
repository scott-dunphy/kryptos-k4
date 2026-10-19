"""NYT 2010 K1/K2 coding charts (data/web/sheets/K1FromPdf.jpg, K2FromPdf.jpg) vs copper, cell by cell. Sanborn D read as D (looks like O).
Output: every cell where chart key != ideal keyword, chart PT != final PT, KA-Vig(PT,key) != chart CT, or chart CT != copper."""
import sys; sys.path.insert(0,'/Users/scottdunphy/PycharmProjects/K4')
from kryptos_texts import K1_PT,K1_CT,K2_PT,K2_CT,KA
enc=lambda p,k: KA[(KA.index(p)+KA.index(k))%26]
K1=[("BETWEENSUBTLESHADINGANDTHEABSEN","PALIMPSESTPALIMPSESTPALIMPSESTP","EMUFPHZLRFAXYUSDJKZLDKRNSHGNFIV"),
    ("CEOFLIGHTLIESTHENUANCEOFILLUSIO","ALIMPSESTPALIMPSESTPALIMPCESTPA","JYQTQUXQBQVYUVLLTREVJYQTMKYRDMF"),
    ("N","L","D")]
K2=[("ITWASTOTALLYINVISIBLEHOWSTHATPO","ABSCISSAABSCISSAABSCISSAABSCISS","VFPJUDEEHZWETZYVGWHKKQETGFQJNCE"),
    ("SSIBLE?THEYUSEDTHEEARTHSMAGNETI","AABSCI?SSAABSCISSAABSCISSAABSCI","GGWHKK?DQMCPFQZDQMMIAGPFXHQRLGT"),
    ("CFIELDXTHEINFORMATIONWASGATHERED","SSAABSCISSAABSCISSAABSCISSAABSCI","IMVMZJANQLVKQEDAGDVFRPJUNGEUNAQZ"),
    ("ANDTRANSMITTEDUNDERGROUNDTOANUN","SSAABSCISSAABSCISSAABSCISSAABSC","GZLECGYUXUEENJTBJLBQCETBJDFHRRY"),
    ("KNOWNLOCATIONXDOESLANGLEYKNOWAB","ISSAABSCISSAABSCISSAABSCISSAABS","IZETKZEMVDUFKSJHKFWHKUWQLSZFTIH"),
    ("OUTTHIS?THEYSHOULDITSBURIEDOUTT","CISSAAB?SCISSAABSCISSAABSCISSAA","HDDDUVH?DWKBFUFPWNTDFIYCUQZEREE")]
def run(name,rows,PT,CT,KW):
    P="".join(r[0] for r in rows);K="".join(r[1] for r in rows);C="".join(r[2] for r in rows)
    P,K,C=[s.replace("?","") for s in (P,K,C)]
    print(name,len(P),len(K),len(C),"copper",len(CT))
    ideal=(KW*99)[:len(P)]
    for i in range(len(P)):
        e=enc(P[i],K[i]); notes=[]
        if K[i]!=ideal[i]: notes.append(f"key {K[i]}!={ideal[i]}")
        if P[i]!=PT[i]: notes.append(f"chartPT {P[i]} vs finalPT {PT[i]}")
        if e!=C[i]: notes.append(f"chart enc {e} != chartCT {C[i]}")
        if i<len(CT) and C[i]!=CT[i]: notes.append(f"chartCT {C[i]} vs copper {CT[i]} (copper=enc({PT[i]},{ideal[i]})={enc(PT[i],ideal[i])})")
        if notes: print(f"  idx {i} row {i//31} col {i%31}:", "; ".join(notes))
run("K1",K1,K1_PT,K1_CT,"PALIMPSEST")
run("K2",K2,K2_PT,K2_CT,"ABSCISSA")
