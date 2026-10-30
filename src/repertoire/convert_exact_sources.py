"""Narrow, auditable converters for two verified Mutopia source files.
No melody, chord, duration, or fingering is generated. Unsupported note tokens fail.
Original LilyPond remains authoritative for engraving and expressive marks.
"""
import pathlib,json,re,hashlib,struct,collections
from fractions import Fraction
ROOT=pathlib.Path(__file__).parent
LETTERS='cdefgab';SEMITONES=[0,2,4,5,7,9,11]
NOTE=r"[a-g](?:isis|eses|is|es)?[',]*"
TOKEN=re.compile(r'<[^>]*>\d*\.*|'+NOTE+r'\d*\.*|r\d*\.*|~|\(|\)|ACCENT|\\[a-zA-Z]+|[^\s]')
def parse_note(raw,previous,relative=True,transpose=0):
 m=re.fullmatch(r"([a-g])(isis|eses|is|es)?([',]*)",raw)
 if not m:raise ValueError('Unsupported pitch '+raw)
 letter,acc,marks=m.groups();i=LETTERS.index(letter)
 if relative:
  prev_diatonic=previous
  candidates=[7*oct+i for oct in range(prev_diatonic//7-2,prev_diatonic//7+3)]
  d=min(candidates,key=lambda x:abs(x-prev_diatonic))
 else:d=3*7+i
 d+=7*(marks.count("'")-marks.count(','))
 oct=d//7;alter={'':0,'is':1,'isis':2,'es':-1,'eses':-2}[acc or ''];midi=12*(oct+1)+SEMITONES[i]+alter+transpose
 # Lily c' is scientific C4. Our absolute Lily base is C3.
 spelling=letter.upper()+('#'*max(alter,0))+('b'*max(-alter,0))+str(oct+transpose//12)
 return d,dict(midi=midi,step=letter.upper(),alter=alter,octave=oct+transpose//12,spelling=spelling)
def parse_stream(src,anchor,hand,voice,pickup,relative=True,transpose=0,allowed_commands=()):
 src=re.sub(r'%[^\n]*','',src)
 # Remove commands that control layout/duration context; expressive marks are tracked below.
 src=re.sub(r'\\(?:clef|key|time|partial)\s+(?:[a-z]+\\?\s*\\major|[a-z]+|\d+/\d+|\d+)',' ',src)
 src=re.sub(r'\\context\s+Voice\s*=\s*"[^"]+"',' ',src)
 src=re.sub(r'\\bar\s+"[^"]*"',' ',src)
 src=re.sub(r'"[^"]*"',' ',src)
 events=[];previous=anchor;dur=Fraction(1);beat=Fraction(0);tie=False;skip=0
 src=src.replace('->','ACCENT')
 tokens=list(TOKEN.finditer(src));i=0
 ignored={'stemUp','stemDown','stemNeutral','slurDown','slurUp','slurNeutral','voiceOne','voiceTwo'}
 while i<len(tokens):
  tok=tokens[i].group();i+=1
  if tok in '{}|[]^_':continue
  if tok=='~':
   if not events or events[-1]['kind']=='rest':raise ValueError('Tie without note')
   events[-1]['tieStart']=True;tie=True;continue
  if tok in ('(',')','ACCENT'):
   if not events:raise ValueError('Mark without event')
   events[-1].setdefault('marks',[]).append({'(':'slurStart',')':'slurEnd','ACCENT':'accent'}[tok]);continue
  if tok.startswith('\\'):
   cmd=tok[1:]
   if cmd in ignored:continue
   if cmd in {'p','mf','f','ff','pp'}:
    events[-1].setdefault('marks',[]).append('dynamic:'+cmd);continue
   raise ValueError('Unsupported command '+tok)
  if tok not in ['~'] and not re.match(r'^(?:<|[a-gr])',tok):raise ValueError('Unsupported token '+tok)
  md=re.fullmatch(r'(<[^>]+>|'+NOTE+r'|r)(\d*)(\.*)',tok)
  if not md:raise ValueError('Unsupported token '+tok)
  atom,num,dots=md.groups()
  if num:
   dur=Fraction(4,int(num));dur*=sum(Fraction(1,2**x) for x in range(len(dots)+1))
  elif dots:raise ValueError('Unexpected durationless dots')
  pitches=[]
  if atom!='r':
   rawp=atom[1:-1] if atom.startswith('<') else atom
   # Chord articulation may appear inside the final pitch in this exact source.
   accent='ACCENT' in rawp;rawp=rawp.replace('ACCENT','')
   raws=rawp.split();chordprev=previous;first=None
   for raw in raws:
    chordprev,p=parse_note(raw,chordprev,relative,transpose);pitches.append(p)
    if first is None:first=chordprev
   previous=first
  else:accent=False
  b=float(beat)
  bar=1 if pickup and beat<pickup else int((beat-pickup)//3)+2 if pickup else int(beat//4)+1
  barstart=Fraction(0) if pickup and bar==1 else pickup+Fraction(3*(bar-2)) if pickup else Fraction(4*(bar-1))
  event=dict(id=f'{voice}-{len(events)+1}',kind='rest' if atom=='r' else 'note',hand=hand,voice=voice,startBeat=b,durationBeats=float(dur),bar=bar,beatInBar=float(beat-barstart),pitches=pitches,sourceToken=tok)
  if accent:event['marks']=['accent']
  if tie:
   event['tieStop']=True;tie=False
   if events[-1]['pitches']!=pitches:raise ValueError('Tie changes pitch')
  events.append(event);beat+=dur
 return events,float(beat)
def braces_after(src,key):
 s=src.index('{',src.index(key));depth=1;e=s+1
 while depth:
  if src[e]=='{':depth+=1
  elif src[e]=='}':depth-=1
  e+=1
 return src[s+1:e-1]
def blue():
 p=ROOT/'sources/blue-danube.ly';src=p.read_text();ev=[]
 for key,anchor,hand,voice in [('upper =',28,'right','upper'),('lower =',21,'left','lower')]:
  block=braces_after(src,key);block=braces_after(block,'\\relative')
  e,d=parse_stream(block,anchor,hand,voice,Fraction(1));assert d==100,(key,d);ev+=e
 return dict(id='mutopia-519',title='The Blue Danube Waltz — published main-theme piano arrangement',key='C major',meter=[3,4],quarterBpm=150,pickupBeats=1,totalQuarterBeats=100,writtenBars=34,sourceNumbering='Pickup is bar1; full bars2–34',events=ev,expressionCautions=['Source middleDynamics retained in original; not all crescendi are encoded in event marks.'],unencodedSourceFeatures=['source engraving layout','middleDynamics crescendo text'],sourceFile=str(p),sourceSha256=hashlib.sha256(p.read_bytes()).hexdigest(),fingeringStatus='No source fingering; no fingering generated')
def ode():
 p=ROOT/'sources/ode-to-joy-satb.ly';src=p.read_text();block=braces_after(src,'sop =')
 e,d=parse_stream(block,21,'right','soprano',Fraction(0),False,12);assert d==64,d
 return dict(id='mutopia-528-soprano',title='Ode to Joy — unchanged soprano reading line from SATB setting',key='G major',meter=[4,4],quarterBpm=100,totalQuarterBeats=64,writtenBars=16,events=e,sourceFile=str(p),sourceSha256=hashlib.sha256(p.read_bytes()).hexdigest(),extraction='Exact soprano only; not labelled a piano arrangement',fingeringStatus='No source fingering; no fingering generated')
def main():
 out=ROOT/'converted';out.mkdir(exist_ok=True)
 for fn in (blue,ode):
  data=fn();(out/(data['id']+'.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');print(data['id'],len(data['events']),'events',data['totalQuarterBeats'],'beats')
if __name__=='__main__':main()
