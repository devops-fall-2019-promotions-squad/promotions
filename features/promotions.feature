Feature: The promotion service back-end
    As a Promotion Squad Owner
    I need a RESTful catalog service
    So that I can keep track of all my promotions

Background:
    Given the following promotions
        | code      | percentage    | products    | start_date | expiry_date |
        | Save 25   | 75            |10001,10002  | 10/01/2019 | 12/31/2019  |
        | Save 50   | 50            |20001,20002  | 11/01/2019 | 01/01/2020  |

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

Scenario: Update a Promotion
    When I visit the "Home Page"
    And I set the "Code" to "Save 25"
    And I press the "Search" button
    Then I should see "Save 25" in the "Code" field
    And I should see "75" in the "Percentage" field
    When I change "Code" to "Discount 25"
    And I press the "Update" button
    Then I should see the message "Success"
    When I copy the "ID" field
    And I press the "Clear" button
    And I paste the "ID" field
    And I press the "Retrieve" button
    Then I should see "Discount 25" in the "Code" field
    When I press the "Clear" button
    And I press the "Search" button
    Then I should see "Discount 25" in the results
    Then I should not see "Save 25" in the results

Scenario: Read a Promotion
    When I visit the "Home Page"
    And I set the "Code" to "Save 25"
    And I press the "Search" button
    Then I should see "Save 25" in the "Code" field
    When I copy the "ID" field
    And I press the "Clear" button
    And I paste the "ID" field
    And I press the "Retrieve" button
    Then I should see "Save 25" in the "Code" field
    And I should see "75" in the "Percentage" field
    And I should see "10001,10002" in the "Product IDs" field
    And I should see "10/01/2019" in the "Start Date" field
    And I should see "12/31/2019" in the "Expiry Date" field

Scenario: Delete a Promotion
    When I visit the "Home Page"
    And I set the "Code" to "Save 25"
    And I press the "Search" button
    Then I should see "Save 25" in the "Code" field
    And I should see "75" in the "Percentage" field
    When I press the "Delete" button
    Then I should see the message "Promotion has been Deleted!"
    When I copy the "ID" field
    And I press the "Clear" button
    And I paste the "ID" field
    And I press the "Retrieve" button
    Then I should see the message "404 Not Found"

Scenario: Apply Get Discounted Prices Action on A Set of Products
    When I visit the "Home Page"
    And I set the "Code" to "Save 25"
    And I press the "Search" button
    Then I should see "Save 25" in the "Code" field
    And I should see "75" in the "Percentage" field
    And I should see "10001,10002" in the "Product IDs" field
    And I should see "10/01/2019" in the "Start Date" field
    And I should see "12/31/2019" in the "Expiry Date" field
    When I copy the "ID" field
    And I press the "Action Tab" button
    And I paste the "Action ID" field
    And I set the "Action Product ID 1" to "10001"
    And I set the "Action Product Price 1" to "100"
    And I press the "Add Product" button
    And I set the "Action Product ID 2" to "10010"
    And I set the "Action Product Price 2" to "200"
    And I press the "Apply" button
    Then I should see "75" in the "Action Product New Price 1" field
    And I should see "200" in the "Action Product New Price 2" field

Scenario: Query a Promotion
    When I visit the "Home Page"
    And I set the "Code" to "Save 25"
    And I press the "Search" button
    Then I should see "Save 25" in the "Code" field
    And I should see "75" in the "Percentage" field
    And I should see "10001,10002" in the "Product IDs" field
    And I should see "10/01/2019" in the "Start Date" field
    And I should see "12/31/2019" in the "Expiry Date" field

Scenario: List Promotions
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see "Save 25" in the results
    And I should see "Save 50" in the results
