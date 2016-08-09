from selenium import webdriver
from time import sleep, ctime

driver = webdriver.Firefox()
driver.get("http://www.baidu.com")

print ctime()

for i in range(10):
    try:
        e1 = driver.find_element_by_id("kww22")
        if e1.is_displayed():
            break
    except: pass
    sleep(1)
else:
    print "time out"

driver.close()
print ctime()
