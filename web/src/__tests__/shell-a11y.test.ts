import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import React from "react";

import Loading from "@/app/loading";
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
 * Recursively resolves stateless React composite function components down to
 * host elements. Stateful client components are covered by browser tests.
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
 * Searches an expanded React element tree for nodes matching a predicate.
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

test("AppShell composes the required semantic landmark-bearing shell", () => {
  const source = fs.readFileSync(
    path.resolve("src/components/shell/AppShell.tsx"),
    "utf8",
  );

  // AppShell is now a stateful client component because it owns responsive
  // navigation. Runtime landmark behavior is covered by the production shell
  // browser test; this static contract keeps composition explicit without
  // illegally invoking Hooks outside React rendering.
  assert.match(source, /<SkipLink\s*\/>/);
  assert.match(source, /<Sidebar\s+currentPath=\{currentPath\}\s*\/>/);
  assert.match(source, /<MobileNavigation[\s\S]*?open=\{mobileNavOpen\}/);
  assert.match(source, /<Header[\s\S]*?mobileNavOpen=\{mobileNavOpen\}/);
  assert.match(
    source,
    /<main\s+id="main-content"\s+tabIndex=\{-1\}\s+className="content">/,
  );
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

  const brandLogos = findElements(
    tree,
    (el) => el.props?.className === "brand-logo",
  );
  assert.equal(brandLogos.length, 1);

  const activeLinks = findElements(
    tree,
    (el) => el.props?.["aria-current"] === "page",
  );
  assert.equal(activeLinks.length, 1);
  assert.equal(activeLinks[0].props.href, "#applications");

  const inactiveLinks = findElements(
    tree,
    (el) => el.type === "a" && el.props?.["aria-current"] !== "page",
  );
  assert.equal(inactiveLinks.length, 3);

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

test("Header renders title slot and semantic language selector", () => {
  const customTitle = "Hồ sơ ứng tuyển / Application Inbox";
  const tree = expand(React.createElement(Header, { title: customTitle }));

  const h1s = findElements(tree, (el) => el.type === "h1");
  assert.equal(h1s.length, 1);
  assert.equal(String(h1s[0].props.children), customTitle);

  const switchers = findElements(
    tree,
    (el) =>
      el.type === "fieldset" && el.props?.className === "language-switcher",
  );
  assert.equal(switchers.length, 1);

  const legends = findElements(tree, (el) => el.type === "legend");
  assert.equal(legends.length, 1);
  assert.equal(legends[0].props.className, "sr-only");
  assert.match(
    String(legends[0].props.children),
    /Chọn ngôn ngữ \/ Choose language/,
  );

  const buttons = findElements(tree, (el) => el.type === "button");
  // Header now contains the mobile navigation trigger plus VI/EN controls.
  const languageButtons = buttons.filter((button) =>
    String(button.props.className ?? "").includes("lang-btn"),
  );
  assert.equal(languageButtons.length, 2);
  assert.equal(languageButtons[0].props["aria-pressed"], "true");
  assert.equal(languageButtons[1].props["aria-pressed"], "false");
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

  assert.match(
    globalsCss,
    /:focus-visible\s*\{[^}]*outline:\s*2px solid var\(--eiu-blue\)/,
  );
  assert.match(globalsCss, /outline-offset:\s*2px/);

  assert.match(globalsCss, /@media\s*\(prefers-reduced-motion:\s*reduce\)/);
  assert.match(globalsCss, /animation-duration:\s*0\.01ms/);
  assert.match(globalsCss, /transition-duration:\s*0\.01ms/);

  assert.match(globalsCss, /\.skip-link\s*\{[^}]*position:\s*absolute/);
  assert.match(globalsCss, /\.skip-link\s*\{[^}]*top:\s*-999px/);
  assert.match(globalsCss, /\.skip-link:focus\s*\{[^}]*top:\s*16px/);
});
