# wp-guard

Review generated or changed WordPress code — plugins, themes, and blocks — before it ships. Best used reactively after an agent writes, edits, or reviews code touching WordPress APIs: add_action/add_filter, shortcodes, meta boxes, AJAX handlers, REST routes, WP_Query or $wpdb, widgets, or WP-CLI commands. Use on 'review this plugin', 'is this safe to ship', 'make this translatable', 'speed up this query', or after tasks like 'write a plugin' or 'add an endpoint/shortcode/meta box'. Enforces escaping and sanitization, nonces plus capability checks, prepared database queries, core-API-first development, translation-ready strings, and query/caching discipline. DO NOT USE for WooCommerce-specific order, product, or checkout logic (use woo-guard), non-WordPress PHP, generic code quality review (use clean-code-guard), test code review (use test-guard), server or hosting configuration, or conceptual WordPress questions.

## Activation

Use this skill when the request matches the trigger and scope described in `SKILL.md`.

## Prerequisites

Read `SKILL.md` before use. Any tool, runtime, connector, or project requirements are documented there.

## Contents

- `SKILL.md`
- `agents/`
- `references/`

## Usage

Copy this directory into your Codex skills directory, then invoke the skill by its name when the request matches its scope. `SKILL.md` is the authoritative specification.
