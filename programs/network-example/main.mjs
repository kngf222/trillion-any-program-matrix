const r = await fetch('https://example.com');
const b = await r.arrayBuffer();
console.log(JSON.stringify({ program: 'network-example', status: r.status, bytes: b.byteLength }));
