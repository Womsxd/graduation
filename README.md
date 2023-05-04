# graduation

学生成绩管理查询系统

默认管理员账号密码:admin/admin

## 如何使用程序

- **部署方法**

    1.下载[Python3](https://www.python.org/downloads/)

    2.主目录中**Shift+右键** 打开你的命令提示符 cmd 或 powershell (windows 桌面)

    3.requirements.txt 是所需第三方模块，执行 `pip install -r requirements.txt` 安装模块

    4.复制`config.yaml.example`并改名为`config.yaml`

    5.请使用 vscode/notepad++等文本编辑器打开上一步复制好的配置文件

    6.填写cookie.secret(推荐64位随机大小写数字特殊符号)和database相关选项

    7.`python app.py`
