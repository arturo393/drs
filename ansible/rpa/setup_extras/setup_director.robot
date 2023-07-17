*** Settings ***
Documentation       Setup Service Apply Rules.

Library             RPA.Browser.Playwright
Library             Dialogs
Library             RPA.RobotLogListener

*** Variables ***
${host}    %{host}
${passwd}    %{passwd}
${hostname}    ${hostname}
${address}    ${address}

*** Tasks ***
Setup Endpoints
    Log To Console    ---
    Open Icingaweb2 page
    Login
    Add Director Zone    ${hostname}
    Add Director Endpoint    ${hostname}
    Add Director Host    ${hostname}    ${address}

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

Add Director Endpoint
    [Arguments]    ${hostname}
    Log To Console    Add ${hostname} endpoint
    Close Page    CURRENT
    New Page    http://${host}/director/endpoint/add?type=object 
    Type Text    css=#object_name    ${hostname}
    Select Options By    css=#zone_id    label    ${hostname}
    Click    css=#Add
    Wait Until Network Is Idle

Add Director Zone
    [Arguments]    ${hostname}
    Log To Console    Add ${hostname} endpoint
    Close Page    CURRENT
    New Page    http://${host}/director/zone/add?type=object 
    Type Text    css=#object_name    ${hostname}
    Select Options By    css=#parent_id    label    master
    Click    css=#Add
    Wait Until Network Is Idle

Add Director Host
    [Arguments]    ${object_name}    ${address}
    Log To Console    Add Director Custom Field ${object_name}
    Close Page    CURRENT
    New Page    http://${host}/director/host/add?type=object
    Select Options By    css=#imports    label    dmu-host-template
    Type Text    css=#object_name    ${object_name}
    Type Text    css=#display_name    ${object_name}
    Type Text    css=#address    ${address}
    Click    css=#Add


    Wait Until Network Is Idle

Deploy
    Log To Console    Deploy changes
    Close Page    CURRENT
    New Page    http://${host}/director/config/activities
    Click    xpath=/html/body/div[1]/div[2]/div[2]/div[1]/div[1]/div/form/input[3]
    Wait Until Network Is Idle
