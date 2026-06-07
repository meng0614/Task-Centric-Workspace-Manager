# codex-task-workspace-manager

A task-centric workspace and skill governance manager for Codex/OpenClaw users.

`codex-task-workspace-manager` helps AI-assisted work stay understandable over time. Instead of scattering generated files across global `input`, `output`, `logs`, `drafts`, or `temp` folders, it organizes every artifact around the task that created it.

## The Problem

Long-running Codex/OpenClaw workspaces tend to drift:

- outputs are written into whatever directory is current;
- research papers, generated slides, logs, temporary files, and images get separated;
- Skills are installed flat into one huge `skills` folder;
- months later, nobody can answer why a file exists, what task produced it, or which Skill generated it.

A workspace should not be a pile of file types. It should be a memory of completed work.

## Why Task-Centric Workspace?

A task is one complete unit of work, for example:

```text
20260607_DetWAN_GroupMeetingPPT
20260607_AI-Agent_WeChatArticle
20260607_TSN_PaperReview
20260607_RL-TSN_Reproduction
```

Each task owns its inputs, outputs, logs, assets, temporary files, and archives:

```text
20260607_DetWAN_GroupMeetingPPT/
|-- input/
|-- output/
|-- logs/
|-- assets/
|-- temp/
`-- archive/
```

Open the folder and you immediately know what went in, what came out, what supported it, and what happened along the way.

## Core Features

### 1. Workspace Bootstrap

Creates a standard workspace root:

```text
E:\codex
|-- skills
|-- media
|-- research
|-- projects
|-- downloads
|-- logs
|-- temp
`-- archive
```

### 2. Task Router

Creates task folders under the correct domain and area:

```text
E:\codex\research\presentations\20260607_DetWAN_GroupMeetingPPT
|-- input
|-- output
|-- logs
|-- assets
|-- temp
`-- archive
```

### 3. Naming Enforcer

Generated files should use:

```text
YYYYMMDD_TaskName_FilePurpose.ext
```

Forbidden examples:

```text
final.pptx
output.md
result.html
test.png
```

### 4. Skill Manager

Skills are categorized instead of being dumped into one folder:

```text
E:\codex\skills
|-- common
|-- media
|-- research
|-- experimental
`-- archive
```

Skill directories use:

```text
SkillName__ShortDescription
```

Examples:

```text
find__Search_OpenSourceSkills
paper-to-group-meeting-ppt__Generate_AcademicPresentation
yao-expert-skill__ExpertReview_And_Feedback
```

### 5. Skill Registry

Generates:

```text
E:\codex\skills\skill_registry.md
```

Records each Skill's name, category, path, short description, when to use it, when not to use it, source, and enabled state.

### 6. Task Registry

Generates:

```text
E:\codex\task_registry.md
```

Records each task's name, domain, path, inputs, outputs, Skills used, status, and notes.

### 7. Workspace Audit

Scans for:

- legacy global `input/output/logs` folders;
- orphan files without task ownership;
- unclassified Skills;
- Skills missing `SkillName__ShortDescription` naming;
- task folders missing required subfolders.

### 8. Migration Plan

Migration defaults to dry-run. Plans are generated first, then applied only with `--apply`.

### 9. Final Migration

Existing workspaces can be moved toward the final Task-Centric structure without deleting business files.

## Installation

Clone the repository:

```bash
git clone https://github.com/<your-org>/codex-task-workspace-manager.git
cd codex-task-workspace-manager
```

Install in editable mode:

```bash
python -m pip install -e .
```

Or run directly:

```bash
python -m codex_task_workspace_manager --help
```

## Usage

Bootstrap a workspace:

```bash
workspace-manager bootstrap --root E:\codex
```

Create a task:

```bash
workspace-manager create-task --root E:\codex --domain research --type presentations --name DetWAN_GroupMeetingPPT
```

Route a file into a task:

```bash
workspace-manager route-file --root E:\codex --file DetWAN.pdf --task 20260607_DetWAN_GroupMeetingPPT --kind input
```

Audit a workspace:

```bash
workspace-manager audit --root E:\codex
```

Generate a migration plan:

```bash
workspace-manager migrate --root E:\codex --dry-run
```

Apply a migration plan:

```bash
workspace-manager migrate --root E:\codex --apply
```

Audit Skills:

```bash
workspace-manager skill-audit --root E:\codex
```

Regenerate the Skill registry:

```bash
workspace-manager skill-register --root E:\codex
```

## Examples

See the `examples/` folder:

- `research_presentation_example.md`
- `media_wechat_example.md`
- `skill_registry_example.md`
- `task_registry_example.md`

## Roadmap

- richer task inference from filenames and metadata;
- configurable domain routing rules;
- Codex/OpenClaw plugin packaging;
- migration manifests with rollback metadata;
- JSON registry output alongside Markdown;
- integration tests for Windows, macOS, and Linux;
- optional interactive review mode for ambiguous files.

## License

MIT. See `LICENSE`.
