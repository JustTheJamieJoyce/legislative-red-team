"""Checks every stored line of every measure against the writing style guide.

Usage: python3 check_style.py
Exit status is 0 when every line passes.
"""
import json,re,sys,os,glob
HERE=os.path.dirname(os.path.abspath(__file__))
G=json.load(open(os.path.join(HERE,'data','style-guide.json'),encoding='utf8'));L=G['lint']

# Which fields of an analysis hold reader-facing prose.
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

# The checks.
VERB=re.compile(r"\b(is|are|was|were|be|been|has|have|had|does|do|did|can|could|would|will|must|may|might|should|shall|[a-z]+s|[a-z]+ed)\b")
SUBJ_START=re.compile(r"^(Want|Wants|Needs|Need|Prefers|Prefer|Favors|Favor|Opposes|Oppose|Permitted|Depends|Likely|Benefits|Seeks|Seek|Supports|Support|Values|Value|Sees|See|Fears|Fear|Gains|Gain|Loses|Lose|Keeps|Reads)\b")
def syl(w):
    w=re.sub(r'[^a-z]','',w.lower())
    if not w:return 0
    n=len(re.findall(r'[aeiouy]+',w))
    if w.endswith('e') and n>1 and not w.endswith('le'):n-=1
    return max(1,n)
def grade(t):
    s=[x for x in re.split(r'[.!?]+\s',t) if x.strip()];w=re.findall(r"[A-Za-z][A-Za-z'\-]*",t)
    if not s or not w:return 0
    return 0.39*len(w)/len(s)+11.8*sum(syl(x) for x in w)/len(w)-15.59
def sents(t): return [x for x in re.split(r'(?<=[.!?])\s+',t.strip()) if x]
def kind(path):
    p=path.split('.')
    if p[-1] in('label','role','part','issue','function','job','holder','who') or (len(p)>2 and p[-2]=='ladder' and False): return 'label'
    if p[-1] in('title','claim'): return 'title'
    if p[-1]=='dec' or (p[-1]=='q'): return 'question'
    if p[-1]=='h': return 'head'
    return 'prose'
GR=[]
def check(level,F,base):
    iss=[]
    extra=sorted(set(F)-set(base))
    if extra: iss.append(f'{level}: lines with no professional counterpart: {extra[:5]}')
    for path,t in F.items():
        if not isinstance(t,str) or not t.strip(): iss.append(f'{level} {path}: empty');continue
        k=kind(path);tl=t.lower()
        if '—' in t or '–' in t: iss.append(f'{level} {path}: dash')
        if level=='plain' and ';' in t: iss.append(f'{level} {path}: semicolon')
        for i in L['idioms']:
            if i in tl: iss.append(f'{level} {path}: figure of speech "{i}"')
        if k=='label': continue
        if not re.search(r'[.?!"”)]$',t.strip()): iss.append(f'{level} {path}: does not end as a sentence')
        if k in('title','question','head'):
            for v in L['vague']:
                if re.search(r'\b'+re.escape(v)+r'\b',tl) and not re.search(re.escape(v)+r'\s+(for|on|about|of|to|that|in|against)\b',tl): iss.append(f'{level} {path}: vague reference "{v}" with nothing saying which')
        if k=='title':
            n=len(t.split());lo,hi=L[level]['title']
            if n<lo or n>hi: iss.append(f'{level} {path}: title has {n} words, wants {lo} to {hi}')
            if level=='pro' and not t.strip().endswith('.'): iss.append(f'{level} {path}: title must end with a period')
        if k=='question' and not t.strip().endswith('?') and not path.startswith('questions') : iss.append(f'{level} {path}: must be a question ending in ?')
        if path.startswith('questions') and path.endswith('.q') and '?' not in t: iss.append(f'{level} {path}: must contain a question')
        for s in sents(t):
            w=s.split()
            if len(w)>L[level]['sentence'] and k!='title': iss.append(f'{level} {path}: sentence of {len(w)} words (max {L[level]["sentence"]}): {s[:50]}')
            if len(w)<4 and k!='label': iss.append(f'{level} {path}: fragment "{s}"')
            elif not VERB.search(s): iss.append(f'{level} {path}: no verb in "{s[:50]}"')
        if SUBJ_START.match(t) and k in('prose','head'): iss.append(f'{level} {path}: starts without a subject ("{t[:30]}")')
        if level=='plain' and k!='label':
            g=grade(t);GR.append(g)
            if g>L['plain'].get('grade_max',99) and len(t.split())>7: iss.append(f'{level} {path}: reading grade {g:.1f}, wants {L["plain"]["grade_max"]} or lower: {t[:50]}')
        if level=='plain':
            for j in L['plain_jargon']:
                if j.lower() in tl:
                    # allowed if explained in the same sentence
                    s=[x for x in sents(t) if j.lower() in x.lower()][0]
                    if not re.search(r'\b(means|meaning|which is|that is|called|known as|or "|, the |, a |, an )',s): iss.append(f'{level} {path}: technical word "{j.strip()}" not explained in the same sentence')
            if re.search(r'^this matters because',tl): iss.append(f'{level} {path}: starts with "This matters because"')
            if re.search(r'\b(section|sec\.|subsection)\s*\d',tl): iss.append(f'{level} {path}: section number in plain language')
    return iss

def main():
    failed=False
    for path in sorted(glob.glob(os.path.join(HERE,'data','measures','*.json'))):
        name=os.path.basename(path)[:-5];M=json.load(open(path,encoding='utf8'))
        pro=flatten(M['professional']);plain=flatten(M['plain']);del GR[:]
        issues=check('pro',pro,pro)+check('plain',plain,pro)
        if GR:
            avg=sum(GR)/len(GR)
            if round(avg,1)>L['plain'].get('grade_avg',99): issues.append('plain: average reading grade %.1f, wants %.1f or lower'%(avg,L['plain']['grade_avg']))
            print('%s: %d lines, plain-language reading grade %.1f, %d issues'%(name,len(pro)+len(plain),avg,len(issues)))
        for i in issues[:100]: print('  -',i)
        failed=failed or bool(issues)
    return 1 if failed else 0
if __name__=='__main__':
    sys.exit(main())
