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