import os
import shutil
from datetime import datetime as dt
from datetime import timedelta
from time import sleep

from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager

from .utils import Finder, Waiter, decode_credentials, retry


class XeroAutomator:
    def __init__(self, config):
        self.config = config
        if "XERO_CREDENTIALS" in self.config:
            creds = decode_credentials(self.config["XERO_CREDENTIALS"])
            self.config["XERO_EMAIL"] = creds["XERO_EMAIL"]
            self.config["XERO_PASSWORD"] = creds["XERO_PASSWORD"]

        chrome_driver_path = ChromeDriverManager().install()

        profile_path = os.path.join(os.getcwd(), "profile")
        if not os.path.exists(profile_path):
            # make a profile and move it from temp storage to the profile path
            options = ChromeOptions()
            options.add_argument("--headless")
            driver = webdriver.Chrome(service=Service(
                chrome_driver_path), options=options)
            current_profile_path = driver.capabilities['chrome']['userDataDir']

            print("Creating profile ...")
            try:
                shutil.copytree(current_profile_path, profile_path)
            except:
                pass
            driver.quit()

            shutdown_status_file = os.path.join(
                profile_path, "chrome_shutdown_ms.text")
            if os.path.exists(shutdown_status_file):
                with open(shutdown_status_file, 'w') as f:
                    f.write("187")

        options = ChromeOptions()
        options.add_argument(f"--user-data-dir={profile_path}")
        self.driver = webdriver.Chrome(service=Service(chrome_driver_path),
                                       options=options)

        self.wait = Waiter(self.driver)
        self.find = Finder(self.driver)

    def login(self):
        self.driver.get("https://login.xero.com/identity/user/login")

        # close any non-xero windows
        for handle in self.driver.window_handles:
            self.driver.switch_to.window(handle)
            if "xero" not in self.driver.current_url:
                self.driver.close()

        # fill form
        email_field = self.find.id("xl-form-email")
        password_field = self.find.id("xl-form-password")

        email_field.send_keys(self.config["XERO_EMAIL"])
        password_field.send_keys(self.config["XERO_PASSWORD"])

        # click login button
        login_button = self.find.id("xl-form-submit")
        login_button.click()

        # check for authenticator
        if '/login/two-factor' in self.driver.current_url:
            print("Authenticator time ...")

            remember_device_checkbox = self.wait.automation_id_clickable(
                'auth-remembermecheckbox--checkbox')
            remember_device_checkbox.click()

            auth_field = self.wait.automation_id_clickable(
                'auth-onetimepassword--input')
            auth_field.click()

            # wait until redirect
            self.wait.url_contains('https://go.xero.com', 60, 0.5)

    def go_to_time_entries(self):
        # click Projects
        projects_button = self.wait.data_name_clickable(
            "navigation-menu/projects")
        projects_button.click()

        # click Time entries
        time_entries_button = self.wait.data_name_clickable(
            "navigation-menu/projects/time-entries")
        time_entries_button.click()

    def time_entries_pick_date(self, date: str):
        assert '/projects/time-entries' in self.driver.current_url, "Not in time entries page!"

        # click out of the date picker in case it's open
        self.wait.xpath_clickable(
            '//*[@id="shell-app-root"]/header/div/div[1]').click()

        # open date picker
        date_range_button = self.wait.automation_id_clickable(
            'time-entry-date-range-dropdown-button')
        date_range_button.click()

        choose_date_button = self.wait.automation_id_clickable(
            'time-entry-date-range-datepicker-item--body')
        choose_date_button.click()

        # parse date
        ymd = dt.strptime(date, "%Y-%m-%d")
        y, m = str(ymd.year), ymd.strftime("%B")

        # select year
        year_selector = Select(self.find.automation_id(
            'time-entry-date-range-datepicker--yearselector'))
        year_selector.select_by_visible_text(y)

        # select month
        month_selector = Select(self.find.automation_id(
            'time-entry-date-range-datepicker--monthselector'))
        month_selector.select_by_visible_text(m)

        # select day
        day_options = (self.find.automation_id("time-entry-date-range-datepicker")
                       .find_elements(By.CSS_SELECTOR, ".xui-datepicker--day"))
        day_options_mapping = {d.find_element(By.TAG_NAME, 'time').get_attribute(
            'datetime'): d for d in day_options}

        day_options_mapping[date].click()

    def check_hours(self, date: str) -> str:
        assert '/projects/time-entries' in self.driver.current_url, "Not in time entries page!"

        ymd = dt.strptime(date, "%Y-%m-%d")
        day = f"{ymd.strftime('%a')} {str(ymd.day)}"

        self.time_entries_pick_date(date)

        sleep(0.5)  # otherwise time entries may not update

        # get weekdays
        weekdays = self.find.all_automation_id('time-entry-list-weekday-item')

        # find the right day to check
        for d in weekdays:
            if day in d.text:
                return d.text.replace(day, '').strip()

        return ""

    def new_time_entry(self, project: str, task: str, date: str, hours: int = 8):
        assert '/projects/time-entries' in self.driver.current_url, "Not in time entries page!"

        # parse date
        ymd = dt.strptime(date, "%Y-%m-%d")
        y, m = str(ymd.year), ymd.strftime("%B")

        # close the modal if it's already open
        try:
            self.find.automation_id('time-entry-modal-modal--close').click()
        except:
            pass

        # choose the date
        self.time_entries_pick_date(date)

        # press new time entry button
        new_time_entry_button = self.find.automation_id(
            'projects-button-add-time')
        new_time_entry_button.click()

        # choose project
        project_input = self.wait.automation_id_clickable(
            'time-entry-modal-project--input')
        project_input.click()
        project_input.send_keys(project)

        sleep(1)

        project_button = self.wait.automation_id_clickable(
            'autocompleter-option')
        project_button.click()

        # choose task
        task_input = self.wait.automation_id_clickable(
            'time-entry-modal-task-wrap--button')
        task_input.click()

        sleep(0.1)

        task_buttons = self.find.all_automation_id(
            'time-entry-modal-task-option')
        task_buttons_mapping = {t.text: t for t in task_buttons}
        task_buttons_mapping[task].click()

        # enter duration
        duration_input = self.wait.automation_id_clickable(
            'time-entry-modal-duration--input')
        duration_input.click()
        duration_input.send_keys(str(hours))

        # save
        save_button = self.wait.automation_id_clickable(
            'time-entry-modal-save-button-group-save-button')
        save_button.click()

        print("Success!")

    def new_time_entry_safe(self, project: str, task: str, date: str, hours: int = 8):
        # get current hours
        hours_curr = self.check_hours(date)
        if hours_curr != "0:00":
            print(f"Already have time entries for {date}: {hours_curr}")
        else:
            # try to add an 8 hour entry up to 3 times
            retry(self.new_time_entry, 3, project, task, date, hours)

    def eight_hours_today(self):
        # get today's date
        today = dt.today().strftime("%Y-%m-%d")
        project = self.config["DEFAULT_PROJECT"]
        task = self.config["DEFAULT_TASK"]

        self.new_time_entry_safe(project, task, today, 8)

    def fill_range(self, start: str, end: str):
        project = self.config["DEFAULT_PROJECT"]
        task = self.config["DEFAULT_TASK"]

        # parse date
        start_ymd = dt.strptime(start, "%Y-%m-%d")
        end_ymd = dt.strptime(end, "%Y-%m-%d")
        

        delta = end_ymd - start_ymd

        for d in range(delta.days + 1):
            curr_date = start_ymd + timedelta(d)
            if curr_date.weekday() < 5:
                self.new_time_entry_safe(project, task, curr_date.strftime("%Y-%m-%d"), 8)

    def __del__(self):
        self.driver.quit()
