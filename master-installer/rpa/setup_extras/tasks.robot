*** Settings ***
Documentation       Setup Extras.

Library             RPA.Browser.Playwright
Library             Dialogs

*** Variables ***
${host}    %{host}
${passwd}    %{passwd}

*** Tasks ***
Setup Extras
    Open Icingaweb2 page
    Login
    Setup Director Module
    Setup Dependencies Module
    Setup RS485 Module
    Setup Graphite Module
    Setup Sigma Theme

*** Keywords ***
Open Icingaweb2 page
    New Browser     headless=${False}
    New Page    http://${host}/authentication/login

Login
    Type Text    xpath=/html/body/div[1]/div/div/div/div/form/div[1]/input    admin
    Type Text    xpath=/html/body/div[1]/div/div/div/div/form/div[2]/input    ${passwd}
    Click    xpath=/html/body/div[1]/div/div/div/div/form/div[3]/input
    Wait Until Network Is Idle

Setup Sigma Theme
    Close Page    CURRENT
    New Page    http://${host}/config/general

    Select Options By    xpath=//select[@name="themes_default"]    value    sigma-theme/default
    Click    css=#form_config_general-npvmijclsxhk > div:nth-child(11) > label > span    # Users Can't Change Theme
    Click    xpath=//input[@name="btn_submit"]   # Save Changes

Setup Graphite Module
    Close Page    CURRENT
    New Page    http://${host}/graphite/config/backend

    Type Text    xpath=//input[@name="graphite_url"]    http://${host}:8080
    Type Text    xpath=//input[@name="graphite_user"]    root
    Type Text    xpath=//input[@name="graphite_password"]    root

    Click    xpath=//input[@name="btn_submit"]    # Save Changes
Setup RS485 Module
    Create Resource
                ...    rs485_db
                ...    director
                ...    director
                ...    ${passwd}
                ...    utf8
    Close Page    CURRENT
    New Page    http://${host}/rs485/config/backend

    Select Options By    xpath=//select[@name="backend_resource"]    value    rs485_db

    Click    xpath=//input[@name="btn_submit"]            # Save Changes
Setup Director Module
    Create Resource
                ...    director_db
                ...    director
                ...    director
                ...    ${passwd}
                ...    utf8

    ###########################################################################################################################
    Close Page    CURRENT
    New Page    http://${host}/director
    Select Options By    css=#resource    value    director_db
    Sleep    1    # just in case
    Click    css=#Createschema        # Create Schema

    Type Text    css=#endpoint    ${host}
    Type Text    css=#host    ${host}
    Type Text    css=#username    root
    Type Text    css=#password    ${passwd}
    Click    css=#Runimport        # Run Import

    Wait Until Network Is Idle
    ###########################################################################################################################
    Add Director Custom Field
                ...    parents
                ...    Parent Hosts
                ...    Array

    Add Director Custom Field
                ...    isDMUPort
                ...    If is a DMU Port That Connects RDUs
                ...    Boolean

Add Director Custom Field
    [Arguments]
    ...    ${varname}
    ...    ${caption}
    ...    ${datatype}

    Close Page    CURRENT
    New Page    http://${host}/director/datafield/add
    Type Text    css=#varname    ${varname}
    Type Text    css=#caption    ${caption}
    Select Options By    css=#datatype    label    ${datatype}
    Click    css=#Add

Setup Dependencies Module
    Create Resource
                ...    dependencies
                ...    dependencies
                ...    dependencies
                ...    ${passwd}
                ...    utf8

    Close Page    CURRENT
    New Page    http://${host}/network_maps/module/kickstart
    Select Options By    css=#resource-field    value    dependencies
    Type Text    css=#host-field    ${host}
    Type Text    css=#port-field    5665
    Type Text    css=#user-field    dependencies
    Type Text    css=#password-field    ${passwd}

    Click    css=#button-element > input[type=submit]        # Submit

Create Resource
    [Arguments]
    ...    ${resource_name}
    ...    ${database_name}
    ...    ${username}
    ...    ${passwd}
    ...    ${charset}

    Close Page    CURRENT
    New Page    http://${host}/config/createresource

    Type Text    xpath=//input[@name="name"]    ${resource_name}     # Resource Name
    Type Text    xpath=//input[@name="dbname"]    ${database_name}        # Database Name
    Type Text    xpath=//input[@name="username"]    ${username}        # Username
    Type Text    xpath=//input[@name="password"]    ${passwd}       # Password
    Type Text    xpath=//input[@name="charset"]    ${charset}           # Character Set
    Click    xpath=//input[@name="resource_validation"]
    ${val}    Get Text    xpath=//ul[@class="notification-info"]/li
    IF    "${val}" != "The configuration has been successfully validated."
        Fail    Error al crear el recurso ${resource_name}
    END

    Click    xpath=//input[@name="btn_submit"]        # Save Changes