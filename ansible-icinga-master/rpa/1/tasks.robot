*** Settings ***
Documentation       Icingaweb2 setup.
Library             RPA.Browser.Playwright
Library    RPA.FileSystem

*** Tasks ***
Minimal task
    ${token}    Read File    /etc/icingaweb2/setup.token
    Log to Console    ${token}
    New Browser     headless=${True}
    New Page    http://localhost/setup

    # Setup Token
    Type Text    //input[@name="token"]    ${token}
    Click    //button[@name="btn_next"]
    Wait Until Network Is Idle

    # Modules
    Click    //*[@id="setup_modules"]/div[1]/div/div/label/span
    Click    //*[@id="setup_modules"]/div[3]/div/div/label/span
    Click    //button[@name="btn_next"]
    Wait Until Network Is Idle

    # Icinga Web 2
    Click    //button[@name="btn_next"]
    Wait Until Network Is Idle

    # Authentication
    Click    //button[@name="btn_next"]
    Wait Until Network Is Idle

    # Database Resource
    Type Text    //input[@name="port"]    3306
    Type Text    //input[@name="dbname"]    icingaweb2
    Type Text    //input[@name="username"]    root
    Type Text    //input[@name="password"]    Admin.123
    Type Text    //input[@name="charset"]    utf8
    Click    //input[@name="backend_validation"]
    ${val}    Get Text    //ul[@class="notification-info"]/li
    IF    "${val}" != "The configuration has been successfully validated."
        Fail    No paso la validación de la etapa "Database Resource"
    END
    Click    //button[@name="btn_next"]
    Wait Until Network Is Idle

    # Authentication Backend
    Click    //button[@name="btn_next"]
    Wait Until Network Is Idle

    # Administration
    Type Text    //input[@name="new_user"]    admin
    Type Text    //input[@name="new_user_password"]    Admin.123
    Type Text    //input[@name="new_user_2ndpass"]    Admin.123
    Click    //button[@name="btn_next"]
    Wait Until Network Is Idle

    # Application Configuration
    Click    //button[@name="btn_next"]
    Wait Until Network Is Idle

    # You've configured Icinga Web 2 successfully.
    Click    //button[@name="btn_next"]
    Wait Until Network Is Idle

    # Welcome to the configuration of the monitoring module for Icinga Web 2!
    Click    //button[@name="btn_next"]
    Wait Until Network Is Idle

    # Monitoring Backend
    Click    //button[@name="btn_next"]
    Wait Until Network Is Idle

    # Monitoring IDO Resource
    Type Text    //input[@name="port"]    3306
    Type Text    //input[@name="dbname"]    icinga2
    Type Text    //input[@name="username"]    root
    Type Text    //input[@name="password"]    Admin.123
    Type Text    //input[@name="charset"]    utf8
    Click    //input[@name="backend_validation"]
    ${val}    Get Text    //ul[@class="notification-info"]/li
    IF    "${val}" != "The configuration has been successfully validated."
        Fail    No paso la validación de la etapa "Monitoring IDO Resource"
    END
    Click    //button[@name="btn_next"]
    Wait Until Network Is Idle

    # Command Transport
    Type Text    //input[@name="host"]    localhost
    Type Text    //input[@name="username"]    root
    Type Text    //input[@name="password"]    Admin.123
    Click    //input[@name="transport_validation"]
    ${val}    Get Text    //ul[@class="notification-info"]/li
    IF    "${val}" != "The configuration has been successfully validated."
        Fail    No paso la validación de la etapa "Command TransportCommand Transport"
    END
    Click    //button[@name="btn_next"]
    Wait Until Network Is Idle

    # Monitoring Security
    Click    //button[@name="btn_next"]
    Wait Until Network Is Idle

    # You've configured the monitoring module successfully
    Click    //button[@name="btn_next"]
    Wait Until Network Is Idle

    # Finish
    ${val}    Get Text    //*[@id="setup-finish"]/h2//*[@id="setup-finish"]/h2
    Log To Console    ${val}