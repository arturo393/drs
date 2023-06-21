*** Settings ***
Documentation       Icingaweb2 setup.
Library             RPA.Browser.Playwright
Library    RPA.FileSystem

*** Tasks ***
Minimal task
    ${token}    Read File    /etc/icingaweb2/setup.token
    Log to Console    ${token}
    # New Browser     headless=${False}  # starts in headless in Control Room
    # New Page    https://robocorp.com/docs/development-guide/browser/playwright
