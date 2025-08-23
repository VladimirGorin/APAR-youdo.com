from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

from utils import create_browser, save_json
from logs import Logger

from datetime import datetime, timedelta

import config.settings as SETTINGS

import e_types
import time
import random
import re
import os


class BrowserAutomation:
    def __init__(self):
        self.browser = None
        self.logger = Logger()
        self.auth_status = False
        self.filters_active = False
        self.categories_active = False
        self.monitoring_settings = {
            "first_time_launch": True,
            "filtered_tasks": [],
            "stats": SETTINGS.STATS,
            "tasks_file": "./data/monitoring_tasks.json",
            "stats_file": "./data/stats.json"
        }

    def start_browser(self):
        """Initializes the browser and opens the main site."""
        self.browser = create_browser()
        self.browser.get(SETTINGS.MAIN_SITES[0])

    def close_browser(self):
        """Closes the browser if it's open."""
        if self.browser:
            self.browser.quit()

    def check_login(self):
        """Checks if the user is logged in and handles login if necessary."""
        login_button = self.browser.find_elements(
            By.CSS_SELECTOR,
            f"[{e_types.LOGIN_SPAN_CUSTOM[0]}='{e_types.LOGIN_SPAN_CUSTOM[2]}']"
        )

        if login_button:
            self.handle_login()
        else:
            self.auth_status = True
            self.filters_active = True
            self.categories_active = True
            self.logger.info("Your session is active!")

    def handle_login(self):
        """Prompts the user to log in manually and updates the authentication status."""
        self.auth_status = False
        self.filters_active = False
        self.categories_active = False

        self.logger.info("You need to log in.")
        input("\nPlease press ENTER when you finish the login: \n")
        self.logger.info("Thanks! Saving the session.")
        self.auth_status = True

    def apply_filters(self):
        """Applies filters to the tasks on the page."""
        try:
            self.logger.info("Setting up filters")
            time.sleep(2)

            filters_elements = self.browser.find_elements(
                By.CSS_SELECTOR, f"[{e_types.FILTERS_DIV_FILTERS_BUTTON_CLASS[0]}*='{e_types.FILTERS_DIV_FILTERS_BUTTON_CLASS[2]}']"
            )

            if len(filters_elements) == 2:
                filters_popup_button = filters_elements[-1]
                self.browser.execute_script(
                    "arguments[0].scrollIntoView({block: 'center'});", filters_popup_button)

                time.sleep(2)
                filters_popup_button.click()

                time.sleep(2)

                filters_search_radius_select = self.browser.find_elements(
                    By.CLASS_NAME, f"{e_types.FILTERS_DIV_RADIUS_SELECT_CLASS[2]}"
                )

                if not filters_search_radius_select:
                    raise Exception("Filters search radius select not found")

                if len(filters_search_radius_select) > 1:
                    raise Exception(
                        f"Filters search radius select found more than one: {len(filters_search_radius_select)}"
                    )

                time.sleep(2)

                filters_search_radius_select = filters_search_radius_select[0]
                filters_search_radius_select.click()

                time.sleep(2)

                filters_search_radius_select_menu = self.browser.find_element(
                    By.CLASS_NAME, f"{e_types.FILTERS_DIV_MENU_CLASS[2]}"
                )

                filters_search_radius_select_menu_children = filters_search_radius_select_menu.find_elements(
                    By.XPATH, ".//*"
                )

                found_filters_search_radius_menu_children = False

                for child in filters_search_radius_select_menu_children:
                    children_id = child.get_attribute("id")
                    if children_id == e_types.FILTERS_DIV_MENU_FIRST_ITEM_ID[2]:
                        child.click()
                        found_filters_search_radius_menu_children = True
                        break

                if not found_filters_search_radius_menu_children:
                    raise Exception(
                        "Can't find the first item of the radius select menu"
                    )

                time.sleep(2)

                filters_actions = self.browser.find_elements(
                    By.CSS_SELECTOR,
                    f"{e_types.FILTERS_DIV_ACTIONS_CLASS[1]}[{e_types.FILTERS_DIV_ACTIONS_CLASS[0]}*='{e_types.FILTERS_DIV_ACTIONS_CLASS[2]}']"
                )

                if not filters_actions:
                    raise Exception("Filters actions not found")

                if len(filters_actions) > 1:
                    raise Exception(
                        f"Filters actions found more than one: {len(filters_actions)}"
                    )

                filters_actions = filters_actions[0]

                try:
                    filters_submit_button = filters_actions.find_element(
                        By.CSS_SELECTOR, f"{e_types.FILTERS_BUTTON_SUBMIT_CLASS[1]}[{e_types.FILTERS_BUTTON_SUBMIT_CLASS[0]}*='{e_types.FILTERS_BUTTON_SUBMIT_CLASS[2]}']"
                    )

                    filters_submit_button.click()
                    time.sleep(2)

                except Exception as filters_submit_button_e:
                    raise Exception(
                        f"Error trying to click on the filters submit button: {filters_submit_button_e}"
                    )

                self.filters_active = True
                self.logger.info("Filters are active!")
            else:
                raise Exception(
                    f"Filters button not found, expected 2 but found: {len(filters_elements)}"
                )

        except Exception as filter_e:
            self.logger.error(filter_e)

    def apply_categories(self):
        """Applies categories to the tasks."""
        try:
            self.logger.info("Setting up categories")
            time.sleep(2)
            self.browser.get(SETTINGS.MAIN_SITES[0] + "/profile/tariffs")
            time.sleep(5)

            # Get all tariffs info text
            tariffs_info = self.browser.find_elements(
                By.CSS_SELECTOR,
                f"{e_types.TARIFFS_DIV_CONTAINER_CLASS[1]}[{e_types.TARIFFS_DIV_CONTAINER_CLASS[0]}*='{e_types.TARIFFS_DIV_CONTAINER_CLASS[2]}'] {e_types.TARIFFS_DIV_TARIFF_TEXT_CLASS[1]}[{e_types.TARIFFS_DIV_TARIFF_TEXT_CLASS[0]}*='{e_types.TARIFFS_DIV_TARIFF_TEXT_CLASS[2]}']"
            )

            if not tariffs_info:
                raise Exception("Tariffs info not found")

            tariffs_texts = [el.text for el in tariffs_info]

            # tariffs_texts = ['Подключить тариф',
            #                  'Дизайн сайтов и приложений', 'Разработка ПО']

            self.logger.info(f"Tariffs found: {tariffs_texts}")

            time.sleep(2)
            self.browser.get(SETTINGS.MAIN_SITES[0] + "/tasks-all-opened-all")
            time.sleep(5)

            # Get categories
            categories_container = self.browser.find_element(
                By.CSS_SELECTOR, f"{e_types.CATEGORIES_UL_CONTAINER_CLASS[1]}[{e_types.CATEGORIES_UL_CONTAINER_CLASS[0]}*='{e_types.CATEGORIES_UL_CONTAINER_CLASS[2]}']"
            )

            categories_label_items = categories_container.find_elements(
                By.CSS_SELECTOR, f"{e_types.CATEGORY_LABEL_CLASS[1]}[{e_types.CATEGORY_LABEL_CLASS[0]}*='{e_types.CATEGORY_LABEL_CLASS[2]}']"
            )

            categories_items = categories_container.find_elements(
                By.CSS_SELECTOR, f"{e_types.CATEGORIES_LI_CATEGORY_CLASS[1]}[{e_types.CATEGORIES_LI_CATEGORY_CLASS[0]}*='{e_types.CATEGORIES_LI_CATEGORY_CLASS[2]}']"
            )

            if not categories_items:
                raise Exception("Categories items not found")

            if not categories_label_items:
                raise Exception("Categories label items not found")

            # Check if categories active
            all_categories_item = self.browser.find_element(
                By.CSS_SELECTOR,
                f"{e_types.ALL_CATEGORIES_LI_CLASS[1]}[{e_types.ALL_CATEGORIES_LI_CLASS[0]}*='{e_types.ALL_CATEGORIES_LI_CLASS[2]}']"
            )

            all_categories_label_el = all_categories_item.find_element(
                By.CSS_SELECTOR,
                f"{e_types.CATEGORY_LABEL_CLASS[1]}[{e_types.CATEGORY_LABEL_CLASS[0]}*='{e_types.CATEGORY_LABEL_CLASS[2]}']"
            )

            checkbox_input = all_categories_item.find_element(
                By.CSS_SELECTOR,
                f"{e_types.CATEGORIES_INPUT_CHECKBOX_TYPE[1]}[{e_types.CATEGORIES_INPUT_CHECKBOX_TYPE[0]}='{e_types.CATEGORIES_INPUT_CHECKBOX_TYPE[2]}']"
            )

            is_checked = checkbox_input.is_selected()

            if is_checked:
                all_categories_label_el.click()
            else:
                all_categories_label_el.click()
                time.sleep(1)
                all_categories_label_el.click()

            time.sleep(2)

            # Open all categories
            for category_item in categories_items:
                try:
                    category_arrows = category_item.find_elements(
                        By.CSS_SELECTOR, f"{e_types.CATEGORIES_LI_CATEGORY_ARROW_CLASS[1]}[{e_types.CATEGORIES_LI_CATEGORY_ARROW_CLASS[0]}*='{e_types.CATEGORIES_LI_CATEGORY_ARROW_CLASS[2]}']"
                    )

                    if category_arrows:
                        category_arrow = category_arrows[0]
                        arrow_classes = category_arrow.get_attribute(
                            "class")
                        if "Categories_opened" not in arrow_classes:
                            self.browser.execute_script(
                                "arguments[0].scrollIntoView({block: 'center'});", category_arrow)
                            time.sleep(1)
                            category_arrow.click()

                except Exception as category_e:
                    self.logger.error(
                        f"Error while processing category '{category_item.text.strip()}': {category_e}"
                    )

            time.sleep(2)
            # Find categories and subcategories matching tariffs
            for tariff_text in tariffs_texts:
                tariff_text = tariff_text.strip()

                for category_item in categories_label_items:
                    try:
                        category_text = category_item.text.strip()

                        if category_text == tariff_text:
                            self.browser.execute_script(
                                "arguments[0].scrollIntoView({block: 'center'});", category_item
                            )
                            time.sleep(2)

                            category_item.click()
                            self.logger.info(
                                f"Category '{category_text}' activated (matched tariff)"
                            )
                            time.sleep(2)
                            break

                    except Exception as category_e:
                        self.logger.error(
                            f"Error while processing category '{category_item.text.strip()}': {category_e}"
                        )

            self.categories_active = True
            self.logger.info("Categories are active!")

            time.sleep(5)

        except Exception as category_e:
            self.logger.error(category_e)

    def get_element_by_css_selector(self, find_type="element", where=None, element_data=None):
        """Finds an element or elements by CSS selector."""
        if where is None:
            raise Exception(f"'where' can't be {where}")

        if element_data is None:
            raise Exception(f"'element_data' can't be {element_data}")

        if len(element_data) < 3:
            raise Exception(
                f"Element data must have at least 3 items: {element_data}"
            )

        try:
            if find_type == "element":
                data = where.find_element(
                    By.CSS_SELECTOR, f"{element_data[1]}[{element_data[0]}*='{element_data[2]}']"
                )
            elif find_type == "elements":
                data = where.find_elements(
                    By.CSS_SELECTOR, f"{element_data[1]}[{element_data[0]}*='{element_data[2]}']"
                )
        except NoSuchElementException:
            return False

        return data

    def save_html_with_timestamp(self):
        """Saves the current page source with a timestamp."""
        os.makedirs('./errored_pages', exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"page_{timestamp}.html"
        filepath = os.path.join('./errored_pages', filename)

        page_source = self.browser.page_source

        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(page_source)

    def monitoring_tasks(self):
        """Monitors and processes tasks."""
        try:
            def get_template_by_title(title: str) -> str:
                title_lower = title.lower()
                for template in SETTINGS.RESPONSE_TEMPLATES:
                    for template_name, keywords in template.items():
                        for keyword in keywords:
                            if keyword.lower() in title_lower:
                                return template_name
                return SETTINGS.BASE_TEMPLATE_NAME

            def generate_random_time(from_, to_):
                """Generates a random time within the given range."""
                return random.randrange(from_, to_)

            def launch_tasks():
                """Launches the tasks."""
                try:
                    all_tasks = self.monitoring_settings["filtered_tasks"]

                    if not all_tasks:
                        time_to_sleep = generate_random_time(60, 600)
                        self.logger.info(
                            f"No tasks to launch, sleeping for: {time_to_sleep + 5} seconds"
                        )
                        time.sleep(time_to_sleep)

                    for task in all_tasks:
                        try:
                            time.sleep(5)

                            def find_add_order_button():
                                buttons_value_format = e_types.TASK_BUTTON_ADD_OFFER_CUSTOM[2]

                                for id, button_value in enumerate(buttons_value_format):
                                    add_offer_button = self.browser.find_elements(
                                        By.XPATH, f"//*[@data-test='{button_value}']"
                                    )

                                    if add_offer_button:
                                        add_offer_button = add_offer_button[0]
                                        break

                                    if id+1 >= len(buttons_value_format):
                                        add_offer_button = None
                                        self.logger.info("Button not found")
                                        break

                                    if not len(add_offer_button):
                                        self.logger.info(
                                            f"Button type {button_value} not found, trying to search {buttons_value_format[id + 1]}")
                                return add_offer_button

                            if not isinstance(task, dict):
                                raise Exception(
                                    f"Task has to be an object, not: {type(task)}")

                            if "link" not in task:
                                raise Exception(f"Task link not found: {task}")

                            if "price" not in task:
                                raise Exception(
                                    f"Task price not found: {task}")

                            if "title" not in task:
                                raise Exception(
                                    f"Task title not found: {task}")

                            # Emulate user scroll
                            self.browser.get(task["link"])
                            time.sleep(2)
                            time_to_sleep = generate_random_time(10, 60)
                            self.browser.find_element(
                                By.TAG_NAME, 'body').send_keys(Keys.END)
                            time.sleep(5)
                            self.browser.find_element(
                                By.TAG_NAME, 'body').send_keys(Keys.HOME)

                            self.logger.info(
                                f"[{task['link']}] Sleeping before start: {time_to_sleep} sec"
                            )
                            time.sleep(time_to_sleep)

                            # Click on the add offer button
                            add_offer_button = find_add_order_button()

                            if add_offer_button:
                                add_offer_button.click()
                            else:

                                self.save_html_with_timestamp()

                                raise Exception(
                                    "The add offer button is not found")

                            time.sleep(2)

                            # Set price
                            price_wrapper = self.get_element_by_css_selector(
                                find_type="elements", where=self.browser, element_data=e_types.TASK_DIV_PRICE_WRAPPER_CLASS
                            )

                            # Price filter
                            try:

                                task_price = int(task["price"])
                            except Exception:
                                raise Exception(
                                    "Can't parse the task price at number")

                            if task_price <= 10000:
                                task_price += 5000
                            elif task_price > 10000:
                                task_price += 7000

                            for block in price_wrapper:
                                try:
                                    price_input = block.find_element(
                                        By.TAG_NAME, 'input')
                                    price_input.send_keys(task_price)
                                    break
                                except NoSuchElementException:
                                    continue

                            time.sleep(2)

                            # Select the template by title
                            text_templates = self.get_element_by_css_selector(
                                where=self.browser, element_data=e_types.TASK_DIV_TEXT_TEMPLATES_CLASS
                            )

                            try:
                                text_templates.click()
                            except Exception as text_templates_e:
                                self.logger.error(
                                    f"Error trying to click on the text templates: {text_templates_e}")
                                raise Exception(
                                    "Can't click on the text templates")

                            time.sleep(2)

                            text_templates_dropdown = self.get_element_by_css_selector(
                                where=self.browser, element_data=e_types.TASK_DIV_TEXT_TEMPLATES_DROPDOWN_CLASS
                            )
                            text_templates_dropdown = self.get_element_by_css_selector(
                                find_type="elements", where=self.browser, element_data=e_types.TASK_DIV_TEMPLATE_CLASS
                            )

                            if not text_templates_dropdown:
                                raise Exception(
                                    f"Text templates list is empty: {text_templates_dropdown}")

                            time.sleep(2)

                            template_name_by_title = get_template_by_title(
                                task["title"]
                            )

                            templates_texts = [
                                {"text": el.text, "id": el_index}
                                for el_index, el in enumerate(text_templates_dropdown)
                            ]

                            if not templates_texts:
                                raise Exception(
                                    "Text templates list is empty, can't select a template")

                            find_template = False
                            for template in templates_texts:
                                if template["text"] == template_name_by_title:
                                    text_templates_dropdown[template["id"]].click(
                                    )
                                    find_template = True
                                    break

                            if not find_template:
                                raise Exception(
                                    f"Template with title '{template_name_by_title}' not found in the dropdown"
                                )

                            time.sleep(2)

                            # Press the submit button
                            dialog_popup = self.browser.find_element(
                                By.ID, e_types.TASK_DIV_DIALOG_POPUP_ID[2]
                            )
                            task_submit_button = self.get_element_by_css_selector(
                                where=dialog_popup, element_data=e_types.TASK_BUTTON_SUBMIT_CLASS
                            )
                            task_submit_button.click()

                            self.adding_stat(task_link=task["link"],
                                             task_title=task["title"])

                            time.sleep(2)

                        except Exception as launch_task_e:
                            self.logger.error(
                                f"Error in task processing (CONTINUE): {launch_task_e}"
                            )

                except Exception as launch_tasks_e:
                    self.logger.error(
                        f"Error in launching tasks: {launch_tasks_e}"
                    )

            def get_tasks(all_tasks):
                """Extracts tasks from the page and filters them."""
                filtered_tasks = []

                for task in all_tasks:
                    if task.tag_name == "li":
                        task_class = task.get_attribute("class")
                        contains_unviewed = e_types.TASKS_LI_TASK_UN_VIEWED_CLASS[2] in task_class
                        contains_banner = e_types.TASKS_LI_TASK_BANNER_CLASS[2] in task_class

                        if not contains_unviewed and not contains_banner:
                            try:
                                task_link = self.get_element_by_css_selector(
                                    where=task, element_data=e_types.TASKS_A_TASK_TITLE_CLASS
                                )

                                task_price = self.get_element_by_css_selector(
                                    find_type="elements", where=task, element_data=e_types.TASKS_DIV_TASK_PRICE_CLASS
                                )

                                if not task_link:
                                    self.logger.error(
                                        f"Some task ignored! ({task.tag_name}:{task.get_attribute('class')})"
                                    )
                                    continue

                                if not task_price:
                                    self.logger.error(
                                        f"Task price is missing. Some task ignored! ({task.tag_name}:{task.get_attribute('class')})"
                                    )
                                    continue

                                if len(task_price) != 2:
                                    self.logger.error(
                                        f"Task price is not as expected (2). Some task ignored! ({task.tag_name}:{task.get_attribute('class')})"
                                    )
                                    continue

                                task_title = task_link.text
                                task_link = task_link.get_attribute("href")
                                task_price = re.sub(
                                    r'\D', '', task_price[1].text)

                                contains_ban_word = any(
                                    word in task_title for word in SETTINGS.BAN_WORDS
                                )

                                if contains_ban_word:
                                    continue

                                filtered_tasks.append(
                                    {"title": task_title, "link": task_link,
                                        "price": task_price}
                                )
                            except Exception as task_e:
                                self.logger.error(
                                    f"Error while trying to get task data (CONTINUE): {task_e}"
                                )

                self.monitoring_settings["filtered_tasks"] = filtered_tasks
                save_json(data=filtered_tasks,
                          filename=self.monitoring_settings["tasks_file"])

            def scroll_tasks():
                """Scrolls down and clicks the 'Show More' button to load more tasks."""
                self.browser.find_element(
                    By.TAG_NAME, 'body').send_keys(Keys.END)
                time.sleep(2)
                show_more_button = self.get_element_by_css_selector(
                    where=self.browser, element_data=e_types.TASKS_BUTTON_SHOW_MORE_CLASS
                )
                if show_more_button:
                    show_more_button.click()
                else:
                    self.logger.info("No 'Show More' button found")
                time.sleep(2)

            time.sleep(5)

            if self.monitoring_settings["first_time_launch"]:
                while self.get_element_by_css_selector(
                    where=self.browser, element_data=e_types.TASKS_BUTTON_SHOW_MORE_CLASS
                ):
                    scroll_tasks()

                all_tasks = self.get_element_by_css_selector(
                    find_type="elements", where=self.browser, element_data=e_types.TASKS_LI_TASK_CLASS
                )

                get_tasks(all_tasks)
                launch_tasks()

                self.monitoring_settings["first_time_launch"] = False
            else:
                all_tasks = self.get_element_by_css_selector(
                    find_type="elements", where=self.browser, element_data=e_types.TASKS_LI_TASK_CLASS
                )

                get_tasks(all_tasks)
                launch_tasks()

            time.sleep(5)
            self.browser.get(SETTINGS.MAIN_SITES[0] + "/tasks-all-opened-all")

        except Exception as monitoring_e:
            self.logger.error(f"Error in monitoring process: {monitoring_e}")

    def adding_stat(self, task_title="", task_link=""):
        """Adds statistics to the stats file."""
        try:

            stat_data = {
                "date": datetime.now(SETTINGS.TIME_ZONE).strftime('%Y-%m-%d %H:%M:%S'),
                "responded": True,
                "task": {
                    "title": task_title,
                    "link": task_link
                }
            }

            self.monitoring_settings["stats"].append(stat_data)
            self.logger.info(f"Adding stat: {stat_data}")

            save_json(data=self.monitoring_settings["stats"],
                      filename=self.monitoring_settings["stats_file"])

        except Exception as e:
            self.logger.error(f"Error writing stats file: {e}")

    def run(self):
        """Main method to start the automation process."""
        try:
            def check_day_allowed():
                today = datetime.now(SETTINGS.TIME_ZONE).weekday()
                return SETTINGS.ACTIVE_DAYS.get(today, False)

            def check_moscow_time():
                current_time = datetime.now(SETTINGS.TIME_ZONE)

                start_time = current_time.replace(
                    hour=SETTINGS.ACTIVE_TIME[0], minute=0, second=0, microsecond=0)
                end_time = current_time.replace(
                    hour=SETTINGS.ACTIVE_TIME[1], minute=0, second=0, microsecond=0)

                if not check_day_allowed():
                    # if the day is not allowed — sleep until tomorrow 00:01
                    next_day = (current_time + timedelta(days=1)).replace(
                        hour=0, minute=1, second=0, microsecond=0
                    )
                    time_to_sleep = (next_day - current_time).total_seconds()
                    self.logger.info(
                        f"Today ({current_time.strftime('%A')}) is a non-working day, sleeping for {time_to_sleep} seconds.")
                    time.sleep(time_to_sleep)
                    return

                if start_time <= current_time < end_time:
                    self.logger.info(
                        f"Between {SETTINGS.ACTIVE_TIME[0]}:00 and {SETTINGS.ACTIVE_TIME[1]}:00 in {SETTINGS.TIME_ZONE}, continue processing.")
                else:
                    if current_time >= end_time:
                        # Calculate the time until 9:00 the next day
                        next_start_time = start_time + timedelta(days=1)
                    else:
                        # Calculate the time until 9:00 today
                        next_start_time = start_time

                    time_to_sleep = (next_start_time -
                                     current_time).total_seconds()
                    self.logger.info(
                        f"Outside of working hours, sleeping for {time_to_sleep} seconds.")
                    time.sleep(time_to_sleep)

            while True:
                try:
                    self.start_browser()
                    self.check_login()

                    time.sleep(5)
                    self.browser.get(
                        SETTINGS.MAIN_SITES[0] + "/tasks-all-opened-all")

                    if not self.categories_active:
                        self.apply_categories()

                    if not self.filters_active:
                        self.apply_filters()

                    self.logger.info("Setting up monitoring")
                    while True:
                        check_moscow_time()
                        self.monitoring_tasks()

                except Exception as e:
                    self.logger.error(e)
                    self.close_browser()
                    time.sleep(10)  # Wait before retrying

        except Exception as global_e:
            self.logger.error(global_e)
            self.close_browser()


if __name__ == "__main__":
    try:
        automation = BrowserAutomation()
        automation.run()
    except KeyboardInterrupt:
        print("\nBye Bye.")
