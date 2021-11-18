import sys

import pytest
from nbgrader.tests.nbextensions import formgrade_utils as utils
from nbgrader.tests.nbextensions.test_formgrader import browser, fake_home_dir, gradebook, monkeypatch_module, nbserver
from pytest_rabbitmq.factories import rabbitmq_proc

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

if sys.platform == "win32":
    tz = "Coordinated Universal Time"
else:
    tz = "UTC"


@pytest.mark.formgrader
def test_before_autograde_assignment(browser, port, gradebook):
    utils._load_gradebook_page(browser, port, "manage_submissions/Problem Set 1")

    # check the contents of the row before grading
    row = browser.find_elements_by_css_selector("tbody tr")[0]
    assert row.find_element_by_css_selector(".student-name").text == "B, Ben"
    assert row.find_element_by_css_selector(".student-id").text == "Bitdiddle"
    assert row.find_element_by_css_selector(
        ".timestamp"
    ).text == "2015-02-02 22:58:23 {}".format(tz)
    assert row.find_element_by_css_selector(".score").text == "1.5 / 13"
    assert utils._child_exists(row, ".autograde a")


@pytest.mark.formgrader
def test_autograde_assignment(browser, port, gradebook, rabbitmq_proc):
    utils._load_gradebook_page(browser, port, "manage_submissions/Problem Set 1")

    # click on the autograde button
    row = browser.find_elements_by_css_selector("tbody tr")[0]
    row.find_element_by_css_selector(".autograde a").click()
    utils._wait_for_element(browser, "success-modal")
    WebDriverWait(browser, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "#success-modal .close"))
    )
    utils._click_element(browser, "#success-modal .close")

    def modal_not_present(browser): return browser.execute_script(
        """return $("#success-modal").length === 0;"""
    )
    WebDriverWait(browser, 10).until(modal_not_present)
