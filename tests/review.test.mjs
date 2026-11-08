import {test} from 'node:test';
import assert from 'node:assert/strict';
import {csv,ris,key,presets} from '../web/review.mjs';

test('CSV escapes quotes, line breaks and spreadsheet formulas',()=>{
 const result=csv([{title:'A "quoted", title',notes:'=1+1',abstract:'first\nsecond'}]);
 assert.ok(result.startsWith('\uFEFF'));
 assert.ok(result.includes('"A ""quoted"", title"'));
 assert.ok(result.includes('"\'=1+1"'));
 assert.ok(result.includes('"first\nsecond"'));
});
test('RIS cannot inject new records through metadata',()=>{
 const result=ris([{title:'Test\nER  -',doi:'10.123/example',year:2024}]);
 assert.ok(result.includes('TI  - Test ER  -'));
 assert.equal(result.split('\n').filter(line=>line==='ER  -').length,1);
 assert.ok(result.includes('DO  - 10.123/example'));
});
test('DOIs deduplicate regardless of case and presets separate boolean syntax',()=>{
 assert.equal(key({doi:'10.1/ABC'}),key({doi:'10.1/abc'}));
 assert.equal(presets.length,6);
 for(const p of presets){assert.ok(p.boolean.includes('AND'));assert.ok(!p.query.includes(' AND '));}
});
