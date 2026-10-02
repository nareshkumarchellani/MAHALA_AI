import re
from difflib import SequenceMatcher

def _tokens(s): return set(re.findall(r'\w+',(s or '').lower()))
def run(text,category,latitude,longitude,existing):
    best=None; best_score=0
    a=_tokens(text)
    for row in existing:
        b=_tokens((row.get('description') or '')+' '+(row.get('title') or ''))
        text_score=SequenceMatcher(None,' '.join(sorted(a)),' '.join(sorted(b))).ratio() if a and b else 0
        cat=1 if category and row.get('category')==category else 0
        dist=0
        if latitude is not None and longitude is not None and row.get('latitude') is not None and row.get('longitude') is not None:
            dist=((latitude-row['latitude'])**2+(longitude-row['longitude'])**2)**0.5
        loc=1 if dist<0.01 else 0
        score=round((text_score*.65+cat*.2+loc*.15)*100)
        if score>best_score: best_score=score; best=row
    return {'is_duplicate':best_score>=82,'similarity':best_score,'related':best}
