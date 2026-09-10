import assert from "node:assert/strict";
import test from "node:test";
import { build } from "esbuild";
import { type Browser, chromium, type Page } from "playwright";

const WIDTHS = [360, 390, 430, 768, 1024, 1280, 1440] as const;

async function bundleHarness() {
  const bundle = await build({
    absWorkingDir: process.cwd(),
    bundle: true,
    entryPoints: ["src/__tests__/fixtures/hr-report-browser-harness.tsx"],
    format: "iife",
    outdir: "hr-report-browser-fixture",
    platform: "browser",
    conditions: ["browser"],
    write: false,
  });
  const script = bundle.outputFiles.find((file) => file.path.endsWith(".js"))?.text;
  const style = bundle.outputFiles.find((file) => file.path.endsWith(".css"))?.text;
  if (!script || !style) throw new Error("HR Report browser fixture did not bundle");
  return { script, style };
}

async function openHarness(
  browser: Browser,
  assets: { script: string; style: string },
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
  await page.addStyleTag({ content: assets.style });
  await page.addScriptTag({ content: assets.script });
  await page.locator('[data-harness-ready="hr-report"]').waitFor({
    state: "visible",
    timeout: 5_000,
  });
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

test(
  "HR Report preserves exact table geometry and responsive scroll containment",
  { timeout: 180_000 },
  async () => {
    const assets = await bundleHarness();
    let browser: Browser | undefined;
    try {
      browser = await chromium.launch();
      for (const width of WIDTHS) {
        const { page, errors } = await openHarness(browser, assets, width);
        await assertNoPageOverflow(page, `hr-report@${width}`);
        assert.deepEqual(errors, [], `hr-report@${width} console/page errors`);

        const table = page.getByRole("table");
        const tableWidth = await table.evaluate(
          (element) => element.getBoundingClientRect().width,
        );
        assert.ok(
          Math.abs(tableWidth - 1610) <= 1,
          `hr-report@${width}: table must remain 1610px`,
        );

        const headers = await page.getByRole("columnheader").allTextContents();
        assert.deepEqual(headers.map((value) => value.trim()), [
          "Chọn tất cả",
          "Họ và tên",
          "Vị trí",
          "Thời gian phỏng vấn",
          "Địa điểm",
          "Trạng thái",
          "Ghi chú",
          "Action",
        ]);

        const scroll = await page.locator(".ui-table-scroll").evaluate((element) => ({
          clientWidth: element.clientWidth,
          scrollWidth: element.scrollWidth,
        }));
        if (width < 1440) {
          assert.ok(
            scroll.scrollWidth > scroll.clientWidth,
            `hr-report@${width}: wide table overflow must stay inside TableScrollContainer`,
          );
        }

        const sticky = await table
          .locator("tbody tr")
          .first()
          .locator("td")
          .evaluateAll((cells) =>
            cells.slice(0, 2).map((cell) => ({
              position: getComputedStyle(cell).position,
              left: getComputedStyle(cell).left,
            })),
          );
        assert.equal(sticky[0]?.position, "sticky");
        assert.equal(sticky[0]?.left, "0px");
        assert.equal(sticky[1]?.position, "sticky");
        assert.equal(sticky[1]?.left, "48px");

        const badgeWidth = await page
          .locator(".ui-status-badge")
          .first()
          .evaluate((element) => element.getBoundingClientRect().width);
        assert.ok(
          Math.abs(badgeWidth - 144) <= 1,
          `hr-report@${width}: operational status badge must use 144px benchmark`,
        );

        await page.close();
      }
    } finally {
      await browser?.close();
    }
  },
);

test(
  "HR Report status, drawer, unsaved-change and report-specific destructive UX share production primitives",
  { timeout: 120_000 },
  async () => {
    const assets = await bundleHarness();
    let browser: Browser | undefined;
    try {
      browser = await chromium.launch();
      const { page, errors } = await openHarness(browser, assets, 390, 700);

      let rowStatus = page.getByRole("button", {
        name: "Đổi trạng thái của Nguyễn Minh Anh",
      });
      await rowStatus.click();
      assert.equal(await page.getByRole("menuitemradio").count(), 8);
      await page.keyboard.press("Escape");
      assert.equal(
        await rowStatus.evaluate((element) => document.activeElement === element),
        true,
        "Escape must restore focus to the status trigger",
      );

      await rowStatus.click();
      await page.getByRole("menuitemradio", { name: "Đã gửi Báo cáo" }).click();
      await page.getByText("Đã cập nhật trạng thái báo cáo.").waitFor({
        state: "visible",
      });
      rowStatus = page.getByRole("button", {
        name: "Đổi trạng thái của Nguyễn Minh Anh",
      });
      assert.equal(
        (await rowStatus.locator(".ui-status-badge").textContent())?.trim(),
        "Đã gửi Báo cáo",
      );

      await page.getByRole("checkbox", { name: "Chọn Nguyễn Minh Anh" }).check();
      const bulkStatus = page.getByRole("button", {
        name: "Đổi trạng thái đã chọn",
      });
      assert.equal(await bulkStatus.isEnabled(), true);
      await bulkStatus.click();
      await page.getByRole("menuitemradio", { name: "Tạm hoãn" }).click();
      await page
        .getByText("Đã cập nhật trạng thái cho các báo cáo đã chọn.")
        .waitFor({ state: "visible" });

      await page.getByRole("button", { name: "Xem" }).first().click();
      const drawer = page.getByRole("dialog", { name: "Chi tiết báo cáo" });
      await drawer.waitFor({ state: "visible" });
      assert.equal(
        await page
          .getByRole("button", { name: "Tải PDF — đang chờ mẫu" })
          .isDisabled(),
        true,
      );
      assert.equal(
        await drawer.getByRole("button", { name: "Xóa / Inactive" }).count(),
        1,
        "destructive action must be report-specific inside a participant card",
      );

      const note = drawer.getByLabel("Nội dung ghi chú");
      await note.fill("Ghi chú chưa lưu");
      await drawer.getByRole("button", { name: "Đóng" }).click();
      const discard = page.getByRole("dialog", { name: "Bỏ thay đổi chưa lưu?" });
      await discard.waitFor({ state: "visible" });
      await discard.getByRole("button", { name: "Tiếp tục sửa" }).click();
      assert.equal(await note.inputValue(), "Ghi chú chưa lưu");

      await drawer.getByRole("button", { name: "Xóa / Inactive" }).click();
      const destructive = page.getByRole("dialog", { name: "Xóa / Inactive báo cáo?" });
      await destructive.waitFor({ state: "visible" });
      assert.ok(
        await destructive
          .getByText(/Chỉ báo cáo cụ thể của người phỏng vấn này bị tác động/)
          .isVisible(),
      );
      await destructive.getByRole("button", { name: "Hủy" }).click();

      assert.deepEqual(errors, [], "HR Report interaction browser errors");
      await page.close();
    } finally {
      await browser?.close();
    }
  },
);
