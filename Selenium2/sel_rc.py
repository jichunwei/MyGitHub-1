from selenium import selenium

sel = selenium("localhost", 4444, '*firefox', 'https://www.baidu.com/')
sel.start()

sel.open('/')
sel.type("id=kw", 'selenium Grid')
sel.wait_for_page_load('3000')

sel.stop()
