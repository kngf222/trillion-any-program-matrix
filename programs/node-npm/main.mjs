import dayjs from 'dayjs';
console.log(JSON.stringify({ program: 'node-npm', sample: dayjs('2026-11-27T00:00:00Z').add(3, 'day').format('YYYY-MM-DD'), node: process.version }));
