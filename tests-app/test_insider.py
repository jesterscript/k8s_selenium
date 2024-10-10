"""Test module."""

import time
from selenium.webdriver import Chrome, ChromeOptions, ActionChains, Remote
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import pytest


class InsiderPage:
    """Base page class with extra helper methods."""

    def __init__(self, driver_) -> None:
        """Init

        Args:
            driver_ (_type_): Web driver
        """
        self.driver: Chrome = driver_
        self.url = None

    def accept_cookies(self):
        """Accept cookies if it's clickable."""
        # click if it's clickable
        cookie_button = self.wait_until_displayed(By.ID, "wt-cli-accept-all-btn")
        if not cookie_button:
            return
        time.sleep(5)
        cookie_button.click()
        time.sleep(2)

    def navigate(self):
        """Get to URL."""
        if self.driver.current_url == self.url:
            return
        self.driver.get(self.url)
        self.accept_cookies()

    def wait_until_displayed(self, by: By, value: str, timeout: int = 5):
        """Wait until element is visible."""
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located((by, value))
            )
        except TimeoutException as e:
            print("cant find", value)
            return False

    def wait_until_find(self, by: By, value: str, timeout: int = 5):
        """Wait until element is rendered."""
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
        except TimeoutException as e:
            print("cant find", value)
            return False

class HomePage(InsiderPage):
    """Home page class."""

    def __init__(self, driver_) -> None:
        """Init with URL.

        Args:
            driver_ (_type_): _description_
        """
        super().__init__(driver_)
        self.url = "https://useinsider.com/"

    def goto_careers(self):
        """Get to Careers page."""
        comp_dd = self.wait_until_find(
            By.XPATH, "//html/body/nav/div[2]/div/ul[1]/li[6]/a"
        )
        comp_dd.click()
        time.sleep(1)
        careers_link = comp_dd = self.wait_until_find(
            By.XPATH, "//a[@class='dropdown-sub' and text()='Careers']"
        )
        careers_link.click()
        time.sleep(1)


class CareersPage(InsiderPage):
    """Careers class.

    Args:
        InsiderPage (_type_): _description_
    """
    def __init__(self, driver_) -> None:
        super().__init__(driver_)
        self.url = "https://useinsider.com/careers/"

    def get_teams_verifier(self):
        """Get 'See all teams' button."""
        return self.wait_until_find(
            By.XPATH, "//a[contains(@class, 'loadmore') and text()='See all teams']"
        )

    def get_location_verifier(self):
        """Get location slider."""
        return self.wait_until_find(By.XPATH, '//*[@id="location-slider"]')

    def get_life_at_insider_verifier(self):
        """Get one of aria-label from life-at-insider images."""
        return self.wait_until_find(
            By.XPATH, "//*[contains(@aria-label, 'life-at-insider')]"
        )


class QAPage(InsiderPage):
    """QA Page class.

    Args:
        InsiderPage (_type_): _description_
    """
    def __init__(self, driver_) -> None:
        """Init with URL.

        Args:
            driver_ (_type_): _description_
        """
        super().__init__(driver_)
        self.url = "https://useinsider.com/careers/quality-assurance/"

    def click_see_all_jobs(self):
        """Click See all jobs button."""
        button = self.wait_until_find(
            By.XPATH, "//a[contains(@class, 'btn') and text()='See all QA jobs']"
        )
        button.click()


class OpenPositions(InsiderPage):
    """Open positions class.

    Args:
        InsiderPage (_type_): _description_
    """
    def __init__(self, driver_) -> None:
        super().__init__(driver_)
        self.url = (
            "https://useinsider.com/careers/open-positions/?department=qualityassurance"
        )

    def filter_by_location(self, location: str):
        """Set Location filter to given value.

        Args:
            location (str): _description_
        """
        location_list = self.wait_until_displayed(
            By.ID, "select2-filter-by-location-container"
        )
        time.sleep(10)
        location_list.click()
        time.sleep(2)
        location_item = self.wait_until_find(
            By.XPATH,
            f"//li[contains(@class, 'select2-results__option') and text()='{location}']",
        )
        time.sleep(1)
        location_item.click()
        time.sleep(5)

    def filter_by_department(self, department: str):
        """Set department filter to given value.

        Args:
            department (str): _description_
        """
        dept_list = self.wait_until_displayed(
            By.ID, "select2-filter-by-department-container"
        )
        time.sleep(10)
        dept_list.click()
        time.sleep(2)
        dept_item = self.wait_until_find(
            By.XPATH,
            f"//li[contains(@class, 'select2-results__option') and text()='{department}']",
        )
        time.sleep(1)
        dept_item.click()
        time.sleep(5)

    def get_jobs(self):
        """Get listed jobs with attributes title, dept, location and apply button.

        Returns:
            _type_: _description_
        """
        jobs_list = self.wait_until_displayed(By.ID, "jobs-list")
        assert jobs_list is not False
        time.sleep(5)
        # Print details about each child element
        positions = self.driver.find_elements(
            By.CLASS_NAME, "position-list-item-wrapper"
        )  # Replace with your XPath TODO: check with exception
        position_details = []
        # Print details about each element
        for pos in positions:
            title = pos.find_element(By.CLASS_NAME, "position-title")
            dept = pos.find_element(By.CLASS_NAME, "position-department")
            loc = pos.find_element(By.CLASS_NAME, "position-location")
            apply_button = pos.find_element(
                By.XPATH, ".//a[contains(@class, 'btn') and text()='View Role']"
            )
            position_details.append(
                {
                    "title": title.get_attribute("textContent"),
                    "dept": dept.get_attribute("textContent"),
                    "loc": loc.get_attribute("textContent"),
                    "apply": apply_button,
                }
            )
        return position_details

    def click_view_role(self, apply_button):
        """Click view role button.

        Args:
            apply_button (_type_): _description_
        """
        # Move to element then click.
        actions = ActionChains(self.driver)
        actions.move_to_element(apply_button).click().perform()
        time.sleep(5)
        windows = self.driver.window_handles
        self.driver.switch_to.window(windows[-1])

class LeverJobs(InsiderPage):
    """Lever Jobs page class.

    Args:
        InsiderPage (_type_): _description_
    """
    def get_apply_button(self):
        """Return apply button to verify page is open.

        Returns:
            _type_: _description_
        """
        return self.wait_until_find(
            By.XPATH,
            "//a[text()='Apply for this job']",
        )

# tests
@pytest.fixture(autouse=True, scope="session")
def driver(pytestconfig):
    """Set up driver class with external arguments.

    Args:
        pytestconfig (_type_): _description_

    Yields:
        _type_: _description_
    """
    # Parse chrome node pod IP argument for Remove driver.
    chrome_ip = pytestconfig.getoption("chromeip")
    options = ChromeOptions()
    # Auto accept notifications.
    prefs = {
        "profile.default_content_setting_values.notifications": 1
    }
    options.add_experimental_option("prefs", prefs)
    # Add headless arguments.
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    #Connection to Chrome Node Pod
    driver = Remote(f"http://{chrome_ip}:4444/wd/hub", options=options)
    # set window size for lazy testing.
    driver.set_window_size(1600, 900)
    yield driver
    driver.quit()

def test_case1(driver):
    """Check if browser got to Home page.

    Args:
        driver (_type_): _description_
    """
    home = HomePage(driver)
    home.navigate()
    driver.save_screenshot('home.png')
    home.goto_careers()
    driver.save_screenshot('careers.png')
    assert "Insider" in driver.title


def test_case2(driver):
    """Check if Careers page contains requested blocks.

    Args:
        driver (_type_): _description_
    """
    careers = CareersPage(driver)
    careers.navigate()
    assert careers.get_teams_verifier() is not None
    assert careers.get_location_verifier() is not None
    assert careers.get_life_at_insider_verifier() is not None
    driver.save_screenshot('case2.png')


def test_case3(driver):
    """Go to Open Positions page to do filtering and check results.

    Args:
        driver (_type_): _description_
    """
    qa = QAPage(driver)
    qa.navigate()
    qa.click_see_all_jobs()
    open_positions = OpenPositions(driver)
    open_positions.filter_by_location("Istanbul, Turkey")
    open_positions.filter_by_department("Quality Assurance")
    jobs = open_positions.get_jobs()
    print(jobs)
    driver.save_screenshot('case3-prejobs.png')
    for job in jobs:
        assert "Quality Assurance" in job["title"]
        assert "Quality Assurance" in job["dept"]
        assert "Istanbul, Turkey" in job["loc"]
    driver.save_screenshot('case3-jobs.png')
    open_positions.click_view_role(jobs[0]["apply"])
    lever = LeverJobs(driver)
    assert lever.get_apply_button() is not False
    driver.save_screenshot('case3-lever.png')


def test_sanity(driver):
    """Check if pytest can get to Google to see it's working.

    Args:
        driver (_type_): _description_
    """
    driver.get("https://google.com")
    assert "Google" in driver.title
