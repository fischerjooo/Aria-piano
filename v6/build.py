import json, pathlib, sys
root=pathlib.Path(__file__).resolve().parent
catalog=[json.loads(pathlib.Path(p).read_text()) for p in sys.argv[1:]]
template=(root/'template.html').read_text()
learning=json.loads((root.parent/'src/repertoire/learning-path.json').read_text())
html=template.replace('/*__LEARNING__*/{}',json.dumps(learning,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')).replace('/*__CATALOG__*/[]', json.dumps(catalog,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')).replace('/*__INPUT__*/',(root/'input.js').read_text().replace('</script','<\\/script')).replace('/*__PLAYER__*/',(root/'player.js').read_text().replace('</script','<\\/script'))
(root.parent/'aria-piano-v6.0-candidate.html').write_text(html)
