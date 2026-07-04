/**
 * 集成测试:直接调 services/bilibili.js,打几个真实 ID 看返回。
 * 不启 Express,纯走业务逻辑。
 */

const bilibili = require('./src/services/bilibili');

const CASES = [
  // 普通视频 BV
  'BV1GJ411x7h7',
  // 普通视频 av (老格式)
  'av170001',
  // 番剧 ep
  'ep317925',
  // 番剧 ss
  'ss25820',
  // 番剧 md
  'md28223043',
];

(async () => {
  for (const c of CASES) {
    process.stdout.write(`[${c}] `);
    const t0 = Date.now();
    const r = await bilibili.resolve(c);
    const ms = Date.now() - t0;
    if (!r.ok) {
      console.log(`FAIL (${ms}ms) code=${r.code} error=${r.error}`);
      continue;
    }
    const d = r.data;
    console.log(
      `OK (${ms}ms) type=${r.type} title="${(d.title || '').slice(0, 30)}" cover=${(d.cover || '').slice(0, 60)}...`,
    );
  }
})();