## Evoman

Evoman is a video game playing framework inspired on Megaman.

A demo can be found here:  https://www.youtube.com/watch?v=ZqaMjd1E4ZI

#### Installation
```bash
pipenv install --dev
pipenv shell
```

#### Play yourself
```bash
python human_demo.py
```

#### Changes to the original evoman framework
  - Fix issue with `getchildren` in `tmx` on Python 3.9
  - Remove python cached files
    ```
    find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf
    ```
  - Make imports absolute to allow importing from the top level dir
