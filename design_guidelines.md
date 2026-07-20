{
  "product": {
    "name": "GPOS by Grahmos",
    "institution_context_example": "Howard University · powered by Grahmos",
    "design_personality": [
      "governance-forward",
      "institutional + premium",
      "evidence-first",
      "calm density (operator-grade, not flashy)",
      "accessible by default (WCAG 2.2 AA core paths)"
    ],
    "co_branding_rules": {
      "constant": [
        "Grahmos shield mark",
        "GPOS by Grahmos wordmark",
        "typography",
        "navigation shell",
        "component system",
        "semantic colors (navy/teal/purple)"
      ],
      "institution_limited_to": [
        "workspace header",
        "reports",
        "selected highlights (small accents only)"
      ],
      "do_not": [
        "Do NOT create per-institution white-label UI",
        "Do NOT show Accio or Activepieces as customer-facing products"
      ]
    }
  },

  "design_tokens": {
    "notes": [
      "Light theme first. Non-transparent surfaces for readability.",
      "Navy anchors governance & trust; Teal = procurement/decisions; Purple = learning/employment.",
      "Gradients are decorative only and must follow the GRADIENT RESTRICTION RULE appended below."
    ],

    "css_custom_properties": {
      "add_to": "/app/frontend/src/index.css (replace :root tokens; keep Tailwind layers)",
      "tokens": "@layer base {\n  :root {\n    /* Brand semantics */\n    --g-navy-950: 214 63% 12%; /* #0B1F3A */\n    --g-navy-900: 214 55% 18%;\n    --g-navy-800: 214 45% 26%;\n    --g-teal-700: 174 72% 28%; /* #0F766E-ish */\n    --g-teal-600: 173 80% 36%; /* #0D9488-ish */\n    --g-teal-500: 173 84% 41%; /* #14B8A6-ish */\n    --g-purple-700: 270 67% 44%;\n    --g-purple-600: 270 72% 52%;\n    --g-purple-500: 270 80% 60%;\n\n    /* Neutral surfaces (cool, institutional) */\n    --g-slate-950: 222 47% 11%;\n    --g-slate-900: 222 35% 16%;\n    --g-slate-800: 222 25% 22%;\n    --g-slate-700: 222 18% 32%;\n    --g-slate-600: 222 14% 42%;\n    --g-slate-500: 222 12% 52%;\n    --g-slate-200: 220 18% 92%;\n    --g-slate-100: 220 20% 96%;\n    --g-slate-50: 220 25% 98%;\n\n    /* State colors (avoid gradients here) */\n    --g-success: 160 84% 32%;\n    --g-warning: 38 92% 50%;\n    --g-danger: 0 84% 60%;\n    --g-info: 199 89% 48%;\n\n    /* Shadcn semantic mapping (light) */\n    --background: var(--g-slate-50);\n    --foreground: var(--g-slate-950);\n    --card: 0 0% 100%;\n    --card-foreground: var(--g-slate-950);\n    --popover: 0 0% 100%;\n    --popover-foreground: var(--g-slate-950);\n\n    /* Primary = NAVY (governance) */\n    --primary: var(--g-navy-950);\n    --primary-foreground: 0 0% 100%;\n\n    /* Secondary = cool neutral */\n    --secondary: var(--g-slate-100);\n    --secondary-foreground: var(--g-slate-950);\n\n    --muted: var(--g-slate-100);\n    --muted-foreground: var(--g-slate-600);\n\n    /* Accent = TEAL (procurement/decisions) */\n    --accent: 173 84% 95%;\n    --accent-foreground: var(--g-teal-700);\n\n    --destructive: var(--g-danger);\n    --destructive-foreground: 0 0% 100%;\n\n    --border: 220 16% 88%;\n    --input: 220 16% 88%;\n    --ring: var(--g-teal-600);\n\n    --radius: 0.75rem;\n\n    /* Data viz */\n    --chart-1: var(--g-teal-600);\n    --chart-2: var(--g-navy-800);\n    --chart-3: var(--g-purple-600);\n    --chart-4: 38 92% 50%;\n    --chart-5: 0 84% 60%;\n\n    /* App-specific tokens */\n    --shell-bg: 0 0% 100%;\n    --shell-rail: 220 25% 98%;\n    --shell-rail-border: 220 16% 90%;\n    --focus-ring: var(--g-teal-600);\n\n    --shadow-elev-1: 0 1px 2px rgba(15, 23, 42, 0.06);\n    --shadow-elev-2: 0 8px 24px rgba(15, 23, 42, 0.10);\n\n    --mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, \"Liberation Mono\", \"Courier New\", monospace;\n  }\n}\n\n@layer base {\n  html {\n    font-feature-settings: \"cv02\", \"cv03\", \"cv04\", \"cv11\";\n  }\n  body {\n    background: hsl(var(--background));\n    color: hsl(var(--foreground));\n  }\n  .tabular-nums {\n    font-variant-numeric: tabular-nums;\n  }\n}\n"
    },

    "tailwind_usage_notes": [
      "Use hsl(var(--token)) via shadcn classes (bg-background, text-foreground, border-border, ring-ring).",
      "Prefer cool neutrals for surfaces; reserve teal/purple for meaning, not decoration.",
      "Never use purple for procurement actions; purple is learning/employment only."
    ],

    "spacing_system": {
      "base": "4px",
      "dense_tables": "py-2 px-3 (mobile), py-2.5 px-4 (desktop)",
      "cards": "p-4 sm:p-5",
      "page_gutters": "px-4 sm:px-6 lg:px-8",
      "max_content_width": "max-w-[1280px] for narrative pages; operator grids can be full-width"
    },

    "radius_and_elevation": {
      "radius": {
        "sm": "rounded-md",
        "md": "rounded-lg",
        "lg": "rounded-xl"
      },
      "shadows": {
        "card": "shadow-[var(--shadow-elev-1)]",
        "drawer": "shadow-[var(--shadow-elev-2)]"
      },
      "borders": "Use 1px cool borders (border-border) + subtle row separators; avoid heavy outlines"
    }
  },

  "typography": {
    "font_pairing": {
      "ui": {
        "google_font": "IBM Plex Sans",
        "fallback": "Inter, system-ui, -apple-system, Segoe UI, Roboto, sans-serif",
        "why": "IBM Plex Sans reads institutional/credible while staying modern for dense dashboards."
      },
      "data": {
        "css_var": "--mono",
        "usage": "IDs, amounts, timestamps, SLA durations, quote normalization rows"
      }
    },
    "implementation": {
      "add_to_index_html": "<link rel=\"preconnect\" href=\"https://fonts.googleapis.com\">\n<link rel=\"preconnect\" href=\"https://fonts.gstatic.com\" crossorigin>\n<link href=\"https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&display=swap\" rel=\"stylesheet\">",
      "tailwind_classes": {
        "app_default": "font-[\"IBM Plex Sans\"]",
        "page_title": "text-2xl sm:text-3xl font-semibold tracking-[-0.02em]",
        "section_title": "text-sm font-semibold text-slate-900",
        "body": "text-sm leading-6 text-slate-800",
        "meta": "text-xs text-slate-600",
        "mono": "font-mono tabular-nums"
      }
    },
    "text_size_hierarchy": {
      "h1": "text-4xl sm:text-5xl lg:text-6xl",
      "h2": "text-base md:text-lg",
      "body": "text-base (mobile: text-sm)",
      "small": "text-sm or text-xs"
    }
  },

  "layout_system": {
    "global_shell": {
      "pattern": "Operator-grade 3-zone shell",
      "zones": {
        "left_rail": "Icon + label nav (collapsible). Fixed width 264px desktop; drawer on mobile.",
        "top_workspace_header": "Institution context + case switcher + global search + Demo Mode role switcher.",
        "main_canvas": "Page content; supports split panes (table + record drawer)."
      },
      "grid": {
        "desktop": "12-col grid; main content spans 8–9 cols, side panels 3–4 cols",
        "operator_views": "Full-width with sticky table header + right record drawer",
        "mobile": "Single column; drawers/sheets for secondary panels"
      },
      "sticky_rules": [
        "Sticky top header (z-40) with subtle border + blur OFF (keep opaque).",
        "Sticky table header for queues.",
        "Record drawer uses shadcn Drawer/Sheet; never overlay critical text with transparency."
      ]
    },

    "page_blueprints": {
      "grahmos_today_home": {
        "goal": "One view of pending decisions, active procurements, agent findings, student assignments, impact tiles.",
        "layout": [
          "Top: ‘Today’ header + quick filters (My role / All) + date range",
          "Row 1: 4 KPI tiles (Pending approvals, At-risk SLAs, Active cases, Student hours this week)",
          "Row 2: Split: Left ‘My Queue’ (table) | Right ‘Agent Findings’ (cards with evidence chips)",
          "Row 3: ‘Active Procurements’ timeline strip + ‘Student Assignments’ list"
        ],
        "components": ["Card", "Tabs", "Table", "Badge", "Progress", "Skeleton"],
        "micro_interactions": [
          "KPI tile hover: elevate + show delta tooltip",
          "Queue row hover: reveal quick actions (Approve/Request info)"
        ]
      },

      "decision_room": {
        "goal": "Coordinate a single case; visually separate agent recommendation vs authorized human decision.",
        "layout": [
          "Header: Case title + stage pill + deadline + ‘Show Audit Trail’",
          "Left column: Request summary, stakeholders, constraints, budget",
          "Center: Recommendation panel (agent) with evidence chips + unknowns/conflicts",
          "Right: Decision & Approvals panel (human) with SoD status + role-based approvals"
        ],
        "visual_separation": {
          "agent_panel": "Teal-tinted header strip + ‘Prepared by Grahmos Assist’ label; includes evidence lineage chips.",
          "human_panel": "Navy header strip + ‘Authorized Decision’ label; requires explicit action + rationale input.",
          "dissent_unknowns": "Purple ‘Learning/Review’ callouts for dissent/unknowns; never teal for dissent."
        },
        "components": ["Card", "Accordion", "Badge", "Separator", "Textarea", "Dialog", "Tooltip"],
        "required_elements": [
          "Dissent list (who/why)",
          "Unknowns list (what evidence missing)",
          "Exceptions banner (policy override) with required justification",
          "Decision rationale field (required)"
        ]
      },

      "campus_memory": {
        "goal": "Notion-like institutional memory: policies, prior decisions, contracts, evidence artifacts.",
        "layout": [
          "Left: Collections sidebar (Policies, Contracts, Decisions, Suppliers, Evidence)",
          "Main: Search + filters + results list",
          "Right drawer: Document viewer with provenance + linked cases"
        ],
        "components": ["Command", "Tabs", "Table", "Sheet", "Breadcrumb"],
        "notes": ["Use Command component for global search with keyboard-first UX."]
      },

      "approval_center": {
        "goal": "Linear-style focused work queue + policy path visualization + SoD status + SLA aging.",
        "layout": [
          "Top: My approvals (count) + SLA aging legend",
          "Main: Queue table with row selection",
          "Right: Record drawer with policy path stepper + evidence + approve/reject"
        ],
        "components": ["Table", "Drawer", "Badge", "Progress", "Separator"],
        "sla_visual": "Use subtle left border color on rows: teal (on track), amber (due soon), red (overdue)."
      },

      "supplier_360": {
        "goal": "Airtable-like supplier comparison grid + quote normalization + risk flags + certifications.",
        "layout": [
          "Top: Saved views + filters (certified, diverse, local, risk)",
          "Main: Comparison grid (sticky header, horizontal scroll)",
          "Right drawer: Supplier profile + quote history + evidence"
        ],
        "components": ["Table", "Tabs", "Badge", "Popover", "Tooltip"],
        "data_rules": [
          "Show multi-currency conversion source + timestamp in mono text",
          "Risk flags are neutral + icon + label; avoid alarmist red unless critical"
        ]
      },

      "student_work_board": {
        "goal": "Deputy-like board for paid student work: assignments, prerequisites, hours, pay, supervisor.",
        "layout": [
          "Top: Available assignments + filters (skills, hours, pay)",
          "Main: Board/list toggle",
          "Drawer: Assignment detail + apply/accept + learning prerequisites"
        ],
        "components": ["Tabs", "Card", "Badge", "Drawer", "Progress"],
        "purple_usage": "Use purple accents for learning prerequisites and verified skills only."
      },

      "skills_passport_career_launch": {
        "goal": "Workable/Indeed-like profile: verified skills, credentials, portfolio, job opportunities.",
        "layout": [
          "Header: Student profile + verification status",
          "Left: Skills passport (verified badges)",
          "Right: Opportunities list + match score"
        ],
        "components": ["Card", "Badge", "Tabs", "Progress"],
        "purple_usage": "Primary highlights are purple; keep procurement teal out of this surface."
      },

      "impact_command_center": {
        "goal": "Midday-like finance dashboard: cycle time, savings, supplier performance, paid hours, conversions.",
        "layout": [
          "Top: KPI strip (Savings, Cycle time, On-time delivery, Paid hours)",
          "Middle: 2 charts (trend + breakdown)",
          "Bottom: Table of cases with filters"
        ],
        "components": ["Card", "Table", "Tabs"],
        "charts": {
          "library": "recharts",
          "notes": "Use muted gridlines, tabular nums, and tooltips with evidence links."
        }
      },

      "operator_saved_views_workspace": {
        "goal": "Control plane: saved views (My Queue, Needs Info, Sourcing, Approval Aging, Exceptions, In Transit, Student Tasks, Offline Conflicts).",
        "layout": [
          "Left: Saved views list (collapsible)",
          "Main: Table with filter/group/sort bar",
          "Right: Record drawer with inline permitted edits + policy-gated bulk actions"
        ],
        "components": ["Table", "DropdownMenu", "Popover", "Drawer", "Checkbox"],
        "bulk_actions": "Show disabled state with tooltip explaining policy gate."
      }
    }
  },

  "component_specs": {
    "component_path": {
      "shadcn_primary": "/app/frontend/src/components/ui/",
      "use_components": {
        "navigation": ["navigation-menu.jsx", "breadcrumb.jsx", "menubar.jsx"],
        "shell": ["sheet.jsx", "drawer.jsx", "scroll-area.jsx", "resizable.jsx", "separator.jsx"],
        "forms": ["form.jsx", "input.jsx", "textarea.jsx", "select.jsx", "checkbox.jsx", "switch.jsx", "radio-group.jsx"],
        "data_display": ["table.jsx", "card.jsx", "badge.jsx", "tabs.jsx", "tooltip.jsx", "popover.jsx", "hover-card.jsx", "skeleton.jsx"],
        "dialogs": ["dialog.jsx", "alert-dialog.jsx"],
        "search": ["command.jsx"],
        "calendar": ["calendar.jsx"],
        "toasts": ["sonner.jsx"]
      }
    },

    "nav_shell": {
      "left_rail": {
        "style": "Light rail with navy iconography; active item has teal left indicator + subtle teal-tint background.",
        "tailwind": "bg-[hsl(var(--shell-rail))] border-r border-[hsl(var(--shell-rail-border))]",
        "active_item": "relative bg-[hsl(173_84%_95%)] text-[hsl(var(--g-navy-950))] before:absolute before:left-0 before:top-2 before:bottom-2 before:w-1 before:rounded-r before:bg-[hsl(var(--g-teal-600))]"
      },
      "top_header": {
        "style": "Opaq header with institution context pill + global search + Demo Mode role switcher.",
        "institution_pill": "text-xs font-medium px-2.5 py-1 rounded-full bg-slate-100 border border-slate-200",
        "demo_mode": "Always visible; uses Alert-style framing to feel safe/intentional."
      }
    },

    "demo_mode_role_switcher": {
      "label": "Demo Mode",
      "pattern": "A compact, clearly bordered control in header; opens Dialog with role list + explanation of SoD.",
      "roles": ["Requester", "Procurement Operator", "Approver (Finance)", "Approver (Facilities)", "Student Fellow", "Supplier", "Executive"],
      "copy_rules": [
        "Use plain language: ‘You are impersonating…’",
        "Show current role as a pill",
        "Provide ‘Exit Demo Mode’ action"
      ],
      "data_testids": {
        "open": "demo-mode-open-button",
        "current_role": "demo-mode-current-role",
        "switch_select": "demo-mode-role-select",
        "confirm": "demo-mode-confirm-switch-button",
        "exit": "demo-mode-exit-button"
      }
    },

    "tables_and_queues": {
      "row_density": "Default text-sm; use text-xs for meta columns only.",
      "row_hover": "hover:bg-slate-50",
      "selected_row": "data-[state=selected]:bg-[hsl(173_84%_95%)]",
      "sla_aging": {
        "on_track": "border-l-2 border-l-[hsl(var(--g-teal-600))]",
        "due_soon": "border-l-2 border-l-amber-400",
        "overdue": "border-l-2 border-l-red-500"
      },
      "inline_edits": "Only allow inline edits where policy permits; show lock icon + tooltip otherwise."
    },

    "record_drawer": {
      "pattern": "Right-side Drawer/Sheet with sections: Summary, Policy Path, Evidence, Actions, Audit.",
      "width": "w-full sm:max-w-[520px]",
      "header": "Sticky within drawer; includes stage + SoD status badges.",
      "data_testids": {
        "open": "record-drawer-open",
        "close": "record-drawer-close",
        "policy_path": "record-drawer-policy-path",
        "evidence": "record-drawer-evidence-section",
        "actions": "record-drawer-actions-section"
      }
    },

    "timeline_state_machine": {
      "pattern": "Case timeline strip + audit trail drawer",
      "visual": {
        "stepper": "Use Tabs-like segmented stepper with stage labels; current stage has navy fill + white text; completed stages have teal dot; blocked stages show amber icon.",
        "audit_entries": "Each entry: actor, action, timestamp (mono), rationale, evidence chips"
      },
      "evidence_chips": {
        "style": "Small rounded chips with icon + source label; click opens evidence viewer.",
        "tailwind": "inline-flex items-center gap-1 rounded-full border border-slate-200 bg-white px-2 py-0.5 text-xs text-slate-700 hover:bg-slate-50",
        "copy_examples": [
          "Evidence captured from Accio.",
          "Grahmos Assist prepared this comparison.",
          "Workflow resumed after reconnecting."
        ]
      }
    },

    "decision_vs_approval_separation": {
      "rule": "Recommendation is never visually identical to authorization.",
      "recommendation_card": {
        "header": "bg-[hsl(173_84%_95%)] border-b border-slate-200",
        "badge": "Badge variant outline + teal text: ‘Agent recommendation’",
        "cta": "Primary CTA is disabled until human reviews evidence checklist"
      },
      "authorization_card": {
        "header": "bg-[hsl(var(--g-navy-950))] text-white",
        "badge": "Badge variant secondary: ‘Authorized decision’",
        "required": ["rationale textarea", "confirm dialog", "SoD check summary"]
      }
    },

    "badges_and_status": {
      "status_badges": {
        "in_review": "bg-slate-100 text-slate-800",
        "needs_info": "bg-amber-50 text-amber-900 border border-amber-200",
        "approved": "bg-emerald-50 text-emerald-900 border border-emerald-200",
        "blocked": "bg-red-50 text-red-900 border border-red-200",
        "learning": "bg-[hsl(270_80%_96%)] text-[hsl(var(--g-purple-700))] border border-[hsl(270_60%_88%)]"
      },
      "risk_flags": "Use neutral icon + label; reserve red for critical compliance failures only."
    },

    "empty_loading_error_states": {
      "loading": "Use Skeleton rows for tables; keep layout stable.",
      "empty": "Provide next-best action: ‘Create request’, ‘Adjust filters’, ‘Switch view’.",
      "error": "Plain-language recovery + retry; include error id in mono; never blame user."
    }
  },

  "motion_and_micro_interactions": {
    "library": {
      "recommended": "framer-motion",
      "install": "npm i framer-motion",
      "usage": [
        "Drawer entrance: x from 24px + opacity 0→1 (200ms)",
        "Queue row quick actions: fade in on hover (150ms)",
        "KPI tiles: subtle lift (translateY -1) + shadow increase"
      ]
    },
    "principles": [
      "No universal transition: never transition: all.",
      "Respect prefers-reduced-motion: reduce durations to 0 and remove parallax.",
      "Motion communicates state changes (approved/rejected) with small, non-distracting feedback."
    ]
  },

  "data_viz": {
    "library": "recharts",
    "install": "npm i recharts",
    "chart_style": {
      "grid": "stroke: hsl(220 16% 90%)",
      "axis": "tick: text-slate-600 text-xs",
      "tooltip": "Card-like tooltip with evidence chips + mono timestamp"
    },
    "empty_state": "Show ‘Not enough data yet’ + link to seeded demo cases."
  },

  "iconography": {
    "library": "lucide-react",
    "rules": [
      "No emoji icons.",
      "Use consistent stroke width (1.75–2).",
      "Use teal for action icons, navy for structure, purple for learning."
    ]
  },

  "image_urls": {
    "workspace_header_context": [
      {
        "category": "institution_context",
        "description": "Optional small header background image for reports only (keep subtle, low-contrast).",
        "url": "https://images.unsplash.com/photo-1576588728682-273e5c9d5553?crop=entropy&cs=srgb&fm=jpg&ixlib=rb-4.1.0&q=85"
      }
    ],
    "student_learning_surfaces": [
      {
        "category": "student_work_board_hero",
        "description": "Use in Student Work Board empty state / onboarding panel (not as full-page background).",
        "url": "https://images.pexels.com/photos/8199762/pexels-photo-8199762.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"
      },
      {
        "category": "student_work_board_secondary",
        "description": "Secondary image for Skills Passport onboarding card.",
        "url": "https://images.pexels.com/photos/5940844/pexels-photo-5940844.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"
      }
    ],
    "textures": [
      {
        "category": "subtle_texture_reference",
        "description": "Reference texture for creating a CSS noise overlay (do not use as heavy background).",
        "url": "https://images.unsplash.com/photo-1602475063211-3d98d60e3b1f?crop=entropy&cs=srgb&fm=jpg&ixlib=rb-4.1.0&q=85"
      }
    ]
  },

  "instructions_to_main_agent": {
    "global": [
      "Replace CRA default App.css styles; do NOT center the app container.",
      "Implement the shell: left rail + top workspace header + main canvas.",
      "Ensure every interactive element and key info element has data-testid (kebab-case).",
      "Keep surfaces opaque (no glass). Light theme only for demo.",
      "Never show Accio/Activepieces as products; only as ‘Grahmos found…’ / ‘Evidence captured…’ copy."
    ],
    "copy_snippets": {
      "agent_actions": [
        "Grahmos found 12 qualified suppliers.",
        "Grahmos Assist prepared this comparison.",
        "Approval workflow is waiting for Finance.",
        "Evidence was captured from Accio.",
        "Workflow resumed after reconnecting."
      ]
    },
    "accessibility": [
      "All dialogs/drawers must trap focus and have aria-labels.",
      "Keyboard: Command palette opens with Ctrl/Cmd+K.",
      "Tables: ensure row selection is keyboard reachable.",
      "Contrast: verify teal/purple text on tinted backgrounds meets AA."
    ],
    "demo_controls": [
      "Golden Demo controls live in a right-side ‘Demo’ drawer: Reset Demo, Jump to Stage, Show Audit Trail.",
      "Case state-machine timeline is always visible in Decision Room header."
    ]
  },

  "gradient_restriction_rule": {
    "prohibited": [
      "NEVER use dark/saturated gradient combos (e.g., purple/pink) on any UI element.",
      "Prohibited gradients: blue-500 to purple 600, purple 500 to pink-500, green-500 to blue-500, red to pink etc",
      "NEVER use dark gradients for logo, testimonial, footer etc",
      "NEVER let gradients cover more than 20% of the viewport.",
      "NEVER apply gradients to text-heavy content or reading areas.",
      "NEVER use gradients on small UI elements (<100px width).",
      "NEVER stack multiple gradient layers in the same viewport.",
      "ENFORCEMENT RULE: Id gradient area exceeds 20% of viewport OR affects readability, THEN use solid colors"
    ],
    "allowed_usage": [
      "Section backgrounds (not content backgrounds)",
      "Hero section header content (2–3 mild colors)",
      "Decorative overlays and accent elements only",
      "Gradients can be horizontal, vertical or diagonal"
    ]
  },

  "general_ui_ux_design_guidelines_appendix": "<General UI UX Design Guidelines>\n    - You must **not** apply universal transition. Eg: `transition: all`. This results in breaking transforms. Always add transitions for specific interactive elements like button, input excluding transforms\n    - You must **not** center align the app container, ie do not add `.App { text-align: center; }` in the css file. This disrupts the human natural reading flow of text\n   - NEVER: use AI assistant Emoji characters like`🤖🧠💭💡🔮🎯📚🎭🎬🎪🎉🎊🎁🎀🎂🍰🎈🎨🎰💰💵💳🏦💎🪙💸🤑📊📈📉💹🔢🏆🥇 etc for icons. Always use **FontAwesome cdn** or **lucid-react** library already installed in the package.json\n\n **GRADIENT RESTRICTION RULE**\nNEVER use dark/saturated gradient combos (e.g., purple/pink) on any UI element.  Prohibited gradients: blue-500 to purple 600, purple 500 to pink-500, green-500 to blue-500, red to pink etc\nNEVER use dark gradients for logo, testimonial, footer etc\nNEVER let gradients cover more than 20% of the viewport.\nNEVER apply gradients to text-heavy content or reading areas.\nNEVER use gradients on small UI elements (<100px width).\nNEVER stack multiple gradient layers in the same viewport.\n\n**ENFORCEMENT RULE:**\n    • Id gradient area exceeds 20% of viewport OR affects readability, **THEN** use solid colors\n\n**How and where to use:**\n   • Section backgrounds (not content backgrounds)\n   • Hero section header content. Eg: dark to light to dark color\n   • Decorative overlays and accent elements only\n   • Hero section with 2-3 mild color\n   • Gradients creation can be done for any angle say horizontal, vertical or diagonal\n\n- For AI chat, voice application, **do not use purple color. Use color like light green, ocean blue, peach orange etc**\n\n</Font Guidelines>\n\n- Every interaction needs micro-animations - hover states, transitions, parallax effects, and entrance animations. Static = dead. \n   \n- Use 2-3x more spacing than feels comfortable. Cramped designs look cheap.\n\n- Subtle grain textures, noise overlays, custom cursors, selection states, and loading animations: separates good from extraordinary.\n   \n- Before generating UI, infer the visual style from the problem statement (palette, contrast, mood, motion) and immediately instantiate it by setting global design tokens (primary, secondary/accent, background, foreground, ring, state colors), rather than relying on any library defaults. Don't make the background dark as a default step, always understand problem first and define colors accordingly\n    Eg: - if it implies playful/energetic, choose a colorful scheme\n           - if it implies monochrome/minimal, choose a black–white/neutral scheme\n\n**Component Reuse:**\n\t- Prioritize using pre-existing components from src/components/ui when applicable\n\t- Create new components that match the style and conventions of existing components when needed\n\t- Examine existing components to understand the project's component patterns before creating new ones\n\n**IMPORTANT**: Do not use HTML based component like dropdown, calendar, toast etc. You **MUST** always use `/app/frontend/src/components/ui/ ` only as a primary components as these are modern and stylish component\n\n**Best Practices:**\n\t- Use Shadcn/UI as the primary component library for consistency and accessibility\n\t- Import path: ./components/[component-name]\n\n**Export Conventions:**\n\t- Components MUST use named exports (export const ComponentName = ...)\n\t- Pages MUST use default exports (export default function PageName() {...})\n\n**Toasts:**\n  - Use `sonner` for toasts\"\n  - Sonner component are located in `/app/src/components/ui/sonner.tsx`\n\nUse 2–4 color gradients, subtle textures/noise overlays, or CSS-based noise to avoid flat visuals.\n</General UI UX Design Guidelines>"
}
