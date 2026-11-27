console.log(JSON.stringify({ program: 'node-nvm', version: process.version, execPath: process.execPath, path_head: (process.env.PATH ?? '').split(':').slice(0, 2) }));
