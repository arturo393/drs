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
    Add Master host    ${hostname}    drs-alive-host-template    ${hostname}
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

Add Director Service Apply Data
    [Arguments]    ${object_name}    ${imports}    ${assign_filter-id_1-column}    ${assign_filter-id_1-sign}    ${assign_filter-id_1-value}
    Log To Console    Add Director Custom Field ${object_name}
    Close Page    CURRENT
    New Page    http://${host}/director/service/add?type=apply
    Type Text    css=#object_name    ${object_name}
    Type Text    css=#imports    ${imports}
    Click    xpath=/html/body/div[1]/div[2]/div[2]/div[1]/div[2]/form/fieldset[2]/dl/dd/ul/div/input[1]
    Type Text    css=#assign_filter-id_1-column    ${assign_filter-id_1-column}
    Click    xpath=/html/body/div[1]/div[2]/div[2]/div[1]/div[2]/form/fieldset[2]/dl/dd/ul/div/select
    Click    xpath=/html/body/div[1]/div[2]/div[2]/div[1]/div[2]/form/fieldset[2]/dl/dd/ul/div/select
    Select Options By    css=#assign_filter-id_1-sign    label    ${assign_filter-id_1-sign}
    Click    xpath=/html/body/div[1]/div[2]/div[2]/div[1]/div[2]/form/fieldset[2]/dl/dd/ul/div/div/input
    Type Text    css=#assign_filter-id_1-value    ${assign_filter-id_1-value}
    Click    css=#Add
    Wait Until Network Is Idle

Add Director OPT Service Apply Data
    [Arguments]    ${object_name}    ${imports}    ${assign_filter-id_1-column}    ${assign_filter-id_1-sign}    ${assign_filter-id_1-value}    ${port}
    Log To Console    Add Director Custom Field ${object_name}
    Close Page    CURRENT
    New Page    http://${host}/director/service/add?type=apply
    Type Text    css=#object_name    ${object_name}
    Type Text    css=#imports    ${imports}
    Click    xpath=/html/body/div[1]/div[2]/div[2]/div[1]/div[2]/form/fieldset[2]/dl/dd/ul/div/input[1]
    Type Text    css=#assign_filter-id_1-column    ${assign_filter-id_1-column}
    Click    xpath=/html/body/div[1]/div[2]/div[2]/div[1]/div[2]/form/fieldset[2]/dl/dd/ul/div/select
    Click    xpath=/html/body/div[1]/div[2]/div[2]/div[1]/div[2]/form/fieldset[2]/dl/dd/ul/div/select
    Select Options By    css=#assign_filter-id_1-sign    label    ${assign_filter-id_1-sign}
    Click    xpath=/html/body/div[1]/div[2]/div[2]/div[1]/div[2]/form/fieldset[2]/dl/dd/ul/div/div/input
    Type Text    css=#assign_filter-id_1-value    ${assign_filter-id_1-value}
    Click    xpath=/html/body/div[1]/div[2]/div[2]/div[1]/div[2]/form/fieldset[3]/legend/span
    Type Text    css=#var_port    ${port}
    Click    css=#Add
    Wait Until Network Is Idle

Add Director host Service Apply Data
    [Arguments]    ${object_name}    ${imports}    ${assign_filter-id_1-column}    ${assign_filter-id_1-sign}    ${assign_filter-id_1-value}    ${cmd}
    Log To Console    Add Director Custom Field ${object_name}
    Close Page    CURRENT
    New Page    http://${host}/director/service/add?type=apply
    Type Text    css=#object_name    ${object_name}
    Type Text    css=#imports    ${imports}
    Click    xpath=/html/body/div[1]/div[2]/div[2]/div[1]/div[2]/form/fieldset[2]/dl/dd/ul/div/input[1]
    Type Text    css=#assign_filter-id_1-column    ${assign_filter-id_1-column}
    Click    xpath=/html/body/div[1]/div[2]/div[2]/div[1]/div[2]/form/fieldset[2]/dl/dd/ul/div/select
    Click    xpath=/html/body/div[1]/div[2]/div[2]/div[1]/div[2]/form/fieldset[2]/dl/dd/ul/div/select
    Select Options By    css=#assign_filter-id_1-sign    label    ${assign_filter-id_1-sign}
    Click    xpath=/html/body/div[1]/div[2]/div[2]/div[1]/div[2]/form/fieldset[2]/dl/dd/ul/div/div/input
    Type Text    css=#assign_filter-id_1-value    ${assign_filter-id_1-value}
    Type Text    css=#check_command    ${cmd}
    Click    css=#Add
    Click    css=#Add
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

Add Master host
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