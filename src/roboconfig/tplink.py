import os
from playwright.sync_api import sync_playwright

PASSWORD = os.environ["TPLINK_PSK"]
NTP1_DESIRED = "10.10.10.123"
NTP2_DESIRED = "time.nist.gov"
GUEST_SSID_2G = "-NYC Mesh guest 2G-"
GUEST_SSID_5G = "-NYC Mesh guest-"

def _setup_auth(page):
    setup_selector = 'a[title="Let\'s Get Started"]'
    try:
        page.wait_for_selector(setup_selector)
        print("setting password")
        _set_password(page)
    except Exception as e:
        print(str(e))
        print("password alredy set logging in")
        _login(page)

def _set_password(page):
    page.type(".password-container .password-text.password-hidden", PASSWORD)
    page.type("#confirm-pwd-tb .password-text", PASSWORD)
    page.click('a[title="Let\'s Get Started"]')

def _login(page):
    page.type("input.password-text", PASSWORD)
    page.click('a[title="LOG IN"]')

def _quit_setup(page):
    quit_selector = 'a[title="Quit"]'
    try:
        page.wait_for_selector(quit_selector)
        page.click(quit_selector)
        page.click('a[title="QUIT"]')
        print("quit setup")
    except:
        print("no quit button, continuing")

def _set_ntp(page):
    page.goto('http://192.168.0.1/#timeSettings')
    ntp1 = 'div[label-field="{TIMESETTING.NTP1}"] input'
    ntp2 = 'div[label-field="{TIMESETTING.NTP2}"] input'
    page.wait_for_selector(ntp1)
    ntp1_actual = page.eval_on_selector(ntp1, "el => el.value")
    ntp2_actual = page.eval_on_selector(ntp2, "el => el.value")
    if NTP1_DESIRED == ntp1_actual and NTP2_DESIRED == ntp2_actual:
        print("NTP already configured")
    else:
        page.eval_on_selector(ntp1, "el => el.value = ''")
        page.eval_on_selector(ntp2, "el => el.value = ''")
        page.type(ntp1, NTP1_DESIRED)
        page.type(ntp2, NTP2_DESIRED)
        page.click('#save-data a[title="SAVE"]')

def _set_guest_network(page):
    page.goto("http://192.168.0.1/#guestNetworkAdv")
    changed = False
    try:
        page.wait_for_selector("#guest-network-adv-24g-enable .checked")
    except:
        changed = True
        page.click("#guest-network-adv-24g-enable span.text")
    guest_2g_selector = '#guest-network-adv-24g-content div[label-field="{GUEST_NW_ADV.NETWORK_NAME_SSID}"] input'
    page.eval_on_selector(guest_2g_selector, "el => el.value = ''")
    page.type(guest_2g_selector, GUEST_SSID_2G)

    try:
        page.wait_for_selector("#guest-network-adv-5g-enable .checked")
    except:
        changed = True
        page.click("#guest-network-adv-5g-enable span.text")
    guest_5g_selector = '#guest-network-adv-5g-content div[label-field="{GUEST_NW_ADV.NETWORK_NAME_SSID}"] input'
    page.eval_on_selector(guest_5g_selector, "el => el.value = ''")
    page.type(guest_5g_selector, GUEST_SSID_5G)

    if changed:
        page.click('#save-data a[title="SAVE"]')
        print("setup guest network")
    else:
        print("no changes to guest network")


def _set_auto_update(page):
    page.goto("http://192.168.0.1/#firmware")
    try:
        page.waitForSelector("#auto-update-enable .checked")
        print("auto update enabled already")
    except:
        page.click('div[label-field="{FIRMWARE.AUTO_UPDATE}"] .switch-label')
        print("auto update enabled")

def _check_update(page):
    page.goto("http://192.168.0.1/#firmware")
    check_update_selector = 'a[title="CHECK FOR UPDATES"]'

    check_update_button = None
    try:
        check_update_button = page.waitForSelector(check_update_selector)
    except:
        print("no check for updates button")
    if check_update_button is not None:
        print("checking for updates")
        page.click(check_update_selector)
        
    first_update_selector = '#online-upgrade-btn a[title="UPDATE"]'
    first_update_button = None
    try:
        page.waitForSelector(first_update_selector)
    except:
        print("update button is not visible")
        first_update_button = None
    if first_update_button is not None:
        print("clicking update")
        page.click(first_update_selector)
        page.click('#firmware-upgrade-msg-btn-ok a[title="UPDATE"]')
    else:
        print("no update available")

def tplink_setup():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("http://192.168.0.1")
        _setup_auth(page)
        _quit_setup(page)
        _set_ntp(page)
        _set_guest_network(page)
        _set_auto_update(page)
        _check_update(page)

        browser.close()
