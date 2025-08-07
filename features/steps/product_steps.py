from behave import given, when, then
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

############################################
# Steps compartilhados
############################################

@given('the following products')
def step_impl(context):
    """Delete all products and load new ones"""
    context.execute_steps('''
        Given the following products
            | name       | description     | price   | available | category   |
            | Hat        | A red fedora    | 59.95   | True      | CLOTHS     |
            | Shoes      | Blue shoes      | 120.50  | False     | CLOTHS     |
            | Big Mac    | 1/4 lb burger   | 5.99    | True      | FOOD       |
            | Sheets     | Full bed sheets | 87.00   | True      | HOUSEWARES |
    ''')

@when('I visit the "Home Page"')
def step_impl(context):
    context.driver.get(context.base_url)
    WebDriverWait(context.driver, context.wait_seconds).until(
        EC.presence_of_element_located((By.ID, "name"))
    )

@when('I set the "{field}" to "{value}"')
def step_impl(context, field, value):
    element = context.driver.find_element(By.ID, field.lower())
    element.clear()
    element.send_keys(value)

@when('I select "{value}" in the "{field}" dropdown')
def step_impl(context, value, field):
    select = Select(context.driver.find_element(By.ID, field.lower()))
    select.select_by_visible_text(value)

@when('I press the "{button}" button')
def step_impl(context, button):
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        EC.element_to_be_clickable((By.ID, button.lower()))
    )
    element.click()

@then('I should see the message "{message}"')
def step_impl(context, message):
    WebDriverWait(context.driver, context.wait_seconds).until(
        EC.text_to_be_present_in_element((By.ID, "message"), message)
    )

############################################
# Steps específicos para atualização
############################################

@when('I change "{field}" to "{value}"')
def step_impl(context, field, value):
    element = context.driver.find_element(By.ID, field.lower())
    element.clear()
    element.send_keys(value)

@then('I should see "{text}" in the "{field}" field')
def step_impl(context, text, field):
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        EC.presence_of_element_located((By.ID, field.lower()))
    assert text in element.get_attribute('value')

############################################
# Steps específicos para exclusão
############################################

@then('the "{field}" field should be empty')
def step_impl(context, field):
    element = context.driver.find_element(By.ID, field.lower())
    assert element.get_attribute('value') == ''

############################################
# Steps específicos para listagem e busca
############################################

@then('I should see "{count}" products in the results')
def step_impl(context, count):
    results = WebDriverWait(context.driver, context.wait_seconds).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#search_results tbody tr"))
    )
    assert len(results) == int(count)

@then('I should see "{text}" in the results')
def step_impl(context, text):
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        EC.text_to_be_present_in_element((By.ID, "search_results"), text)
    )

@then('I should not see "{text}" in the results')
def step_impl(context, text):
    assert text not in context.driver.page_source

############################################
# Steps para copiar/colar ID
############################################

@when('I copy the "{field}" field')
def step_impl(context, field):
    element = context.driver.find_element(By.ID, field.lower())
    context.clipboard = element.get_attribute('value')

@when('I paste the "{field}" field')
def step_impl(context, field):
    element = context.driver.find_element(By.ID, field.lower())
    element.clear()
    element.send_keys(context.clipboard)