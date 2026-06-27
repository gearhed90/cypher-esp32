# Contributing to Cypher

Thank you for your interest in contributing to the Cypher robot project!

## Core Philosophy

The most important rule in this project is:

> **Protect the foundation.**

Motor control and basic movement must remain stable and predictable. New features should be added **on top** of the existing layers rather than modifying core motor logic directly.

## How to Contribute

### Reporting Issues
- Use clear, descriptive titles
- Include steps to reproduce
- Mention which part of the system is affected (ESP32 firmware, dashboard, vision, etc.)
- Include relevant logs or error messages when possible

### Code Contributions

1. **Fork** the repository and create a feature branch from `main`.
2. **Keep changes focused** — one feature or fix per pull request.
3. **Follow the architecture** described in `docs/ARCHITECTURE.md`.
4. **Do not modify core motor control** in `firmware/src/main.cpp` unless the change is well-justified and discussed first.
5. Test your changes on actual hardware when possible.

### Commit Messages

Use clear, descriptive commit messages. Example:
Add heartbeat monitoring to UART bridge

ESP32 now sends periodic status packets
Pi detects lost connection and triggers safe stop

text### Documentation

If you add new features, please update the relevant documentation:
- `docs/SETUP.md`
- `docs/ROADMAP.md`
- `docs/ARCHITECTURE.md`
- `docs/UART_PROTOCOL.md` (when working on communication)

## Questions?

Feel free to open an issue for discussion before starting work on larger changes.

---

Thank you for helping keep the foundation solid!
