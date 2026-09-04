import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import React from "react";

import Loading from "@/app/loading";
import { AppShell } from "@/components/shell/AppShell";
import { Header } from "@/components/shell/Header";
import { Sidebar } from "@/components/shell/Sidebar";
import { SkipLink } from "@/components/shell/SkipLink";

interface ElementProps {
  id?: string;
  className?: string;
  tabIndex?: number;
  role?: string;
  href?: string;
  "aria-label"?: string;
  "aria-live"?: string;
  "aria-current"?: string;
  "aria-pressed"?: string;
  children?: React.ReactNode;
  [key: string]: unknown;
}

type TestElement = React.ReactElement<ElementProps>;

function isReactElement(node: unknown): node is React.ReactElement {
  return React.isValidElement(node);
}

/**
 * Recursively resolves React composite function components down to host elements
 */
function expand(node: React.ReactNode): React.ReactNode {
  if (!isReactElement(node)) {
    return node;
  }

  if (typeof node.type === "function") {
    const Component = node.type as (props: unknown) => React.ReactNode;
    return expand(Component(node.props));
  }

  const props = node.props as ElementProps;
  if (props?.children) {
    const children = React.Children.map(props.children, expand);
    return React.cloneElement(node, undefined, children);
  }

  return node;
}

/**
 * Searches an expanded React element tree for nodes matching a predicate
 */
function findElements(
  node: React.ReactNode,
  predicate: (el: TestElement) => boolean,
  results: TestElement[] = [],
): TestElement[] {
  if (!isReactElement(node)) {
    return results;
  }

  const el = node as TestElement;
  if (predicate(el)) {
    results.push(el);
  }

  const props = el.props as ElementProps;
  if (props?.children) {
    const children = Array.isArray(props.children)
      ? props.children
      : [props.children];
    for (const child of children) {
      findElements(child as React.ReactNode, predicate, results);
    }
  }

  return results;
}

test("AppShell renders all required semantic landmarks", () => {
  const tree = expand(
    React.createElement(
      AppShell,
      null,
      React.createElement("div", { id: "test-child" }, "Child Content"),
    ),
  );

  // 1. Semantic <aside> sidebar landmark
  const asides = findElements(tree, (el) => el.type === "aside");
  assert.equal(asides.length, 1);
  assert.equal(
    asides[0].props["aria-label"],
    "Thanh điều hướng chính / Main sidebar",
  );

  // 2. Semantic <nav> navigation landmark
  const navs = findElements(tree, (el) => el.type === "nav");
  assert.equal(navs.length, 1);
  assert.equal(navs[0].props["aria-label"], "Menu chức năng / Navigation menu");

  // 3. Semantic <header> topbar landmark
  const headers = findElements(tree, (el) => el.type === "header");
  assert.equal(headers.length, 1);
  assert.equal(headers[0].props.className, "topbar");

  // 4. Semantic <main> landmark targeting #main-content with tabIndex={-1}
  const mains = findElements(tree, (el) => el.type === "main");
  assert.equal(mains.length, 1);
  assert.equal(mains[0].props.id, "main-content");
  assert.equal(mains[0].props.tabIndex, -1);
});

test("SkipLink renders an accessible skip link targeting #main-content", () => {
  const tree = expand(React.createElement(SkipLink, null)) as TestElement;

  assert.equal(tree.type, "a");
  assert.equal(tree.props.href, "#main-content");
  assert.equal(tree.props.className, "skip-link");
  assert.match(
    String(tree.props.children),
    /Chuyển đến nội dung chính \/ Skip to main content/,
  );
});

test("Sidebar renders brand header, navigation active state, and user card", () => {
  const tree = expand(
    React.createElement(Sidebar, { currentPath: "#applications" }),
  );

  // Brand header
  const brandLogos = findElements(
    tree,
    (el) => el.props?.className === "brand-logo",
  );
  assert.equal(brandLogos.length, 1);

  // Active navigation link has aria-current="page"
  const activeLinks = findElements(
    tree,
    (el) => el.props?.["aria-current"] === "page",
  );
  assert.equal(activeLinks.length, 1);
  assert.equal(activeLinks[0].props.href, "#applications");

  // Inactive navigation links do not have aria-current
  const inactiveLinks = findElements(
    tree,
    (el) => el.type === "a" && el.props?.["aria-current"] !== "page",
  );
  assert.equal(inactiveLinks.length, 3);

  // Accessible user card
  const avatars = findElements(
    tree,
    (el) => el.props?.className === "user-avatar",
  );
  assert.equal(avatars.length, 1);
  assert.equal(avatars[0].props.role, "img");
  assert.match(
    avatars[0].props["aria-label"] ?? "",
    /Ảnh đại diện người dùng \/ User avatar/,
  );
});

test("Header renders title slot and language toggle with accessible labels", () => {
  const customTitle = "Hồ sơ ứng tuyển / Application Inbox";
  const tree = expand(React.createElement(Header, { title: customTitle }));

  // Title slot renders h1
  const h1s = findElements(tree, (el) => el.type === "h1");
  assert.equal(h1s.length, 1);
  assert.equal(String(h1s[0].props.children), customTitle);

  // Language switcher has group role and accessible label
  const switchers = findElements(
    tree,
    (el) => el.props?.className === "language-switcher",
  );
  assert.equal(switchers.length, 1);
  assert.equal(switchers[0].props.role, "group");
  assert.match(
    switchers[0].props["aria-label"] ?? "",
    /Chọn ngôn ngữ \/ Choose language/,
  );

  // Language toggle buttons have accessible states
  const buttons = findElements(tree, (el) => el.type === "button");
  assert.equal(buttons.length, 2);
  assert.equal(buttons[0].props["aria-pressed"], "true");
  assert.equal(buttons[1].props["aria-pressed"], "false");
});

test("loading boundary conforms to accessible status semantics", () => {
  const tree = expand(React.createElement(Loading, null)) as TestElement;

  assert.equal(tree.type, "div");
  assert.equal(tree.props.role, "status");
  assert.equal(tree.props["aria-live"], "polite");
  assert.equal(tree.props.className, "loading-indicator");
  assert.match(String(tree.props.children), /Đang tải\.\.\. \/ Loading\.\.\./);
});

test("globals.css defines focus visibility, reduced motion, and skip link styles", () => {
  const globalsCss = fs.readFileSync(
    path.resolve("src/app/globals.css"),
    "utf8",
  );

  // Focus visible ring
  assert.match(
    globalsCss,
    /:focus-visible\s*\{[^}]*outline:\s*2px solid var\(--eiu-blue\)/,
  );
  assert.match(globalsCss, /outline-offset:\s*2px/);

  // prefers-reduced-motion media query
  assert.match(globalsCss, /@media\s*\(prefers-reduced-motion:\s*reduce\)/);
  assert.match(globalsCss, /animation-duration:\s*0\.01ms/);
  assert.match(globalsCss, /transition-duration:\s*0\.01ms/);

  // Skip link styles
  assert.match(globalsCss, /\.skip-link\s*\{[^}]*position:\s*absolute/);
  assert.match(globalsCss, /\.skip-link\s*\{[^}]*top:\s*-999px/);
  assert.match(globalsCss, /\.skip-link:focus\s*\{[^}]*top:\s*16px/);
});
