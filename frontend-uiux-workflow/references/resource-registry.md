# UI/UX Resource Registry

This registry is a routing hint for research. URLs and product capabilities can change. Verify the current page, access conditions, license, and implementation details before relying on them. A registry entry is not an endorsement and is never a substitute for project context or usability testing.

## Real Product And Flow Evidence

| Resource | Best for | Search or inspect | Do not infer |
| --- | --- | --- | --- |
| [Mobbin](https://mobbin.com/) | Mobile/Web screens, UI elements, and complete flows | A concrete flow such as onboarding, checkout, settings, or refund | That a copied visual works in the user's business context |
| [UXSnaps](https://uxsnaps.com/) | Annotated product examples and design reasoning | Information architecture, progressive disclosure, error prevention, feedback | That an annotation is a fixed rule rather than a design tradeoff |
| [SaaSFrame](https://www.saasframe.io/) | SaaS marketing pages, product flows, and lifecycle email | Acquisition, activation, upgrade, billing, or retention journey | Conversion performance or business metrics not shown by the source |
| [posts.design](https://posts.design/) | Product launches and brand communication | Launch announcements, product cards, and brand packaging | Complex product interaction or task usability |

## Design Principles And System Structure

| Resource | Best for | Search or inspect | Do not infer |
| --- | --- | --- | --- |
| [Component Gallery](https://component.gallery/) | Comparing the same component across mature systems | Breadcrumb, popover, rating, tree view, form feedback, and documented states | That one system's API or tone fits the current product |
| [Design System Checklist](https://designsystemchecklist.com/zh-cn) | Checking design-language, foundation, component, and maintenance coverage | Naming, documentation, versioning, contribution, and governance | That a complete checklist means the system is usable in practice |
| [UI Skills](https://ui-skills.com/) | Agent-oriented playbooks for UI, accessibility, motion, performance, and systems | A narrowly relevant playbook during generation or review | That installing more skills supplies missing product goals or taste |
| [DTCG Design Tokens](https://www.designtokens.org/technical-reports/) | Token naming and cross-tool interoperability | Primitive, semantic, and component token boundaries | That every value should be tokenized before reuse is demonstrated |

## Behavior, Components, And Motion

| Resource | Best for | Search or inspect | Do not infer |
| --- | --- | --- | --- |
| [Base UI](https://base-ui.com/) | Unstyled accessible React behavior and composition | Dialogs, menus, popovers, form controls, and edge cases | That unstyled primitives provide visual language or product content |
| [React Aria](https://react-spectrum.adobe.com/react-aria/) | Accessible, internationalized, complex interaction foundations | Keyboard behavior, focus management, selection, and form semantics | That a primitive removes the need for project-level testing |
| [ReUI](https://reui.io/components) | Copyable React/Tailwind/shadcn-style business components | Data grids, dashboards, Kanban, billing, upload, and CRM patterns | That copied code matches local tokens, dependencies, or API quality |
| [Transitions.dev](https://transitions.dev/) | State-linked CSS transitions and product interaction patterns | Modal, tooltip, toast, tabs, skeleton, streamed text, and AI states | That every available effect belongs in a high-frequency workflow |
| [Motion Primitives](https://motion-primitives.com/) | Customizable open-source motion components | Layout, reveal, gesture, and feedback patterns | That animation quantity improves comprehension or conversion |

## Accessibility And Performance Validation

| Resource | Best for | Search or inspect | Do not infer |
| --- | --- | --- | --- |
| [WCAG 2.2](https://www.w3.org/TR/WCAG22/) | Normative accessibility success criteria | The target criterion relevant to the interaction or content | That passing an automated subset proves full accessibility |
| [web.dev](https://web.dev/) | Performance, Core Web Vitals, and web platform guidance | LCP, INP, CLS, loading, rendering, and responsive behavior | That lab scores predict every real device and network condition |

## Selection Rule

For each task, return a small evidence set rather than a link dump:

```text
Task -> resource category -> 1-3 sources -> observed pattern -> local adaptation -> validation
```

If no listed source fits, use the project's existing documentation or a current primary source. Do not force a registry match.
