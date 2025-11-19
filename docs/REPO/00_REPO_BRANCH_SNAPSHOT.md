# Neuron Repository Branch Snapshot

**Generated:** 2025-11-19  
**Purpose:** Document current repository state before normalization

## Current Branches (Local + Remote)

### Local Branches
- `main` – canonical / current trunk (target for normalization)
- `phase-0-research-architecture-docs` – early research & architecture docs
- `foundation-scaffolding-complete` – full foundation scaffold (app + blueprint)
- `feature/thread-a-meta-engines` – AI core Thread A docs

### Remote Branches
- `origin/main` – canonical remote trunk
- `origin/phase-0-research-architecture-docs` – early research & architecture docs (backup)
- `origin/foundation-scaffolding-complete` – full foundation scaffold (backup)
- `origin/feature/thread-a-meta-engines` – AI core Thread A docs (backup)

## Branch Status and Roles

### Active Development Branch
- **`main`** – The canonical truth branch for all future development

### Historical/Backup Branches (DO NOT DEVELOP ON THESE)
- **`phase-0-research-architecture-docs`** – Historical snapshot of early research phase
- **`foundation-scaffolding-complete`** – Historical snapshot of foundation scaffolding work
- **`feature/thread-a-meta-engines`** – Historical source branch for Thread A specification

**Important:** All new feature work should branch from `main`. Historical branches are preserved as backups only.

## Git Status Output

```
On branch feature/thread-a-meta-engines
Your branch is up to date with 'origin/feature/thread-a-meta-engines'.

nothing to commit, working tree clean
```

## Git Branch Output

```
* feature/thread-a-meta-engines
  foundation-scaffolding-complete
  main
  phase-0-research-architecture-docs
  remotes/origin/HEAD -> origin/main
  remotes/origin/feature/thread-a-meta-engines
  remotes/origin/foundation-scaffolding-complete
  remotes/origin/main
  remotes/origin/phase-0-research-architecture-docs
```

## Next Steps

1. Normalize `main` branch to contain all critical documentation
2. Ensure Thread A and foundation content is properly merged into `main`
3. Update branching rules in engineering and agent handbooks
4. Create alignment report for Thread A vs Blueprint consistency