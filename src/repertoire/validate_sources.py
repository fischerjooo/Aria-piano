"""Independent source-fidelity checks against original publisher MIDI, not our parser."""
import json,pathlib,hashlib,collections
from midi_reference import midi,expected
R=pathlib.Path(__file__).parent

def validate():
 manifest=json.loads((R/'source-manifest.json').read_text())
 for asset in manifest['assets']:
  p=R/asset['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==asset['sha256'],p
 for filename,partcount,total in [('mutopia-519-blue-danube.json',2,48000),('mutopia-528-ode-satb.json',1,30720)]:
  s=json.loads((R/filename).read_text());assert s['ticksPerQuarter']==480
  assert s['totalDuration']==total
  assert s['measures'][0]['number']==1 and s['measures'][0]['start']==0
  assert len({e['id'] for e in s['events']})==len(s['events'])
  assert sum(m['duration'] for m in s['measures'])==total
  assert all(s['measures'][i]['start']+s['measures'][i]['duration']==s['measures'][i+1]['start'] for i in range(len(s['measures'])-1))
  parts=set(e['part'] for e in s['events']);assert len(parts)==partcount
  for part in parts:
   es=sorted([e for e in s['events'] if e['part']==part],key=lambda e:e['tick']);assert es[0]['tick']==0
   assert all(es[i]['tick']+es[i]['duration']==es[i+1]['tick'] for i in range(len(es)-1)),part
   assert es[-1]['tick']+es[-1]['duration']==total
  for event in s['events']:
   assert event['duration']>0 and event['tick']>=0
   assert event['type']=='rest' if not event['pitches'] else event['type']=='note'
   assert not any('finger' in p for p in event['pitches']),'Unpublished finger number'
   for pitch in event['pitches']:
    semitones={'C':0,'D':2,'E':4,'F':5,'G':7,'A':9,'B':11}
    assert pitch['midi']==12*(pitch['octave']+1)+semitones[pitch['step']]+pitch['alter'],pitch
   m=s['measures'][event['measure']-1];assert m['start']<=event['tick']<m['start']+m['duration']
  assert hashlib.sha256((R/s['sourceAsset']).read_bytes()).hexdigest()==s['sourceSha256']
  for sec in s['sections']:
   assert 0<=sec['start']<sec['end']<=total
   # Sections must not split any written note or continuation tie.
   for e in s['events']:
    assert not e['tick']<sec['end']<e['tick']+e['duration']
    if e['tick']==sec['end']:assert not any(p.get('tieStop') for p in e['pitches'])
 b=json.loads((R/'mutopia-519-blue-danube.json').read_text())
 assert [(e['measure'],p['midi']) for e in b['events'] for p in e['pitches'] if p.get('tieStart')]==[(27,69),(29,76)]
 assert [(e['measure'],p['midi']) for e in b['events'] for p in e['pitches'] if p.get('tieStop')]==[(28,69),(30,76)]
 blue=R/'mutopia-519-blue-danube.json';_,tracks=midi(R/'sources/blue-danube.mid')
 for part,track,n in [('right',1,96),('left',2,151)]:
  exp=collections.Counter(expected(blue,part));actual=collections.Counter(t[:3] for t in tracks[track]['notes'])
  assert sum(exp.values())==n and exp==actual,(part,exp-actual,actual-exp)
  print(f'PASS Blue Danube {part}: {n} notes, exact source MIDI pitches, onsets and tied durations')
 ode=R/'mutopia-528-ode-satb.json';_,tracks=midi(R/'sources/ode-to-joy-satb.mid')
 exp=collections.Counter(expected(ode));actual=collections.Counter(t[:3] for t in tracks[1]['notes'])
 assert sum(exp.values())==62 and not exp-actual,exp-actual
 print('PASS Ode: all 62 unchanged soprano notes match source SATB upper MIDI track; alto remains excluded')
 print('PASS assets/hashes, measure coverage, rests, pitch spellings, ties, sections, absent unsupported fingering')
if __name__=='__main__':validate()
