import assert from "node:assert/strict";
import test from "node:test";
import { build } from "esbuild";
import { type Browser, chromium, type Page } from "playwright";

const WIDTHS = [360, 390, 430, 768, 1024, 1280, 1440] as const;
type HarnessMode = "production" | "locale";

async function bundleHarness() {
  const bundle = await build({
    absWorkingDir: process.cwd(),
    bundle: true,
    entryPoints: [
      "src/__tests__/fixtures/interviewer-report-browser-harness.tsx",
    ],
    format: "iife",
    outdir: "interviewer-report-browser-fixture",
    platform: "browser",
    conditions: ["browser"],
    write: false,
  });
  const script = bundle.outputFiles.find((file) =>
    file.path.endsWith(".js"),
  )?.text;
  const style = bundle.outputFiles.find((file) =>
    file.path.endsWith(".css"),
  )?.text;
  if (!script || !style) throw new Error("Report browser fixture did not bundle");
  return { script, style };
}

async function openHarness(
  browser: Browser,
  assets: { script: string; style: string },
  mode: HarnessMode,
  width: number,
  height = 900,
): Promise<{ page: Page; errors: string[] }> {
  const page = await browser.newPage({ viewport: { width, height } });
  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  page.on("console", (message) => {
    if (message.type() === "error") errors.push(message.text());
  });
  await page.setContent('<div id="root"></div>');
  await page.evaluate((value) => {
    document.body.dataset.harness = value;
  }, mode);
  await page.addStyleTag({ content: assets.style });
  await page.addScriptTag({ content: assets.script });
  await page
    .locator(`[data-harness-ready="${mode}"]`)
    .waitFor({ state: "visible", timeout: 5_000 });
  return { page, errors };
}

async function assertNoPageOverflow(page: Page, label: string) {
  const dimensions = await page.evaluate(() => ({
    clientWidth: document.documentElement.clientWidth,
    scrollWidth: document.documentElement.scrollWidth,
  }));
  assert.ok(
    dimensions.scrollWidth <= dimensions.clientWidth + 1,
    `${label}: unexpected page overflow ${dimensions.scrollWidth} > ${dimensions.clientWidth}`,
  );
}

test("Interviewer report route passes responsive, modal, and historical-read browser behavior", {
  timeout: 180_000,
}, async () => {
  const assets = await bundleHarness();
  let browser: Browser | undefined;
  try {
    browser = await chromium.launch();

    for (const width of WIDTHS) {
      const { page, errors } = await openHarness(
        browser,
        assets,
        "production",
        width,
      );
      await assertNoPageOverflow(page, `report@${width}`);
      assert.deepEqual(errors, [], `report@${width} console/page errors`);

      const badge = page.locator(".interviewer-report__status-badge").first();
      const badgeWidth = await badge.evaluate(
        (element) => element.getBoundingClientRect().width,
      );
      assert.ok(
        Math.abs(badgeWidth - 168) <= 1,
        `report@${width}: status badge must use 168px Report token`,
      );

      const table = page.locator(".interviewer-report__table");
      if (width <= 640) {
        assert.equal(
          await table.evaluate((element) => getComputedStyle(element).display),
          "block",
          `report@${width}: phone presentation must use structured rows`,
        );
      } else {
        assert.equal(
          await table.evaluate((element) => getComputedStyle(element).display),
          "table",
          `report@${width}: tablet/desktop keeps semantic table`,
        );
        if (width <= 1024) {
          const scroll = await page
            .locator(".interviewer-report__table-scroll")
            .evaluate((element) => ({
              clientWidth: element.clientWidth,
              scrollWidth: element.scrollWidth,
            }));
          assert.ok(
            scroll.scrollWidth > scroll.clientWidth,
            `report@${width}: dense table overflow must stay contained`,
          );
        }
      }

      if (width === 390 || width === 1280) {
        const trigger = page.getByRole("button", { name: "Báo cáo PV" });
        await trigger.click();
        const drawer = page.locator(".ui-drawer");
        await drawer.waitFor({ state: "visible" });
        assert.equal(await page.locator("#app-root").getAttribute("inert"), "");
        assert.equal(
          await page.evaluate(() => document.body.style.overflow),
          "hidden",
        );
        assert.ok(
          await page.getByLabel("Kiến thức chuyên môn").isVisible(),
          `report@${width}: edit form exposes labelled field`,
        );

        await page.keyboard.press("Escape");
        await drawer.waitFor({ state: "detached" });
        assert.equal(
          await trigger.evaluate((element) => document.activeElement === element),
          true,
          `report@${width}: Drawer must restore focus to its trigger`,
        );

        await page.getByRole("button", { name: "Xem" }).click();
        await drawer.waitFor({ state: "visible" });
        await page.getByRole("button", { name: "Vòng 1" }).click();
        assert.ok(
          await page.getByText(/Vòng lịch sử chỉ hiển thị/).isVisible(),
          `report@${width}: historical round is visible but preview stays current-only`,
        );
        assert.equal(
          await page.getByRole("button", { name: "Lưu báo cáo" }).count(),
          0,
          `report@${width}: historical round must not expose write action`,
        );
        await page.keyboard.press("Escape");
        await drawer.waitFor({ state: "detached" });
      }

      await page.close();
    }

    const constrained = await openHarness(
      browser,
      assets,
      "production",
      390,
      560,
    );
    await constrained.page.getByRole("button", { name: "Báo cáo PV" }).click();
    const constrainedDrawer = constrained.page.locator(".ui-drawer");
    const bounds = await constrainedDrawer.boundingBox();
    assert.ok(bounds && bounds.height <= 561 && bounds.height >= 559);
    assert.deepEqual(constrained.errors, [], "constrained-height Drawer errors");
    await constrained.page.close();
  } finally {
    await browser?.close();
  }
});

test("Interviewer report draft survives a production locale-context change", {
  timeout: 60_000,
}, async () => {
  const assets = await bundleHarness();
  let browser: Browser | undefined;
  try {
    browser = await chromium.launch();
    const { page, errors } = await openHarness(
      browser,
      assets,
      "locale",
      390,
    );
    await page.getByRole("button", { name: "Báo cáo PV" }).click();
    const field = page.getByLabel("Kiến thức chuyên môn");
    await field.fill("Draft survives locale switch");

    await page.getByTestId("test-switch-en").click();
    assert.equal(await field.inputValue(), "Draft survives locale switch");
    assert.ok(await page.getByLabel("Professional Knowledge").isVisible());
    assert.equal(await page.evaluate(() => document.documentElement.lang), "en");

    await page.getByRole("button", { name: "Save report" }).click();
    assert.ok(await page.getByText("Draft survives locale switch").isVisible());
    assert.deepEqual(errors, [], "locale/draft browser errors");
    await page.close();
  } finally {
    await browser?.close();
  }
});
