*** Settings ***
Documentation       Setup Extras.

Library             RPA.Browser.Playwright
Library    Dialogs


*** Tasks ***
Setup Extras
    Open Icingaweb2 page
    Login
    Setup Director Module

*** Keywords ***
Open Icingaweb2 page
    New Browser     headless=${False}
    New Page    http://192.168.0.108/authentication/login

Login
    Type Text    xpath=/html/body/div[1]/div/div/div/div/form/div[1]/input    admin
    Type Text    xpath=/html/body/div[1]/div/div/div/div/form/div[2]/input    Admin.123
    Click    xpath=/html/body/div[1]/div/div/div/div/form/div[3]/input

Setup Director Module
    Click    xpath=/html/body/div[1]/div[2]/div[1]/div[3]/nav/ul/li[7]/a        # Configuration
    Click    xpath=/html/body/div[1]/div[2]/div[2]/div[1]/div[2]/a[1]           # Application
    Click    xpath=/html/body/div[1]/div[2]/div[2]/div[1]/div[1]/ul/li[2]/a     # Resources
    Click    xpath=/html/body/div[1]/div[2]/div[2]/div[1]/div[2]/a              # Add Resource
    Type Text    xpath=/html/body/div[1]/div[2]/div[2]/div[2]/div[2]/form/div[3]/input    director_db
    Type Text    xpath=/html/body/div[1]/div[2]/div[2]/div[2]/div[2]/form/div[7]/input    director
    Type Text    xpath=/html/body/div[1]/div[2]/div[2]/div[2]/div[2]/form/div[8]/input    director
    Type Text    xpath=/html/body/div[1]/div[2]/div[2]/div[2]/div[2]/form/div[9]/input    Admin.123
    Type Text    xpath=/html/body/div[1]/div[2]/div[2]/div[2]/div[2]/form/div[10]/input    utf8
    Click    xpath=/html/body/div[1]/div[2]/div[2]/div[2]/div[2]/form/div[12]/input[2]
    ${val}    Get Text    xpath=/html/body/div[1]/div[2]/div[2]/div[2]/div[2]/form/div[2]/ul/li/ul/li
    IF    "${val}" != "The configuration has been successfully validated."
        Fail    Error al configurar el modulo director
    END
    # Save Changes
    Click    xpath=/html/body/div[1]/div[2]/div[2]/div[2]/div[2]/form/div[13]/input[1]
    Click    xpath=/html/body/div[1]/div[2]/div[1]/div[3]/nav/ul/li[4]/a    # Director menu
    Click    xpath=/html/body/div[1]/div[2]/div[2]/div[1]/div[2]/form/dd/dl/input    # Create Schema
    Select Options By    xpath=/html/body/div[1]/div[2]/div[2]/div[1]/div[2]/form/fieldset[1]/dl/dd/select    value    director_db
    Type Text    xpath=/html/body/div[1]/div[2]/div[2]/div[1]/div[2]/form/fieldset[2]/dl/dd[1]/input    master
    Type Text    xpath=/html/body/div[1]/div[2]/div[2]/div[1]/div[2]/form/fieldset[2]/dl/dd[2]/input    192.168.0.108
    Type Text    xpath=/html/body/div[1]/div[2]/div[2]/div[1]/div[2]/form/fieldset[2]/dl/dd[4]/input    root
    Type Text    xpath=/html/body/div[1]/div[2]/div[2]/div[1]/div[2]/form/fieldset[2]/dl/dd[5]/input    Admin.123
    Click    xpath=/html/body/div[1]/div[2]/div[2]/div[1]/div[2]/form/dd/dl/input        # Run Import
        

    Pause Execution


# Resource Name: director_db
# Database Name: director
# Username: director
# Password: Admin.123
# Charset: utf8