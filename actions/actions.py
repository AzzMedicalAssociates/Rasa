# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List, Union, Optional
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
from selenium.webdriver.support.select import Select
import re
from selenium.webdriver.chrome.service import Service
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.events import SlotSet, AllSlotsReset
from rasa_sdk.executor import CollectingDispatcher


class ActionAskId(Action):
    def name(self) -> Text:
        return "action_ask_id"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(template="utter_ask_id")
        return []


class ActionMakeEncounterForScp(Action):
    def name(self) -> Text:
        return "action_make_encounter_for_scp"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        patient_id = tracker.get_slot("id")
        date_1 = tracker.get_slot("date")

        # details = tracker.get_slot("details")
        #
        # if details:
        #     for detail in details:
        #         print("Detail:", detail)
        #         # Perform actions with each detail
        # else:
        #     print("No details found")

        ########################### SCRIPT #########################

        class ReadingsExtraction:
            def __init__(self, webdriver_path, date_1):
                self.webdriver_path = webdriver_path
                self.date_1 = date_1
                self.options = Options()
                self.options.add_argument("--headless")
                self.driver_service = Service(self.webdriver_path)
                self.driver = webdriver.Chrome(service=self.driver_service, options=self.options)

            readings_data = []
            not_readings_data = []
            final_name = ""
            systolic_average = ""
            diastolic_average = ""
            pulse_average = ""
            total_time = ""
            sorted_data = ""

            def start_request(self, url):
                self.driver.get(url)
                self.login()

            def login(self):

                print("Patient ID from User prompt:", patient_id)
                username = self.driver.find_element(By.NAME, "username")
                username.send_keys("sheherbano.azz@gmail.com")
                password = self.driver.find_element(By.NAME, "password")
                password.send_keys("Azzmedassistb1!#")
                button = self.driver.find_element(By.ID, "login-btn")
                button.click()
                time.sleep(3)
                self.after_login(patient_id)

            def after_login(self, patient_id_scp):
                url = f"https://portal.smartmeterrpm.com/patient/weights-vitals/edit/{patient_id_scp}"

                self.driver.get(url)
                time.sleep(5)
                select_element = self.driver.find_element(By.ID, "reading_type")
                option_elements = select_element.find_element(By.TAG_NAME, "option")

                flag = option_elements.get_attribute("label")
                print("Value of the first option:", flag)

                if flag == "Blood Glucose - Time Period" or flag == "Blood Glucose":
                    # print("Glucometer-Charting")
                    dispatcher.utter_message(text="Glucometer-Charting")

                    time.sleep(5)
                    self.extract_reading_for_blood_glucose()
                    average = str(self.get_average_for_blood_glucose())

                    total_time = 60 - len(self.readings_data)
                    if len(self.readings_data) <= 5:
                        total_time = 30
                        for item in self.not_readings_data:
                            item["Date"] = item["Date"].replace("(2 min)", "(1 min)")

                    total_list = self.readings_data + self.not_readings_data
                    sorted_data = sorted(total_list, key=lambda x: x['Date'])

                    if total_list:
                        # print("Charting Created Successfully!")
                        dispatcher.utter_message(text="Charting Created Successfully!\n")

                    if len(self.readings_data) >= 10 and len(self.readings_data) < 16:
                        message = "Please Ask your patient to take readings regularly!"
                        # print(message)
                        dispatcher.utter_message(text=message)

                    # print(f"Total Readings: {len(self.readings_data)}")
                    # print(f"Average Reading: {average}")
                    # print(f"Documentation Time: {total_time} minutes\n")
                    dispatcher.utter_message(text=f"Total Readings: {len(self.readings_data)}")
                    dispatcher.utter_message(text=f"Average Reading: {average}")
                    dispatcher.utter_message(text=f"Documentation Time: {total_time} minutes\n")

                    for item in sorted_data:
                        print(f"{item['Date']}")
                        if item['Glucose_Reading'] == "No Reading Checked twice":
                            # print(f"{item['Glucose_Reading']}")
                            dispatcher.utter_message(text=f"{item['Glucose_Reading']}")
                        else:
                            # print(f"{item['Glucose_Reading']}mg/dL")
                            dispatcher.utter_message(text=f"{item['Glucose_Reading']}mg/dL")

                elif flag == "Blood Pressure":
                    # print("Blood-Pressure-Charting")
                    dispatcher.utter_message(text="Blood-Pressure-Charting")

                    time.sleep(5)
                    self.extract_reading_for_blood_pressure()

                    systolic_average = self.get_average_systolic_for_blood_pressure()
                    diastolic_average = self.get_average_diastolic_for_blood_pressure()
                    pulse_average = self.get_average_pulse_for_blood_pressure()

                    total_time = 60 - len(self.readings_data)

                    if len(self.readings_data) <= 5:
                        total_time = 30
                        for item in self.not_readings_data:
                            item["Date"] = item["Date"].replace("(2 min)", "(1 min)")

                    total_list = self.readings_data + self.not_readings_data

                    if total_list:
                        print("Charting Created Successfully!")
                        dispatcher.utter_message(text="Charting Created Successfully!\n")

                    sorted_data = sorted(total_list, key=lambda x: datetime.strptime(x["Date"], '%m/%d/%Y (%M min)'))
                    # print(f"sorted_data : {sorted_data}")

                    final_name = self.final_name

                    # print(f"Total Readings: {len(self.readings_data)}")
                    # print(f"Average systolic: {systolic_average}")
                    # print(f"Average diastolic: {diastolic_average}")
                    # print(f"Average pulse: {pulse_average}")
                    # print(f"Documentation Time: {total_time} minutes\n")
                    dispatcher.utter_message(text=f"Total Readings: {len(self.readings_data)}")
                    dispatcher.utter_message(text=f"Average systolic: {systolic_average}")
                    dispatcher.utter_message(text=f"Average diastolic: {diastolic_average}")
                    dispatcher.utter_message(text=f"Average pulse: {pulse_average}")
                    dispatcher.utter_message(text=f"Documentation Time: {total_time} minutes\n")

                    for item in sorted_data:
                        print(f"{item['Date']}")
                        if item['bp'] == "No Reading Checked twice":
                            # print(f"{item['bp']}")
                            dispatcher.utter_message(text=f"{item['bp']}")

                        else:
                            # print(f"{item['bp']} mmHg")
                            dispatcher.utter_message(text=f"{item['bp']} mmHg")

                        if 'pulse' in item:
                            # print(f"{item['pulse']} bpm")
                            dispatcher.utter_message(text=f"{item['pulse']} bpm")

                    if total_list:
                        # self.write_to_file(sorted_data, systolic_average, diastolic_average, pulse_average, final_name,
                        #                    total_time)
                        # print(f"Charting Created Successfully of patient **{final_name}**")
                        dispatcher.utter_message(text=f"Charting Created Successfully of patient **{final_name}**")

                    self.readings_data = []
                    self.not_readings_data = []
                    self.final_name = ""
                    time.sleep(5)

                elif flag == "Weight":
                    print("Weight-Charting")
                    dispatcher.utter_message(text="Weight-Charting")

                    time.sleep(5)
                    self.extract_reading_for_weight()
                    average = str(self.get_average_for_weight())

                    total_time = 60 - len(self.readings_data)
                    if len(self.readings_data) <= 5:
                        total_time = 30
                        for item in self.not_readings_data:
                            item["Date"] = item["Date"].replace("(2 min)", "(1 min)")

                    total_list = self.readings_data + self.not_readings_data
                    sorted_data = sorted(total_list, key=lambda x: x['Date'])

                    if total_list:
                        print("Charting Created Successfully!")
                        dispatcher.utter_message(text="Charting Created Successfully!\n")

                    if len(self.readings_data) >= 10 and len(self.readings_data) < 16:
                        message = "Please Ask your patient to take readings regularly!"
                        # print(message)
                        dispatcher.utter_message(text=message)

                    # print(f"Total Readings: {len(self.readings_data)}")
                    # print(f"Average Reading: {average}")
                    # print(f"Documentation Time: {total_time}\n minutes")
                    dispatcher.utter_message(text=f"Total Readings: {len(self.readings_data)}")
                    dispatcher.utter_message(text=f"Average Reading: {average}")
                    dispatcher.utter_message(text=f"Documentation Time: {total_time}\n minutes")

                    for item in sorted_data:
                        print(f"{item['Date']}")
                        if item['Weight_(lbs)'] == "No Reading Checked twice":
                            print(f"{item['Weight_(lbs)']}")
                            dispatcher.utter_message(text=f"\n{item['Weight_(lbs)']}")

                        else:
                            print(f"{item['Weight_(lbs)']}lbs")
                            dispatcher.utter_message(text=f"{item['Weight_(lbs)']}lbs")

            def get_average_for_weight(self):
                if len(self.readings_data) == 0:
                    return 0
                sum = 0
                for i in self.readings_data:
                    sum += float(i["Weight_(lbs)"])
                average_reading = sum // len(self.readings_data)
                avg = str(average_reading) + "lbs"
                return avg

            def get_dates_for_weight(self):
                current_date = self.date_1
                date_format = "%Y-%m-%d"
                start_date = datetime.strptime(current_date, date_format)
                last_date = start_date + timedelta(days=30)

                dates = []
                while start_date < last_date:
                    formatted_date = start_date.strftime("%m/%d/%Y")
                    dates.append(formatted_date)
                    start_date += timedelta(days=1)

                return dates, current_date, last_date.strftime("%Y-%m-%d")

            def extract_reading_for_weight(self):
                dates, start_date, end_date = self.get_dates_for_weight()
                try:
                    select = Select(self.driver.find_element(By.NAME, "select-graph"))
                    select.select_by_value("weight")
                    button = self.driver.find_element(By.ID, "search")
                    button.click()
                    time.sleep(5)
                    self.driver.implicitly_wait(20)
                    start_date_field = self.driver.find_element(By.ID, "start-date")
                    end_date_field = self.driver.find_element(By.ID, "end-date")

                    start_date_field.click()
                    start_date_field.clear()
                    start_date_field.send_keys(start_date)
                    end_date_field.click()
                    end_date_field.clear()
                    end_date_field.send_keys(end_date)

                    button.click()
                    time.sleep(5)

                    soup = BeautifulSoup(self.driver.page_source, "html.parser")
                    for date in dates:
                        date_column = soup.find("td", string=date)
                        if date_column:
                            weight_reading = self.driver.find_element(By.XPATH,
                                                                      f'//tr[contains(., "{date}")]//following-sibling::tr/td[@class="text-center"]').text
                            patient_reading = {
                                "Date": date + " " + "(1 min)",
                                "Weight_(lbs)": weight_reading
                            }
                            self.readings_data.append(patient_reading)
                        else:
                            patient_reading = {
                                "Date": date + " " + "(2 min)",
                                "Weight_(lbs)": "No Reading Checked twice"
                            }
                            self.not_readings_data.append(patient_reading)
                except Exception:
                    message = "Exception"
                    title = "Please check your connection and try again."
                    # easygui.msgbox(message, title)
                    dispatcher.utter_message(text=message)
                    dispatcher.utter_message(text=title)

            ##################################
            def get_average_for_blood_glucose(self):
                if len(self.readings_data) == 0:
                    return 0
                sum = 0
                for i in self.readings_data:
                    sum += int(i["Glucose_Reading"])
                average_reading = sum // len(self.readings_data)
                avg = str(average_reading) + " " + "mg/dl"
                return avg

            def get_dates_for_blood_glucose(self):
                current_date = self.date_1
                date_format = "%Y-%m-%d"
                start_date = datetime.strptime(current_date, date_format)
                last_date = start_date + timedelta(days=30)

                dates = []
                while start_date < last_date:
                    formatted_date = start_date.strftime("%m/%d/%Y")
                    dates.append(formatted_date)
                    start_date += timedelta(days=1)

                return dates, current_date, last_date.strftime("%Y-%m-%d")

            def extract_reading_for_blood_glucose(self):
                dates, start_date, end_date = self.get_dates_for_blood_glucose()
                try:
                    select = Select(self.driver.find_element(By.NAME, "select-graph"))
                    select.select_by_value("blood_glucose")
                    button = self.driver.find_element(By.ID, "search")
                    button.click()
                    time.sleep(5)
                    self.driver.implicitly_wait(20)
                    start_date_field = self.driver.find_element(By.ID, "start-date")
                    end_date_field = self.driver.find_element(By.ID, "end-date")

                    start_date_field.click()
                    start_date_field.clear()
                    start_date_field.send_keys(start_date)

                    end_date_field.click()
                    end_date_field.clear()
                    end_date_field.send_keys(end_date)

                    button.click()
                    time.sleep(5)

                    soup = BeautifulSoup(self.driver.page_source, "html.parser")
                    for date in dates:
                        date_column = soup.find("td", string=date)
                        if date_column:
                            glucose_reading = self.driver.find_element(By.XPATH,
                                                                       f'//tr[contains(., "{date}")]//following-sibling::tr/td[@class="text-center"]').text
                            patient_reading = {
                                "Date": date + " " + "(1 min)",
                                "Glucose_Reading": glucose_reading
                            }
                            self.readings_data.append(patient_reading)
                        else:
                            patient_reading = {
                                "Date": date + " " + "(2 min)",
                                "Glucose_Reading": "No Reading Checked twice"
                            }
                            self.not_readings_data.append(patient_reading)
                except Exception:
                    message = "Exception"
                    title = "Please check your connection and try again."
                    dispatcher.utter_message(text=message)
                    dispatcher.utter_message(text=title)
                    # easygui.msgbox(message, title)

            ##################################

            def get_average_systolic_for_blood_pressure(self):
                if len(self.readings_data) == 0:
                    return 0
                sum = 0
                for i in self.readings_data:
                    sum += int(i["systolic"])
                average_reading = sum // len(self.readings_data)
                avg = str(average_reading) + " " + "mmHg"
                return avg

            def get_average_diastolic_for_blood_pressure(self):
                if len(self.readings_data) == 0:
                    return 0
                sum = 0
                for i in self.readings_data:
                    sum += int(i["diastolic"])
                average_reading = sum // len(self.readings_data)
                avg = str(average_reading) + " " + "mmHg"
                return avg

            def get_average_pulse_for_blood_pressure(self):
                if len(self.readings_data) == 0:
                    return 0
                sum = 0
                for i in self.readings_data:
                    sum += int(i["pulse"])
                average_reading = sum // len(self.readings_data)
                avg = str(average_reading) + " " + "bpm"
                return avg

            def get_dates_for_blood_pressure(self):
                current_date = self.date_1
                print(current_date)
                date_format = "%Y-%m-%d"
                start_date = datetime.strptime(current_date, date_format)
                last_date = start_date + timedelta(days=30)

                dates = []
                while start_date < last_date:
                    formatted_date = start_date.strftime("%m/%d/%Y")
                    dates.append(formatted_date)
                    start_date += timedelta(days=1)

                return dates, current_date, last_date.strftime("%Y-%m-%d")

            def extract_reading_for_blood_pressure(self):
                dates, start_date, end_date = self.get_dates_for_blood_pressure()
                try:

                    select = Select(self.driver.find_element(By.NAME, "select-graph"))

                    select.select_by_value("blood_pressure")
                    button = self.driver.find_element(By.ID, "search")
                    button.click()
                    time.sleep(5)
                    self.driver.implicitly_wait(20)
                    start_date_field = self.driver.find_element(By.ID, "start-date")
                    end_date_field = self.driver.find_element(By.ID, "end-date")

                    start_date_field.click()
                    start_date_field.clear()
                    start_date_field.send_keys(start_date)

                    end_date_field.click()
                    end_date_field.clear()
                    end_date_field.send_keys(end_date)

                    button.click()
                    time.sleep(5)

                    soup = BeautifulSoup(self.driver.page_source, "html.parser")

                    name = soup.find('h1', class_='h2 mb-4 text-gray-800 text-center')

                    self.final_name = name.text.strip()

                    for date in dates:
                        date_column = soup.find("td", string=date)
                        # print(f"date Column {date_column}")
                        if date_column:
                            reading = self.driver.find_elements(By.XPATH,
                                                                f'//tr[contains(., "{date}")]//following-sibling::tr/td[@class="text-center"]')
                            if len(reading) >= 2:
                                systolic = reading[0].text
                                diastolic = reading[1].text
                                pulse = reading[2].text
                                bp_reading = f"{systolic}/{diastolic}"
                                patient_reading = {
                                    "Date": date + " " + "(1 min)",
                                    "bp": bp_reading,
                                    "systolic": systolic,
                                    "diastolic": diastolic,
                                    "pulse": pulse
                                }
                                self.readings_data.append(patient_reading)
                        else:
                            patient_reading = {
                                "Date": date + " " + "(2 min)",
                                "bp": "No Reading Checked twice",
                            }
                            self.not_readings_data.append(patient_reading)
                except Exception:
                    message = "Exception"
                    title = "Please check your connection and try again."
                    dispatcher.utter_message(text=message)
                    dispatcher.utter_message(text=title)
        driver_path = "/app/actions/chromedriver"
        # date_1 = get_valid_date()
        x = ReadingsExtraction(driver_path, date_1)
        x.start_request("https://portal.smartmeterrpm.com/login")

        ############################################################

        return []


class ValidateIdForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_id_form"

    def validate_id(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[str, Any]
    ) -> Union[Dict[str, Optional[Any]], Dict[str, str]]:
        if slot_value is None:
            return {"id": None}

        if len(slot_value) != 7:
            dispatcher.utter_message(text="Invalid Id length. Please enter a 7-digit Id.")
            return {"id": None}
        if not re.match(r"^[0-9]+$", slot_value):
            dispatcher.utter_message(text="Invalid Id. Id only contain numeric values.")
            return {"id": None}

        return {"id": slot_value}

    def validate_date(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[str, Any]
    ) -> Union[Dict[str, Optional[Any]], Dict[str, str]]:
        if slot_value is None:
            return {"date": None}

        date_pattern = r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$"
        if not re.match(date_pattern, slot_value):
            dispatcher.utter_message(
                text="Invalid date format. Please enter the date in the format yyyy-mm-dd."
            )
            return {"date": None}

        return {"date": slot_value}


class ActionResetAllSlots(Action):

    def name(self):
        return "action_reset_all_slots"

    def run(self, dispatcher, tracker, domain):
        return [AllSlotsReset()]

# dispatcher.utter_message(template="utter_script_response", response=response)
