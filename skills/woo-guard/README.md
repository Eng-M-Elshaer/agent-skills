# woo-guard

Review generated or changed WooCommerce code — extensions, payment and shipping integrations, checkout customizations, and order/product logic — before it ships. Best used reactively after an agent writes, edits, or reviews code touching WooCommerce APIs: wc_get_order, wc_get_orders, wc_get_product, WC() cart or session, woocommerce_* hooks, Store API endpoints, payment gateways, order or product meta, HPOS, subscriptions, or bookings. Use on 'review this Woo plugin', 'is this HPOS compatible', or after tasks like 'write a WooCommerce extension', 'add a checkout field', 'hook into the order flow', or 'update stock'. Enforces HPOS-safe order access, CRUD over direct meta, feature-compatibility declarations, server-side checkout validation, money-handling discipline, and hooks over template overrides. DO NOT USE for WordPress code without WooCommerce APIs (use wp-guard), generic code review (use clean-code-guard), test review (use test-guard), or store configuration and admin-screen questions.

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
