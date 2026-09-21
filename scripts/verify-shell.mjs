import { createInterface } from 'node:readline';
import { spawn } from 'node:child_process';

const [binary, expected = 'bash'] = process.argv.slice(2);
if (!binary) throw new Error('usage: node verify-shell.mjs <codex.exe> [expected-shell]');

const child = spawn(binary, ['exec-server', '--listen', 'stdio'], {
  stdio: ['pipe', 'pipe', 'pipe'],
  windowsHide: true,
});
let stderr = '';
let response;
let failure;
const timer = setTimeout(() => {
  failure = new Error('exec-server initialization timed out');
  child.kill();
}, 60000);
child.stderr.on('data', chunk => { stderr = (stderr + chunk).slice(-10000); });
createInterface({ input: child.stdout }).on('line', line => {
  try {
    const message = JSON.parse(line);
    if (message.id !== 1) return;
    if (message.error) throw new Error(JSON.stringify(message.error));
    response = message.result?.environmentInfo?.shell;
    if (!response || response.name !== expected) {
      throw new Error(`expected shell ${expected}, got ${JSON.stringify(response)}`);
    }
    console.log(JSON.stringify(response));
  } catch (error) {
    failure = error;
  } finally {
    child.stdin.end();
  }
});
child.stdin.write(JSON.stringify({
  jsonrpc: '2.0',
  id: 1,
  method: 'initialize',
  params: { clientName: 'codex-git-bash-ci' },
}) + '\n');
child.on('close', code => {
  clearTimeout(timer);
  if (failure || !response || code !== 0) {
    console.error(failure ?? `exec-server exited with code ${code}`);
    if (stderr) console.error(stderr);
    process.exitCode = 1;
  }
});
