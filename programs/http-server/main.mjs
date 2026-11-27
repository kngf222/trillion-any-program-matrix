import http from 'node:http';
const port = Number(process.argv[2] ?? 0);
const server = http.createServer((q, r) => { console.log(JSON.stringify({ served: q.url })); r.end('hello from http-server\n'); });
server.listen(port, '127.0.0.1', () => console.log(JSON.stringify({ program: 'http-server', listening: server.address().port, pid: process.pid })));
