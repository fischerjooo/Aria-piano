"""Validate instructional claims against canonical, unchanged source notation.
This validates passage content, not playing technique or teaching effectiveness.
"""
import collections,json,pathlib
R=pathlib.Path(__file__).resolve().parent

def validate():
 path=json.loads((R/'learning-path.json').read_text());scores={}
 skills={s['id'] for s in path['skills']};stages={s['id'] for s in path['stages']};ids=set();bindings=set()
 for lesson in path['lessons']:
  lid=lesson['id'];assert lid not in ids,lid;ids.add(lid)
  b=lesson['binding'];sid=b['scoreId'];scores.setdefault(sid,json.loads((R/(sid+'.json')).read_text()));s=scores[sid]
  assert lesson['stageId'] in stages,lid
  assert set(lesson['prerequisiteSkillIds']+lesson['developsSkillIds'])<=skills,lid
  assert set(b['parts'])<=set(s['parts']),lid
  ms=[m for m in s['measures'] if b['sourceBarStart']<=m['number']<=b['sourceBarEnd']]
  assert len(ms)==b['sourceBarEnd']-b['sourceBarStart']+1 and ms,lid
  start,end=ms[0]['start'],ms[-1]['start']+ms[-1]['duration']
  ev=[e for e in s['events'] if e['part'] in b['parts'] and start<=e['tick']<end]
  assert ev and any(e['pitches'] for e in ev),lid
  assert all(e['tick']+e['duration']<=end for e in ev),lid
  assert not any(p.get('tieStop') for e in ev if e['tick']==start for p in e['pitches']),lid
  assert not any(p.get('tieStart') for e in ev if e['tick']+e['duration']==end for p in e['pitches']),lid
  key=(sid,start,end,tuple(b['parts']));assert key not in bindings,(lid,'duplicate source task');bindings.add(key)
  if lesson['kind']=='whole-score':assert start==0 and end==s['totalDuration'] and set(b['parts'])==set(s['parts']),lid
  assert lesson['fingering']=={'status':'not-supplied','displayNumbers':False},lid
  assert all(lesson['guide'].get(k) for k in ['beforePlaying','practiceSteps','listenFor','readyWhen']),lid
  evidence=lesson['sourceEvidence'];assert evidence['startTick']==start and evidence['endTick']==end and evidence['measureCount']==len(ms),lid
  assert evidence['quarterBeats']==(end-start)/s['ticksPerQuarter'],lid
  assert evidence['writtenEvents']==len(ev) and evidence['soundingNotes']==sum(len(e['pitches']) for e in ev),lid
  if lesson['completion']['microphone']=='monophonic-pitch-study':
   notes=[e for e in ev if e['pitches']];assert all(len(e['pitches'])==1 for e in notes),lid
   assert len({e['part'] for e in notes})==1,lid
 ode=scores['mutopia-528-ode-satb'];blue=scores['mutopia-519-blue-danube']
 def events(s,a,b,part):return [e for e in s['events'] if a<=e['measure']<=b and e['part']==part]
 # Specific claims shown in lesson text must actually exist in this edition.
 assert all(e['duration']==480 for e in events(ode,1,3,'soprano'))
 assert [e['duration'] for e in events(ode,4,4,'soprano')]==[720,240,960]
 assert events(ode,12,12,'soprano')[-1]['pitches'][0]['midi']==62
 assert events(ode,13,13,'soprano')[0]['pitches'][0]['midi']==71
 assert any(p['alter']==1 and p['step']=='F' for e in events(blue,28,28,'right') for p in e['pitches'])
 assert [(e['measure'],p['midi']) for e in events(blue,26,30,'right') for p in e['pitches'] if p.get('tieStart')]==[(27,69),(29,76)]
 assert events(blue,25,25,'left')[0]['duration']==1440
 assert events(blue,34,34,'right')[-1]['type']=='rest'
 print(f'PASS {len(ids)} distinct source-bound tasks: exact bars/parts, longer bridges, whole scopes, tie-safe boundaries, source evidence and notation claims')
if __name__=='__main__':validate()
