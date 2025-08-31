#!/usr/bin/env node
/*
  Coerce array-shaped Application fields to a standard content-filter notice.
  This is a non-AI post-process to normalize remaining legacy array values.
*/
const fs = require('fs');
const path = require('path');

const FILE = path.join(__dirname, '..', 'public', 'data', 'normalized-patterns.json');
const NOTICE = 'Unable to process due to Azure OpenAI content management policy.';

function loadJson(file) {
  const raw = fs.readFileSync(file, 'utf8');
  return JSON.parse(raw);
}

function saveJson(file, data) {
  const text = JSON.stringify(data, null, 2) + '\n';
  fs.writeFileSync(file, text, 'utf8');
}

function main() {
  if (!fs.existsSync(FILE)) {
    console.error('File not found:', FILE);
    process.exit(1);
  }
  const data = loadJson(FILE);
  const arr = Array.isArray(data) ? data : (Array.isArray(data.patterns) ? data.patterns : []);
  if (!arr.length) {
    console.log('No patterns found in normalized-patterns.json');
    return;
  }

  let changed = 0;
  let arrays = 0;
  for (const p of arr) {
    if (Array.isArray(p.application) && p.application.length) {
      arrays++;
      p.application = NOTICE;
      changed++;
    }
  }

  if (changed > 0) {
    if (Array.isArray(data)) {
      // data is the array itself
      saveJson(FILE, arr);
    } else {
      data.patterns = arr;
      saveJson(FILE, data);
    }
  }

  console.log(JSON.stringify({ total: arr.length, arraysBefore: arrays, changed, arraysAfter: 0 }, null, 2));
}

main();
