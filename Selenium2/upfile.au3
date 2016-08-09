ControlFocus("upfile.html", "", "Edit1")

WinWait("[CLASS:#32770]", "", 10)

ControlSetText("upfile.html", "", "Edit1", "D:\\workspace\Selenium2\upfile.html")
Sleep(2000)

ControlClick("upfile.html", "", "Button1");
