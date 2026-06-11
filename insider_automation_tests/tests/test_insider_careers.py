import pytest
from pages.home_page import HomePage
from pages.open_positions_page import OpenPositionsPage


class TestInsiderCareers:
    """
    Test suite for Insider One careers flow.

    Steps:
        1. Open homepage and verify it loads correctly.
        2. Click "We're hiring" (footer link) -> verify Careers page + 'Explore open roles' button.
        3. Click 'Explore open roles' -> click Quality Assurance department card.
        4. Verify QA job listings load on the Lever jobs board.
        5. Verify Istanbul QA jobs appear in the listing.
        6. Click Apply on the first Istanbul job and verify redirect to Lever application form.
    """

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

        # ── Step 3: Quality Assurance department -> Lever board ───────────────
        open_positions = careers.click_explore_open_roles()
        open_positions.click_quality_assurance_positions()

        # ── Step 4: Verify QA jobs load ───────────────────────────────────────
        jobs = open_positions.wait_for_jobs_to_load()
        assert len(jobs) > 0, "No Quality Assurance jobs found on Lever board"

        for job in jobs:
            title = open_positions.get_job_title(job)
            assert any(kw in title.lower() for kw in ["qa", "quality"]), (
                f"Job '{title}' does not appear to be a Quality Assurance role"
            )

        # ── Step 5: Verify Istanbul QA jobs exist ─────────────────────────────
        istanbul_jobs = open_positions.get_istanbul_jobs(jobs)
        assert len(istanbul_jobs) > 0, (
            "No Istanbul QA jobs found in the listing"
        )

        for job in istanbul_jobs:
            location = open_positions.get_job_location(job)
            assert "ISTANBUL" in location.upper(), (
                f"Job location '{location}' does not contain 'Istanbul'"
            )

        # ── Step 6: Apply -> Lever application form ───────────────────────────
        open_positions.click_apply_on_first_istanbul_job(istanbul_jobs)
        open_positions.switch_to_new_tab()
        assert "lever.co" in open_positions.current_url, (
            f"Not redirected to Lever application form. "
            f"Current URL: '{open_positions.current_url}'"
        )
