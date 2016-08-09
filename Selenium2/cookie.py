# coding:utf-8
'''
    操作cookie
    webdriver
    get_cookies()
    get_cookie(name)： 返回字典的Keyw为“name”的cookie信息
    add_cookie(cookie_dict): 添加cookie。 “cook_dict"指字典的对象， 必须有name和value
    delete_cookie(name, optionsString):
    delete_all_cookies() 
'''
from selenium import webdriver

driver = webdriver.Firefox()
driver.get("http://www.youdao.com")

# 获得cookie信息
cookie = driver.get_cookies()
# 将获得cookie的信息打印
print cookie

# 向cookie的name 和 value中添加会话信息
driver.add_cookie({'name': 'key_tan', 'value': 'value_tan'})

# 遍历 cookies 中的name 和value信息并打印， 当然还有上面添加的信息
for cookie in driver.get_cookies():
    print "%s--> %s" % (cookie['name'], cookie['value'])

# quit webbrowser
driver.quit()
