import { expect, test } from "@playwright/test";

test("loads fictional teams and generates a labeled forecast", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "AnalyzNow AI" })).toBeVisible();
  await expect(page.getByText("Synthetic demonstration data").first()).toBeVisible();

  const homeTeam = page.getByLabel("Home Team");
  const awayTeam = page.getByLabel("Away Team");
  await expect(homeTeam).toBeEnabled();
  await expect(awayTeam).toBeEnabled();
  await homeTeam.selectOption({ label: "Demo City" });
  await awayTeam.selectOption({ label: "Demo East" });

  await page.getByRole("button", { name: "Generate Forecast" }).click();

  await expect(page.getByRole("heading", { name: "Demo City vs Demo East" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Match Outcome Probabilities" })).toBeVisible();
  await expect(page.getByText("Synthetic demonstration data").last()).toBeVisible();
  await expect(page.getByText(/fictional.*not real match predictions/i)).toBeVisible();
});

test("shows a clear message if the team API is unavailable", async ({ page }) => {
  await page.route("**/api/teams", async route => {
    await route.fulfill({
      status: 503,
      contentType: "application/json",
      body: JSON.stringify({ error: "Temporarily unavailable" }),
    });
  });

  await page.goto("/");
  await expect(page.getByRole("alert")).toContainText("Cannot load teams");
  await expect(page.getByRole("button", { name: "Generate Forecast" })).toBeDisabled();
});

test("shows a server error instead of inventing a forecast", async ({ page }) => {
  await page.goto("/");
  const button = page.getByRole("button", { name: "Generate Forecast" });
  await expect(button).toBeEnabled();

  await page.route("**/api/forecast", async route => {
    await route.fulfill({
      status: 502,
      contentType: "application/json",
      body: JSON.stringify({ error: "Forecast service temporarily unavailable" }),
    });
  });
  await button.click();

  await expect(page.getByRole("alert")).toContainText("Forecast service temporarily unavailable");
  await expect(page.getByRole("heading", { name: "Match Outcome Probabilities" })).toHaveCount(0);
});

test("navigates to Data Health and Model Quality", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("link", { name: "View Data Health" }).click();
  await expect(page).toHaveURL(/\/data-health$/);
  await expect(page.getByText("Synthetic demonstration data").first()).toBeVisible();

  await page.goto("/");
  await page.getByRole("link", { name: "View Model Quality" }).click();
  await expect(page).toHaveURL(/\/model-quality$/);
});
