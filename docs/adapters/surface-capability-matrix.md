# Surface Capability Matrix

| Surface | Global instructions | Project instructions | Uploaded sources | Local runtime | Durable writeback | Expected state |
|---|---:|---:|---:|---:|---:|---|
| Claude Code | Yes | Yes | Filesystem | Yes | Filesystem | `RUNTIME_FULL` or `RUNTIME_PARTIAL` |
| Codex | Yes | Yes | Filesystem | Yes | Filesystem | `RUNTIME_FULL` or `RUNTIME_PARTIAL` |
| Gemini CLI | Yes | Yes | Filesystem | Yes | Filesystem | `RUNTIME_FULL` or `RUNTIME_PARTIAL` |
| ChatGPT Project | Yes | Yes | Yes | No | Project source save or re-upload | `PROJECT_SIMULATION` |
| Claude Project | Account dependent | Yes | Yes | No | Knowledge-file update | `PROJECT_SIMULATION` |
| Gemini Gem | Account dependent | Yes | Yes | No | Knowledge-file or Drive update | `PROJECT_SIMULATION` |
| Ordinary browser chat | Account dependent | Prompt scoped | Attachments | No | Handoff only | `CHAT_SIMULATION` |
| Unknown surface | Unknown | Unknown | Unknown | Unknown | Unknown | `NOT_VERIFIED` |

Capability claims must be verified on the active surface. This table is an adapter design target, not proof of runtime state.
