// Independently compare the complete materialized catalogs in the original and built apps.
const fs = require('fs'), path = require('path'), vm = require('vm'), assert = require('assert');
const root = path.join(__dirname, '..');
const harness = fs.readFileSync(path.join(__dirname, 'piano-curriculum-tests.cjs'), 'utf8').split("assert.equal(run('courseLength')")[0];
function catalog(file) {
  const source = harness.replace("path.join(__dirname,'../index.html')", `path.join(__dirname,${JSON.stringify('../' + file)})`);
  const context = {require, __dirname, console};
  vm.createContext(context);
  return vm.runInContext(source + "\nrun('JSON.stringify({levels: lessonLevels, melodies: melodyData, lessons: lessons, games: gameMelodies, courseLength: courseLength, labels: levelLabels})')", context);
}
const original = JSON.parse(catalog('aria-piano-v5.26.html'));
const built = JSON.parse(catalog('index.html'));
assert.equal(original.levels.length, 68);
assert.equal(original.levels.flat().length, 204);
assert.equal(original.melodies.length, 142);
assert.deepStrictEqual(built, original, 'built runtime catalog differs from stable v5.26');
console.log('PASS exact runtime parity for 204 course variants and 142 melodies');
