"""Rebuild player scores directly from retained LilyPond; no stale intermediate inputs."""
import json,pathlib,shutil,hashlib,sys
from convert_exact_sources import blue,ode
ROOT=pathlib.Path(__file__).parent
DEST=ROOT if ROOT.name=='repertoire' else ROOT.parent/'piano/src/repertoire';DEST.mkdir(parents=True,exist_ok=True)
(DEST/'sources').mkdir(exist_ok=True)
sys.path.insert(0, str(ROOT.parents[1] / 'scripts'))
from lib.catalogue import read_yaml, validate_document
metadata = read_yaml(ROOT.parents[1] / 'data/experimental/score-descriptions.yaml')
validate_document(metadata, 'score-descriptions.schema.json')
configs=metadata['scores']
for filename,cfg in configs.items():
 x=(blue if filename=='mutopia-519' else ode)();pickup=x.get('pickupBeats',0);beats=x['meter'][0]
 def startbar(n):return 0 if n==1 else (pickup+(n-2)*beats) if pickup else (n-1)*beats
 measures=[dict(number=n,start=int(startbar(n)*480),duration=int((pickup if n==1 and pickup else beats)*480)) for n in range(1,x['writtenBars']+1)]
 events=[]
 for e in x['events']:
  marks=e.get('marks',[]);ps=[]
  for p in e['pitches']:
   pitch=dict(p)
   for k in ['tieStart','tieStop']:
    if e.get(k):pitch[k]=True
   ps.append(pitch)
  ev=dict(id=e['id'],measure=e['bar'],tick=round(e['startBeat']*480),duration=round(e['durationBeats']*480),staff='RH' if e['hand']=='right' else 'LH',part='soprano' if filename.endswith('soprano') else e['hand'],voice=1,type=e['kind'],pitches=ps,sourceToken=e['sourceToken'])
  if 'accent' in marks:ev['articulations']=['accent']
  if 'slurStart' in marks:ev['slurStart']=True
  if 'slurEnd' in marks:ev['slurStop']=True
  dynamics=[m[8:] for m in marks if m.startswith('dynamic:')]
  if dynamics:ev['dynamics']=dynamics
  events.append(ev)
 sections=[dict(id=id,label=label,start=round(startbar(a)*480),end=round((startbar(b)+(pickup if b==1 and pickup else beats))*480),sourceBarStart=a,sourceBarEnd=b) for id,label,a,b in cfg.pop('ranges')]
 data=dict(**cfg,title=x['title'],meter=dict(beats=beats,beatType=4),key=dict(fifths=0 if filename=='mutopia-519' else 1),ticksPerQuarter=480,tempo=x['quarterBpm'],pickup=round(pickup*480),totalDuration=round(x['totalQuarterBeats']*480),measures=measures,sections=sections,events=events,fingeringStatus=x['fingeringStatus'],sourceSha256=x['sourceSha256'],sourceAsset='sources/'+pathlib.Path(x['sourceFile']).name,conversion=dict(method='Deterministic parsing of actual LilyPond pitches/chords/durations; no newly composed or simplified music',transformation='Direct notation conversion' if filename=='mutopia-519' else 'Extract soprano unchanged; source transpose c c-prime retained',script='convert_exact_sources.py',sourceAuthoritative=True))
 if filename=='mutopia-519':
  data['dynamics']=[dict(tick=0,value='mf',source='middleDynamics'),dict(tick=47*480,value='cresc.',source='middleDynamics'),dict(tick=64*480,value='cresc.',source='middleDynamics'),dict(tick=72*480,value='f',source='middleDynamics')]
 (DEST/(cfg['id']+'.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');
 if pathlib.Path(x['sourceFile']).resolve() != (DEST/'sources'/pathlib.Path(x['sourceFile']).name).resolve():shutil.copy2(x['sourceFile'],DEST/'sources'/pathlib.Path(x['sourceFile']).name)
 print(DEST/(cfg['id']+'.json'))
for file in ['convert_exact_sources.py','export_engine_scores.py']:
 
 if (ROOT/file).resolve() != (DEST/file).resolve():shutil.copy2(ROOT/file,DEST/file)
