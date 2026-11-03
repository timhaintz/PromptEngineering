import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { createRequire } from 'node:module';

const { glob, globSync } = createRequire(require.resolve('jest-config'))('glob');

describe('glob cancellation and discovery (GHSA-3g3m-2fjr-6pw4)', () => {
  let directory;
  beforeEach(() => {
    directory = fs.mkdtempSync(path.join(os.tmpdir(), 'glob-security-'));
    for (const name of ['src/nested', 'ignored/nested']) {
      fs.mkdirSync(path.join(directory, name), { recursive: true });
      fs.writeFileSync(path.join(directory, name, 'example.test.ts'), '');
    }
  });
  afterEach(() => fs.rmSync(directory, { recursive: true, force: true }));

  it('stops directory reads after an aborted async walk rejects', async () => {
    const controller = new AbortController();
    const reason = new Error('cancel traversal');
    let reads = 0;
    const filesystem = {
      ...fs,
      readdir(entry, options, callback) {
        reads++;
        fs.readdir(entry, options, (error, entries) => {
          controller.abort(reason);
          callback(error, entries);
        });
      },
    };
    await expect(glob('**/*', { cwd: directory, signal: controller.signal, fs: filesystem }))
      .rejects.toThrow('cancel traversal');
    const readsAtRejection = reads;
    await new Promise(resolve => setTimeout(resolve, 30));
    expect(reads).toBe(readsAtRejection);
    expect(reads).toBe(1);
  });

  it('preserves sync and async test discovery with ignore options', async () => {
    const options = { cwd: directory, nodir: true, dot: true, posix: true, windowsPathsNoEscape: true, ignore: ['ignored/**'] };
    expect(globSync('**/*.test.ts', options)).toEqual(['src/nested/example.test.ts']);
    await expect(glob('**/*.test.ts', options)).resolves.toEqual(['src/nested/example.test.ts']);
  });
});
