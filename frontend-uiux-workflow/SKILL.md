---
name: frontend-uiux-workflow
description: "Plan, research, implement, and audit frontend UI/UX work with task-driven resource discovery, design-system constraints, accessible components, motion, and performance checks. Use for frontend interface design, template research, UI refinement, and design-system work; not for backend-only tasks or undirected inspiration browsing."
---

# Frontend UI/UX Workflow

Use this skill when a user asks to design, build, refine, review, or find references for a frontend interface. Treat external galleries and component registries as research hints, not as mandatory dependencies or proof that a design is usable.

## Start With The Task

Before choosing a visual direction or a template, establish:

- The user task and the page or flow that must support it.
- Product context: SaaS or internal tool, marketing site, AI product, consumer app, or design system.
- Existing repository conventions: framework, styling system, component primitives, tokens, test setup, and installed dependencies. Inspect the repository before proposing a new library.
- Constraints that change decisions: brand, content, responsive targets, internationalization, accessibility, performance, browser support, licensing, and delivery format.

Ask only for missing information that materially changes the result. If the request is clear, make a conservative assumption and state it briefly.

## Use Resources As A Routing Layer

When the task needs examples or templates, read [references/resource-registry.md](references/resource-registry.md). Select one to three sources by the problem being solved; do not browse every site or recommend a site merely because it is in the registry.

Use this sequence:

1. Classify the need as a real product flow, visual or brand direction, component behavior, implementation code, motion, or quality validation.
2. Search with task-specific terms such as `AI workspace streaming`, `complex filter form`, `SaaS onboarding`, or `billing error state`, not just `beautiful dashboard`.
3. Prefer evidence that shows a complete flow, interaction, or documented behavior over isolated screenshots.
4. Extract the reusable decision: information hierarchy, state model, interaction behavior, content pattern, or implementation technique.
5. Record the source URL, what was observed, why it fits, what must not be copied, implementation cost, license or access limits, and any uncertainty.

If a source is inaccessible, paywalled, stale, or only shows a static image, say so and do not present unverified details as facts. Use an available official documentation source or ask the user for an artifact when evidence is necessary.

## Move From Evidence To A System

Translate research into project-specific decisions before writing UI code:

- Define the content hierarchy and the primary, secondary, and failure paths.
- Establish only the tokens the project actually reuses: color, typography, spacing, radius, elevation, and high-frequency component values. Prefer primitive, semantic, then component-level naming.
- Specify component anatomy, states, keyboard behavior, responsive boundaries, long-content behavior, and internationalization limits.
- Keep behavior and accessibility in the foundation layer (existing primitives or Base UI, React Aria, or Radix where appropriate). Treat visual or business components from registries as raw material that must be normalized to the project tokens and API.
- Use Storybook or the repository's equivalent when it exists to document states and run visual, interaction, or accessibility checks.

Do not introduce a large design system, token set, or dependency solely because a reference site uses one. Optimize for the current user task and the smallest maintainable change.

## Motion And Visual Enhancement

Add motion only when it clarifies hierarchy, causality, progress, feedback, or state change. For each animation, check `prefers-reduced-motion`, input blocking, touch behavior, low-end device stability, and its effect on LCP, INP, and CLS. Backgrounds, gradients, 3D, and decorative effects are optional finishing material, never substitutes for content structure or interaction design.

## Quality Gate

Before calling the work complete, verify as far as the project and tools allow:

- Primary task completion, empty, loading, error, offline, permission, success, and cancellation states.
- Keyboard access, visible focus, correct names/roles/states, screen-reader messaging, and non-color-only status cues.
- Contrast, reduced motion, zoom, touch targets, narrow screens, long text, and localization expansion.
- Layout stability and performance, including LCP, INP, and CLS when measurable.
- Real-task walkthrough on representative content, plus the repository's available automated tests.
- Third-party component licenses, source attribution where required, and maintenance or dependency risk.

Automated scores are evidence, not a substitute for manual keyboard, assistive-technology, touch, and real-task checks.

## Deliverables

Match the output to the request:

- For research or recommendations: a short task definition, a focused reference shortlist with links and rationale, proposed design decisions, and risks or unknowns.
- For implementation: the same decision record followed by repository-aligned changes and a verification summary.
- For review or audit: findings ordered by severity with file or screen evidence, then residual test gaps.
- For a template request: identify the template type, show where it was found, explain what can be reused, and separate copied structure from project-specific content and styling.

Never claim that a page is high quality because it resembles a gallery example. The acceptance criterion is whether the target user can complete the task reliably, accessibly, and with acceptable performance.
