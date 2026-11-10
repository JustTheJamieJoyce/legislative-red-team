"""Builds index.html from the page template and the data files.

Usage: python3 build.py
"""
import json,os,glob,subprocess,sys
HERE=os.path.dirname(os.path.abspath(__file__))
def load(*parts): return json.load(open(os.path.join(HERE,'data',*parts),encoding='utf8'))

# 1. Every stored line must pass the writing style guide.
if subprocess.run([sys.executable,os.path.join(HERE,'check_style.py')]).returncode!=0:
    sys.exit('The style check failed. Fix the lines listed above, then build again.')

# 2. Gather the data the page needs.
measures={}
for path in sorted(glob.glob(os.path.join(HERE,'data','measures','*.json'))):
    m=json.load(open(path,encoding='utf8'))
    measures[os.path.basename(path)[:-5]]={'text':m['text'],'analysis':m['professional'],'pla':m['plain']}
ORDER=['efta','saa','gnd']
measures={k:measures[k] for k in ORDER if k in measures}|{k:v for k,v in measures.items() if k not in ORDER}
data={'measures':measures,'kb':load('knowledge-base.json'),'rules':load('rules.json'),'style':load('style-guide.json'),'coi':load('conflict-types.json')}

# 3. Put the data into the template and write the site.
payload=json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
page=open(os.path.join(HERE,'template.html'),encoding='utf8').read().replace('__DATA__',payload)
HEAD='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="description" content="Legislative Red Team: find out whether a bill does what it says."><style>:root{color-scheme:light;box-sizing:border-box}body{margin:0;padding:0;font:14px -apple-system,BlinkMacSystemFont,sans-serif}img{max-width:100%}[hidden]{display:none!important}</style></head><body>\n'
open(os.path.join(HERE,'..','index.html'),'w',encoding='utf8').write(HEAD+page+'\n</body></html>\n')
print('Wrote index.html (%d measures, %d patterns).'%(len(measures),len(data['kb']['patterns'])))
