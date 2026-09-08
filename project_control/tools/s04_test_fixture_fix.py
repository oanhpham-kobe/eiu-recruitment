from pathlib import Path

path = Path(__file__).resolve().parents[2] / "web/src/__tests__/interview-commands.test.ts"
text = path.read_text(encoding="utf-8")
old = '''      participantAppUserIds: [ids.user],
      idempotencyKey: ids.key,
    },
    { client, resolveSession: async () => session(["interviews.manage"]) },
  );
  assert.equal(calls.length, 1);'''
new = '''      participantAppUserIds: [ids.user],
      idempotencyKey: ids.key,
    },
    {
      client,
      resolveSession: async () =>
        session(["interviews.manage", "interviews.view"]),
    },
  );
  assert.equal(calls.length, 1);'''
if text.count(old) != 1:
    raise SystemExit(f"copy fixture anchor: expected one, found {text.count(old)}")
path.write_text(text.replace(old, new, 1).rstrip() + "\n", encoding="utf-8")
print("S04 copy fixture repaired")
