import pytest
from pages.home_page import HomePage
from pages.open_positions_page import OpenPositionsPage


class TestInsiderCareers:
    """
    Test suite for Insider One careers flow.

    Steps:
        1. Open homepage and verify it loads correctly.
        2. Click "We're hiring" -> verify Careers page + 'Explore open roles' button.
        3. Click 'Explore open roles' -> click Software Development open positions link.
        4. Filter by Location='Istanbul, Turkiye' and Team='Quality Assurance'.
        5. Verify every listed job contains 'Quality Assurance' and 'Istanbul, Turkiye'.
        6. Click Apply on the first job and verify redirect to Lever application form.
    """

    LOCATION = "Istanbul, Turkiye"
    TEAM = "Quality Assurance"

    def test_careers_flow(self, driver):
        # ── Step 1: Homepage ──────────────────────────────────────────────────
        home = HomePage(driver)
        home.open_homepage()
        assert home.is_homepage_loaded(), (
            f"Insider homepage did not load. Page title: '{home.title}'"
        )

        # ── Step 2: Careers page ──────────────────────────────────────────────
        careers = home.click_we_are_hiring()
        assert careers.is_careers_page(), (
            f"Not on Careers page after clicking 'We're hiring'. URL: '{careers.current_url}'"
        )
        assert careers.is_explore_roles_button_visible(), (
            "'Explore open roles' button is not visible on the Careers page"
        )

        # ── Step 3: Open positions -> Software Development ────────────────────
        open_positions = careers.click_explore_open_roles()
        open_positions.click_software_development_positions()

        # ── Step 4: Apply filters ─────────────────────────────────────────────
        open_positions.select_location(self.LOCATION)
        open_positions.select_team(self.TEAM)

        jobs = open_positions.wait_for_jobs_to_load()
        assert len(jobs) > 0, (
            f"No job listings found for team='{self.TEAM}' in location='{self.LOCATION}'"
        )

        # ── Step 5: Verify each job listing ──────────────────────────────────
        for job in jobs:
            title = open_positions.get_job_title(job)
            dept = open_positions.get_job_department(job)
            location = open_positions.get_job_location(job)

            assert self.TEAM in title or self.TEAM in dept, (
                f"Job does not belong to '{self.TEAM}'. "
                f"Title: '{title}', Department: '{dept}'"
            )
            assert self.LOCATION in location, (
                f"Job location '{location}' does not contain '{self.LOCATION}'"
            )

        # ── Step 6: Apply -> Lever form ───────────────────────────────────────
        open_positions.click_apply_on_first_job()
        open_positions.switch_to_new_tab()
        assert "lever.co" in open_positions.current_url, (
            f"Not redirected to Lever application form. "
            f"Current URL: '{open_positions.current_url}'"
        )
