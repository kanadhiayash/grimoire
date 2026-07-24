# Yash AI Cross-Surface Instructions v3.0.0

Paste each numbered Markdown file into the matching surface. Copy the file body exactly.

## Canonical provenance

- Engineering Standards: https://github.com/kanadhiayash/engineering-standards
- Zeref Memory Engine: https://github.com/kanadhiayash/zeref-memory-engine

## Placement

| File | Paste into | Characters | Budget |
|---|---|---:|---:|
| `01_Claude_Global_Instructions.md` | Claude Settings > Profile > preferences | 3,079 | 3,500 |
| `02_Claude_Cowork_Instructions.md` | Claude Cowork global instructions | 2,573 | 3,500 |
| `03_Claude_Chat_Project_Folder_Instructions.md` | Claude Project > Set project instructions | 2,535 | 4,000 |
| `04_Claude_Cowork_Project_Folder_Instructions.md` | Claude Cowork project or folder instructions | 2,510 | 4,000 |
| `05_ChatGPT_Global_Instructions.md` | ChatGPT Settings > Personalization > Custom Instructions | 2,861 | 5,000 |
| `06_ChatGPT_Project_Folder_Instructions.md` | ChatGPT Project > Project settings > Project instructions | 2,905 | 4,000 |
| `07_Codex_Global_Instructions_Customization.md` | `~/.codex/AGENTS.md` global customization | 2,662 | 4,000 |

ChatGPT paid plans publish a 5,000-character custom-instructions limit. Anthropic and OpenAI do not publish a fixed limit for every other surface listed here, so this pack uses conservative internal budgets.

## Why the ChatGPT pair is different

ChatGPT Project instructions override global custom instructions. The project file therefore repeats all critical safety, evidence, approval, Zeref, token, and completion rules. It does not depend on the global file.

## Expected activation behavior

- Local verified Zeref runtime: `RUNTIME_FULL` or `RUNTIME_PARTIAL`.
- Complete browser project source pack: `PROJECT_SIMULATION`.
- Instructions without a complete pack or runtime: `INSTRUCTION_ONLY`.
- Insufficient inspection: `NOT_VERIFIED`.

Uploaded files and repository links never prove that the local Zeref runtime or canonical writer executed.

## Cost controls

The pack minimizes repeated tokens by using:

1. thin global kernels;
2. self-contained project kernels only where platform precedence requires it;
3. manifest-first and index-first context loading;
4. one lead role by default;
5. lowest-cost sufficient model or tool routing;
6. direct responses for simple tasks;
7. deep analysis only for high-risk or ambiguous work.

## Validation

The repository test suite validates file presence, character budgets, provenance, completion statuses, cost routing, approval boundaries, source-pack boot behavior, local contract precedence, and prohibited wording.

Run:

```bash
python3 scripts/standards.py check
```

## Live smoke test

After pasting each instruction, start a fresh session and ask:

```text
State your active instruction sources, Zeref activation status, approval boundary, completion statuses, and the first files you would read for a material project task. Do not claim access you cannot verify.
```

See `SMOKE_TESTS.md` for the full manual test set.
