# usage: python3 lint.py <id>  -> checks style/<id>.plain.json and style/<id>.pro.json against style.json
import json,re,sys
import os
D=os.path.dirname(os.path.abspath(__file__))+'/'
G=json.load(open(D+'style.json'));L=G['lint']
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
    if set(F)!=set(base): iss.append(f'{level}: keys differ: missing {sorted(set(base)-set(F))[:5]} extra {sorted(set(F)-set(base))[:5]}')
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
if __name__=='__main__':
    n=sys.argv[1];base=json.load(open(D+n+'.flat.json'));iss=[];warn=[]
    for level in('plain','pro'):
        try:F=json.load(open(D+f'{n}.{level}.json'))
        except Exception as e: iss.append(f'{level}: cannot read file: {e}');continue
        iss+=check(level,F,base)
        for p,t in F.items():
            if p in base:
                for num in set(re.findall(r'\b\d{2,}[\d,]*\b',base[p])):
                    if num not in t and num.replace(',','') not in t.replace(',',''): warn.append(f'{level} {p}: check that the number {num} was dropped on purpose (allowed only for section or citation numbers in plain language)')
    if GR:
        avg=sum(GR)/len(GR);print('plain average grade %.1f'%avg)
        if avg>L['plain'].get('grade_avg',99): iss.append('plain: average reading grade %.1f, wants %.1f or lower'%(avg,L['plain']['grade_avg']))
    print('ISSUES',len(iss));[print(' -',i) for i in iss[:150]]
    print('WARNINGS',len(warn));[print(' ~',i) for i in warn[:60]]
    sys.exit(1 if iss else 0)
