console.log(JSON.stringify({ program: 'bun-run', bun: Bun.version, execPath: process.execPath, sum: [1,2,3].reduce((a: number, b: number) => a + b, 0) }));
