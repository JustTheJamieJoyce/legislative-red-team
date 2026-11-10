import json,re
import os,copy,sys,subprocess
sys.path.insert(0,'style')
from flatten import flatten,setpath
STYLE=json.load(open('style/style.json'))
M={};GATE=[]
for n in ['efta','saa','gnd']:
    A=json.load(open(f'analysis/{n}.json'));base=flatten(A)
    json.dump(base,open(f'style/{n}.flat.json','w'),ensure_ascii=False,indent=0) if not os.path.exists(f'style/{n}.pro.json') else None
    pla=None
    if os.path.exists(f'style/{n}.pro.json') and os.path.exists(f'style/{n}.plain.json'):
        r=subprocess.run(['python3','style/lint.py',n],capture_output=True,text=True)
        if r.returncode!=0: GATE.append(n+': '+r.stdout.split('\n')[0])
        pro=json.load(open(f'style/{n}.pro.json'));pl=json.load(open(f'style/{n}.plain.json'))
        pla=copy.deepcopy(A)
        for k in base:
            if k in pro: setpath(A,k,pro[k])
            if k in pl: setpath(pla,k,pl[k])
    else: GATE.append(n+': no styled text yet')
    if pla: pla['findings']=[f for f in pla['findings'] if f.get('aud')!='pro']
    M[n]={'text':json.load(open(f'texts/{n}.json')),'analysis':A,'pla':pla}
kb=json.load(open('kb.json'))
for p in kb['patterns']:
    pass
rules=json.load(open('rules.json'))
RA=json.load(open('research_add.json'))
for x in RA['patterns']:
    kb['patterns'].append({'id':x['id'],'name':x['name'],'family':x['family'],'detect':x['detect'],'origin':'research','headings':[],'plain':x['plain'],'cues':[],'fix':'','cand':True,'src':x.get('src',''),'url':x.get('url',''),'verified':x.get('verified',True)})
have={s['n'].lower() for s in rules['src']}
for x in RA['sources']:
    if x['n'].lower() in have: continue
    rules['src'].append({'n':x['n'],'k':x['k'],'u':x.get('u',''),'y':x.get('y',''),'fam':[],'st':x['st']})
for x in RA['standards']:
    if 'senate' in x['n'].lower() and 'manual' in x['n'].lower(): x['public']=False
rules['standards']=RA['standards'];rules['conflicts']=RA['conflicts']
import os
G={}
for fn in ['gen_a.json','gen_b.json']:
    if os.path.exists(fn): G.update(json.load(open(fn)))
GC=json.load(open('gen_c.json')) if os.path.exists('gen_c.json') else {'kb':{},'research':{}}
byid={p['id']:p for p in kb['patterns']}
drop=set()
for i,g in G.items():
    p=byid.get(i)
    if not p: continue
    if g['status']=='merge' and g.get('merge_into') in byid and g['merge_into']!=i:
        t=byid[g['merge_into']]; t.setdefault('headings',[]).extend(p.get('headings',[]))
        if g.get('ex_ai') and not t.get('ex_ai'): t['ex_ai']=g['ex_ai']
        drop.add(i); continue
    for k in ['name','plain','check','fix','ex_ai','ex_other']:
        if g.get(k): p[k]=g[k]
    if g.get('cues') is not None and g['status']!='merge': p['cues']=g['cues']
    p['origin']='pack-ai' if g['status']=='pack' else 'lists'
for i,g in GC.get('kb',{}).items():
    p=byid.get(i)
    if not p: continue
    for k in ['name','plain','check','fix','ex_ai']:
        if g.get(k): p[k]=g[k]
    if g.get('cues') is not None: p['cues']=g['cues']
    p['origin']='lists'
for i,g in GC.get('research',{}).items():
    p=byid.get(i)
    if p:
        if g.get('check'): p['check']=g['check']
        if g.get('fix'): p['fix']=g['fix']
kb['patterns']=[p for p in kb['patterns'] if p['id'] not in drop]
print('patterns',len(kb['patterns']),'merged',len(drop),'pack',sum(1 for p in kb['patterns'] if p['origin']=='pack-ai'),'with check',sum(1 for p in kb['patterns'] if p.get('check')))
KO={}
for j in (1,2,3):
    fn=f'style/kb{j}.out.json'
    if os.path.exists(fn): KO.update(json.load(open(fn)))
    else: GATE.append(f'kb{j}: no styled text yet')
byid={p['id']:p for p in kb['patterns']}
for k,v in KO.items():
    if k.startswith('pat.'):
        _,pid,f=k.split('.',2)
        # pattern ids may contain dots: match by longest id
        pid=k[4:k.rfind('.')];f=k[k.rfind('.')+1:]
        if pid in byid and isinstance(byid[pid].get(f),str): byid[pid][f]=v
    elif k.startswith('rules.'):
        o=rules;ps=k.split('.')[1:]
        try:
            for p in ps[:-1]: o=o[int(p)] if isinstance(o,list) else o[p]
            last=int(ps[-1]) if isinstance(o,list) else ps[-1]
            if isinstance(o[last],str): o[last]=v
        except Exception as e: GATE.append('kb path failed '+k)
print('STYLE GATE:', 'pass' if not GATE else GATE)
COI=json.load(open('coi.json'))
for t in COI['types']:
    kb['patterns'].append({'id':'coi-'+t['id'],'name':t['name'],'family':'conflict','detect':'structure','origin':'conflict','headings':[],'plain':t['plain'],'cues':[],'fix':t['guard'],'check':t['check'],'ex_other':t['ex'],'src':(t['src'] or {}).get('l',''),'url':(t['src'] or {}).get('u',''),'verified':True})
data=json.dumps({'measures':M,'kb':kb,'rules':rules,'style':STYLE,'coi':COI},ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
html=open('template.html',encoding='utf8').read().replace('__DATA__',data)
open('legislative-red-team.html','w',encoding='utf8').write(html)
SK='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><style>:root{color-scheme:light}body{margin:0}[hidden]{display:none!important}</style></head><body>\n'
open('../index.html','w',encoding='utf8').write(SK+html+'\n</body></html>\n')
js=re.findall(r'<script>\n(.*?)</script>',html,re.S)[-1]
open('app.check.js','w').write(js)
print(len(html), html.count('—'), html.count('–'))
