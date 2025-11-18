# AI Agents and Orchestration

## Overview

This document outlines the AI agent architecture and orchestration patterns for Neuron ImmigrationOS. The system employs a multi-agent approach with specialized roles and responsibilities.

## Agent Architecture

### Primary Agents

1. **ChatGPT** - Strategic planning and high-level decision making
2. **OpenHands** - System orchestration and blueprint management
3. **Cursor** - Code review and quality assurance
4. **Cline** - Feature implementation and development

### Agent Responsibilities

Each agent has specific responsibilities and constraints to ensure system integrity and prevent drift.

## Orchestration Patterns

### Task Flow

The typical task flow follows this pattern:
1. ChatGPT defines requirements and acceptance criteria
2. OpenHands creates implementation plan and tasks
3. Cline implements features according to specifications
4. Cursor reviews and validates implementation
5. OpenHands merges approved changes

### Communication Protocols

Agents communicate through structured handoffs with clear documentation and validation checkpoints.

## Quality Assurance

All agent interactions are governed by quality gates and validation rules to ensure consistency and prevent errors.

## Link to Canonical AI Core / Meta-Engine Specification (Thread A)

The detailed design of Neuron's AI Core (all meta-engines, officer simulation, refusal reconstruction, portfolio viability, universal case preparation, etc.) is defined in the Thread A specification:

- [Neuron Meta-Engines — FULL Specification](../AI_CORE/Neuron_ThreadA_MetaEngines_FULL.md)
- [Neuron Meta-Engines — Table of Contents](../AI_CORE/Neuron_ThreadA_MetaEngines_TOC.md)
- [Neuron Meta-Engines — Executive Summary](../AI_CORE/Neuron_ThreadA_MetaEngines_SUMMARY.md)

All future implementations of AI orchestration, case reasoning, refusal-proofing, and officer simulation **must follow these documents as the canonical source of truth**.  
If implementation ever diverges, engineers must either:
- update the implementation to match Thread A, or  
- raise a proposal to evolve the blueprint (with explicit sign-off).