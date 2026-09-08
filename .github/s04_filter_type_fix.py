from pathlib import Path

path = Path("web/src/lib/interview/server.ts")
text = path.read_text(encoding="utf-8")
old = "  const applications = applicationData as Array<Record<string, unknown>>;\n"
new = "  const applications = applicationData as unknown as Array<Record<string, unknown>>;\n"
if text.count(old) != 1:
    raise RuntimeError("expected exactly one applicationData cast")
path.write_text(text.replace(old, new, 1), encoding="utf-8")
print("applied Supabase dynamic-select type boundary")
