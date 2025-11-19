# Neuron Agent Handbook

## Overview

This handbook provides guidance for AI agents working within the Neuron ImmigrationOS ecosystem. All agents must follow the governance and orchestration patterns defined in this system.

## Agent Roles

### ChatGPT
- Strategic planning and architecture decisions
- High-level requirement definition
- Final approval for major changes
- Blueprint evolution oversight

### OpenHands
- System orchestration and task coordination
- Blueprint management and updates
- Repository structure maintenance
- Multi-agent workflow coordination

### Cursor
- Code review and quality assurance
- Implementation validation
- Testing oversight
- Code quality enforcement

### Cline
- Feature implementation
- Code development
- Unit testing
- Documentation updates

## Core Principles

1. **Blueprint First**: Always consult the blueprint before making changes
2. **Governance Compliance**: Follow all governance rules and enforcement protocols
3. **Quality Gates**: Respect all quality checkpoints and validation rules
4. **Clear Handoffs**: Use structured communication for all task transitions

## AI Core and Meta-Engine Specifications

For detailed AI orchestration, case reasoning, and meta-engine implementation guidance, agents should reference the Thread A specification:

### Primary Reference
- **[Thread A Executive Summary](AI_CORE/Neuron_ThreadA_MetaEngines_SUMMARY.md)** - Start here for quick orientation and cost-effective token usage

### Detailed Implementation
- **[Thread A Full Specification](AI_CORE/Neuron_ThreadA_MetaEngines_FULL.md)** - Complete specification for engineers/agents doing deep implementation work
- **[Thread A Table of Contents](AI_CORE/Neuron_ThreadA_MetaEngines_TOC.md)** - Navigation and section index for targeted reference

### Usage Guidelines

**For Quick Reference**: Read the Executive Summary first to understand the overall architecture and your role within it.

**For Implementation**: Consult specific sections in the Full Specification when implementing AI core features, meta-engines, or orchestration patterns.

**For Navigation**: Use the Table of Contents to quickly locate relevant sections for your current task.

## Workflow Patterns

### Standard Task Flow
1. Receive task from orchestrator
2. Validate against blueprint and Thread A specifications
3. Implement according to governance rules
4. Document changes and update logs
5. Hand off to next agent in chain

### Escalation Procedures
- Ambiguity → Escalate to ChatGPT
- Blueprint conflicts → Escalate to OpenHands
- Quality issues → Escalate to Cursor
- Implementation blocks → Document and escalate

## Quality Standards

All work must meet FAANG-grade standards as defined in the Thread A specification. This includes:
- Comprehensive testing
- Clear documentation
- Proper error handling
- Performance considerations
- Security compliance

## Continuous Improvement

Agents should continuously learn from interactions and improve their performance while staying within governance boundaries defined in Thread A.