# x-notification-telegram-bot
Get new post from Twitter (or X) on telegram


## Setup
Firstly, install requirements materials

1. python env
```
pip install -r requirements.txt
```
2. chrominum driver
driver
```
sudo apt install chromium-chromedriver
```
browser
```
sudo apt install chromium-browser
```

version of driver must be match on browser
3. selenium webdriver
webdriver
```
pip install selenium
```


Secondary, edit data in `config.py` file

Finally, run bot

```
python3 main.py
```

## Usage
Interact with bot using command:
1.  add user get notification
```
/add_user <x_username>
````
2.  remove user from database, user list
```
/remove_user <x_username_from_list_users>
```
3.  check user got notification from list user
```
/list_users
```
4.  start get notification
After setting please ```/start_crawl``` for reset bot

