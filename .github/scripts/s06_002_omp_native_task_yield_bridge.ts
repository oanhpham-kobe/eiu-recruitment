import type { ExtensionAPI } from "@oh-my-pi/pi-coding-agent";
import { createAssistantMessageEventStream } from "@oh-my-pi/pi-ai/utils/event-stream";

const CANDIDATE = "73f03e00b6c2f90874eb17419e57ca58715a6990";
const CHILD_HEAD_TOKEN = "OMP_EIU_REVIEWER_CHILD_HEAD_OK";
const FINAL_TOKEN = "OMP_EIU_REVIEWER_BRIDGE_OK_73F03E0";
const PROVIDER = "omp-review-proof";
const MODEL = "bridge-model";

const zeroUsage = () => ({
  input: 0,
  output: 0,
  cacheRead: 0,
  cacheWrite: 0,
  totalTokens: 0,
  cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0, total: 0 },
});

function baseMessage(model: any, content: any[], stopReason: "stop" | "toolUse") {
  return {
    role: "assistant" as const,
    content,
    api: model.api,
    provider: model.provider,
    model: model.id,
    usage: zeroUsage(),
    stopReason,
    timestamp: Date.now(),
  };
}

function emitToolCall(model: any, name: string, args: Record<string, unknown>, id: string) {
  const stream = createAssistantMessageEventStream();
  const toolCall = { type: "toolCall" as const, id, name, arguments: args };
  const partial = baseMessage(model, [toolCall], "toolUse");
  stream.push({ type: "start", partial } as any);
  stream.push({ type: "toolcall_start", contentIndex: 0, partial } as any);
  stream.push({
    type: "toolcall_delta",
    contentIndex: 0,
    delta: JSON.stringify(args),
    partial,
  } as any);
  stream.push({ type: "toolcall_end", contentIndex: 0, toolCall, partial } as any);
  stream.push({ type: "done", reason: "toolUse", message: partial } as any);
  return stream;
}

function emitText(model: any, text: string) {
  const stream = createAssistantMessageEventStream();
  const message = baseMessage(model, [{ type: "text" as const, text }], "stop");
  stream.push({ type: "start", partial: message } as any);
  stream.push({ type: "text_start", contentIndex: 0, partial: message } as any);
  stream.push({ type: "text_delta", contentIndex: 0, delta: text, partial: message } as any);
  stream.push({ type: "text_end", contentIndex: 0, content: text, partial: message } as any);
  stream.push({ type: "done", reason: "stop", message } as any);
  return stream;
}

function toolResultText(context: any, toolName: string): string | undefined {
  const messages = Array.isArray(context?.messages) ? context.messages : [];
  for (let i = messages.length - 1; i >= 0; i--) {
    const message = messages[i];
    if (message?.role !== "toolResult" || message?.toolName !== toolName) continue;
    const blocks = Array.isArray(message.content) ? message.content : [];
    return blocks.filter((b: any) => b?.type === "text").map((b: any) => b.text ?? "").join("\n");
  }
  return undefined;
}

function isReviewerChild(context: any): boolean {
  const tools = Array.isArray(context?.tools) ? context.tools : [];
  if (tools.some((tool: any) => tool?.name === "yield")) return true;
  const system = Array.isArray(context?.systemPrompt) ? context.systemPrompt.join("\n") : String(context?.systemPrompt ?? "");
  return system.includes("Read-only EIU implementation reviewer") || system.includes("eiu-reviewer");
}

export default function bridgeProof(pi: ExtensionAPI) {
  pi.registerProvider(PROVIDER, {
    baseUrl: "bridge://local",
    apiKey: "not-used",
    api: "omp-review-proof",
    models: [
      {
        id: MODEL,
        name: "OMP native task/yield bridge proof",
        contextWindow: 200000,
        maxTokens: 4096,
      },
    ],
    streamSimple: (model: any, context: any) => {
      if (isReviewerChild(context)) {
        const bashResult = toolResultText(context, "bash");
        if (!bashResult) {
          return emitToolCall(
            model,
            "bash",
            {
              command: `set -euo pipefail; test "$(git rev-parse HEAD)" = '${CANDIDATE}'; printf '${CHILD_HEAD_TOKEN}\\n'`,
            },
            "proof-child-bash",
          );
        }
        if (!bashResult.includes(CHILD_HEAD_TOKEN)) {
          return emitText(model, `BRIDGE_PROOF_CHILD_HEAD_FAILURE\n${bashResult}`);
        }
        return emitToolCall(
          model,
          "yield",
          { type: "result", data: FINAL_TOKEN },
          "proof-child-yield",
        );
      }

      const taskResult = toolResultText(context, "task");
      if (taskResult) {
        return emitText(model, `OMP_NATIVE_TASK_RESULT\n${taskResult}`);
      }

      return emitToolCall(
        model,
        "task",
        {
          context: `# Goal\nProve native OMP custom-agent dispatch on exact candidate ${CANDIDATE}.\n# Constraints\nRead-only. Do not modify files, refs, databases, deployments, or external state.\n# Contract\nSpawn exactly the project custom agent eiu-reviewer; it must verify exact HEAD using bash and return the proof token through its native yield tool.`,
          tasks: [
            {
              name: "BridgeProof",
              agent: "eiu-reviewer",
              task: `# Target\nExact checked-out repository HEAD ${CANDIDATE}.\n# Change\nNo changes. Verify exact HEAD with the allowed read-only bash tool.\n# Acceptance\nReturn exactly ${FINAL_TOKEN} through the native yield result payload after exact HEAD verification succeeds.`,
            },
          ],
        },
        "proof-parent-task",
      );
    },
  } as any);
}
