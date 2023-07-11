*** Settings ***
Documentation       Icingaweb2 setup.
Library             RPA.Browser.Playwright
Library    RPA.FileSystem
Library    Dialogs

*** Variables ***
${host}    %{host}
${passwd}    %{passwd}
${token}    %{token}

*** Tasks ***
Setup Icingaweb2
    Log To Console    ---
    New Browser     headless=${False}
    Set Browser Timeout    1m 30 seconds
    New Page    http://${host}/setup

    # Setup Token
    Log To Console    Setup Token
    Type Text    //input[@name="token"]    ${token}
    Click    //button[@name="btn_next" and @class="control-button btn-primary"]
    Wait Until Network Is Idle

    # Modules
    Log To Console    Modules
    Click    //*[@id="setup_modules"]/div[1]/div/div/label/span
    Click    //*[@id="setup_modules"]/div[3]/div/div/label/span
    # Click    xpath=/html/body/div[1]/div[1]/div[2]/form/div[8]/button[3]
    Click    xpath=//button[@name="btn_next" and @class="control-button btn-primary" and @class="control-button btn-primary"]
    Wait Until Network Is Idle

    # Icinga Web 2
    Log To Console    Icinga Web 2
    # Click    xpath=/html/body/div[1]/div[1]/div[2]/form/div/button[3]
    Click    xpath=//button[@name="btn_next" and @class="control-button btn-primary"]
    Wait Until Network Is Idle

    # Authentication
    Log To Console    Authentication
    # Click    xpath=/html/body/div[1]/div[1]/div[2]/form/div[3]/button[3]
    Sleep    1s
    Wait Until Network Is Idle
    Click    xpath=//button[@name="btn_next" and @class="control-button btn-primary"]
    Wait Until Network Is Idle

    # Database Resource
    Log To Console    Database Resource
    Type Text    //input[@name="port"]    3306
    Type Text    //input[@name="dbname"]    icingaweb2
    Type Text    //input[@name="username"]    root
    Type Text    //input[@name="password"]    ${passwd}
    Type Text    //input[@name="charset"]    utf8
    # Click    xpath=/html/body/div[1]/div[1]/div[2]/form/div[11]/input
    Click    xpath=//input[@name="backend_validation"]
    ${val}    Get Text    //ul[@class="notification-info"]/li
    IF    "${val}" != "The configuration has been successfully validated."
        Fail    No paso la validación de la etapa "Database Resource"
    END
    # Click    xpath=/html/body/div[1]/div[1]/div[2]/form/div[12]/button[3]
    Click    xpath=//button[@name="btn_next" and @class="control-button btn-primary"]
    Wait Until Network Is Idle

    # Authentication Backend
    Log To Console    Authentication Backend
    # Click    xpath=/html/body/div[1]/div[1]/div[2]/form/div[3]/button[3]
    Click    xpath=//button[@name="btn_next" and @class="control-button btn-primary"]
    Wait Until Network Is Idle

    # Administration
    Log To Console    Administration
    Type Text    //input[@name="new_user"]    admin
    Type Text    //input[@name="new_user_password"]    ${passwd}
    Type Text    //input[@name="new_user_2ndpass"]    ${passwd}
    # Click    xpath=/html/body/div[1]/div[1]/div[2]/form/div[5]/button[3]
    Click    xpath=//button[@name="btn_next" and @class="control-button btn-primary"]
    Wait Until Network Is Idle

    # Application Configuration
    Log To Console    Application Configuration
    # Click    xpath=/html/body/div[1]/div[1]/div[2]/form/div[10]/button[3]
    Click    xpath=//button[@name="btn_next" and @class="control-button btn-primary"]
    Wait Until Network Is Idle

    # You've configured Icinga Web 2 successfully.
    Click    xpath=/html/body/div[1]/div[1]/div[2]/form/div/button[3]
    # Click    xpath=//button[@name="btn_next" and @class="control-button btn-primary finish"]
    Wait Until Network Is Idle

    # Welcome to the configuration of the monitoring module for Icinga Web 2!
    # Click    xpath=/html/body/div[1]/div[1]/div[2]/form/div[2]/button[3]
    Click    xpath=//button[@name="btn_next" and @class="control-button btn-primary"]
    Wait Until Network Is Idle

    # Monitoring Backend
    Log To Console    Monitoring Backend
    # Click    xpath=/html/body/div[1]/div[1]/div[2]/form/div[4]/button[3]
    Click    xpath=//button[@name="btn_next" and @class="control-button btn-primary"]
    Wait Until Network Is Idle

    # Monitoring IDO Resource
    Log To Console    Monitoring IDO Resource
    Type Text    //input[@name="port"]    3306
    Type Text    //input[@name="dbname"]    icinga2
    Type Text    //input[@name="username"]    root
    Type Text    //input[@name="password"]    ${passwd}
    Type Text    //input[@name="charset"]    utf8
    # Click    xpath=/html/body/div[1]/div[1]/div[2]/form/div[11]/input
    Click    xpath=//input[@name="backend_validation"]
    ${val}    Get Text    //ul[@class="notification-info"]/li
    IF    "${val}" != "The configuration has been successfully validated."
        Fail    No paso la validación de la etapa "Monitoring IDO Resource"
    END
    # Click    xpath=/html/body/div[1]/div[1]/div[2]/form/div[12]/button[3]
    Click    xpath=//button[@name="btn_next" and @class="control-button btn-primary"]
    Wait Until Network Is Idle

    # Command Transport
    Log To Console    Command Transport
    Type Text    xpath=/html/body/div[1]/div[1]/div[2]/form/div[4]/input        localhost
    Type Text    xpath=//input[@name="username"]    root
    Type Text    xpath=//input[@name="password"]    ${passwd}
    # Click    xpath=/html/body/div[1]/div[1]/div[2]/form/div[8]/input
    Click    xpath=//input[@name="transport_validation"]
    ${val}    Get Text    //ul[@class="notification-info"]/li
    IF    "${val}" != "The configuration has been successfully validated."
        Fail    No paso la validación de la etapa "Command TransportCommand Transport"
    END
    # Click    xpath=/html/body/div[1]/div[1]/div[2]/form/div[9]/button[3]
    Click    xpath=//button[@name="btn_next" and @class="control-button btn-primary"]
    Wait Until Network Is Idle

    # Monitoring Security
    Log To Console    Monitoring Security
    # Click    xpath=/html/body/div[1]/div[1]/div[2]/form/div[3]/button[3]
    Click    xpath=//button[@name="btn_next" and @value="setup_monitoring_summary" and @class="control-button btn-primary"]
    Wait Until Network Is Idle

    # You've configured the monitoring module successfully
    # Click    xpath=/html/body/div[1]/div[1]/div[2]/form/div/button[3]
    
    Click    xpath=//button[@name="btn_next" and @class="control-button btn-primary finish"]
    Wait Until Network Is Idle

    # # Finish
    ${val}    Get Text    css=#setup-finish > h2
    Log To Console    ${val}

