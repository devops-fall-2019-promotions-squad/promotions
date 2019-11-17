Feature: The promotion service back-end
    As a Promotion Squad Owner
    I need a RESTful catalog service
    So that I can keep track of all my promotions

Background:
    Given the server is started

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Promotion Demo RESTful Service" in the title
    And I should not see "404 Not Found"

Scenario: Create a Promotion
    When I visit the "Home Page"
    And I set the "Code" to "Save 20"
    And I set the "Percentage" to "80"
    And I set the "Product IDs" to "17427,13826"
    And I set the "Start Date" to "11/15/2019"
    And I set the "Expiry Date" to "12/15/2019"
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "ID" field
    And I press the "Clear" button
    Then the "ID" field should be empty
    And the "Code" field should be empty
    And the "Percentage" field should be empty
    And the "Product IDs" field should be empty
    And the "Start Date" field should be empty
    And the "Expiry Date" field should be empty
    When I paste the "ID" field
    And I press the "Retrieve" button
    Then I should see "Save 20" in the "Code" field
    And I should see "80" in the "Percentage" field
    And I should see "17427,13826" in the "Product IDs" field
    And I should see "11/15/2019" in the "Start Date" field
    And I should see "12/15/2019" in the "Expiry Date" field
