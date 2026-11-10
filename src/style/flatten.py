# flatten(analysis) -> {path: string} of every reader-facing prose string the style guide governs
import json,sys
KEYS={'title','plain','tech','use','cost','label','h','d','open','dec','why','want','role','lead','note','part','issue','banner','checks','p','function','stage','vehicle','skeptic','m_note','job','holder','over','guard','roles_note','claim','detail','who','conf_note'}
def flatten(A):
    out={}
    def idx(parent_key,i,v):
        if isinstance(v,dict) and 'id' in v and parent_key in('findings','am','stake'): return str(v['id'])
        return str(i)
    def walk(o,path,key,anc):
        if isinstance(o,dict):
            for k,v in o.items():
                if k in('a','ops','s','stated','marketed') and not (k=='a' and isinstance(v,str)): continue
                walk(v,path+[k],k,anc+[k])
        elif isinstance(o,list):
            for i,v in enumerate(o): walk(v,path+[idx(key,i,v)],key,anc)
        elif isinstance(o,str) and o.strip():
            ok=key in KEYS or 'ladder' in anc or key in('keep','close') or (key=='q' and ('inq' in anc or 'questions' in anc)) or (key=='a' and 'questions' in anc)
            if key in('vehicle','stage') : ok=False
            if ok: out['.'.join(path)]=o
    walk(A,[],'',[])
    return out
def setpath(A,path,val):
    o=A;parts=path.split('.')
    for j,p in enumerate(parts):
        last=j==len(parts)-1
        if isinstance(o,list):
            k=next((i for i,v in enumerate(o) if isinstance(v,dict) and str(v.get('id'))==p),None)
            if k is None: k=int(p)
        else: k=p
        if last:
            assert isinstance(o[k],str),path; o[k]=val
        else: o=o[k]
if __name__=='__main__':
    n=sys.argv[1];A=json.load(open(f'analysis/{n}.json'));F=flatten(A)
    json.dump(F,open(f'style/{n}.flat.json','w'),ensure_ascii=False,indent=0)
    print(n,len(F),sum(len(v.split()) for v in F.values()),'words')
