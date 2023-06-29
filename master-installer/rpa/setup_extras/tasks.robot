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

    Select Options By    xpath=/html/body/div[1]/div[2]/div[2]/div[1]/div[2]/form/div[10]/select    value    sigma-theme/default
    Click    /html/body/div[1]/div[2]/div[2]/div[1]/div[2]/form/div[11]/label/span    # Users Can't Change Theme
    Click    xpath=/html/body/div[1]/div[2]/div[2]/div[1]/div[2]/form/div[13]/input   # Save Changes

Setup Graphite Module
    Close Page    CURRENT
    New Page    http://${host}/graphite/config/backend

    Type Text    xpath=/html/body/div[1]/div[2]/div[2]/div[1]/div[2]/form/div[1]/input    http://${host}:8080
    Type Text    xpath=/html/body/div[1]/div[2]/div[2]/div[1]/div[2]/form/div[2]/input    root
    Type Text    xpath=/html/body/div[1]/div[2]/div[2]/div[1]/div[2]/form/div[3]/input    root

    Click    xpath=/html/body/div[1]/div[2]/div[2]/div[1]/div[2]/form/div[5]/input    # Save Changes
Setup RS485 Module
    Create Resource
                ...    rs485_db
                ...    director
                ...    director
                ...    ${passwd}
                ...    utf8
    Close Page    CURRENT
    New Page    http://${host}/rs485/config/backend

    Select Options By    xpath=/html/body/div[1]/div[2]/div[2]/div[1]/div[2]/form/div[1]/select    value    rs485_db

    Click    xpath=/html/body/div[1]/div[2]/div[2]/div[1]/div[2]/form/div[2]/input            # Save Changes
Setup Director Module
    Create Resource
                ...    director_db
                ...    director
                ...    director
                ...    ${passwd}
                ...    utf8

    ###########################################################################################################################
    Click    xpath=/html/body/div[1]/div[2]/div[1]/div[3]/nav/ul/li[4]/a                # Director Nav Menu
    Select Options By    /html/body/div[1]/div[2]/div[2]/div[1]/div[2]/form/fieldset/dl/dd/select    value    director_db

    Click    xpath=/html/body/div[1]/div[2]/div[2]/div[1]/div[2]/form/dd/dl/input        # Create Schema

    Type Text    xpath=/html/body/div[1]/div[2]/div[2]/div[1]/div[2]/form/fieldset[2]/dl/dd[1]/input    ${host}
    Type Text    xpath=/html/body/div[1]/div[2]/div[2]/div[1]/div[2]/form/fieldset[2]/dl/dd[2]/input    ${host}
    Type Text    xpath=/html/body/div[1]/div[2]/div[2]/div[1]/div[2]/form/fieldset[2]/dl/dd[4]/input    root
    Type Text    xpath=/html/body/div[1]/div[2]/div[2]/div[1]/div[2]/form/fieldset[2]/dl/dd[5]/input    ${passwd}
    Click    xpath=/html/body/div[1]/div[2]/div[2]/div[1]/div[2]/form/dd/dl/input        # Run Import

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
    Select Options By    xpath=/html/body/div[1]/div[2]/div[2]/div[1]/div[2]/form[1]/fieldset/dl/dd/select    value    dependencies
    Type Text    xpath=/html/body/div[1]/div[2]/div[2]/div[1]/div[2]/form[2]/fieldset/dl/dd[1]/input    ${host}
    Type Text    xpath=/html/body/div[1]/div[2]/div[2]/div[1]/div[2]/form[2]/fieldset/dl/dd[2]/input    5665
    Type Text    xpath=/html/body/div[1]/div[2]/div[2]/div[1]/div[2]/form[2]/fieldset/dl/dd[3]/input    dependencies
    Type Text    xpath=/html/body/div[1]/div[2]/div[2]/div[1]/div[2]/form[2]/fieldset/dl/dd[4]/input    ${passwd}

    Click    xpath=/html/body/div[1]/div[2]/div[2]/div[1]/div[2]/form[2]/fieldset/dd/input        # Submit

Create Resource
    [Arguments]
    ...    ${resource_name}
    ...    ${database_name}
    ...    ${username}
    ...    ${passwd}
    ...    ${charset}

    Close Page    CURRENT
    New Page    http://${host}/config/createresource

    Type Text    xpath=/html/body/div[1]/div[2]/div[2]/div[2]/div[2]/form/div[3]/input    ${resource_name}     # Resource Name
    Type Text    xpath=/html/body/div[1]/div[2]/div[2]/div[2]/div[2]/form/div[7]/input    ${database_name}        # Database Name
    Type Text    xpath=/html/body/div[1]/div[2]/div[2]/div[2]/div[2]/form/div[8]/input    ${username}        # Username
    Type Text    xpath=/html/body/div[1]/div[2]/div[2]/div[2]/div[2]/form/div[9]/input    ${passwd}       # Password
    Type Text    xpath=/html/body/div[1]/div[2]/div[2]/div[2]/div[2]/form/div[10]/input    ${charset}           # Character Set
    Click    xpath=/html/body/div[1]/div[2]/div[2]/div[2]/div[2]/form/div[12]/input[2]
    ${val}    Get Text    xpath=/html/body/div[1]/div[2]/div[2]/div[2]/div[2]/form/div[2]/ul/li/ul/li
    IF    "${val}" != "The configuration has been successfully validated."
        Fail    Error al crear el recurso ${resource_name}
    END

    Click    xpath=/html/body/div[1]/div[2]/div[2]/div[2]/div[2]/form/div[13]/input[1]        # Save Changes