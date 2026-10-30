import pathlib,struct,json,collections
R=pathlib.Path(__file__).parent

def midi(path):
 d=path.read_bytes();assert d[:4]==b'MThd';_,fmt,ntracks,division=struct.unpack('>IHHH',d[4:14]);pos=14;tracks=[]
 def vlq(d,i):
  value=0
  while True:
   b=d[i];i+=1;value=(value<<7)|(b&127)
   if not b&128:return value,i
 for tr in range(ntracks):
  assert d[pos:pos+4]==b'MTrk';size=int.from_bytes(d[pos+4:pos+8],'big');chunk=d[pos+8:pos+8+size];pos+=8+size;i=0;t=0;running=0;active={};notes=[];name=''
  while i<len(chunk):
   delta,i=vlq(chunk,i);t+=delta;status=chunk[i]
   if status<128:status=running
   else:i+=1
   if status==255:
    typ=chunk[i];i+=1;n,i=vlq(chunk,i);data=chunk[i:i+n];i+=n
    if typ==3:name=data.decode(errors='replace')
    continue
   if status in [240,247]:n,i=vlq(chunk,i);i+=n;continue
   running=status;op=status&240;ch=status&15;n=1 if op in [192,208] else 2;payload=chunk[i:i+n];i+=n
   if op==144 and payload[1]>0:active[(ch,payload[0])]=t
   elif op==128 or (op==144 and payload[1]==0):
    key=(ch,payload[0]);start=active.pop(key);notes.append((start/division,(t-start)/division,payload[0],ch))
  tracks.append(dict(name=name,notes=sorted(notes)))
 return division,tracks

def expected(file,part=None):
 x=json.loads(file.read_text());res=[];active={}
 for e in sorted(x['events'],key=lambda e:(e['tick'],e['id'])):
  if part and e['part']!=part:continue
  for p in e['pitches']:
   key=(e['part'],e['voice'],p['midi'])
   if p.get('tieStop'):
    assert key in active,key
    j=active[key];st,du,pi=res[j];res[j]=(st,du+e['duration']/480,pi)
   else:j=len(res);res.append((e['tick']/480,e['duration']/480,p['midi']))
   if p.get('tieStart'):active[key]=j
   else:active.pop(key,None)
 assert not active
 return sorted(res)
if __name__=='__main__':
 for n in ['blue-danube','ode-to-joy-satb','minuet-g']:
  div,ts=midi(R/'sources'/f'{n}.mid');print(n,'division',div)
  for i,t in enumerate(ts):print(i,t['name'],len(t['notes']),t['notes'][:8])
