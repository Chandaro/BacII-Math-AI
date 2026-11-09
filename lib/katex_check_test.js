// Usage: node lib/katex_check_test.js finetune/test60b.jsonl. Parses the math in test questions and answer keys.
const path = require('path'), fs = require('fs');
const katex = require(path.join(__dirname, '..', 'dataset', 'preview_assets', 'katex.min.js'));
let n = 0, bad = 0;
for (const line of fs.readFileSync(process.argv[2], 'utf8').trim().split('\n')) {
  const r = JSON.parse(line);
  const parts = [r.answer_latex];
  const re = /\$\$([\s\S]+?)\$\$|\$([^$]+?)\$/g;
  let m;
  while ((m = re.exec(r.messages[1].content))) parts.push(m[1] || m[2]);
  for (const s of parts) {
    n++;
    try { katex.renderToString(s, { throwOnError: true, strict: false }); }
    catch (e) { bad++; console.log(r.id, e.message.slice(0, 90)); }
  }
}
console.log('fragments', n, 'bad', bad);
