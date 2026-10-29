// ============ 规则合并（分层） ============
// 单一事实来源：本文件是 deepMerge 的唯一实现。
//   · build.py 会把本文件内联进 app_template.html 的 <script>（运行时合并规则栈）
//   · 命令行 node merge_rules.js ... 直接用同一份逻辑合并规则文件
// 改合并逻辑只改这里，HTML 与命令行自动同步。
function isObj(v){ return v && typeof v === "object" && !Array.isArray(v); }
function entryField(e){
  if(isObj(e)){
    if(e.id !== undefined) return "id";
    if(e.name !== undefined) return "name";
    if(e.key !== undefined) return "key";
  }
  return null;
}
function deepMerge(base, patch){
  // undefined 表示「无改动」，保留 base；null 才是显式删除
  if(patch === undefined) return base;
  if(Array.isArray(patch)) return mergeArray(Array.isArray(base) ? base : [], patch);
  if(!isObj(patch)) return patch;
  const out = isObj(base) ? {...base} : {};
  for(const k of Object.keys(patch)){
    const pv = patch[k];
    if(pv === null){ delete out[k]; continue; }
    const bv = out[k];
    if(k === "areaLayout" && isObj(pv)){ out[k] = pv; }  // 显式覆盖：上层定义就完全覆盖下层
    else if(Array.isArray(pv)){ out[k] = mergeArray(Array.isArray(bv) ? bv : [], pv); }
    else if(isObj(pv) && isObj(bv)){ out[k] = deepMerge(bv, pv); }
    else { out[k] = pv; }
  }
  return out;
}
// 取不到键的项（字符串、数字、嵌套数组、无键对象）没有「同一项」的概念，
// 只能整体覆盖——否则上层每叠一次就追加一遍，buttons 这类会翻倍
function keyedArray(patchArr){
  return patchArr.every(pe => entryField(pe) !== null);
}
function mergeArray(baseArr, patchArr){
  // 整体覆盖：深拷贝，避免合并结果与规则 JSON 共享引用
  if(!keyedArray(patchArr)) return patchArr.map(cloneDeep);
  const out = baseArr.map(x => isObj(x) ? {...x} : x);
  for(const pe of patchArr){
    const field = entryField(pe);
    const val = pe[field];
    const idx = out.findIndex(x => isObj(x) && x[field] === val);
    if(pe.$delete === true){
      if(idx !== -1) out.splice(idx, 1);
      continue;
    }
    if(idx !== -1) out[idx] = deepMerge(out[idx], pe);
    else out.push({...pe});
  }
  return out;
}
function cloneDeep(v){
  if(Array.isArray(v)) return v.map(cloneDeep);
  if(isObj(v)){ const o = {}; for(const k of Object.keys(v)) o[k] = cloneDeep(v[k]); return o; }
  return v;
}

// ============ Node CLI ============
// 内联进浏览器（app_template.html）时没有 module，整段跳过；
// 命令行 `node merge_rules.js <底层.json> [规则包.json ...] [-o 输出.json]` 时执行。
if (typeof module !== "undefined" && typeof require !== "undefined" && module.exports) {
  module.exports = { isObj, entryField, deepMerge, keyedArray, mergeArray, cloneDeep };

  if (require.main === module) {
    const fs = require("fs");

    function usage(){
      console.error("用法：node merge_rules.js <底层.json> [规则包.json ...] [-o 输出.json]");
      process.exit(2);
    }

    const argv = process.argv.slice(2);
    const files = [];
    let outFile = null;
    for(let i = 0; i < argv.length; i++){
      const a = argv[i];
      if(a === "-o" || a === "--out"){
        outFile = argv[++i];
        if(!outFile) usage();
      } else if(a === "-h" || a === "--help"){
        usage();
      } else {
        files.push(a);
      }
    }
    if(!files.length) usage();

    let acc = {};
    for(const file of files){
      const data = JSON.parse(fs.readFileSync(file, "utf8"));
      acc = deepMerge(acc, data);
    }

    const text = JSON.stringify(acc, null, 2) + "\n";
    if(outFile){
      fs.writeFileSync(outFile, text, "utf8");
      console.error("已合并 " + files.length + " 份规则 → " + outFile);
    } else {
      process.stdout.write(text);
    }
  }
}
