import pytest

from base.base_test import *
from pages.Career.insider_home_page import InsiderHomePage
from pages.Career.insider_career_page import InsiderCareerPage
from pages.Career.insider_open_positions_page import InsiderOpenPositionsPage


@Owner.ece_us
@Priority.HIGH
@pytest.mark.Smoke
@ProductTeam.QA
@decorator_loader(error_logger)
class TestInsiderCareerPage(BaseTest):
    """ Test case is:

        1. Navigate to Insider homepage and verify it loaded correctly
        2. Click "We're hiring!" and verify Career page is opened with "Explore open roles" button
        3. Click "Explore open roles" and click "Open Positions" under Software Development
        4. Filter Location: "Istanbul, Turkiye" and Team: "Quality Assurance", verify listings appear
        5. Verify all listings contain "Quality Assurance" in position and "Istanbul, Turkiye" in location
        6. Click "Apply Now" and verify redirect to Lever Application Form

    """

    HOME_URL = "https://useinsider.com/"
    EXPECTED_LOCATION = "Istanbul, Turkiye"
    EXPECTED_TEAM = "Quality Assurance"

    def setUp(self):
        pass

    def test_insider_career_page(self):
        """Tests career page navigation, job filtering, and Apply redirect to Lever"""

        self.logger.info("1. Navigate to Insider homepage and verify it loaded correctly")
        self.navigate_url(self.HOME_URL)
        home_page = InsiderHomePage(self.driver)
        self.assertTrue(home_page.is_loaded(),
                        "Insider homepage did not load correctly!")
        self.logger.info("Insider homepage loaded successfully")

        self.logger.info("2. Click \"We're hiring!\" and verify Career page with \"Explore open roles\" button")
        home_page.click_we_are_hiring()
        career_page = InsiderCareerPage(self.driver)
        self.assertTrue(career_page.is_loaded(),
                        "Career page did not open — URL does not contain 'careers'!")
        self.assertTrue(career_page.is_explore_open_roles_visible(),
                        "\"Explore open roles\" button is not visible on Career page!")
        self.logger.info("Career page loaded and \"Explore open roles\" button is visible")

        self.logger.info("3. Click \"Explore open roles\" and click Open Positions under Software Development")
        career_page.click_explore_open_roles()
        career_page.click_software_development_open_positions()
        self.logger.info("Navigated to Software Development open positions")

        self.logger.info("4. Filter by Location: '{}' and Team: '{}'".format(
            self.EXPECTED_LOCATION, self.EXPECTED_TEAM))
        open_positions_page = InsiderOpenPositionsPage(self.driver)
        open_positions_page.select_location(self.EXPECTED_LOCATION)
        open_positions_page.select_team(self.EXPECTED_TEAM)
        self.assertTrue(open_positions_page.are_jobs_listed(),
                        "No job listings appeared after applying filters!")
        self.logger.info("Job listings are visible after applying filters")

        self.logger.info("5. Verify all listings contain correct position and location")
        jobs = open_positions_page.get_job_listings()
        self.assertGreater(len(jobs), 0, "Job list is empty after filtering!")
        for index, job in enumerate(jobs):
            position = job.get_position()
            location = job.get_location()
            self.assertIn(self.EXPECTED_TEAM, position,
                          "Job #{} position '{}' does not contain '{}'!".format(
                              index + 1, position, self.EXPECTED_TEAM))
            self.assertIn(self.EXPECTED_LOCATION, location,
                          "Job #{} location '{}' does not contain '{}'!".format(
                              index + 1, location, self.EXPECTED_LOCATION))
        self.logger.info("All {} listings verified — position and location are correct".format(len(jobs)))

        self.logger.info("6. Click Apply Now on first listing and verify redirect to Lever Application Form")
        jobs[0].click_apply()
        open_positions_page.switch_to_new_tab()
        self.assertTrue(open_positions_page.is_lever_application_form_open(),
                        "Did not redirect to Lever Application Form after clicking Apply!")
        self.logger.info("Successfully redirected to the Lever Application Form")
        self.logger.info("All test steps completed successfully!")

    def tearDown(self):
        self.quit_driver()
