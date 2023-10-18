*** Settings ***
Documentation       Setup Service Apply Rules.

Library             RPA.Browser.Playwright
Library             Dialogs
Library             RPA.RobotLogListener

*** Variables ***
${host}    %{host}
${passwd}    %{passwd}
${hostname}    %{hostname}
${master_host}    %{master_host}

*** Tasks ***
Setup Service Apply Rules
    Log To Console    ---
    Open Icingaweb2 page
    Login
    Add UqommWeb host    Uqommweb    localhost-host-template    Master
    Add Master Serial host    ${hostname}    serial-host-template    ${hostname}
    Deploy

*** Keywords ***
Open Icingaweb2 page
    New Browser     headless=${False}
    Set Browser Timeout    1m 30 seconds
    New Page    http://${host}/authentication/login

Login
    Log To Console    Login
    Type Text    xpath=/html/body/div[1]/div/div/div/div/form/div[1]/input    admin
    Type Text    xpath=/html/body/div[1]/div/div/div/div/form/div[2]/input    ${passwd}
    Click    xpath=/html/body/div[1]/div/div/div/div/form/div[3]/input
    Wait Until Network Is Idle

Deploy
    Log To Console    Deploy changes
    Close Page    CURRENT
    New Page    http://${host}/director/config/activities
    Click    xpath=/html/body/div[1]/div[2]/div[2]/div[1]/div[1]/div/form/input[3]
    Wait Until Network Is Idle


Add UqommWeb host
    [Arguments]    ${object_name}    ${imports}    ${display_name}
    Log To Console    Add Director Custom Field ${object_name}
    Close Page    CURRENT
    New Page    http://${host}/director/host/add?type=object
    Select Options By    css=#imports    value    ${imports}
    Type Text    css=#object_name    ${object_name}
    Type Text    css=#display_name    ${display_name}
    Type Text    css=#address    localhost
    Click    css=#Add
    Wait Until Network Is Idle

Add Master Ethernet host
    [Arguments]    ${object_name}    ${imports}    ${display_name}
    Log To Console    Add Director Custom Field ${object_name}
    Close Page    CURRENT
    New Page    http://${host}/director/host/add?type=object
    Select Options By    css=#imports    value    ${imports}
    Type Text    css=#object_name    ${object_name}
    Type Text    css=#display_name    ${display_name}
    Type Text    css=#address    ${master_host}
    Click    css=#Add
    Wait Until Network Is Idle

Add Master Serial host
    [Arguments]    ${object_name}    ${imports}    ${display_name}
    Log To Console    Add Director Custom Field ${object_name}
    Close Page    CURRENT
    New Page    http://${host}/director/host/add?type=object
    Select Options By    css=#imports    value    ${imports}
    Type Text    css=#object_name    ${object_name}
    Type Text    css=#display_name    ${display_name}
    Type Text    css=#address    localhost
    Click    css=#Add
    Wait Until Network Is Idle